from app.routers.mappers.base_mapper import BaseResponseMapper
from app.routers.schemas.response_schemas import (
    DayReportResponse,
    WeekReportResponse,
    YearReportResponse,
)
from enum import Enum


class ReportMapper(BaseResponseMapper):
    def map_list_to_response(self, results: tuple):
        pass

    def transform_to_response(self, total_weights: int = 0):
        return DayReportResponse(total_weights=total_weights if total_weights else 0)

    def map_to_weekly_response(self, results: tuple = tuple()):
        dict_result = {}
        for index, result in enumerate(results):
            dict_result[" ".join(["Week", str(index + 1)])] = result

        return WeekReportResponse(dict_result)

    def map_to_year_response(self, results: tuple):
        dict_results = {}
        for index, month in enumerate(MONTH):
            dict_results[month.value] = results[index]

        return YearReportResponse(dict_results)


class TIMERANGE(Enum):
    DAY = "day"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class WEEKDAY(Enum):
    MON = "monday"
    TUE = "tuesday"
    WED = "wednesday"
    THU = "thursday"
    FRI = "friday"
    SAT = "saturday"
    SUN = "sunday"


class MONTH(Enum):
    JAN = "january"
    FEB = "february"
    MAR = "march"
    APR = "april"
    MAY = "may"
    JUN = "june"
    JUL = "july"
    AUG = "august"
    SEP = "september"
    OCT = "october"
    NOV = "november"
    DEC = "december"
