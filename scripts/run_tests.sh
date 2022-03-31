#!/usr/bin/env bash

# Installs test dependencies and runs the tests

docker exec -it time-tracker poetry install
docker exec -it time-tracker pytest
