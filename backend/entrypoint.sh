#!/bin/bash
# entrypoint.sh

# 1. Run database migrations
echo "Running database migrations..."
alembic upgrade head

# 2. Start the application server
echo "Starting Gunicorn/Uvicorn server..."
# The $1, $2... are arguments passed from the Dockerfile's CMD
# spawn 4 uvicorn workers
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000