import datetime
import json
import logging
import logging.handlers
from functools import wraps

from flask import request

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    HTTPException,
    ValidationError,
)

AUDIT_LOG_MAX_BYTES = 500 * 1024 * 1024
AUDIT_LOG_BACKUP_COUNT = 5

logger = logging.getLogger('tinyauth.audit')


class AuditFormatter(logging.Formatter):

    _skip_fields = [
        'name',
        'args',
        'pathname',
        'levelno',
        'filename',
        'module',
        'lineno',
        'funcName',
        'processName',
        'message',
        'msg',
        'msecs',
        'created',
    ]

    def _json_default(self, obj):
        if isinstance(obj, (datetime.date, datetime.time)):
            return obj.isoformat()

        return str(obj)

    def formatTime(self, record, datefmt=None):
        ct = datetime.datetime.fromtimestamp(record.created)
        return ct.isoformat()

    def format(self, record):
        message = {}

        message['event'] = record.msg
        message['created'] = self.formatTime(record, self.datefmt)

        for field, value in record.__dict__.items():
            if not value:
                continue
            if field in self._skip_fields:
                continue
            message[field] = value

        return json.dumps(message, default=self._json_default)


def audit_request(event_name):
    '''
    Decorate a view function with automatic audit logging

    All attempts to access the view will be recorded.

    This will pass a dictionary `context` to the view - it should include extra
    metadata that you want to include in the audit event
    '''

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            context = {}

            if 'X-Request-Id' in request.headers:
                context['request-id'] = request.headers['X-Request-Id']

            try:
                response = f(context, *args, **kwargs)
                context['http.status'] = getattr(response, 'status_code', 200)
                return response
            except (ValidationError, AuthorizationError, AuthenticationError) as e:
                context['http.status'] = e.code
                context['errors'] = e.description
                raise e
            except HTTPException as e:
                context['http.status'] = e.code
                raise e
            finally:
                logger.info(
                    event_name,
                    extra=context,
                )
        return wrapper
    return decorator


def audit_request_cbv(event_name):
    '''
    Decorate a view function with automatic audit logging

    All attempts to access the view will be recorded.

    This will pass a dictionary `context` to the view - it should include extra
    metadata that you want to include in the audit event
    '''

    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            context = {}

            if 'X-Request-Id' in request.headers:
                context['request-id'] = request.headers['X-Request-Id']

            try:
                response = f(self, context, *args, **kwargs)
                context['http.status'] = getattr(response, 'status_code', 200)
                return response
            except (ValidationError, AuthorizationError, AuthenticationError) as e:
                context['http.status'] = e.code
                context['errors'] = e.description
                raise e
            except HTTPException as e:
                context['http.status'] = e.code
                raise e
            finally:
                logger.info(
                    event_name,
                    extra=context,
                )
        return wrapper
    return decorator


def format_headers_for_audit_log(headers):
    output = []
    for key, value in headers:
        if key.lower() in ['authorization', 'cookie']:
            value = '** NOT LOGGED **'
        output.append(': '.join((key, value)))
    return output


def setup_audit_log(app):
    if app.config.get('AUDIT_LOG_FILENAME', None):
        handler = logging.handlers.RotatingFileHandler(
            app.config['AUDIT_LOG_FILENAME'],
            maxBytes=app.config.get('AUDIT_LOG_MAX_BYTES', AUDIT_LOG_MAX_BYTES),
            backupCount=app.config.get('AUDIT_LOG_BACKUP_COUNT', AUDIT_LOG_BACKUP_COUNT),
            encoding='utf-8',
            delay=False,
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(AuditFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
