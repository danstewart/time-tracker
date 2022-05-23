#!/usr/bin/env bash

# Wipe out the database

docker exec -it log-my-time rm -f db/time.db
docker compose restart app
