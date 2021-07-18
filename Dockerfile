# syntax = docker/dockerfile:1.2

# Use slim buster images
FROM python:3.9-slim-buster

LABEL version="0.0.1"

# Set env vars
ENV FLASK_ENV "${FLASK_ENV}"
ENV FLASK_APP "${FLASK_APP}"
ENV FLASK_DEBUG "${FLASK_DEBUG}"

# Disable auto-cleanup after install:
RUN rm /etc/apt/apt.conf.d/docker-clean

# Install updates and cache across builds
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,id=apt apt-get update && apt-get -y upgrade && apt-get -y install sqlite3 libsqlite3-dev

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

# Install python deps
# TODO: Pip caching isn't working due to a permission error
COPY --chown=app:app ./requirements.txt ./
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/home/app/.cache/pip,id=pip pip install -r requirements.txt

# Get traceback for C crashes
ENV PYTHONFAULTHANDLER=1

# Copy the source code
COPY --chown=app:app . ./

# Run
EXPOSE 5000

# Blank entrypoint allows passing custom commands via `docker run`
ENTRYPOINT [  ]

CMD [ "./entrypoint.sh" ]
