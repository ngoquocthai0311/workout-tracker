from app.routers.schemas.request_schemas import (
    CreateExerciseRequest,
    UpdateExerciseRequest,
)
from datetime import datetime, timezone
from app.database.common_repository import CommonRepository
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.database.models import Exercise
import logging

logger = logging.getLogger(__name__)


class ExerciseRepository(CommonRepository):
    def get_by_id(self, session: Session, id: int):
        try:
            exercise = session.exec(
                select(Exercise)
                .where(Exercise.id == id)
                .options(joinedload(Exercise.personal_record))
            ).one_or_none()
            return exercise
        except Exception as e:
            logger.error(e)
            raise e

    def get_all(self, session: Session):
        try:
            exercises = session.exec(
                select(Exercise).options(joinedload(Exercise.personal_record))
            ).all()
            return exercises
        except Exception as e:
            logger.error(e)
            raise e

    def remove_by_id(self, session: Session, id: int):
        try:
            exercise = session.get(Exercise, id)
            if not exercise:
                raise HTTPException(status_code=404, detail="Exercise not found")

            session.delete(exercise)
        except Exception as e:
            raise e

    def update(self, session: Session, id: int, input: UpdateExerciseRequest):
        try:
            exercise = self.get_by_id(session, id)
            if not exercise:
                raise HTTPException(status_code=404, detail="Exercise not found")

            is_edited = False
            if input.name and exercise.name != input.name:
                exercise.name = input.name
                is_edited = True

            if input.description and exercise.description != input.description:
                exercise.description = input.description
                is_edited = True

            if input.user_id and exercise.user_id != input.user_id:
                exercise.user_id = input.user_id
                is_edited = True

            if is_edited:
                timestamp = datetime.now(timezone.utc).timestamp()
                exercise.updated_at = timestamp
                session.add(exercise)

                return exercise

            return None
        except Exception as e:
            print(e)
            raise e

    def create(self, session: Session, input: CreateExerciseRequest):
        try:
            timestamp = datetime.now(timezone.utc).timestamp()
            exercise = Exercise(
                name=input.name,
                description=input.description,
                created_at=timestamp,
                updated_at=timestamp,
                user_id=input.user_id,
            )

            session.add(exercise)
            session.flush()
            session.refresh(exercise)

            return exercise
        except Exception as e:
            print(e)
            raise e
