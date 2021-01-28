from typing import Callable
from koseki.util import KosekiUtil
from flask import abort, redirect, request, session, url_for


class KosekiAuth:
    def __init__(self, util: KosekiUtil):
        self.util = util

    def require_session(self, f: Callable, groups=None):
        def wrap(*args, **kwargs):
            if not "uid" in session:
                return redirect(url_for("login", redir=request.base_url))
            else:
                if (
                    groups is None
                    or sum(1 for group in groups if self.util.member_of(group)) > 0
                ):
                    return f(*args, **kwargs)
                else:
                    abort(403)

        wrap.__name__ = f.__name__
        return wrap
