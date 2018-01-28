import uuid


class RequestIdMiddleware(object):

    HEADER = 'X-Request-Id'
    HEADER_KEY = 'HTTP_X_REQUEST_ID'

    def __init__(self, app):
        self.app = app
        self.wsgi_app, app.wsgi_app = app.wsgi_app, self

    def __call__(self, environ, start_response):
        request_id = environ.setdefault(self.HEADER_KEY, str(uuid.uuid4()))

        def new_start_response(status, response_headers, exc_info=None):
            response_headers.append((self.HEADER, request_id))
            return start_response(status, response_headers, exc_info)

        return self.wsgi_app(environ, new_start_response)
