#!/bin/sh
python -m tinyauth db upgrade

export FLASK_APP=tinyauth.wsgi
export FLASK_DEBUG=1
export PYTHONPATH=$(pwd)
flask run -h 0.0.0.0 -p 8000
