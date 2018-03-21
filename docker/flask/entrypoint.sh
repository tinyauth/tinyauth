#!/bin/bash
set -e
cmd="$@"

if [ -z "$TINYAUTH_AUTH_MODE" ]; then
    export TINYAUTH_AUTH_MODE=db
fi

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

if [ -z "$POSTGRES_HOST" ]; then
    export POSTGRES_HOST=postgres
fi

export DATABASE_URI=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_USER


function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_USER", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="$POSTGRES_HOST")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

if [ "$TINYAUTH_AUTH_MODE" == "db" ]; then
  until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
  done
  >&2 echo "Postgres is up - continuing..."
fi

exec $cmd
