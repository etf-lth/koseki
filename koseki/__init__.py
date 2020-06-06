from koseki.update import Updater
from koseki.mail import Mailer
import os
import base64
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask import Flask
from koseki.db.types import Person, Group, PersonGroup
from koseki.db.storage import Storage
from . import reverse
import logging

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, filename="koseki.log"
)
app = Flask(__name__)
app.config.from_pyfile("../koseki.cfg")
storage = Storage(
    "mysql://%s:%s@%s/%s"
    % (
        app.config["DB_USER"],
        app.config["DB_PASSWORD"],
        app.config["DB_HOST"],
        app.config["DB_DATABASE"],
    )
)
babel = Babel(app)
boostrap = Bootstrap(app)

import koseki.core
from koseki.plugins import *

from koseki.plugins.mail import MailPlugin
from koseki.plugins.salto import SaltoPlugin

from koseki.views.add import AddView
from koseki.views.error import ErrorView
from koseki.views.fees import FeesView
from koseki.views.index import IndexView
from koseki.views.list import ListView
from koseki.views.membership import MembershipView
from koseki.views.session import SessionView
from koseki.views.user import UserView

updater = Updater(app, storage)
mailer = Mailer(app)
core = koseki.core


def register_views():
    MailPlugin(app, core, storage).register()
    SaltoPlugin(app, core, storage).register()

    views = []
    views.append(AddView(app, core, storage, mailer))
    views.append(ErrorView(app))
    views.append(FeesView(app, core, storage, mailer))
    views.append(IndexView(app, core, storage))
    views.append(ListView(app, core, storage))
    views.append(MembershipView(app, core, storage))
    views.append(SessionView(app, core, storage))
    views.append(UserView(app, core, storage))
    for v in views:
        v.register()


def create_app():
    with app.app_context():
        if storage.session.query(Person).count() < 1:
            storage.add(
                Person(
                    uid=1,
                    fname="Test",
                    lname="Testsson",
                    email="test@example.com",
                    stil="admin",
                    password="5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
                )
            )  # pass: password
            storage.add(PersonGroup(uid=1, gid=1))
            storage.commit()
        updater.start()
        register_views()
        app.secret_key = base64.b64decode(app.config["SECRET_KEY"])
        app.debug = app.config["DEBUG"]
        app.wsgi_app = reverse.ReverseProxied(app.wsgi_app)
    return app


def run_koseki():
    create_app().run()


__all__ = ["run_koseki"]
