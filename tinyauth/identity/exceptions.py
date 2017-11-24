class IdentityError(Exception):
    key = "IdentityError"

    def asdict(self):
        return {
            "Authorized": False,
            "ErrorCode": self.key
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
