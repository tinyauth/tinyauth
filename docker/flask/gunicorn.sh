#!/bin/sh
/usr/local/bin/gunicorn --worker-class gevent --config /app/etc/gunicorn.conf --log-config /app/etc/logging.conf tinyauth.wsgi:app
