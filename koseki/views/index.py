from datetime import datetime
from typing import Union

from flask import render_template
from werkzeug.wrappers import Response

from koseki.db.types import Person
from koseki.view import KosekiView


class IndexView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule("/", None, self.auth.require_session(self.index))
        self.util.nav("/", "home", "Home", -999)

    def index(self) -> Union[str, Response]:
        if self.util.member_of("admin") or self.util.member_of("board"):
            active = (
                self.storage.session.query(
                    Person).filter_by(state="active").count()
            )
            pending = (
                self.storage.session.query(Person).filter_by(
                    state="pending").count()
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
