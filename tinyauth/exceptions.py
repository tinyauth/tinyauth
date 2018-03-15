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


class IdentityError(Exception):
    key = "IdentityError"
    status = 401

    def asdict(self):
        return {
            "Authorized": False,
            "ErrorCode": self.key,
            'Status': self.status,
        }


class Unsigned(IdentityError):
    key = "UnsignedRequest"


class InvalidSignature(IdentityError):
    key = "InvalidSignature"

    def __init__(self, *args, identity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity = identity


class NoSuchKey(InvalidSignature):
    key = "NoSuchKey"


class CsrfError(InvalidSignature):
    key = "CsrfError"


class ClockSkewError(InvalidSignature):
    key = "ClockSkew"
