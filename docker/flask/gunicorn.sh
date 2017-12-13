#!/bin/sh
/usr/local/bin/gunicorn --config /app/etc/gunicorn.conf --log-config /app/etc/logging.conf tinyauth.wsgi:app
