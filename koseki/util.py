import base64
import datetime
import hashlib
import logging
from typing import Optional, Union, cast

import requests
from flask import session

from koseki.db.storage import Storage
from koseki.db.types import Group, Person


class KosekiAlertType:
    DANGER = "alert-danger"
    SUCCESS = "alert-success"
    WARNING = "alert-warning"


class KosekiAlert(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, category: str, title: str, message: str):
        dict.__init__(self, category=category, title=title, message=message)
        self.category: str
        self.title: str
        self.message: str


class KosekiNavigationEntry(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, uri: str, icon: str, title: str, weight: int, groups: list[str]):
        dict.__init__(self, uri=uri, icon=icon, title=title,
                      weight=weight, groups=groups)
        self.uri: str
        self.icon: str
        self.title: str
        self.weight: int
        self.groups: list[str]


class KosekiUtil:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.navigation: list[KosekiNavigationEntry] = []
        self.alt_login: list[dict] = []

    def nav(self, uri: str, icon: str, title: str, weight: int = 0, groups: list[str] = None) -> None:
        if groups is None:
            groups = []
        self.navigation.append(KosekiNavigationEntry(
            uri, icon, title, weight, groups))

    def calc_nav(self) -> None:
        nav: list[KosekiNavigationEntry] = []
        for n in self.navigation:
            if n.groups is None or sum(
                1 for group in n.groups if self.member_of(group)
            ) > 0:
                nav.append(n)
        session["nav"] = sorted(nav, key=lambda x: x.weight)

    def start_session(self, uid: int) -> None:
        session["uid"] = uid
        session.permanent = True
        session.modified = True
        self.calc_nav()

    def current_user(self) -> int:
        return session["uid"]

    def destroy_session(self) -> None:
        session.pop("uid", None)

    def gravatar(self, mail: str) -> str:
        return (
            "//gravatar.com/avatar/" +
            hashlib.md5(mail.encode("utf-8")).hexdigest()
        )

    def format_date(self, value: datetime.datetime, date_format: str = "%Y-%m-%d") -> str:
        return value.strftime(date_format)

    def uid_to_name(self, uid: int) -> str:
        person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        return "%s %s" % (person.fname, person.lname) if person else "Nobody"

    def swish_qrcode(self, member: Person) -> str:
        if member.balance >= 0:
            return ""
        data = dict(
            format="png",
            size=350,
            message={"value": member.username, "editable": False},
            amount={"value": -float(member.balance), "editable": False},
            payee={"value": "123 019 24 76", "editable": False},
        )
        headers = {"Content-type": "application/json"}
        response = requests.post(
            "https://mpc.getswish.net/qrg-swish/api/v1/prefilled",
            headers=headers,
            json=data,
        )
        return (
            "data:"
            + response.headers["Content-Type"]
            + ";"
            + "base64,"
            + str(base64.b64encode(response.content), "utf-8")
        )

    def member_of(self, group: Union[int, str, Group, None], person: Optional[Person] = None) -> bool:
        if group is None:
            raise ValueError("group cannot be None when checking member_of")
        if person is None:
            person = self.storage.query(Person).filter_by(
                uid=self.current_user()).scalar()

        if type(group) == int:
            group = self.storage.query(Group).filter_by(gid=group).scalar()
        elif type(group) == str:
            group = self.storage.query(Group).filter_by(name=group).scalar()

        if group is None:
            return False

        g: Group = cast(Group, group)
        return sum(1 for x in person.groups if x.gid == g.gid) > 0

    def alert(self, alert: KosekiAlert) -> None:
        if "alerts" not in session:
            session["alerts"] = []
        session["alerts"].append(alert)

    def render_alerts(self) -> list[KosekiAlert]:
        alerts: list[KosekiAlert] = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def get_alternate_logins(self) -> list[dict]:
        return self.alt_login

    def alternate_login(self, alt: dict) -> None:
        self.alt_login.append(alt)
        logging.info("Registered alternate login provider: %s", alt["button"])
