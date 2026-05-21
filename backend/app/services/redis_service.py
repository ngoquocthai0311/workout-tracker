from fastapi import Depends
from decimal import Decimal
from enum import Enum
from redis import Redis
import json
import os


class RedisResourceKey(Enum):
    EXERCISES = "exercises"
    WORKOUT_SESSION = "workout_sessions"
    DASHBOARDS = "dashboards"
    ROUTINES = "routines"
    DASHBOARDS = "DASHBOARDS"


class RedisService:
    def __init__(self, redis_session: Redis | None):
        self.redis_session: Redis | None = redis_session
        # 2 hours
        self.key_duration: int = 7200

    def get_value(self, resource_type: RedisResourceKey, user_id: int = None):
        if self.redis_session and resource_type:
            try:
                key: str = f"{resource_type.value}/{user_id if user_id else 1}"
                value_str = self.redis_session.get(key)
                if value_str:
                    return json.loads(value_str)
            except Exception:
                # NOTE: Do logging here
                print("Redis may be failed or empty")
                pass

        return None

    def cache_value(
        self,
        resource_type: RedisResourceKey,
        value: list | object | str,
        user_id: int = None,
    ):
        def custom_json_serializer(obj):
            if isinstance(obj, Decimal):
                return float(obj)

            # 2. Handle Pydantic/SQLModel (recurses automatically)
            if hasattr(obj, "model_dump"):
                return obj.model_dump()

            # 3. Handle older Pydantic v1
            if hasattr(obj, "dict"):
                return obj.dict()

            raise TypeError(
                f"Object of type {type(obj).__name__} is not JSON serializable"
            )

        if self.redis_session:
            # maybe trigger background tasks here instead of waiting
            # save response in 2 hours
            try:
                key: str = f"{resource_type.value}/{user_id if user_id else 1}"
                payload = json.dumps(value, default=custom_json_serializer)
                self.redis_session.setex(
                    key,
                    self.key_duration,
                    payload,
                )
            except Exception as e:
                print("Can't cache_value")
                print(e)
                pass

    def remove_cache(self, resource_type: RedisResourceKey, user_id: int = None):
        if self.redis_session:
            try:
                key: str = f"{resource_type.value}/{user_id if user_id else 1}"

                if not self.redis_session.get(key):
                    # NOTE: add logger here to indicate no action
                    return

                self.redis_session.delete(key)
            except Exception as e:
                print("Can't remove cache")
                print(e)
                pass


def _get_redis():
    session = None
    try:
        session = Redis(
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


def get_redis_service(redis_session=Depends(_get_redis)):
    return RedisService(redis_session)
