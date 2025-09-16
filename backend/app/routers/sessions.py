from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from app.database.models import SessionExercise, WorkoutSession, MaxWeightRecord
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
                joinedload(WorkoutSession.exercise_links).joinedload(
                    SessionExercise.exercise
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
    workout_session_id: int,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
):
    workout_session = (
        session.exec(
            select(WorkoutSession)
            .where(WorkoutSession.id == workout_session_id)
            .options(
                joinedload(WorkoutSession.exercise_links).joinedload(
                    SessionExercise.exercise
                )
            )
        )
        .unique()
        .one_or_none()
    )
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
        duration=input.duration,
    )
    session.add(workout_session)

    # add each exercise set to workout session based on the input
    if input.exercises:
        for exercise_index, exercise in enumerate(input.exercises):
            exercise_details: CreateWorkoutSessionRequest.RoutineExerciseRequest = (
                exercise
            )

            # ignore empty sets
            if not exercise_details.sets:
                continue

            # add each performed set of an exercise to become an session exercise
            for set_index, set in enumerate(exercise_details.sets):
                exercise_set: CreateWorkoutSessionRequest.RoutineExerciseRequest.ExerciseSet = set

                workout_session_exercise = SessionExercise(
                    session=workout_session,
                    exercise_id=exercise_details.id,
                    order=exercise_index + 1,
                    set_number=set_index + 1,
                    set_type=exercise_set.set_type,
                    weight_lifted=exercise_set.weight_lifted,
                    reps_completed=exercise_set.reps_completed,
                    created_at=timestamp,
                )
                session.add(workout_session_exercise)

                max_weight = (
                    workout_session_exercise.exercise.max_weight
                    if workout_session_exercise.exercise
                    else None
                )
                # check if the exercise set performed has best records
                if max_weight:
                    if max_weight.weight < exercise_set.weight_lifted:
                        workout_session_exercise.exercise.max_weight.weight = (
                            exercise_set.weight_lifted
                        )
                        workout_session_exercise.exercise.max_weight.updated_at = (
                            timestamp
                        )
                        workout_session_exercise.exercise.max_weight.session_exercise = workout_session_exercise
                else:
                    max_weight = MaxWeightRecord(
                        user_id=input.user_id,
                        exercise_id=exercise_details.id,
                        weight=exercise_set.weight_lifted,
                        updated_at=timestamp,
                        session_exercise=workout_session_exercise,
                    )
                    session.add(max_weight)

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
    workout_session: WorkoutSession = (
        session.exec(
            select(WorkoutSession)
            .where(WorkoutSession.id == workout_session_id)
            .options(
                joinedload(WorkoutSession.exercise_links).options(
                    joinedload(SessionExercise.exercise),
                )
            )
        )
        .unique()
        .one()
    )

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

    if input.duration:
        workout_session.user_id = input.user_id
        is_edited = True

    if input.exercises and len(input.exercises) > 0:
        is_edited = True

        # idea:
        # get dictionary for session exercise
        # then iterate through the input to keep track of the exercise order and set number
        # do the update accordingly, if not exist then create new
        # then remove the remaining session exercises within a session

        session_exercises: dict = {
            exercise_session.id: exercise_session
            for exercise_session in workout_session.exercise_links
        }

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
                if exercise_set.id in session_exercises.keys():
                    workout_session_exercise: SessionExercise = session_exercises[
                        exercise_set.id
                    ]
                    workout_session_exercise.order = exercise_index + 1
                    workout_session_exercise.set_number = set_index + 1
                    workout_session_exercise.set_type = exercise_set.set_type
                    workout_session_exercise.weight_lifted = exercise_set.weight_lifted
                    workout_session_exercise.reps_completed = (
                        exercise_set.reps_completed
                    )

                    del session_exercises[exercise_set.id]
                else:
                    workout_session_exercise = SessionExercise(
                        session=workout_session,
                        exercise_id=exercise_details.id,
                        order=exercise_index + 1,
                        set_number=set_index + 1,
                        set_type=exercise_set.set_type,
                        weight_lifted=exercise_set.weight_lifted,
                        reps_completed=exercise_set.reps_completed,
                        created_at=timestamp,
                    )

                session.add(workout_session_exercise)

                max_weight = (
                    workout_session_exercise.exercise.max_weight
                    if workout_session_exercise.exercise
                    else None
                )
                # check if the exercise set performed has best records
                if max_weight:
                    if max_weight.weight < exercise_set.weight_lifted:
                        workout_session_exercise.exercise.max_weight.weight = (
                            exercise_set.weight_lifted
                        )
                        workout_session_exercise.exercise.max_weight.updated_at = (
                            timestamp
                        )
                        workout_session_exercise.exercise.max_weight.session_exercise = workout_session_exercise
                else:
                    max_weight = MaxWeightRecord(
                        user_id=input.user_id,
                        exercise_id=exercise_details.id,
                        weight=exercise_set.weight_lifted,
                        updated_at=timestamp,
                        session_exercise=workout_session_exercise,
                    )
                    session.add(max_weight)
        # remove remaining session_exercises
        for removed_session_exercises in session_exercises.values():
            # update max_weight if possible
            if removed_session_exercises.max_weight:
                max_weight = removed_session_exercises.max_weight
                if max_weight:
                    session.delete(max_weight)
                    # find updated session to fill in
                    new_best_exercise_session = session.exec(
                        select(SessionExercise)
                        .where(
                            SessionExercise.id != removed_session_exercises.id,
                            SessionExercise.exercise_id
                            == removed_session_exercises.exercise_id,
                        )
                        .order_by(SessionExercise.created_at.desc())
                        .limit(1)
                    ).one()

                    if new_best_exercise_session:
                        max_weight.session_exercise_id = new_best_exercise_session.id
                        max_weight.weight = new_best_exercise_session.weight_lifted
                        max_weight.updated_at = timestamp

            session.delete(removed_session_exercises)

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
