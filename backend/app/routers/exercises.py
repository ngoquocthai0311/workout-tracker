from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from app.database.models import Exercise
from app.routers.schemas.request_schemas import (
    CreateExerciseRequest,
    UpdateExerciseRequest,
)
from app.dependencies import get_db, get_exercise_mapper
from app.routers.schemas.response_schemas import ExerciseResponse
from app.routers.mappers.exercises_mapper import ExerciseMapper

router = APIRouter(tags=["exercises"], prefix="/exercises")


@router.get(
    "",
    response_model=list[ExerciseResponse],
    dependencies=[Depends(get_db), Depends(get_exercise_mapper)],
)
def read_exercises(
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
):
    exercises = session.exec(
        select(Exercise).options(joinedload(Exercise.personal_record))
    ).all()

    return mapper.map_list_to_response(exercises)


@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse,
    dependencies=[Depends(get_db), Depends(get_exercise_mapper)],
)
def get_exercise(
    exercise_id: int,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
):
    exercise = session.exec(
        select(Exercise)
        .where(Exercise.id == exercise_id)
        .options(joinedload(Exercise.personal_record))
    ).one()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return mapper.transform_to_response(exercise=exercise)


@router.post(
    "",
    response_model=ExerciseResponse,
    dependencies=[Depends(get_db), Depends(get_exercise_mapper)],
)
def create_exercise(
    input: CreateExerciseRequest,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
):
    timestamp = datetime.now(timezone.utc).timestamp()
    exercise = Exercise(
        name=input.name,
        description=input.description,
        created_at=timestamp,
        updated_at=timestamp,
        user_id=input.user_id,
    )

    session.add(exercise)
    session.commit()
    session.refresh(exercise)

    return mapper.transform_to_response(exercise=exercise)


@router.patch(
    "/{exercise_id}",
    response_model=ExerciseResponse,
    dependencies=[Depends(get_db), Depends(get_exercise_mapper)],
)
def update_exercise(
    exercise_id: int,
    input: UpdateExerciseRequest,
    mapper: ExerciseMapper = Depends(get_exercise_mapper),
    session: Session = Depends(get_db),
):
    exercise = session.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    is_edited = False
    if input.name and exercise.name != input.name:
        exercise.name = input.name
        is_edited = True

    if input.description is not None and exercise.description != input.description:
        exercise.description = input.description
        is_edited = True

    if input.user_id and exercise.user_id != input.user_id:
        exercise.user_id = input.user_id
        is_edited = True

    if is_edited:
        timestamp = datetime.now(timezone.utc).timestamp()
        exercise.updated_at = timestamp
        session.add(exercise)
        session.commit()
        session.refresh(exercise)

        return mapper.transform_to_response(exercise, personal_record=True)

    return Response(status_code=204)


@router.delete("/{exercise_id}", dependencies=[Depends(get_db)])
def delete_exercise(exercise_id: int, session: Session = Depends(get_db)):
    exercise = session.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    session.delete(exercise)
    session.commit()
    return JSONResponse(
        status_code=200, content={"message": "Exercise deleted successfully"}
    )
