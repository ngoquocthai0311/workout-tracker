from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, and_, case, func, select

from app.database.models import SessionExercise
from app.routers.schemas.response_schemas import (
    DayReportResponse,
    WeekReportResponse,
    YearReportResponse,
)
from app.dependencies import get_db, get_report_mapper
from app.routers.mappers.dashboard_mapper import MONTH, ReportMapper

router = APIRouter(tags=["dashboards"], prefix="/dashboards")


@router.get(
    "/weights/total/day",
    response_model=DayReportResponse,
    dependencies=[Depends(get_db), Depends(get_report_mapper)],
)
def get_total_weights_by_day(
    date: str = datetime.today().strftime("%Y-%m-%d"),
    mapper: ReportMapper = Depends(get_report_mapper),
    session: Session = Depends(get_db),
):
    current_day = datetime.today().strftime("%Y-%m-%d")
    total_weights = 0

    if date == current_day:
        timestamp = (
            datetime.strptime(date, "%Y-%m-%d")
            .replace(tzinfo=ZoneInfo("UTC"))
            .timestamp()
        )
        total_weights = session.exec(
            select(func.coalesce(func.sum(SessionExercise.weight_lifted), 0)).where(
                SessionExercise.created_at > timestamp
            )
        ).one()
    else:
        date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=ZoneInfo("UTC"))
        start_timestamp = date_obj.timestamp()
        end_timestamp = (
            date_obj + relativedelta(days=date_obj.weekday() + 1)
        ).timestamp()
        total_weights = session.exec(
            select(func.sum(SessionExercise.weight_lifted)).where(
                and_(
                    SessionExercise.created_at > start_timestamp,
                    SessionExercise.created_at < end_timestamp,
                )
            )
        ).one()

    return mapper.transform_to_response(total_weights)


@router.get(
    "weights/total/week",
    response_model=WeekReportResponse,
    dependencies=[Depends(get_db), Depends(get_report_mapper)],
)
def get_total_weights_by_week(
    start_date: str = datetime.today().strftime("%Y-%m-%d"),
    end_date: str = datetime.today().strftime("%Y-%m-%d"),
    mapper: ReportMapper = Depends(get_report_mapper),
    session: Session = Depends(get_db),
):
    # idea: get the week of start day
    # get the week of end day -> count how many week
    # then construct each week from mon sun and
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").replace(
        tzinfo=ZoneInfo("UTC")
    )
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").replace(
        tzinfo=ZoneInfo("UTC")
    )
    week_start_day_obj = start_date_obj - relativedelta(days=start_date_obj.weekday())
    # next Monday
    week_end_day_obj = end_date_obj + relativedelta(days=7 - end_date_obj.weekday())

    # get how many days apart
    diff_days = (week_end_day_obj - week_start_day_obj).days
    # get weeks
    weeks = diff_days // 7

    statements = []
    for week in range(1, weeks + 1):
        start_date_timestamp = week_start_day_obj.timestamp()
        end_date_timestamp = (week_start_day_obj + relativedelta(days=7)).timestamp()

        statement = func.sum(
            case(
                (
                    (SessionExercise.created_at > start_date_timestamp)
                    & (SessionExercise.created_at < end_date_timestamp),
                    SessionExercise.weight_lifted,
                ),
                else_=0,
            )
        )
        statements.append(statement)

        week_start_day_obj = week_start_day_obj + relativedelta(days=7)

    results = session.exec(select(*statements)).one()

    return mapper.map_to_weekly_response(results)


@router.get(
    "/weights/total/year",
    response_model=YearReportResponse,
    dependencies=[Depends(get_db), Depends(get_report_mapper)],
)
def get_total_weights_by_year(
    year: int = datetime.now().year,
    mapper: ReportMapper = Depends(get_report_mapper),
    session: Session = Depends(get_db),
):
    current_month_start = datetime(year, 1, 1, tzinfo=timezone.utc)
    timestamp_dict = {}
    # construct timestamp for each month
    for month in MONTH:
        timestamp_dict[month] = {"start_date": current_month_start.timestamp()}
        current_month_start += relativedelta(months=1)
        timestamp_dict[month].update({"end_date": current_month_start.timestamp()})

    # construct each statement to calculate sum of weights lifted each month
    sum_statements = []
    for month in MONTH:
        start_date_timestamp = timestamp_dict[month]["start_date"]
        end_date_timestamp = timestamp_dict[month]["end_date"]
        statement = func.sum(
            case(
                (
                    (SessionExercise.created_at > start_date_timestamp)
                    & (SessionExercise.created_at < end_date_timestamp),
                    SessionExercise.weight_lifted,
                ),
                else_=0,
            )
        ).label(month.value)
        sum_statements.append(statement)

    statement = select(*sum_statements)
    results = session.exec(statement).one()

    return mapper.map_to_year_response(results)
