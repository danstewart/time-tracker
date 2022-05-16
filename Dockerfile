# syntax = docker/dockerfile:1.2

# Use slim buster images
FROM python:3.10-slim-buster

LABEL version="0.0.1"

# Set env vars
ENV FLASK_ENV "${FLASK_ENV}"
ENV FLASK_APP "${FLASK_APP}"
ENV FLASK_DEBUG "${FLASK_DEBUG}"

# Disable auto-cleanup after install:
RUN rm /etc/apt/apt.conf.d/docker-clean

# Install updates and cache across builds
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,id=apt apt-get update && apt-get -y upgrade && apt-get -y install curl sqlite3 libsqlite3-dev

# Create user and work dir
RUN useradd --create-home app

USER app
WORKDIR /home/app/time-tracker
RUN mkdir --parents /home/app/time-tracker
RUN mkdir --parents /home/app/time-tracker/db/
RUN touch /home/app/.sqliterc
RUN echo ".headers on\n.mode columns" > /home/app/.sqliterc

# Set PATH
ENV PATH "/home/app/.local/bin/:${PATH}"
ENV PROJECT_ROOT '/home/app/time-tracker'

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0b1

# Install python deps
COPY --chown=app:app pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root --with dev,test

# Get traceback for C crashes
ENV PYTHONFAULTHANDLER=1

# Copy the source code
COPY --chown=app:app . ./

# Run
EXPOSE 5000

# Blank entrypoint allows passing custom commands via `docker run`
ENTRYPOINT [  ]

CMD [ "./entrypoint.sh" ]
