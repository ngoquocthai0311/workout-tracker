from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select, and_
from sqlalchemy.orm import joinedload

from app.database.models import Routine, RoutineExercise, RoutineExerciseSet
from app.routers.schemas.request_schemas import (
    CreateRoutineRequest,
    UpdateRoutineRequest,
)
from app.dependencies import get_db, get_routine_mapper
from typing import Optional
from app.routers.schemas.response_schemas import RoutineResponse
from app.routers.mappers.routines_mapper import RoutineMapper

router = APIRouter(tags=["routines"], prefix="/routines")


@router.get(
    "",
    response_model=list[RoutineResponse],
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def read_routines(
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
):
    routines = (
        session.exec(
            select(Routine).options(
                joinedload(Routine.exercise_links).joinedload(
                    RoutineExercise.routine_exercise_sets
                )
            )
        )
        .unique()
        .all()
    )

    return mapper.map_list_to_response(routines)


@router.get(
    "/{routine_id}",
    response_model=RoutineResponse,
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def get_routine(
    routine_id: int,
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
):
    routine = session.exec(
        select(Routine)
        .where(Routine.id == routine_id)
        .options(
            joinedload(Routine.exercise_links).joinedload(
                RoutineExercise.routine_exercise_sets
            )
        )
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    return mapper.transform_to_response(routine)


@router.post(
    "",
    response_model=RoutineResponse,
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def create_routine(
    input: CreateRoutineRequest,
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
):
    timestamp = datetime.now(timezone.utc).timestamp()
    routine = Routine(
        name=input.name,
        description=input.description,
        created_at=timestamp,
        updated_at=timestamp,
        user_id=input.user_id,
        exercise_links=[
            RoutineExercise(
                exercise_id=exercise.exercise_id,
                order=exercise_index + 1,
                created_at=timestamp,
                updated_at=timestamp,
                exercise_set=[
                    RoutineExerciseSet(
                        set_number=set_index + 1,
                        set_type="normal",
                        targeted_reps=each_set.targeted_reps,
                        targeted_weight=each_set.targeted_weight,
                    )
                    for set_index, each_set in enumerate(exercise.sets)
                ],
            )
            for exercise_index, exercise in enumerate(input.exercises)
        ],
    )

    session.add(routine)
    session.flush()

    session.commit()
    session.refresh(routine)
    # do eager loading before manually mapping database model to response model
    # this is to avoid sqlpmodel triggering additional queries to fetch relationship attrs

    routine = (
        session.exec(
            select(Routine)
            .where(Routine.id == routine.id)
            .options(
                joinedload(Routine.exercise_links)
                .joinedload(RoutineExercise.exercise)
                .joinedload(RoutineExercise.routine_exercise_sets)
            )
        )
        .unique()
        .one()
    )

    if not routine:
        # this case should not happen after a successful commit
        raise HTTPException(
            status_code=500, detail="Failed to retrieve created routine"
        )
    return mapper.transform_to_response(routine)


@router.patch(
    "/{routine_id}",
    response_model=RoutineResponse,
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def update_routine(
    routine_id: int,
    input: UpdateRoutineRequest,
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
):
    routine = session.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    timestamp = datetime.now(timezone.utc).timestamp()
    is_edited = False
    if input.name and routine.name != input.name:
        routine.name = input.name
        is_edited = True

    if input.description is not None and routine.description != input.description:
        routine.description = input.description
        is_edited = True

    if input.user_id and routine.user_id != input.user_id:
        routine.user_id = input.user_id
        is_edited = True

    if input.exercises and len(input.exercises) > 0:
        is_edited = True
        associated_exercise_ids = [
            exercise.exercise_id for exercise in routine.exercise_links
        ]

        # update new one
        # including new exercise add in based the index of the exercise array
        for index, exercise in enumerate(input.exercises):
            exercise_details: UpdateRoutineRequest.RoutineExerciseRequest = exercise

            # check for routine_exercise, update or create
            routine_exercise = None
            if exercise_details.exercise_id not in associated_exercise_ids:
                routine_exercise = RoutineExercise(
                    routine=routine,
                    exercise_id=exercise_details.exercise_id,
                    order=index + 1,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            else:
                routine_exercise: Optional[RoutineExercise] = session.exec(
                    select(RoutineExercise).where(
                        and_(
                            RoutineExercise.routine_id == routine_id,
                            RoutineExercise.exercise_id == exercise_details.exercise_id,
                        )
                    )
                ).one()
                routine_exercise.order = index + 1
                routine_exercise.updated_at = (timestamp,)

            # update exercise set based on exercise details
            # get a list of sets
            for index, each_set in enumerate(exercise_details.sets):
                set_details: UpdateRoutineRequest.RoutineExerciseRequest.ExerciseSet = (
                    each_set
                )
                exercise_set = None
                if not set_details.set_id:
                    exercise_set = RoutineExerciseSet(
                        routine_exercise=routine_exercise,
                        set_number=index + 1,
                        set_type="normal",
                        targeted_reps=each_set.targeted_reps,
                        targeted_weight=each_set.targeted_weight,
                    )
                    session.add(exercise_set)
                else:
                    exercise_set = session.exec(
                        select(RoutineExerciseSet).where(
                            RoutineExerciseSet.id == set_details.set_id
                        )
                    ).one()
                    exercise_set.set_number = index + 1
                    exercise_set.targeted_reps = set_details.targeted_reps
                    exercise_set.targeted_weight = set_details.targeted_weight

            session.add(routine_exercise)

    if is_edited:
        routine.updated_at = timestamp
        session.add(routine)
        session.commit()
        session.refresh(routine)

        return mapper.transform_to_response(routine)
    return Response(status_code=204)


@router.delete("/{routine_id}", dependencies=[Depends(get_db)])
def delete_routine(routine_id: int, session: Session = Depends(get_db)):
    routine = session.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    session.delete(routine)
    session.commit()
    return JSONResponse(
        status_code=200, content={"message": "Routine deleted successfully"}
    )
