from app.services.redis_service import RedisResourceKey
from app.dependencies import get_db
from app.database.routine_repository import RoutineRepository
from app.services.redis_service import get_redis_service
from fastapi import Depends
from app.routers.mappers.routines_mapper import RoutineMapper
from app.database.base_repository import BaseRepository
from app.services.redis_service import RedisService
from app.services.base_service import BaseService
from sqlmodel import Session


class RoutineService(BaseService):
    def __int__(
        self,
        redis_service: RedisService,
        repository: BaseRepository,
        db_session: Session,
        mapper: RoutineMapper,
        redis_key: str,
    ):
        super().__init__(
            redis_service=redis_service,
            repository=repository,
            db_session=db_session,
            mapper=mapper,
            redis_key=redis_key,
        )


def get_routine_service(
    redis_service: RedisService = Depends(get_redis_service),
    repository: RoutineRepository = Depends(RoutineRepository),
    session: Session = Depends(get_db),
    mapper: RoutineMapper = Depends(RoutineMapper),
):
    return RoutineService(
        redis_service=redis_service,
        repository=repository,
        db_session=session,
        mapper=mapper,
        redis_key=RedisResourceKey.ROUTINES,
    )
