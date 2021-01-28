import importlib
import logging

from flask import Flask, g
from flask_bootstrap import Bootstrap

from koseki.config import KosekiConfig
from koseki.core import KosekiCore
from koseki.db.storage import Storage
from koseki.db.types import Person, PersonGroup
from koseki.plugin import KosekiPlugin
from koseki.reverse import ReverseProxied
from koseki.update import Updater
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
    format="%(asctime)s %(message)s", level=logging.DEBUG, filename="koseki.log"
)
app = Flask(__name__)
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
core = KosekiCore(app, storage)
updater = Updater(core)


## Return connections to db pool after closure
@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def register_views():
    views = []
    views.append(AddView(app, core, storage))
    views.append(APIView(app, core, storage))
    views.append(ErrorView(app))
    views.append(FeesView(app, core, storage))
    views.append(IndexView(app, core, storage))
    views.append(ListView(app, core, storage))
    views.append(MailView(app, core, storage))
    views.append(MembershipView(app, core, storage))
    views.append(SessionView(app, core, storage))
    views.append(UserView(app, core, storage))
    for v in views:
        v.register()


def create_app():
    with app.app_context():
        storage.insert_initial_values()
        updater.start()
        core.plugins.register_plugins()
        register_views()
        app.wsgi_app = ReverseProxied(app.wsgi_app)
    return app


def run_koseki():
    create_app().run()


__all__ = ["run_koseki"]
