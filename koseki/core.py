
import datetime
import os
import time

from flask import session
from flask_multistatic import MultiStaticFlask  # type: ignore

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
    def __init__(self):
        #
        # Flask App
        #
        app = MultiStaticFlask("koseki")
        app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore
        app.config.from_object(KosekiConfig())
        app.config.from_pyfile(os.path.join("..", "koseki.cfg"))
        self.app = app

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
        self.storage = Storage(
            "mysql://%s:%s@%s/%s"
            % (
                app.config["DB_USER"],
                app.config["DB_PASSWORD"],
                app.config["DB_HOST"],
                app.config["DB_DATABASE"],
            )
        )
        # Return connections to db pool after closure
        self.app.teardown_appcontext(self.storage.close)

        # Misc Utilities
        self.util = KosekiUtil(self.storage)
        self.auth = KosekiAuth(self.util)
        self.mail = KosekiMailer(self.app)
        self.scheduler = KosekiScheduler(app, self.storage, self.mail)
        self.plugins = KosekiPluginManager(
            self.app, self.storage, self.auth, self.util)

    def start(self, flask_server=True):
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
                    self.app.run(host="127.0.0.1", port=self.app.config["WEB_PORT"])
                except SystemExit:
                    pass  # Flask shut down.

    def _register_views(self):
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
            view = viewType(self.app, self.auth, self.mail, self.plugins, self.storage,
                            self.util)
            view.register()

    def _register_context_processors(self):
        self.app.context_processor(lambda : dict(plugin_isenabled=self.plugins.isenabled))
        self.app.context_processor(lambda : dict(gravatar=self.util.gravatar))
        self.app.context_processor(lambda : dict(make_nav=lambda: session["nav"]))
        self.app.context_processor(lambda : dict(member_of=self.util.member_of))
        self.app.context_processor(lambda : 
            dict(now=lambda: datetime.datetime(2000, 1, 1).fromtimestamp(time.time())))
        self.app.context_processor(lambda : dict(swish_qrcode=self.util.swish_qrcode))
        self.app.context_processor(lambda : dict(uid_to_name=self.util.uid_to_name))
        self.app.context_processor(lambda : dict(alerts=self.util.render_alerts()))
        self.app.add_template_filter(self.util.format_date, "date")
