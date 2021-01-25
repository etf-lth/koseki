import base64
import logging
import os

from flask import Flask, g
from flask_babel import Babel
from flask_bootstrap import Bootstrap

from koseki.core import KosekiCore
from koseki.db.storage import Storage
from koseki.db.types import Group, Person, PersonGroup
from koseki.mail import Mailer
from koseki.plugins.cas import CASPlugin
from koseki.plugins.salto import SaltoPlugin
from koseki.reverse import ReverseProxied
from koseki.update import Updater
from koseki.views.add import AddView
from koseki.views.api import APIView
from koseki.views.error import ErrorView
from koseki.views.fees import FeesView
from koseki.views.index import IndexView
from koseki.views.kiosk import KioskView
from koseki.views.list import ListView
from koseki.views.mail import MailView
from koseki.views.membership import MembershipView

if os.name != "nt":
    from koseki.views.print import PrintView

from koseki.views.session import SessionView
from koseki.views.store import StoreView
from koseki.views.user import UserView

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

mailer = Mailer(app)
updater = Updater(app, storage, mailer)
core = KosekiCore(app, storage, babel)


def register_plugins():
    cas = CASPlugin(app, core, storage)
    cas.register()
    SaltoPlugin(app, core, storage).register()
    core.alternate_login(cas.cas_login)


## Return connections to db pool after closure
@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def register_views():
    views = []
    views.append(APIView(app, core, storage))
    views.append(AddView(app, core, storage, mailer))
    views.append(ErrorView(app))
    views.append(FeesView(app, core, storage, mailer))
    views.append(IndexView(app, core, storage))
    views.append(KioskView(app, core, storage))
    views.append(ListView(app, core, storage))
    views.append(MailView(app, core, storage))
    views.append(MembershipView(app, core, storage))
    if os.name != "nt":
        views.append(PrintView(app, core, storage))
    views.append(SessionView(app, core, storage))
    views.append(StoreView(app, core, storage))
    views.append(UserView(app, core, storage))
    for v in views:
        v.register()


def create_app():
    with app.app_context():
        if storage.session.query(Person).count() < 1:
            storage.add(
                Person(
                    uid=1,
                    fname="Admin",
                    lname="Testsson",
                    email="admin@example.com",
                    stil="admin",
                    password="5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
                )
            )  # pass: password
            storage.add(
                Person(
                    uid=1,
                    fname="User",
                    lname="Testsson",
                    email="user@example.com",
                    stil="user",
                    password="5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
                )
            )  # pass: password
            storage.add(PersonGroup(uid=1, gid=1))
            storage.commit()
        updater.start()
        register_plugins()
        register_views()
        app.secret_key = base64.b64decode(app.config["SECRET_KEY"])
        app.debug = app.config["DEBUG"]
        app.wsgi_app = ReverseProxied(app.wsgi_app)
    return app


def run_koseki():
    create_app().run()


__all__ = ["run_koseki"]
