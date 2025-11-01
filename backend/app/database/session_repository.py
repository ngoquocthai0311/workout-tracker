from app.routers.schemas.request_schemas import (
    CreateWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
)
from datetime import datetime, timezone
from app.database.common_repository import CommonRepository
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.database.models import WorkoutSession, SessionExercise, PersonalRecord
import logging

logger = logging.getLogger(__name__)


class SessionRepository(CommonRepository):
    def get_by_id(self, session: Session, id: int):
        try:
            workout_session = (
                session.exec(
                    select(WorkoutSession)
                    .where(WorkoutSession.id == id)
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
            return workout_session
        except Exception as e:
            logger.error(e)
            raise e

    def get_all(self, session: Session):
        try:
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
            return workout_sessions
        except Exception as e:
            logger.error(e)
            raise e

    def remove_by_id(self, session: Session, id: int):
        try:
            workout_session = session.get(WorkoutSession, id)
            if not workout_session:
                raise HTTPException(status_code=404, detail="Workout session not found")

            session.delete(workout_session)
        except Exception as e:
            raise e

    def update(self, session: Session, id: int, input: UpdateWorkoutSessionRequest):
        try:
            workout_session = self.get_by_id(session, id)
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

                # track of total performed weights
                total_weights: int = 0

                # idea:
                # get dictionary for session exercise
                # then iterate through the input to keep track of the exercise order and set number
                # do the update accordingly, if not exist then create new
                # then remove the remaining session exercises within a session

                session_exercises: dict[int, SessionExercise] = {
                    exercise_session.id: exercise_session
                    for exercise_session in workout_session.exercise_links
                }

                for exercise_index, exercise in enumerate(input.exercises):
                    exercise_details: UpdateWorkoutSessionRequest.RoutineExerciseRequest = exercise

                    # iterate through performed sets of each exercise and update
                    # if not have an idea, create one using exercise_id to link cuz
                    # the set is not in an routine
                    for set_index, set in enumerate(exercise_details.sets):
                        exercise_set: UpdateWorkoutSessionRequest.RoutineExerciseRequest.ExerciseSet = set
                        workout_session_exercise = None
                        if exercise_set.id in session_exercises.keys():
                            workout_session_exercise: SessionExercise = (
                                session_exercises[exercise_set.id]
                            )
                            workout_session_exercise.exercise_name = (
                                exercise_details.name,
                            )
                            workout_session_exercise.order = exercise_index + 1
                            workout_session_exercise.set_number = set_index + 1
                            workout_session_exercise.set_type = exercise_set.set_type
                            workout_session_exercise.weight_lifted = (
                                exercise_set.weight_lifted
                            )
                            workout_session_exercise.reps_completed = (
                                exercise_set.reps_completed
                            )

                            del session_exercises[exercise_set.id]
                        else:
                            workout_session_exercise = SessionExercise(
                                session=workout_session,
                                exercise_id=exercise_details.id,
                                exercise_name=exercise_details.name,
                                order=exercise_index + 1,
                                set_number=set_index + 1,
                                set_type=exercise_set.set_type,
                                weight_lifted=exercise_set.weight_lifted,
                                reps_completed=exercise_set.reps_completed,
                                created_at=timestamp,
                            )

                        session.add(workout_session_exercise)

                        # increment total weight from each exercise set
                        total_weights += exercise_set.weight_lifted

                        # personal record is valid for valid exercise id
                        if exercise_details.id:
                            personal_record = (
                                workout_session_exercise.exercise.personal_record
                                if workout_session_exercise.exercise
                                else None
                            )
                            # check if the exercise set performed has best records
                            if personal_record:
                                if personal_record.weight < exercise_set.weight_lifted:
                                    workout_session_exercise.exercise.personal_record.weight = exercise_set.weight_lifted
                                    workout_session_exercise.exercise.personal_record.updated_at = timestamp
                                    workout_session_exercise.exercise.personal_record.session_exercise = workout_session_exercise
                            else:
                                personal_record = PersonalRecord(
                                    user_id=input.user_id,
                                    exercise_id=exercise_details.id,
                                    weight=exercise_set.weight_lifted,
                                    updated_at=timestamp,
                                    session_exercise=workout_session_exercise,
                                )
                                session.add(personal_record)

                # update total weights for the session
                workout_session.total_weights = total_weights

                # remove remaining session_exercises
                for removed_session_exercises in session_exercises.values():
                    # update personal_record if possible
                    if removed_session_exercises.personal_record:
                        personal_record = removed_session_exercises.personal_record
                        if personal_record:
                            session.delete(personal_record)
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
                                personal_record.session_exercise_id = (
                                    new_best_exercise_session.id
                                )
                                personal_record.weight = (
                                    new_best_exercise_session.weight_lifted
                                )
                                personal_record.updated_at = timestamp

                    session.delete(removed_session_exercises)

            if is_edited:
                workout_session.updated_at = timestamp
                session.add(workout_session)
                session.flush()
                session.refresh(workout_session)
                return workout_session

            return None
        except Exception as e:
            print(e)
            raise e

    def create(self, session: Session, input: CreateWorkoutSessionRequest):
        try:
            timestamp = datetime.now(timezone.utc).timestamp()

            workout_session = WorkoutSession(
                name=input.name,
                description=input.description,
                user_id=input.user_id,
                routine_id=input.routine_id,
                created_at=timestamp,
                updated_at=timestamp,
                notes=input.notes,
                duration=input.duration,
            )
            session.add(workout_session)

            # track of total performed weights
            total_weights: int = 0

            # add each exercise set to workout session based on the input
            if input.exercises:
                # get personal record from all  exercises id and construct a hashmap for it
                exercise_ids: list[int] = [exercise.id for exercise in input.exercises]
                personal_records: list[PersonalRecord] = session.exec(
                    select(PersonalRecord).where(
                        PersonalRecord.exercise_id.in_(exercise_ids)
                    )
                ).all()
                map_exercise_personal_records: dict = {
                    personal_record.exercise_id: personal_record
                    for personal_record in personal_records
                }

                for exercise_index, exercise in enumerate(input.exercises):
                    exercise_details: CreateWorkoutSessionRequest.RoutineExerciseRequest = exercise

                    # ignore empty sets
                    if not exercise_details.sets:
                        continue

                    # add each performed set of an exercise to become an session exercise
                    for set_index, set in enumerate(exercise_details.sets):
                        exercise_set: CreateWorkoutSessionRequest.RoutineExerciseRequest.ExerciseSet = set

                        workout_session_exercise = SessionExercise(
                            session=workout_session,
                            exercise_id=exercise_details.id,
                            exercise_name=exercise_details.name,
                            order=exercise_index + 1,
                            set_number=set_index + 1,
                            set_type=exercise_set.set_type,
                            weight_lifted=exercise_set.weight_lifted,
                            reps_completed=exercise_set.reps_completed,
                            created_at=timestamp,
                        )

                        # increment total weigh lifted
                        total_weights += exercise_set.weight_lifted

                        session.add(workout_session_exercise)

                        personal_record: PersonalRecord = (
                            map_exercise_personal_records.get(
                                workout_session_exercise.exercise_id, None
                            )
                        )
                        # check if the exercise set performed has best records
                        if personal_record:
                            if personal_record.weight < exercise_set.weight_lifted:
                                personal_record.weight = exercise_set.weight_lifted
                                personal_record.updated_at = timestamp
                                personal_record.session_exercise = (
                                    workout_session_exercise
                                )
                        else:
                            personal_record = PersonalRecord(
                                user_id=input.user_id,
                                exercise_id=exercise_details.id,
                                weight=exercise_set.weight_lifted,
                                updated_at=timestamp,
                                session_exercise=workout_session_exercise,
                            )
                            session.add(personal_record)

            # update workout_session with total_weights
            workout_session.total_weights = total_weights
            session.flush()
            session.refresh(workout_session)

            return workout_session
        except Exception as e:
            print(e)
            raise e
