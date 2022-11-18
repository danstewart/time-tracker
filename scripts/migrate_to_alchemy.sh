#!/usr/bin/env bash

# This script migrates the database from the old schema to the new one.

# Rename tables
sqlite3 db/time.db "ALTER TABLE LoginSession RENAME TO login_session;"

# Rename columns
sqlite3 db/time.db "ALTER TABLE login_session RENAME COLUMN user TO user_id;"
sqlite3 db/time.db "ALTER TABLE time RENAME COLUMN user TO user_id;"
sqlite3 db/time.db "ALTER TABLE break RENAME COLUMN time TO time_id;"
sqlite3 db/time.db "ALTER TABLE settings RENAME COLUMN user TO user_id;"

# Fixing constraints
sqlite3 db/time.db <<EOF
CREATE TABLE IF NOT EXISTS "break_temp" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "time_id" INTEGER NOT NULL REFERENCES "Time" ("id") ON DELETE CASCADE,
  "start" INTEGER NOT NULL,
  "end" INTEGER,
  "note" TEXT
);
EOF

sqlite3 db/time.db 'INSERT INTO break_temp SELECT * FROM break;'
sqlite3 db/time.db 'DROP TABLE break;'
sqlite3 db/time.db 'ALTER TABLE break_temp RENAME TO break;'
sqlite3 db/time.db 'CREATE INDEX "idx_break__time" ON "break" ("time_id");'

echo "OK"
