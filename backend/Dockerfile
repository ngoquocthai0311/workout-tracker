FROM python:3.13-slim

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

# Copy alembic
COPY ./alembic /backend/alembic
COPY ./alembic.ini /backend/alembic.ini

# Copy source code
COPY ./app /backend/app

# Copy and ensure the script is executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Set the entry point to the script
ENTRYPOINT ["/backend/entrypoint.sh"]

# CMD provides the arguments to the ENTRYPOINT (though the script above hardcodes the Gunicorn command)
# If the script hardcodes the Gunicorn command, the CMD can be left out or used to override the default.
