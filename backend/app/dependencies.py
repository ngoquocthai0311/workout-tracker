from sqlmodel import Session, create_engine
from app.routers.mappers.sessions_mapper import WorkoutSessionMapper
from functools import lru_cache
from app.routers.mappers.routines_mapper import RoutineMapper
from app.routers.mappers.dashboard_mapper import ReportMapper
from app.routers.mappers.exercises_mapper import ExerciseMapper
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

        self.DATABASE_URL: str = f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASS}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        self.SQLALCHEMY_URL: str = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASS}@{self.DATABASE_HOST}/{self.DATABASE_NAME}"


# use this to init database
# SQLModel.metadata.create_all(engine)


@lru_cache
def get_settings():
    return Settings()


engine = create_engine(get_settings().DATABASE_URL, echo=get_settings().DATABASE_ECHO)


# @lru_cache
# @contextmanager
def get_db():
    with Session(engine) as session:
        yield session


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
def get_exercise_mapper():
    return ExerciseMapper()
