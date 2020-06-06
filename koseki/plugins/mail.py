from koseki.core import require_session, nav
from koseki.db.types import Person
from flask import render_template


class MailPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule("/mail", None, self.mail)
        self.core.nav(
            "/mail", "envelope", "Mail", 4, ["admin", "board", "pr", "m3", "krangare"]
        )

    @require_session(["admin", "board", "pr", "m3", "krangare"])
    def mail(self):
        return render_template(
            "list_mail.html",
            persons=self.storage.session.query(Person).filter_by(state="active").all(),
        )
