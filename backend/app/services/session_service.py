from app.dependencies import get_db
from fastapi import Depends
from app.services.redis_service import get_redis_service
from app.services.redis_service import RedisResourceKey
from app.routers.mappers.sessions_mapper import WorkoutSessionMapper
from app.database.session_repository import SessionRepository
from app.services.redis_service import RedisService
from app.services.base_service import BaseService
from sqlmodel import Session


class SessionService(BaseService):
    def __init__(
        self,
        redis_service: RedisService,
        repository: SessionRepository,
        db_session: Session,
        mapper: WorkoutSessionMapper,
        redis_key: RedisResourceKey,
    ):
        super().__init__(
            redis_service=redis_service,
            repository=repository,
            db_session=db_session,
            mapper=mapper,
            redis_key=redis_key,
        )


def get_session_service(
    redis_service: RedisService = Depends(get_redis_service),
    repository: SessionRepository = Depends(SessionRepository),
    session: Session = Depends(get_db),
    mapper: WorkoutSessionMapper = Depends(WorkoutSessionMapper),
):
    return SessionService(
        redis_service=redis_service,
        repository=repository,
        db_session=session,
        mapper=mapper,
        redis_key=RedisResourceKey.WORKOUT_SESSION,
    )
