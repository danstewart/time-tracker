#!/usr/bin/env bash

if [[ $FLASK_ENV == 'dev' ]]; then
  exec flask run --host 0.0.0.0 --port 5000
else
  exec gunicorn \
    --workers 4 \
    --threads 4 \
    --worker-class gevent \
    --bind 0.0.0.0:5000 \
    --worker-tmp-dir /dev/shm \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    'app:create_app()'
fi
