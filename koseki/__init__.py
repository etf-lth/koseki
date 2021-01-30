import logging

from flask import Flask, g
from flask_babel import Babel  # type: ignore
from flask_bootstrap import Bootstrap  # type: ignore

from koseki.config import KosekiConfig
from koseki.core import KosekiCore
from koseki.db.storage import Storage
from koseki.reverse import ReverseProxied
from koseki.update import Updater
from koseki.view import KosekiView
from koseki.views.add import AddView
from koseki.views.api import APIView
from koseki.views.error import ErrorView
from koseki.views.fees import FeesView
from koseki.views.index import IndexView
from koseki.views.list import ListView
from koseki.views.mail import MailView
from koseki.views.membership import MembershipView
from koseki.views.session import SessionView
from koseki.views.user import UserView

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler('koseki.log', 'a', 'utf-8')])

app = Flask("koseki")
app.config.from_object(KosekiConfig())
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
Bootstrap(app)
Babel(app)
core = KosekiCore(app, storage)
updater = Updater(app, storage, core.mail)


# Return connections to db pool after closure
@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def register_views():
    views = [
        AddView,
        APIView,
        ErrorView,
        FeesView,
        IndexView,
        ListView,
        MailView,
        MembershipView,
        SessionView,
        UserView,
    ]
    view: KosekiView
    for viewType in views:
        view = viewType(app, storage, core.auth, core.util, core.mail)
        view.register()


def create_app():
    with app.app_context():
        storage.insert_initial_values()
        updater.start()
        core.plugins.register_plugins()
        register_views()  # Must come after creation of Core
        app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore
    return app


def run_koseki():
    create_app().run()


__all__ = ["run_koseki"]
