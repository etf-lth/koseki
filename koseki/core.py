
from flask import Flask

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
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
    def __init__(self, app: Flask, storage: Storage):
        self.app = app
        self.storage = storage
        self.util = KosekiUtil(self.storage)
        self.auth = KosekiAuth(self.util)
        self.mail = KosekiMailer(self.app)
        self.scheduler = KosekiScheduler(app, storage, self.mail)
        self.plugins = KosekiPluginManager(
            self.app, self.storage, self.auth, self.util)

        # Register own context processors
        self._register_context_processors()

        # Register views
        self._register_views()

        # =========================
        #
        # Enable plugins
        #
        # =========================
        #
        # Do this before activating stuff to allow them to register hooks.
        self.plugins.register_plugins()

        # Enable the scheduler
        self.scheduler.start()

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
            view = viewType(self.app, self.storage, self.auth, self.util, self.mail)
            view.register()

    def _register_context_processors(self):
        self.app.context_processor(self.util.gravatar_processor)
        self.app.context_processor(self.util.make_nav_processor)
        self.app.context_processor(self.util.member_of_processor)
        self.app.context_processor(self.util.now_processor)
        self.app.context_processor(self.util.swish_qrcode_processor)
        self.app.context_processor(self.util.uid_to_name)
        self.app.add_template_filter(self.util.format_date, "date")
