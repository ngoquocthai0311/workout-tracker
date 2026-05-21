from backend.app.services.session_service import get_session_service
from backend.app.services.session_service import SessionService

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.routers.schemas.request_schemas import (
    CreateWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
)
from app.routers.schemas.response_schemas import (
    SessionResponse,
)

router = APIRouter(tags=["sessions"], prefix="/sessions")


@router.get(
    "",
    response_model=list[SessionResponse],
)
def read_sessions(
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return session_service.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{workout_session_id}",
    response_model=SessionResponse,
)
def get_session(
    workout_session_id: int,
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return session_service.get_one(workout_session_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.post(
    "",
    response_model=SessionResponse,
)
def create_session(
    input: CreateWorkoutSessionRequest,
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return session_service.create(input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.patch(
    "/{workout_session_id}",
    response_model=SessionResponse,
)
def update_session(
    workout_session_id: int,
    input: UpdateWorkoutSessionRequest,
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return session_service.update(workout_session_id, input)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.delete("/{workout_session_id}")
def delete_Session(
    workout_session_id: int,
    session_service: SessionService = Depends(get_session_service),
):
    try:
        session_service.delete(workout_session_id)
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
