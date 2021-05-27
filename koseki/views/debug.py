from typing import Union

from flask import render_template
from werkzeug.wrappers import Response

from koseki.view import KosekiView

class DebugView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/debug",
            None,
            self.auth.require_session(self.debug_general, ["admin"]),
            methods=["GET"],
        )

    def debug_general(self) -> Union[str, Response]:
        return render_template(
            "debug_general.html"
        )