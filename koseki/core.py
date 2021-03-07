
import datetime
import os
import time

from flask import session
from flask.app import Flask
from flask_multistatic import MultiStaticFlask  # type: ignore
from markupsafe import Markup

from koseki.auth import KosekiAuth
from koseki.config import KosekiConfig
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
from koseki.reverse import ReverseProxied
from koseki.schedule import KosekiScheduler
from koseki.theme import install_theme
from koseki.util import KosekiUtil
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


class KosekiCore:
    def __init__(self) -> None:
        #
        # Flask App
        #
        app = MultiStaticFlask("koseki")
        app.wsgi_app = ReverseProxied(app.wsgi_app)
        app.config.from_object(KosekiConfig())
        app.config.from_pyfile(os.path.join("..", "koseki.cfg"))
        self.app: Flask = app

        #
        # Theme
        #
        static_folders: list[str] = []
        install_theme(app, "koseki", static_folders)

        theme: str = app.config["THEME"]
        if theme is not None and len(theme.strip()) > 0 and theme != "koseki":
            install_theme(app, theme, static_folders)

        app.static_folder = static_folders

        #
        # Storage
        #
        if app.config["DB_TYPE"].lower() == "sqlite":
            self.storage = Storage("sqlite:///%s" %
                                   app.config["DB_SQLITE_PATH"])
        elif app.config["DB_TYPE"].lower() == "mysql":
            self.storage = Storage(
                "mysql://%s:%s@%s/%s"
                % (
                    app.config["DB_USER"],
                    app.config["DB_PASSWORD"],
                    app.config["DB_HOST"],
                    app.config["DB_DATABASE"],
                )
            )
        else:
            raise ValueError(
                "DB_TYPE is unsupported. Please choose between sqlite/mysql.")
        # Return connections to db pool after closure
        self.app.teardown_appcontext(self.storage.close)

        # Misc Utilities
        self.auth = KosekiAuth(self.storage)
        self.util = KosekiUtil(app, self.auth, self.storage)
        self.mail = KosekiMailer(self.app)
        self.scheduler = KosekiScheduler(app, self.storage, self.mail)
        self.plugins = KosekiPluginManager(
            self.app, self.storage, self.auth, self.util, self.scheduler)

    def start(self, flask_server: bool = True) -> None:
        with self.app.app_context():
            # Register own context processors
            self._register_context_processors()

            # Register views
            self._register_views()

            #
            # Enable Plugins
            #
            # Do this before activating stuff to allow them to register hooks.
            self.plugins.register_plugins()

            # Enable the scheduler
            self.scheduler.start()

            # Start the webserver
            if flask_server:
                try:
                    self.app.run(host=self.app.config["WEB_HOST"],
                                 port=self.app.config["WEB_PORT"])
                except SystemExit:
                    pass  # Flask shut down.

    def _register_views(self) -> None:
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
        for viewType in views:
            view: KosekiView = viewType(self.app, self.auth, self.mail, self.plugins, self.storage,
                                        self.util)
            view.register()

    def _register_context_processors(self) -> None:
        self.app.context_processor(lambda: dict(
            plugin_isenabled=self.plugins.isenabled))
        self.app.context_processor(lambda: dict(gravatar=self.util.gravatar))
        self.app.context_processor(
            lambda: dict(make_nav=lambda: session["nav"]))
        self.app.context_processor(lambda: dict(member_of=self.auth.member_of))
        self.app.context_processor(lambda: dict(now=lambda: datetime.datetime(2000, 1, 1)
                                                .fromtimestamp(time.time())))
        self.app.context_processor(lambda: dict(
            generate_swish_code=self.util.generate_swish_code))
        self.app.context_processor(lambda: dict(
            uid_to_name=self.util.uid_to_name))
        self.app.context_processor(lambda: dict(
            alerts=self.util.render_alerts()))
        self.app.add_template_filter(self.util.format_date, "date")
        self.app.add_template_filter(lambda x: x if x is not None else Markup(
            '<span class="text-muted">None</span>'), "pretty_none")
