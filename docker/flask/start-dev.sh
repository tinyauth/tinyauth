#! /bin/bash

if [ "$TINYAUTH_AUTH_MODE" == "db" ]; then
  python -m tinyauth db upgrade
fi

export FLASK_APP=tinyauth.wsgi
export FLASK_DEBUG=1
export PYTHONPATH=$(pwd)
flask run -h 0.0.0.0 -p 8000
