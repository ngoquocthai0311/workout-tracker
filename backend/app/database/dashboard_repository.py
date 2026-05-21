from zoneinfo import ZoneInfo
from app.routers.mappers.dashboard_mapper import MONTH
from sqlmodel import Session
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlmodel import case, func, select, and_
from app.database.models import SessionExercise, WorkoutSession


class DashboardRepository:
    def get_glance(self, session: Session):
        # total recent workout
        current_date_obj = datetime.now(timezone.utc)
        week_start_day_obj = current_date_obj - relativedelta(
            days=current_date_obj.weekday()
        )
        recent_workouts = session.exec(
            select(
                func.count(
                    case(
                        (
                            (WorkoutSession.created_at > week_start_day_obj.timestamp())
                            & (
                                WorkoutSession.created_at < current_date_obj.timestamp()
                            ),
                            1,
                        ),
                        else_=0,
                    )
                )
            )
        ).one()

        # total volumes 1 week
        total_volumes = session.exec(
            select(
                func.sum(
                    case(
                        (
                            (
                                SessionExercise.created_at
                                > week_start_day_obj.timestamp()
                            )
                            & (
                                SessionExercise.created_at
                                < current_date_obj.timestamp()
                            ),
                            SessionExercise.weight_lifted,
                        ),
                        else_=0,
                    )
                )
            )
        ).one()
        # current streak
        first_day_of_a_year_obj = datetime(
            current_date_obj.year, 1, 1, tzinfo=timezone.utc
        )
        streaks = session.exec(
            select(
                func.count(
                    case(
                        (
                            (
                                WorkoutSession.created_at
                                > first_day_of_a_year_obj.timestamp()
                            )
                            & (
                                WorkoutSession.created_at < current_date_obj.timestamp()
                            ),
                            1,
                        ),
                        else_=0,
                    )
                )
            )
        ).one()

        # last workout
        last_workout_statement = (
            select(WorkoutSession.created_at)
            .order_by(WorkoutSession.created_at.desc())
            .limit(1)
        )
        last_workout = session.exec(last_workout_statement).one_or_none()

        return {
            "total_workouts": recent_workouts or 0,
            "total_volumes": total_volumes or 0,
            "streaks": streaks or 0,
            "last_workout": last_workout or None,
        }

    def get_total_weight_by_year(self, session: Session, year: int):
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

        return results

    def get_total_weight_by_week(
        self, session: Session, start_date: int, end_date: int
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
        week_start_day_obj = start_date_obj - relativedelta(
            days=start_date_obj.weekday()
        )
        # next Monday
        week_end_day_obj = end_date_obj + relativedelta(days=7 - end_date_obj.weekday())

        # get how many days apart
        diff_days = (week_end_day_obj - week_start_day_obj).days
        # get weeks
        weeks = diff_days // 7

        statements = []
        for week in range(1, weeks + 1):
            start_date_timestamp = week_start_day_obj.timestamp()
            end_date_timestamp = (
                week_start_day_obj + relativedelta(days=7)
            ).timestamp()

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

        return results

    def get_total_weight_by_day(self, session: Session, target_date: int):
        current_day = datetime.today().strftime("%Y-%m-%d")

        total_weights = 0

        if target_date == current_day:
            timestamp = (
                datetime.strptime(target_date, "%Y-%m-%d")
                .replace(tzinfo=ZoneInfo("UTC"))
                .timestamp()
            )
            total_weights = session.exec(
                select(func.coalesce(func.sum(SessionExercise.weight_lifted), 0)).where(
                    SessionExercise.created_at > timestamp
                )
            ).one()
        else:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d").replace(
                tzinfo=ZoneInfo("UTC")
            )
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

        return total_weights
