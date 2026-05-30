from app.services.routine_service import RoutineService
from app.services.routine_service import get_routine_service
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.routers.schemas.request_schemas import (
    CreateRoutineRequest,
    UpdateRoutineRequest,
)

from app.routers.schemas.response_schemas import RoutineResponse

router = APIRouter(tags=["routines"], prefix="/routines")


@router.get(
    "",
    response_model=list[RoutineResponse],
)
def read_routines(
    routine_service: RoutineService = Depends(get_routine_service),
):
    try:
        return routine_service.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{routine_id}",
    response_model=RoutineResponse,
)
def get_routine(
    routine_id: int,
    routine_service: RoutineService = Depends(get_routine_service),
):
    try:
        return routine_service.get_by_id(routine_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.post(
    "",
    response_model=RoutineResponse,
)
def create_routine(
    input: CreateRoutineRequest,
    routine_service: RoutineService = Depends(get_routine_service),
):
    try:
        return routine_service.create(input)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.patch(
    "/{routine_id}",
    response_model=RoutineResponse,
)
def update_routine(
    routine_id: int,
    input: UpdateRoutineRequest,
    routine_service: RoutineService = Depends(get_routine_service),
):
    try:
        return routine_service.update(routine_id, input)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.delete("/{routine_id}")
def delete_routine(
    routine_id: int,
    routine_service: RoutineService = Depends(get_routine_service),
):
    try:
        routine_service.delete(routine_id)
        return JSONResponse(
            status_code=200, content={"message": "Routine deleted successfully"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )
