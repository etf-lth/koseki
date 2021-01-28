from flask import Flask

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.mail import KosekiMailer
from koseki.util import KosekiUtil


class KosekiView:
    def __init__(
        self,
        app: Flask,
        storage: Storage,
        auth: KosekiAuth,
        util: KosekiUtil,
        mail: KosekiMailer,
    ):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util
        self.mail = mail

    def register(self) -> None:
        pass
