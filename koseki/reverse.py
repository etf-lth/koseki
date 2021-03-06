from typing import Callable

from flask.app import Flask
from werkzeug.wrappers import Response


class ReverseProxied(object):
    def __init__(self, app: Flask) -> None:
        self.app = app

    def __call__(self, environ: dict, start_response: Callable) -> Response:
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name):]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)
