#!/bin/sh
 
# This script will migrate schema and data from a SQLite3 database to PostgreSQL.
# Schema translation based on http://stackoverflow.com/a/4581921/1303625.
# Some column types are not handled (e.g blobs).
 
PG_DB_NAME=paideia
PG_USER_NAME=ianwscott
 
SQLITE_DUMP_FILE=$1
 
#sqlite3 $SQLITE_DB_PATH .dump > $SQLITE_DUMP_FILE
 
# PRAGMAs are specific to SQLite3.
sed -i '/PRAGMA/d' $SQLITE_DUMP_FILE
# Convert sequences.
sed -i '/sqlite_sequence/d ; s/integer PRIMARY KEY AUTOINCREMENT/serial PRIMARY KEY/ig' $SQLITE_DUMP_FILE
# Convert column types.
sed -i 's/datetime/timestamp/g ; s/integer[(][^)]*[)]/integer/g ; s/text[(]\([^)]*\)[)]/varchar(\1)/g' $SQLITE_DUMP_FILE
 
#createdb -U $PG_USER_NAME $PG_DB_NAME
psql $PG_DB_NAME $PG_USER_NAME < $SQLITE_DUMP_FILE
 
# Update Postgres sequences.
psql $PG_DB_NAME $PG_USER_NAME -c "\ds" | grep sequence | cut -d'|' -f2 | tr -d '[:blank:]' |
while read sequence_name; do
  table_name=${sequence_name%_id_seq}
 
  psql $PG_DB_NAME $PG_USER_NAME -c "select setval('$sequence_name', (select max(id) from $table_name))"
done
