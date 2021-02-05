
import base64
import datetime
import hashlib
import logging

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

    def __init__(self, type: str, title: str, message: str):
        dict.__init__(self, type=type, title=title, message=message)
        self.type: str
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

    def nav(self, uri, icon, title, weight=0, groups=None) -> None:
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

    def start_session(self, uid) -> None:
        session["uid"] = int(uid)
        session.permanent = True
        session.modified = True
        self.calc_nav()

    def destroy_session(self) -> None:
        session.pop("uid", None)

    def gravatar(self, mail) -> str:
        return (
            "//gravatar.com/avatar/" +
            hashlib.md5(mail.encode("utf-8")).hexdigest()
        )

    def format_date(self, value: datetime.datetime, format="%Y-%m-%d") -> str:
        return value.strftime(format)

    def uid_to_name(self, uid) -> str:
        person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        return "%s %s" % (person.fname, person.lname) if person else "Nobody"

    def swish_qrcode(self, member) -> str:
        if member.balance >= 0:
            return ""
        data = dict(
            format="png",
            size=350,
            message={"value": member.stil, "editable": False},
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

    def member_of(self, group, person=None) -> bool:
        if person is None:
            person = self.current_user()
        if type(person) in (int, int):
            person = self.storage.query(Person).filter_by(uid=person).scalar()
        if type(group) == int:
            group = self.storage.query(Group).filter_by(gid=group).scalar()
        elif type(group) == str:
            group = self.storage.query(Group).filter_by(name=group).scalar()

        if group is None:
            return False

        return sum(1 for x in person.groups if x.gid == group.gid) > 0

    # TODO: move current_user to auth?
    def current_user(self):
        return session["uid"]

    def fetch_alerts(self) -> list[KosekiAlert]:
        alerts: list[KosekiAlert] = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def set_alerts(self, alerts: list[KosekiAlert]) -> None:
        session["alerts"] = alerts

    def get_alternate_logins(self) -> list[dict]:
        return self.alt_login

    def alternate_login(self, alt: dict):
        self.alt_login.append(alt)
        logging.info("Registered alternate login provider: %s" % alt["button"])
