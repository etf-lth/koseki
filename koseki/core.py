
import os

from flask_bs4 import Bootstrap  # type: ignore
from flask_multistatic import MultiStaticFlask  # type: ignore

from koseki.auth import KosekiAuth
from koseki.config import KosekiConfig
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
from koseki.reverse import ReverseProxied
from koseki.schedule import KosekiScheduler
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
        Bootstrap(app)
        self.app = app

        #
        # Theme
        #
        theme: str = app.config["THEME"]
        if theme is None or not theme.strip():
            theme = "koseki"

        app.config.from_pyfile(os.path.join("themes", "koseki", "theme.cfg"))
        app.config.from_pyfile(os.path.join("themes", theme, "theme.cfg"))

        # Static folders are prioritized in ascending order.
        app.static_folder = [
            os.path.join(app.root_path, "themes", theme),
            os.path.join(app.root_path, "themes", "koseki"),
        ]

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

    def start(self):
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
            self.app.run()

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
            view = viewType(self.app, self.storage,
                            self.auth, self.util, self.mail)
            view.register()

    def _register_context_processors(self):
        self.app.context_processor(self.util.gravatar_processor)
        self.app.context_processor(self.util.make_nav_processor)
        self.app.context_processor(self.util.member_of_processor)
        self.app.context_processor(self.util.now_processor)
        self.app.context_processor(self.util.swish_qrcode_processor)
        self.app.context_processor(self.util.uid_to_name)
        self.app.add_template_filter(self.util.format_date, "date")
