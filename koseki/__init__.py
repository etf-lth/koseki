import logging

from flask import Flask
from flask_babel import Babel  # type: ignore
from flask_bootstrap import Bootstrap  # type: ignore

from koseki.config import KosekiConfig
from koseki.core import KosekiCore
from koseki.db.storage import Storage
from koseki.reverse import ReverseProxied

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler('koseki.log', 'a', 'utf-8')])


def create_app():
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

    # Return connections to db pool after closure
    app.teardown_appcontext(storage.close)

    with app.app_context():
        Bootstrap(app)
        Babel(app)
        KosekiCore(app, storage)
        app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore
    return app


def run_koseki():
    create_app().run()


__all__ = ["run_koseki"]
