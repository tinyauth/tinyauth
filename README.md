# tinyauth

[![Docker Automated build](https://img.shields.io/docker/automated/tinyauth/tinyauth.svg)](https://hub.docker.com/r/tinyauth/tinyauth/) [![PyPI](https://img.shields.io/pypi/v/tinyauth.svg)](https://pypi.python.org/pypi/tinyauth) [![Codecov](https://img.shields.io/codecov/c/github/tinyauth/tinyauth.svg)](https://codecov.io/gh/tinyauth/tinyauth)

This codebase implements a simple authentication and authorization system as a microservice.


## Dev Environment

You can get a simple dev environment with Docker and docker-compose. Dev happens on macOS with Docker for Mac:

```
docker-compose -f dev.yml build
docker-compose -f dev.yml up
```

This will automatically run any migrations.

You can run tests with:

```
docker-compose -f dev.yml run --rm flask py.test tinyauth/
```

And run flake8 with:

```
docker-compose -f dev.yml run --rm flask flake8 tinyauth/
```
