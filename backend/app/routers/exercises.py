from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from app.database.models import Exercise
from app.routers.schemas.request_schemas import (
    CreateExerciseRequest,
    UpdateExerciseRequest,
)
from app.dependencies import (
    get_db,
    get_exercise_mapper,
    get_redis_service,
    RedisService,
)
from app.routers.schemas.response_schemas import ExerciseResponse
from app.routers.mappers.exercises_mapper import ExerciseMapper
from app.database.exercise_repository import ExerciseRepository
from app.dependencies import get_exercise_repository
from typing import Optional

router = APIRouter(tags=["exercises"], prefix="/exercises")


@router.get(
    "",
    response_model=list[ExerciseResponse],
)
def read_exercises(
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
    redis_service: RedisService = Depends(get_redis_service),
):
    try:
        # TODO: Assume one user only with id 1
        cache_value = redis_service.get_value("user_1_exercises")
        if cache_value:
            return cache_value

        exercises = exercise_repository.get_all(session=session)

        exercises = mapper.map_list_to_response(exercises)

        # cache value in redis
        redis_service.cache_value("user_1_exercises", exercises)

        return exercises
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
def get_exercise(
    exercise_id: int,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
):
    try:
        exercise = exercise_repository.get_by_id(session, exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        mapper.transform_to_response(exercise=exercise)
        return mapper.transform_to_response(exercise=exercise)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.post(
    "",
    response_model=ExerciseResponse,
)
def create_exercise(
    input: CreateExerciseRequest,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
):
    exercise = exercise_repository.create(session, input)

    # remove cache
    redis_service.remove_cache("user_1_exercises")

    return mapper.transform_to_response(exercise=exercise)


@router.patch(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
def update_exercise(
    exercise_id: int,
    input: UpdateExerciseRequest,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
):
    try:
        updated_exercise: Optional[Exercise] = exercise_repository.update(
            session, exercise_id, input
        )

        if updated_exercise:
            # remove cache
            redis_service.remove_cache("user_1_exercises")
            return mapper.transform_to_response(updated_exercise)

        return Response(status_code=204)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.delete(
    "/{exercise_id}", dependencies=[Depends(get_db), Depends(get_redis_service)]
)
def delete_exercise(
    exercise_id: int,
    session: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
):
    try:
        exercise_repository.remove_by_id(session, exercise_id)
        # remove cache
        redis_service.remove_cache("user_1_exercises")
        return JSONResponse(
            status_code=200, content={"message": "Exercise deleted successfully"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )
