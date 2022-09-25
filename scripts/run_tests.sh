#!/usr/bin/env bash

# Installs test dependencies and runs the tests

docker exec -it log-my-time pipenv install --dev
docker exec -it log-my-time pipenv run pytest
