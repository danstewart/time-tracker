#!/usr/bin/env bash

# Installs test dependencies and runs the tests

docker exec -it time-tracker poetry install --with test
docker exec -it time-tracker poetry run pytest
