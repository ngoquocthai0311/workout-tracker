from app.services.base_service import BaseService
from app.database.exercise_repository import ExerciseRepository
from app.routers.mappers.exercises_mapper import ExerciseMapper
from fastapi import Depends
from app.dependencies import get_db
from app.services.redis_service import (
    RedisService,
    RedisResourceKey,
    get_redis_service,
)
from sqlmodel import Session


class ExerciseService(BaseService):
    def __init__(
        self,
        redis_service: RedisService,
        repository: ExerciseRepository,
        db_session: Session,
        mapper: ExerciseMapper,
        redis_key: RedisResourceKey,
    ):
        super().__init__(
            redis_service=redis_service,
            repository=repository,
            db_session=db_session,
            mapper=mapper,
            redis_key=redis_key,
        )


def get_exercise_service(
    redis_service: RedisService = Depends(get_redis_service),
    repository: ExerciseRepository = Depends(ExerciseRepository),
    session: Session = Depends(get_db),
    mapper: ExerciseMapper = Depends(ExerciseMapper),
):
    return ExerciseService(
        redis_service=redis_service,
        repository=repository,
        db_session=session,
        mapper=mapper,
        redis_key=RedisResourceKey.EXERCISES,
    )
