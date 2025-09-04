from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select

from app.database.models import User
from app.routers.schemas.request_schemas import CreateUserRequest, UpdateUserRequest
from app.dependencies import get_db

router = APIRouter(tags=["users"], prefix="/users")


@router.get("", response_model=list[User], dependencies=[Depends(get_db)])
def read_users(session: Session = Depends(get_db)):
    users = session.exec(select(User)).all()

    return users


@router.get("/{user_id}", response_model=User, dependencies=[Depends(get_db)])
def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("", response_model=User, dependencies=[Depends(get_db)])
def create_user(input: CreateUserRequest, session: Session = Depends(get_db)):
    timestamp = datetime.now(timezone.utc).timestamp()
    user = User(
        username=input.username,
        created_at=timestamp,
        updated_at=timestamp,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=User, dependencies=[Depends(get_db)])
def update_user(
    user_id: int, input: UpdateUserRequest, session: Session = Depends(get_db)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timestamp = datetime.now(timezone.utc).timestamp()
    if input.username and user.username != input.username:
        user.username = input.username
        user.updated_at = timestamp

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return Response(status_code=204)


@router.delete("/{user_id}", dependencies=[Depends(get_db)])
def delete_user(user_id: int, session: Session = Depends(get_db)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return JSONResponse(
        status_code=200, content={"message": "User deleted successfully"}
    )
