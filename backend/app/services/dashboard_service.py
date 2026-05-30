from app.services.redis_service import get_redis_service
from app.services.redis_service import RedisService
from fastapi import Depends
from app.database.dashboard_repository import DashboardRepository
from app.dependencies import get_db
from sqlmodel import Session
from app.routers.mappers.dashboard_mapper import ReportMapper
from app.services.redis_service import RedisResourceKey


class DashboardService:
    def __init__(
        self,
        redis_service: RedisService,
        repository: DashboardRepository,
        db_session: Session,
        mapper: ReportMapper,
        redis_key: RedisResourceKey,
    ):
        self.redis_service = redis_service
        self.repository = repository
        self.db_session = db_session
        self.mapper = mapper
        self.redis_key = redis_key

        # store each key by year and day
        # TODO: kill this key
        self.year_dashboard_redis_key = f"{self.redis_key}/{{year}}"
        self.day_dashboard_redis_key = f"{self.redis_key}/{{day}}"
        self.week_dashboard_redis_key = f"{self.redis_key}/{{start_date}}/{{end_date}}"

    def get_a_glance(self):
        cache_value = self.redis_service.get_value(self.redis_key)
        if cache_value:
            return cache_value

        results = self.repository.get_glance(self.db_session)
        result_response = self.mapper.map_glance_response(results)

        if results:
            self.redis_service.cache_value(self.redis_key, result_response)

        return result_response

    def get_total_weight_by_year(self, year: int):
        redis_key: str = self.year_dashboard_redis_key.format(year=year)
        cache_value = self.redis_service.get_value(redis_key)
        if cache_value:
            return cache_value

        results = self.repository.get_total_weight_by_year(self.db_session, year)
        result_response = self.mapper.map_to_year_response(results)

        if results:
            self.redis_service.cache_value(redis_key, result_response)

        return result_response

    def get_total_weight_by_week(self, start_date: str, end_date: str):
        redis_key: str = self.week_dashboard_redis_key.format(
            start_date=start_date, end_date=end_date
        )

        cache_value = self.redis_service.get_value(redis_key)
        if cache_value:
            return cache_value

        results = self.repository.get_total_weight_by_week(
            self.db_session, start_date, end_date
        )
        result_response = self.mapper.map_to_weekly_response(results)

        if results:
            self.redis_service.cache_value(redis_key, result_response)

        return result_response

    def get_total_weight_by_day(self, day: str):
        redis_key: str = self.day_dashboard_redis_key.format(day=day)
        cache_value = self.redis_service.get_value(redis_key)
        if cache_value:
            return cache_value

        results = self.repository.get_total_weight_by_day(self.db_session, day)
        result_response = self.mapper.transform_to_day_response(results)

        if results:
            self.redis_service.cache_value(redis_key, result_response)

        return result_response


def get_dashboard_service(
    redis_service: RedisService = Depends(get_redis_service),
    repository: DashboardRepository = Depends(DashboardRepository),
    session: Session = Depends(get_db),
    mapper: ReportMapper = Depends(ReportMapper),
):
    return DashboardService(
        redis_service=redis_service,
        repository=repository,
        db_session=session,
        mapper=mapper,
        redis_key=RedisResourceKey.DASHBOARDS,
    )
