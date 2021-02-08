from flask import Flask

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.plugin import KosekiPluginManager
from koseki.util import KosekiUtil


class KosekiView:
    def __init__(
        self,
        app: Flask,
        auth: KosekiAuth,
        mail: KosekiMailer,
        plugins: KosekiPluginManager,
        storage: Storage,
        util: KosekiUtil,
    ):
        self.app = app
        self.auth = auth
        self.mail = mail
        self.plugins = plugins
        self.storage = storage
        self.util = util

    def register(self) -> None:
        pass
