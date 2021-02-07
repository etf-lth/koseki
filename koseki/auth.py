from typing import Callable, Union

from argon2 import PasswordHasher  # type: ignore
from argon2.exceptions import VerifyMismatchError  # type: ignore
from flask import abort, redirect, request, session, url_for
from werkzeug.wrappers import Response

from koseki.db.types import Person
from koseki.util import KosekiUtil


class KosekiAuth:
    def __init__(self, util: KosekiUtil):
        self.util = util
        self.__ph = PasswordHasher()

    def require_session(self, f: Callable, groups: list[str] = None) -> Callable:
        def wrap(*args, **kwargs) -> Union[str, Response]: # type: ignore
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

    def hash_password(self, password: str) -> str:
        return self.__ph.hash(password)

    def verify_password(self, person: Person, password: str) -> bool:
        if type(person.password) is None:
            return False
        try:
            self.__ph.verify(person.password, password)
            return True
        except VerifyMismatchError:
            return False
