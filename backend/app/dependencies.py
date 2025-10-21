from app.database.exercise_repository import ExerciseRepository
from app.database.routine_repository import RoutineRepository
from app.database.session_repository import SessionRepository
from fastapi import Depends
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
import redis
from redis import Redis
import json
from typing import Optional


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


class RedisService:
    def __init__(self, redis_session: Optional[Redis]):
        self.redis_session: Optional[Redis] = redis_session
        # 2 hours
        self.key_duration: int = 7200

    def get_value(self, key: str):
        if self.redis_session:
            try:
                value_str = self.redis_session.get(key)
                if value_str:
                    return json.loads(value_str)
            except Exception as e:
                # NOTE: Do logging here
                print("Redis may be failed or empty")
                print(e)
                pass

        return None

    def cache_value(self, key: str, value: list | object):
        if self.redis_session:
            # maybe trigger background tasks here instead of waiting
            # save response in 2 hours
            try:
                self.redis_session.setex(
                    key,
                    self.key_duration,
                    json.dumps([item.__dict__ for item in value])
                    if isinstance(value, list)
                    else json.dumps(value),
                )
            except Exception as e:
                print("Can't cache_value")
                print(e)
                pass

    def remove_cache(self, key: str):
        if self.redis_session:
            try:
                self.redis_session.delete(key)
            except Exception as e:
                print("Can't remove cache")
                print(e)
                pass


# use this to init database
# SQLModel.metadata.create_all(engine)


# NOTE: caching Settings object instance
@lru_cache
def get_settings():
    return Settings()


engine = create_engine(get_settings().DATABASE_URL, echo=get_settings().DATABASE_ECHO)


# NOTE: decorator function to trigger guarantee clean up after use
# TODO: create a connection pool and let other uses it
# @contextmanager
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
def get_exercise_mapper():
    return ExerciseMapper()


# TODO: create a connection pool and let other uses it
# @contextmanager
def get_redis():
    session = None
    try:
        session = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 6379),
            db=os.getenv("REDIS_DATABASE_INDEX", 0),
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
def get_routine_repository():
    return RoutineRepository()


@lru_cache
def get_session_repository():
    return SessionRepository()
