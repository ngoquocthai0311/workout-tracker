from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from app.database.models import Routine, RoutineExercise, RoutineExerciseSet, Exercise
from app.routers.schemas.request_schemas import (
    CreateRoutineRequest,
    UpdateRoutineRequest,
)
from app.dependencies import get_db, get_routine_mapper
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
                joinedload(Routine.exercise_links).options(
                    joinedload(RoutineExercise.routine_exercise_sets),
                    joinedload(RoutineExercise.exercise).joinedload(
                        Exercise.personal_record
                    ),
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
            joinedload(Routine.exercise_links).options(
                joinedload(RoutineExercise.routine_exercise_sets),
                joinedload(RoutineExercise.exercise).joinedload(
                    Exercise.personal_record
                ),
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
                notes=exercise.notes,
                created_at=timestamp,
                updated_at=timestamp,
                routine_exercise_sets=[
                    RoutineExerciseSet(
                        set_number=set_index + 1,
                        set_type="normal",
                        targeted_reps=each_set.targeted_reps,
                        targeted_weight=each_set.targeted_weight,
                    )
                    for set_index, each_set in enumerate(exercise.sets)
                ]
                if exercise.sets
                else [],
            )
            for exercise_index, exercise in enumerate(input.exercises)
        ]
        if input.exercises
        else [],
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
                joinedload(Routine.exercise_links).joinedload(
                    RoutineExercise.routine_exercise_sets
                )
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
    routine = (
        session.exec(
            select(Routine)
            .where(Routine.id == routine_id)
            .options(
                joinedload(Routine.exercise_links).joinedload(
                    RoutineExercise.routine_exercise_sets
                ),
                joinedload(Routine.exercise_links).joinedload(RoutineExercise.exercise),
            )
        )
        .unique()
        .one()
    )
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

        routine_exercises: dict = {
            routine_exercise.id: routine_exercise
            for routine_exercise in routine.exercise_links
        }

        for exercise_order, input_exercise in enumerate(input.exercises):
            # look for routine exercise that match with id
            if input_exercise.id in routine_exercises.keys():
                routine_exercise: RoutineExercise = routine_exercises[input_exercise.id]

                routine_exercise.notes = input_exercise.notes
                routine_exercise.order = exercise_order + 1
                routine_exercise.updated_at = timestamp
                routine_exercise.exercise_id = input_exercise.exercise_id

                # update set
                routine_exercise_sets: dict = {
                    each_set.id: each_set
                    for each_set in routine_exercise.routine_exercise_sets
                }

                for set_order, input_exercise_set in enumerate(input_exercise.sets):
                    if input_exercise_set.id in routine_exercise_sets.keys():
                        routine_exercise_set: RoutineExerciseSet = (
                            routine_exercise_sets[input_exercise_set.id]
                        )
                        routine_exercise_set.set_number = set_order + 1
                        routine_exercise_set.set_type = input_exercise_set.set_type
                        routine_exercise_set.targeted_weight = (
                            input_exercise_set.targeted_weight
                        )
                        routine_exercise_set.targeted_reps = (
                            input_exercise_set.targeted_reps
                        )

                        del routine_exercise_sets[input_exercise_set.id]
                    # create new routine exercise set
                    else:
                        routine_exercise_set: RoutineExerciseSet = RoutineExerciseSet(
                            routine_exercise=routine_exercise,
                            set_number=set_order + 1,
                            set_type="normal",
                            targeted_reps=input_exercise_set.targeted_reps,
                            targeted_weight=input_exercise_set.targeted_weight,
                        )
                        session.add(routine_exercise_set)

                # delete remaining sets:
                for removed_routine_exercise_set in routine_exercise_sets.values():
                    session.delete(removed_routine_exercise_set)

                del routine_exercises[input_exercise.id]
            # create new routine exercise if not exist
            else:
                routine_exercise: RoutineExercise = RoutineExercise(
                    routine=routine,
                    exercise_id=input_exercise.exercise_id,
                    notes=input_exercise.notes,
                    order=exercise_order + 1,
                    created_at=timestamp,
                    updated_at=timestamp,
                    routine_exercise_sets=[
                        RoutineExerciseSet(
                            set_number=set_order + 1,
                            set_type=input_exercise_set.set_type,
                            targeted_reps=input_exercise_set.targeted_reps,
                            targeted_weight=input_exercise_set.targeted_weight,
                        )
                        for set_order, input_exercise_set in enumerate(
                            input_exercise.sets
                        )
                    ]
                    if input_exercise.sets
                    else [],
                )
                session.add(routine_exercise)
        # remove remaining routine_exercises that do not do any update
        for removed_routine_exercise in routine_exercises.values():
            session.delete(removed_routine_exercise)

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
