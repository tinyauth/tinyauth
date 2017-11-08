#!/bin/sh
python -m tinyauth db upgrade
python -m tinyauth run -h 0.0.0.0 -p 8000
