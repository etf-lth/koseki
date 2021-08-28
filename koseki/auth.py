from typing import Callable, Optional, Union, cast

from argon2 import PasswordHasher  # type: ignore
from argon2.exceptions import VerifyMismatchError  # type: ignore
from flask import abort, redirect, request, session, url_for
from werkzeug.wrappers import Response

from koseki.db.storage import Storage
from koseki.db.types import Group, Person


class KosekiAuth:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.__ph = PasswordHasher()

    def current_user(self) -> int:
        return session["uid"]

    def member_of(self, group: Union[int, str, Group, None], person: Optional[Person] = None) -> bool:
        if group is None:
            raise ValueError("group cannot be None when checking member_of")
        if person is None:
            person = self.storage.query(Person).filter_by(
                uid=self.current_user()).scalar()

        if isinstance(group, int):
            group = self.storage.query(Group).filter_by(gid=group).scalar()
        elif isinstance(group, str):
            group = self.storage.query(Group).filter_by(name=group).scalar()

        if group is None:
            return False
        group = cast(Group, group)

        return sum(1 for x in person.groups if x.gid == group.gid) > 0

    def require_session(self, func: Callable, groups: list[str] = None) -> Callable:
        def wrap(*args, **kwargs) -> Union[str, Response]:  # type: ignore
            if "uid" not in session:
                return redirect(url_for("login", redir=request.url))
            else:
                if (
                    groups is None
                    or sum(1 for group in groups if self.member_of(group)) > 0
                ):
                    return func(*args, **kwargs)
                else:
                    abort(403)

        wrap.__name__ = func.__name__
        return wrap

    def hash_password(self, password: str) -> str:
        return self.__ph.hash(password)

    def verify_password(self, password: Union[str, None], password2: str) -> bool:
        if password is None:
            return False
        try:
            self.__ph.verify(password, password2)
            return True
        except VerifyMismatchError:
            return False
