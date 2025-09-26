from fastapi import FastAPI

from app.routers import dashboards, exercises, routines, sessions, users

app = FastAPI()

app.include_router(dashboards.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(routines.router, prefix="/api/v1", tags=["routines"])
app.include_router(exercises.router, prefix="/api/v1", tags=["exercises"])
