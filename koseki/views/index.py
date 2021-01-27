from datetime import datetime

from flask import render_template
from koseki.db.types import Person


class IndexView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule("/", None, self.core.require_session(self.index))
        self.core.nav("/", "home", "Home", -999)

    def index(self):
        if self.core.member_of("admin") or self.core.member_of("board"):
            active = (
                self.storage.session.query(Person).filter_by(state="active").count()
            )
            pending = (
                self.storage.session.query(Person).filter_by(state="pending").count()
            )
            enrolled = (
                self.storage.session.query(Person)
                .filter(Person.enrolled >= datetime.now().replace(month=1, day=1))
                .count()
            )
            return render_template(
                "overview.html", active=active, pending=pending, enrolled=enrolled
            )
        else:
            return render_template("home.html")
