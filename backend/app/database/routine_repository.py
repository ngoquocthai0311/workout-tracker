from app.routers.schemas.request_schemas import (
    CreateRoutineRequest,
    UpdateRoutineRequest,
)
from datetime import datetime, timezone
from app.database.common_repository import CommonRepository
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.database.models import Routine, RoutineExercise, Exercise, RoutineExerciseSet
import logging

logger = logging.getLogger(__name__)


class RoutineRepository(CommonRepository):
    def get_by_id(self, session: Session, id: int):
        try:
            routine = session.exec(
                select(Routine)
                .where(Routine.id == id)
                .options(
                    joinedload(Routine.exercise_links).options(
                        joinedload(RoutineExercise.routine_exercise_sets),
                        joinedload(RoutineExercise.exercise).joinedload(
                            Exercise.personal_record
                        ),
                    )
                )
            ).first()
            return routine
        except Exception as e:
            logger.error(e)
            raise e

    def get_all(self, session: Session):
        try:
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
            return routines
        except Exception as e:
            logger.error(e)
            raise e

    def remove_by_id(self, session: Session, id: int):
        try:
            routine = session.get(Routine, id)
            if not routine:
                raise HTTPException(status_code=404, detail="Routine not found")

            session.delete(routine)
        except Exception as e:
            raise e

    def update(self, session: Session, id: int, input: UpdateRoutineRequest):
        try:
            routine = self.get_by_id(session, id)
            if not routine:
                raise HTTPException(status_code=404, detail="Routine not found")

            timestamp = datetime.now(timezone.utc).timestamp()
            is_edited = False
            if input.name and routine.name != input.name:
                routine.name = input.name
                is_edited = True

            if (
                input.description is not None
                and routine.description != input.description
            ):
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
                        routine_exercise: RoutineExercise = routine_exercises[
                            input_exercise.id
                        ]

                        routine_exercise.notes = input_exercise.notes
                        routine_exercise.order = exercise_order + 1
                        routine_exercise.updated_at = timestamp
                        routine_exercise.exercise_id = input_exercise.exercise_id

                        # update set
                        routine_exercise_sets: dict = {
                            each_set.id: each_set
                            for each_set in routine_exercise.routine_exercise_sets
                        }

                        for set_order, input_exercise_set in enumerate(
                            input_exercise.sets
                        ):
                            if input_exercise_set.id in routine_exercise_sets.keys():
                                routine_exercise_set: RoutineExerciseSet = (
                                    routine_exercise_sets[input_exercise_set.id]
                                )
                                routine_exercise_set.set_number = set_order + 1
                                routine_exercise_set.set_type = (
                                    input_exercise_set.set_type
                                )
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
                        for (
                            removed_routine_exercise_set
                        ) in routine_exercise_sets.values():
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
                session.flush()
                session.refresh(routine)

                return routine

            return None

        except Exception as e:
            print(e)
            raise e

    def create(self, session: Session, input: CreateRoutineRequest):
        try:
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
            session.refresh(routine)

            routine = self.get_by_id(session, routine.id)
            if not routine:
                # this case should not happen after a successful commit
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve created routine"
                )
            return routine
        except Exception as e:
            print(e)
            raise e
