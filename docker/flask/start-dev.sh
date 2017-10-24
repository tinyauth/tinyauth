#!/bin/sh
python -m microauth db upgrade
python -m microauth runserver -h 0.0.0.0 -p 8000
