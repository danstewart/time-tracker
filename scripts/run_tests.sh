#!/usr/bin/env bash

# Installs test dependencies and runs the tests

docker exec -it log-my-time poetry install --with test
docker exec -it log-my-time poetry run pytest
