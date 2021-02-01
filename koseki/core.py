
from flask import Flask

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
from koseki.util import KosekiUtil


class KosekiCore:
    def __init__(self, app: Flask, storage: Storage):
        self.app = app
        self.storage = storage
        self.util = KosekiUtil(self.storage)
        self.auth = KosekiAuth(self.util)
        self.mail = KosekiMailer(self.app)
        self.plugins = KosekiPluginManager(
            self.app, self.storage, self.auth, self.util)

        # Enable plugins
        self.plugins.register_plugins()
        # Register Flask context processors
        self._register_context_processors()

    def _register_context_processors(self):
        self.app.context_processor(self.util.gravatar_processor)
        self.app.context_processor(self.util.make_nav_processor)
        self.app.context_processor(self.util.member_of_processor)
        self.app.context_processor(self.util.now_processor)
        self.app.context_processor(self.util.swish_qrcode_processor)
        self.app.context_processor(self.util.uid_to_name)
        self.app.add_template_filter(self.util.format_date, "date")
