from flask import jsonify, make_response, request
from flask_restful import reqparse

from .exceptions import ValidationError


class RequestParser(reqparse.RequestParser):

    def __init__(self, **kwargs):
        kwargs['bundle_errors'] = True
        super().__init__(**kwargs)

    def parse_args(self, req=None, strict=True, http_error_code=400):
        if req is None:
            req = request

        namespace = self.namespace_class()

        req.unparsed_arguments = dict(self.argument_class('').source(req)) if strict else {}

        errors = {}
        for arg in self.args:
            value, found = arg.parse(req, self.bundle_errors)

            if isinstance(value, ValueError):
                errors.update(found)
                found = None

            if found or arg.store_missing:
                namespace[arg.dest or arg.name] = value

        for key, value in req.unparsed_arguments.items():
            errors[key] = 'Unexpected argument'

        if errors:
            raise ValidationError(response=make_response(jsonify(errors=errors), http_error_code))

        return namespace
