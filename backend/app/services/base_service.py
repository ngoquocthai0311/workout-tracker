from abc import ABC
from typing import Any
from app.database.base_repository import BaseRepository
from app.services.redis_service import RedisService
from sqlmodel import Session
from app.routers.mappers.base_mapper import BaseResponseMapper
from fastapi import HTTPException


class BaseService(ABC):
    def __init__(
        self,
        redis_service: RedisService,
        repository: BaseRepository,
        db_session: Session,
        mapper: BaseResponseMapper,
        redis_key: str | None = None,
    ):
        self.redis_service = redis_service
        self.repository = repository
        self.db_session = db_session
        self.mapper = mapper
        self.redis_key = redis_key

    def get_all(self):
        cache_value = self.redis_service.get_value(self.redis_key)
        if cache_value:
            return cache_value

        query_list = self.repository.get_all(session=self.db_session)
        results = self.mapper.map_list_to_response(query_list)

        self.redis_service.cache_value(self.redis_key, results)

        return results

    def get_one(self, obj_id: int):
        result = self.repository.get_by_id(self.db_session, obj_id)

        if not result:
            raise HTTPException(status_code=404, detail="Not found")

        return self.mapper.transform_to_response(obj=result)

    def create(self, input_data: Any):
        result = self.repository.create(self.db_session, input_data)

        # remove cache
        self.redis_service.remove_cache(self.redis_key)

        return self.mapper.transform_to_response(obj=result)

    def update(self, obj_id: int, input_data: Any):
        updated_result = self.repository.update(self.db_session, obj_id, input_data)

        if updated_result:
            # remove cache
            self.redis_service.remove_cache(self.redis_key)
            return self.mapper.transform_to_response(updated_result)

        return None

    def delete(self, obj_id: int):
        self.repository.remove_by_id(self.db_session, obj_id)
        # remove cache
        self.redis_service.remove_cache(self.redis_key)

        return True
