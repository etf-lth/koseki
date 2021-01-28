import base64
import datetime
import hashlib
from koseki.plugin import KosekiPluginManager
import logging
import time

import requests
from flask import Flask, abort, redirect, request, session, url_for
from flask_babel import Babel, format_datetime

from koseki.db.storage import Storage
from koseki.db.types import Group, Person
from koseki.mail import KosekiMailer


class KosekiCore:
    def __init__(self, app: Flask, storage: Storage):
        self.app = app
        self.storage = storage

        self.babel = Babel(app)
        self.mail = KosekiMailer(app)
        self.plugins = KosekiPluginManager(self)

        self.navigation = []
        self.alt_login = None

        app.context_processor(self.make_nav_processor)
        app.context_processor(self.now_processor)
        app.context_processor(self.gravatar_processor)
        app.add_template_filter(self.format_date, "date")
        app.context_processor(self.uid_to_name)
        app.context_processor(self.member_of_processor)
        app.context_processor(self.swish_qrcode_processor)

    def make_nav_processor(self):
        def make_nav():
            return session["nav"]

        return dict(make_nav=make_nav)

    def now_processor(self):
        def now():
            return datetime.datetime(2000, 1, 1).fromtimestamp(time.time())

        return dict(now=now)

    def nav(self, uri, icon, title, weight=0, groups=None):
        self.navigation.append(
            {
                "uri": uri,
                "icon": icon,
                "title": title,
                "groups": groups,
                "weight": weight,
            }
        )

    def calc_nav(self):
        nav = []
        for n in self.navigation:
            if n["groups"] is None or sum(
                1 for group in n["groups"] if self.member_of(group)
            ):
                nav.append(n)
        session["nav"] = sorted(nav, key=lambda x: x["weight"])

    def gravatar_processor(self):
        def gravatar(mail):
            return (
                "//gravatar.com/avatar/" + hashlib.md5(mail.encode("utf-8")).hexdigest()
            )

        return dict(gravatar=gravatar)

    def format_date(self, value, format="y-MM-dd"):
        return format_datetime(value, format)

    def uid_to_name(self):
        def uid_to_name_inner(uid):
            person = self.storage.session.query(Person).filter_by(uid=uid).scalar()
            return "%s %s" % (person.fname, person.lname) if person else "Nobody"

        return dict(uid_to_name=uid_to_name_inner)

    def member_of(self, group, person=None):
        if person is None:
            person = self.current_user()
        if type(person) in (int, int):
            person = self.storage.session.query(Person).filter_by(uid=person).scalar()
        if type(group) == int:
            group = self.storage.session.query(Group).filter_by(gid=group).scalar()
        elif type(group) == str:
            group = self.storage.session.query(Group).filter_by(name=group).scalar()
        return sum(1 for x in person.groups if x.gid == group.gid)

    def current_user(self):
        return session["uid"]

    def start_session(self, uid):
        session["uid"] = int(uid)
        session.permanent = True
        session.modified = True
        self.calc_nav()

    def destroy_session(self):
        session.pop("uid", None)

    def member_of_processor(self):
        return dict(member_of=self.member_of)

    def get_alternate_login(self):
        return self.alt_login

    def alternate_login(self, alt):
        self.alt_login = alt()
        logging.info("Registered alternate login provider: %s" % self.alt_login)

    def require_session(self, f, groups=None):
        def wrap(*args, **kwargs):
            if not "uid" in session:
                return redirect(url_for("login", redir=request.base_url))
            else:
                if groups is None or sum(
                    1 for group in groups if self.member_of(group)
                ):
                    return f(*args, **kwargs)
                else:
                    abort(403)

        wrap.__name__ = f.__name__
        return wrap

    def fetch_alerts(self):
        alerts = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def set_alerts(self, alerts):
        session["alerts"] = alerts

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
