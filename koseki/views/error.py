from typing import Tuple, Union
from flask import render_template
from werkzeug.wrappers import Response
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView


class ErrorView(KosekiView):
    def register(self) -> None:
        self.app.register_error_handler(400, self.error_bad_request)
        self.app.register_error_handler(403, self.error_forbidden)
        self.app.register_error_handler(404, self.error_not_found)

    def error_bad_request(self, error: Exception) -> Tuple[Union[str, Response], int]:
        self.util.alert(KosekiAlert(
            KosekiAlertType.DANGER,
            "Bad Request",
            "The browser sent an invalid request, unable to be understood by the server. \
                Koseki was therefore unable to produce a correct response. \
                Please contact a member of the staff if the problem persists.",
        ))
        return (
            render_template(
                "error.html",
                code=400,
            ),
            400,
        )

    def error_forbidden(self, error: Exception) -> Tuple[Union[str, Response], int]:
        self.util.alert(KosekiAlert(
            KosekiAlertType.DANGER,
            "Forbidden",
            "You do not have permission to access this page. \
                Koseki was therefore unable to produce a correct response. \
                Please contact a member of the staff if the problem persists.",
        ))
        return (
            render_template(
                "error.html",
                code=403,
            ),
            403,
        )

    def error_not_found(self, error: Exception) -> Tuple[Union[str, Response], int]:
        self.util.alert(KosekiAlert(
            KosekiAlertType.DANGER,
            "Not Found",
            "The requested page or resource was not found. \
                Koseki was therefore unable to produce a correct response. \
                Please contact a member of the staff if the problem persists.",
        ))
        return (
            render_template(
                "error.html",
                code=404,
            ),
            404,
        )
