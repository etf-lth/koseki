import base64
import datetime
import hashlib
import time

import requests
from flask import Flask, session
from flask_babel import format_datetime  # type: ignore

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.db.types import Person
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
from koseki.util import KosekiUtil


class KosekiCore:
    def __init__(self, app: Flask, storage: Storage):
        self.util = KosekiUtil(storage)
        self.auth = KosekiAuth(self.util)
        self.app = app
        self.storage = storage
        self.mail = KosekiMailer(app)
        self.plugins = KosekiPluginManager(self.app, self.storage, self.auth, self.util)

        app.context_processor(self.make_nav_processor)
        app.context_processor(self.now_processor)
        app.context_processor(self.gravatar_processor)
        app.add_template_filter(self.format_date, "date")
        app.context_processor(self.uid_to_name)
        app.context_processor(self.util.member_of_processor)
        app.context_processor(self.swish_qrcode_processor)

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
