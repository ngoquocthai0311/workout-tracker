from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.schemas.request_schemas import (
    CreateExerciseRequest,
    UpdateExerciseRequest,
)
from app.routers.schemas.response_schemas import ExerciseResponse
from app.services.exercise_service import get_exercise_service, ExerciseService

router = APIRouter(tags=["exercises"], prefix="/exercises")


@router.get(
    "",
    response_model=list[ExerciseResponse],
)
def read_exercises(exercise_service: ExerciseService = Depends(get_exercise_service)):
    try:
        return exercise_service.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
def get_exercise(
    exercise_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)
):
    try:
        print("sdasdasd")
        return exercise_service.get_one(exercise_id)
    except Exception as e:
        print(e)
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
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    try:
        return exercise_service.create(input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.patch(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
def update_exercise(
    exercise_id: int,
    input: UpdateExerciseRequest,
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    try:
        return exercise_service.update(exercise_id, input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    try:
        exercise_service.delete(exercise_id)
        return JSONResponse(
            status_code=200, content={"message": "Exercise deleted successfully"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )
