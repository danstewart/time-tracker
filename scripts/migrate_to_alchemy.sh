#!/usr/bin/env bash

# This script migrates the database from the old schema to the new one.

# Rename tables
sqlite3 db/time.db "ALTER TABLE LoginSession RENAME TO login_session;"
sqlite3 db/time.db "ALTER TABLE User RENAME TO user;"
sqlite3 db/time.db "ALTER TABLE Settings RENAME TO settings;"
sqlite3 db/time.db "ALTER TABLE Time RENAME TO time;"
sqlite3 db/time.db "ALTER TABLE Break RENAME TO break;"

# Rename columns
sqlite3 db/time.db "ALTER TABLE login_session RENAME COLUMN user TO user_id;"
sqlite3 db/time.db "ALTER TABLE time RENAME COLUMN user TO user_id;"
sqlite3 db/time.db "ALTER TABLE break RENAME COLUMN time TO time_id;"
sqlite3 db/time.db "ALTER TABLE settings RENAME COLUMN user TO user_id;"

echo "OK"
