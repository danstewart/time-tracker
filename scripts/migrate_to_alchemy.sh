#!/usr/bin/env bash

# This script migrates the database from the old schema to the new one.

echo "Applying migrations to new database..."
docker exec -it log-my-time flask db upgrade

echo "Copying data from old database to new database..."

# Fixing constraints
sqlite3 db/time.db <<EOF
ATTACH DATABASE "db/time.db.old" AS old;

INSERT INTO user SELECT * FROM old.user;
INSERT INTO time SELECT * FROM old.time;
INSERT INTO break SELECT * FROM old.break;
INSERT INTO settings SELECT * FROM old.settings;
EOF

echo "Completed migration."
