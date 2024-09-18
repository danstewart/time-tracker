#!/usr/bin/env bash

if [[ $FLASK_DEBUG == 1 ]]; then
  exec flask run --host 0.0.0.0 --port 5000
else
  exec gunicorn \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --bind 0.0.0.0:5000 \
    --worker-tmp-dir /dev/shm \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --preload \
    'app:create_app()'
fi
