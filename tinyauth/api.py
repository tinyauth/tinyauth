from flask_restful import Api as OldApi


class Api(OldApi):

    def error_router(self, original_handler, e):
        return original_handler(e)
