
import base64
import datetime
import hashlib
import logging
import time

import requests
from flask import session
from flask_babel import format_datetime  # type: ignore
from sqlalchemy.util.langhelpers import NoneType

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
        self.alt_login = None

    def nav(self, uri, icon, title, weight=0, groups=None):
        self.navigation.append(KosekiNavigationEntry(
            uri, icon, title, weight, groups))

    def calc_nav(self):
        nav: list[KosekiNavigationEntry] = []
        for n in self.navigation:
            if n.groups is None or sum(
                1 for group in n.groups if self.member_of(group)
            ) > 0:
                nav.append(n)
        session["nav"] = sorted(nav, key=lambda x: x.weight)

    def start_session(self, uid):
        session["uid"] = int(uid)
        session.permanent = True
        session.modified = True
        self.calc_nav()

    def destroy_session(self):
        session.pop("uid", None)

    def make_nav_processor(self):
        def make_nav():
            return session["nav"]

        return dict(make_nav=make_nav)

    def now_processor(self):
        def now():
            return datetime.datetime(2000, 1, 1).fromtimestamp(time.time())

        return dict(now=now)

    def gravatar_processor(self):
        def gravatar(mail):
            return (
                "//gravatar.com/avatar/" +
                hashlib.md5(mail.encode("utf-8")).hexdigest()
            )

        return dict(gravatar=gravatar)

    def format_date(self, value, format="y-MM-dd"):
        return format_datetime(value, format)

    def uid_to_name(self):
        def uid_to_name_inner(uid):
            person = self.storage.session.query(
                Person).filter_by(uid=uid).scalar()
            return "%s %s" % (person.fname, person.lname) if person else "Nobody"

        return dict(uid_to_name=uid_to_name_inner)

    def swish_qrcode_processor(self):
        def swish_qrcode(member):
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

        return dict(swish_qrcode=swish_qrcode)

    def member_of_processor(self):
        return dict(member_of=self.member_of)

    def member_of(self, group, person=None):
        if person is None:
            person = self.current_user()
        if type(person) in (int, int):
            person = self.storage.query(Person).filter_by(uid=person).scalar()
        if type(group) == int:
            group = self.storage.query(Group).filter_by(gid=group).scalar()
        elif type(group) == str:
            group = self.storage.query(Group).filter_by(name=group).scalar()

        if type(group) is NoneType:
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

    def get_alternate_login(self):
        return self.alt_login

    def alternate_login(self, alt):
        self.alt_login = alt()
        logging.info("Registered alternate login provider: %s" %
                     self.alt_login)
