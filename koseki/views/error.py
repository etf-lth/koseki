from flask import escape, redirect, render_template, request, session, url_for

from koseki.db.types import Person


class ErrorView:
    def __init__(self, app):
        self.app = app

    def register(self):
        self.app.register_error_handler(400, self.error_bad_request)
        self.app.register_error_handler(403, self.error_forbidden)
        self.app.register_error_handler(404, self.error_not_found)

    def error_bad_request(self, error):
        return (
            render_template(
                "error.html",
                code=400,
                codename="Bad Request",
                message="The browser sent an invalid request, unable to be understood by the server.",
            ),
            400,
        )

    def error_forbidden(self, error):
        return (
            render_template(
                "error.html",
                code=403,
                codename="Forbidden",
                message="You do not have permission to access this page.",
            ),
            403,
        )

    def error_not_found(self, error):
        return (
            render_template(
                "error.html",
                code=404,
                codename="Not Found",
                message="The requested page or resource was not found.",
            ),
            404,
        )
