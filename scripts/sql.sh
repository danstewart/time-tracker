#!/usr/bin/env bash

# Starts an sqlite shell within the container

docker exec -it time-tracker sqlite3 db/time.db
