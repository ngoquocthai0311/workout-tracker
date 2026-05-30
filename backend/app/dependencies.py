from sqlmodel import Session, create_engine
from functools import lru_cache
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
