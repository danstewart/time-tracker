#!/usr/bin/env bash

# Wipe out the database

docker exec -it time-tracker rm -f db/time.db
docker compose restart app
