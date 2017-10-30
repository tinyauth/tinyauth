# microauth

[![Docker Automated buil](https://img.shields.io/docker/automated/Jc2k/microauth.svg)]()
[![PyPI](https://img.shields.io/pypi/v/microauth.svg)]()
[![Codecov](https://img.shields.io/codecov/c/github/codecov/example-python.svg)]()

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
docker-compose -f dev.yml run --rm flask py.test microauth/
```

And run flake8 with:

```
docker-compose -f dev.yml run --rm flask flake8 microauth/
```
