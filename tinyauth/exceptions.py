from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    HTTPException,
    Unauthorized,
)

__all__ = [
    'HTTPException',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
]


class AuthenticationError(Unauthorized):
    pass


class AuthorizationError(Forbidden):
    pass


class ValidationError(BadRequest):
    pass
