from app.database.session_repository import SessionRepository

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from app.routers.schemas.request_schemas import (
    CreateWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
)
from app.dependencies import (
    get_db,
    get_workout_session_mapper,
    get_session_repository,
    RedisService,
    get_redis_service,
)
from app.routers.schemas.response_schemas import (
    SessionResponse,
)
from app.routers.mappers.sessions_mapper import WorkoutSessionMapper

router = APIRouter(tags=["sessions"], prefix="/sessions")


@router.get(
    "",
    response_model=list[SessionResponse],
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def read_sessions(
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        workout_sessions = session_repository.get_all(session)
        return mapper.map_list_to_response(workout_sessions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{workout_session_id}",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def get_session(
    workout_session_id: int,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        workout_session = session_repository.get_by_id(session, workout_session_id)
        return mapper.transform_to_response(workout_session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.post(
    "",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def create_session(
    input: CreateWorkoutSessionRequest,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
    session_repository: SessionRepository = Depends(get_session_repository),
    redis_service: RedisService = Depends(get_redis_service),
):
    try:
        created_workout_session = session_repository.create(session, input)
        return mapper.transform_to_response(created_workout_session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.patch(
    "/{workout_session_id}",
    response_model=SessionResponse,
    dependencies=[Depends(get_db), Depends(get_workout_session_mapper)],
)
def update_session(
    workout_session_id: int,
    input: UpdateWorkoutSessionRequest,
    mapper: WorkoutSessionMapper = Depends(get_workout_session_mapper),
    session: Session = Depends(get_db),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        updated_session = session_repository.update(session, workout_session_id, input)
        if not update_session:
            return Response(status_code=204)
        return mapper.transform_to_response(updated_session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.delete("/{workout_session_id}", dependencies=[Depends(get_db)])
def delete_Session(
    workout_session_id: int,
    session: Session = Depends(get_db),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        session_repository.remove_by_id(session, workout_session_id)
        return JSONResponse(
            status_code=200, content={"message": "Workout session deleted successfully"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )
