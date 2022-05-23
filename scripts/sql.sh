#!/usr/bin/env bash

# Starts an sqlite shell within the container

docker exec -it log-my-time sqlite3 db/time.db
