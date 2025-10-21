from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from app.routers.schemas.request_schemas import (
    CreateRoutineRequest,
    UpdateRoutineRequest,
)
from app.dependencies import get_db, get_routine_mapper, get_routine_repository
from app.routers.schemas.response_schemas import RoutineResponse
from app.routers.mappers.routines_mapper import RoutineMapper
from app.database.routine_repository import RoutineRepository

router = APIRouter(tags=["routines"], prefix="/routines")


@router.get(
    "",
    response_model=list[RoutineResponse],
)
def read_routines(
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
    routine_repository: RoutineRepository = Depends(get_routine_repository),
):
    try:
        routines = routine_repository.get_all(session)
        return mapper.map_list_to_response(routines)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/{routine_id}",
    response_model=RoutineResponse,
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def get_routine(
    routine_id: int,
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
    routine_repository: RoutineRepository = Depends(get_routine_repository),
):
    try:
        routine = routine_repository.get_by_id(session, routine_id)

        return mapper.transform_to_response(routine)
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
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
    routine_repository: RoutineRepository = Depends(get_routine_repository),
):
    try:
        routine = routine_repository.create(session, input)

        return mapper.transform_to_response(routine)
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
    dependencies=[Depends(get_db), Depends(get_routine_mapper)],
)
def update_routine(
    routine_id: int,
    input: UpdateRoutineRequest,
    mapper: RoutineMapper = Depends(get_routine_mapper),
    session: Session = Depends(get_db),
    routine_repository: RoutineRepository = Depends(get_routine_repository),
):
    try:
        updated_routine = routine_repository.update(session, routine_id, input)
        if not updated_routine:
            return Response(status_code=204)

        return mapper.transform_to_response(updated_routine)
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
    session: Session = Depends(get_db),
    routine_repository: RoutineRepository = Depends(get_routine_repository),
):
    try:
        routine_repository.remove_by_id(session, routine_id)
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
