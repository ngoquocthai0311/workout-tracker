from sqlmodel import Session
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlmodel import case, func, select
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
