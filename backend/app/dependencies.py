from app.database.dashboard_repository import DashboardRepository
from app.database.routine_repository import RoutineRepository
from app.database.session_repository import SessionRepository
from sqlmodel import Session, create_engine
from app.routers.mappers.sessions_mapper import WorkoutSessionMapper
from functools import lru_cache
from app.routers.mappers.routines_mapper import RoutineMapper
from app.routers.mappers.dashboard_mapper import ReportMapper
from dotenv import load_dotenv
import os
from os.path import join
from pathlib import Path


class Settings:
    def __init__(self):
        load_dotenv(join(Path(os.getcwd()), ".env"))
        # environ attribute to trigger server crash
        self.DATABASE_USER: str = os.environ["DATABASE_USER"]
        self.DATABASE_PASS: str = os.environ["DATABASE_PASS"]
        self.DATABASE_PORT: str = os.environ["DATABASE_PORT"]
        self.DATABASE_NAME: str = os.environ["DATABASE_NAME"]
        self.DATABASE_HOST: str = os.environ["DATABASE_HOST"]

        # getenv for unnecessary env vars
        self.DATABASE_ECHO: bool = bool(os.getenv("DATABASE_ECHO", 0))

        self.REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
        self.REDIS_DATABASE_INDEX: int = int(os.getenv("REDIS_DATABASE_INDEX", 0))

        self.DATABASE_URL: str = f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASS}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        self.SQLALCHEMY_URL: str = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASS}@{self.DATABASE_HOST}/{self.DATABASE_NAME}"


# use this to init database
# SQLModel.metadata.create_all(engine)


# NOTE: caching Settings object instance
@lru_cache
def get_settings():
    return Settings()


engine = create_engine(get_settings().DATABASE_URL, echo=get_settings().DATABASE_ECHO)


def get_db():
    session = Session(engine)
    try:
        yield session

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@lru_cache
def get_workout_session_mapper():
    return WorkoutSessionMapper()


@lru_cache
def get_routine_mapper():
    return RoutineMapper()


@lru_cache
def get_report_mapper():
    return ReportMapper()


@lru_cache
<<<<<<< HEAD
def get_exercise_mapper():
    return ExerciseMapper()


# TODO: create a connection pool and let other uses it
# @contextmanager
def get_redis():
    session = None
    try:
        redis_url = os.getenv("REDIS_URL")
        redis_host = os.getenv("REDIS_HOST", "localhost")
        if redis_url:
            session = redis.Redis.from_url(redis_url, decode_responses=True)
        elif redis_host.startswith("redis://") or redis_host.startswith("rediss://"):
            session = redis.Redis.from_url(redis_host, decode_responses=True)
        else:
            session = redis.Redis(
                host=redis_host,
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DATABASE_INDEX", 0)),
                decode_responses=True,
            )
        yield session
    except Exception as e:
        print("Cant connect to redis database")
        print(e)
        raise e
    finally:
        if session:
            session.close()


def get_redis_service(redis_session=Depends(get_redis)):
    return RedisService(redis_session)


@lru_cache
def get_exercise_repository():
    return ExerciseRepository()


@lru_cache
=======
>>>>>>> 5e3a0e7 (feat: rework backend code)
def get_routine_repository():
    return RoutineRepository()


@lru_cache
def get_session_repository():
    return SessionRepository()


@lru_cache
def get_dashboard_repository():
    return DashboardRepository()
