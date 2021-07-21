#!/usr/bin/env bash

docker exec -it time-tracker rm -f db/time.db
docker-compose restart app
