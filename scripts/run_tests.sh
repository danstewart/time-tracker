#!/usr/bin/env bash

docker exec -it time-tracker poetry install
docker exec -it time-tracker pytest
