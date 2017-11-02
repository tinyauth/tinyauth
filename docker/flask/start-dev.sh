#!/bin/sh
python -m microauth db upgrade
python -m microauth run -h 0.0.0.0 -p 8000
