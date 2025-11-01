from fastapi import FastAPI, HTTPException
from loguru import logger
import sys
import os
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from app.routers import dashboards, exercises, routines, sessions, users

app = FastAPI()

app.include_router(dashboards.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(routines.router, prefix="/api/v1", tags=["routines"])
app.include_router(exercises.router, prefix="/api/v1", tags=["exercises"])

# NOTE: FastAPI makes use of StarletteHTTPException, using it as default http handler
# To inject logger method later in override function
default_http_handler = app.exception_handlers[StarletteHTTPException]

# set up logging

# remove logger handler from root logging built-in
logger.remove()

# add a stylish, ready-to-parse sink
logger.add(
    sys.stdout,
    level="DEBUG" if os.getenv("DEV", 0) else "INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    # NOTE: used to serialize log into other extension file
    serialize=True if os.getenv("DEV", 0) else False,
    # NOTE: may leak production data, used in DEV
    diagnose=False if os.getenv("DEV", 0) else True,
    backtrace=True,
    # NOTE: enforce thread safe logging
    # enqueue=True,
)

# add configuration for log file
logger.add(
    "logs/app.log",
    rotation="10 MB",  # or "00:00" for daily rotation
    retention="20 days",
    compression="zip",
    level="DEBUG" if os.getenv("DEV", 0) else "INFO",
)


# override HTTPException to inject logger method
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    messages: list = [request.method, request.url.path, exc.detail]
    logger.error(" - ".join(messages))
    return await default_http_handler(request, exc)
