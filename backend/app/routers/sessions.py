from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from app.database.models import SessionExercise, WorkoutSession
from app.routers.schemas.request_schemas import (
    CreateWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
)
from app.dependencies import get_db, get_workout_session_mapper
from app.routers.schemas.response_schemas import (
    SessionResponse,
)
from app.routers.mappers.sessions_mapper import WorkoutSessionMapper

router = APIRouter(tags=["sessions"], prefix="/sessions")


@router.get(
    "",
    response_model=list[SessionResponse],
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def read_sessions(
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
):
    workout_sessions = (
        session.exec(
            select(WorkoutSession).options(
                joinedload(WorkoutSession.exercise_links).options(
                    joinedload(SessionExercise.exercise),
                )
            )
        )
        .unique()
        .all()
    )

    return mapper.map_list_to_response(workout_sessions)


@router.get(
    "/{workout_session_id}",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def get_session(
    session_id: int,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
):
    workout_session = session.get(WorkoutSession, session_id)
    if not workout_session:
        raise HTTPException(status_code=404, detail="Workout session not found")

    return mapper.transform_to_response(workout_session)


@router.post(
    "",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def create_session(
    input: CreateWorkoutSessionRequest,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
):
    timestamp = datetime.now(timezone.utc).timestamp()

    workout_session = WorkoutSession(
        name=input.name,
        description=input.description,
        user_id=input.user_id,
        routine_id=input.routine_id,
        created_at=timestamp,
        notes=input.notes,
    )
    session.add(workout_session)

    # add each exercise set to workout session based on the input
    if input.exercises:
        for exercise_index, exercise in enumerate(input.exercises):
            exercise_details: CreateWorkoutSessionRequest.RoutineExerciseRequest = (
                exercise
            )

            # add each performed set of an exercise to become an session exercise
            for set_index, set in enumerate(exercise_details.sets):
                exercise_set: CreateWorkoutSessionRequest.RoutineExerciseRequest.ExerciseSet = set

                workout_session_exercise = SessionExercise(
                    session=workout_session,
                    exercise_id=exercise_details.exercise_id,
                    order=exercise_index + 1,
                    set_number=set_index + 1,
                    set_type=exercise_set.set_type,
                    weight_lifted=exercise_set.weight_lifted,
                    reps_completed=exercise_set.reps_completed,
                    created_at=timestamp,
                )

                session.add(workout_session_exercise)

    session.commit()
    session.refresh(workout_session)

    return mapper.transform_to_response(workout_session)


@router.patch(
    "/{workout_session_id}",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def update_session(
    workout_session_id: int,
    input: UpdateWorkoutSessionRequest,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
):
    workout_session = session.get(WorkoutSession, workout_session_id)
    if not workout_session:
        raise HTTPException(status_code=404, detail="Workout session not found")

    timestamp = datetime.now(timezone.utc).timestamp()
    is_edited = False

    if input.name and workout_session.name != input.name:
        workout_session.name = input.name
        is_edited = True

    if (
        input.description is not None
        and workout_session.description != input.description
    ):
        workout_session.description = input.description
        is_edited = True

    if input.notes and workout_session.notes != input.notes:
        workout_session.notes = input.notes
        is_edited = True

    if input.routine_id:
        workout_session.routine_id = input.routine_id
        is_edited = True

    if input.user_id and workout_session.user_id != input.user_id:
        workout_session.user_id = input.user_id
        is_edited = True

    if input.exercises and len(input.exercises) > 0:
        is_edited = True
        for exercise_index, exercise in enumerate(input.exercises):
            exercise_details: UpdateWorkoutSessionRequest.RoutineExerciseRequest = (
                exercise
            )

            # iterate through performed sets of each exercise and update
            # if not have an idea, create one using exercise_id to link cuz
            # the set is not in an routine
            for set_index, set in enumerate(exercise_details.sets):
                exercise_set: UpdateWorkoutSessionRequest.RoutineExerciseRequest.ExerciseSet = set
                workout_session_exercise = None
                if exercise_set.session_exercise_id:
                    workout_session_exercise = session.exec(
                        select(SessionExercise).where(
                            SessionExercise.id == exercise_set.session_exercise_id
                        )
                    ).one()

                    workout_session_exercise.order = exercise_index + 1
                    workout_session_exercise.set_number = set_index + 1
                    workout_session_exercise.set_type = exercise_set.set_type
                    workout_session_exercise.weight_lifted = exercise_set.weight_lifted
                    workout_session_exercise.reps_completed = (
                        exercise_set.reps_completed
                    )
                else:
                    workout_session_exercise = SessionExercise(
                        session=workout_session,
                        exercise_id=exercise_details.exercise_id,
                        order=exercise_index + 1,
                        set_number=set_index + 1,
                        set_type=exercise_set.set_type,
                        weight_lifted=exercise_set.weight_lifted,
                        reps_completed=exercise_set.reps_completed,
                        created_at=timestamp,
                    )

                session.add(workout_session_exercise)

    if is_edited:
        workout_session.updated_at = timestamp
        session.add(workout_session)
        session.commit()
        session.refresh(workout_session)
        return mapper.transform_to_response(workout_session)

    return Response(status_code=204)


@router.delete("/{workout_session_id}", dependencies=[Depends(get_db)])
def delete_Session(workout_session_id: int, session: Session = Depends(get_db)):
    workout_session = session.get(WorkoutSession, workout_session_id)
    if not workout_session:
        raise HTTPException(status_code=404, detail="Workout session not found")

    session.delete(workout_session)
    session.commit()
    return JSONResponse(
        status_code=200, content={"message": "Workout session deleted successfully"}
    )
