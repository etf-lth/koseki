from typing import Union

from flask import render_template
from werkzeug.wrappers import Response

from koseki.db.types import Person
from koseki.view import KosekiView


class ListView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/list",
            None,
            self.auth.require_session(self.list_members, ["admin", "board"]),
        )
        self.util.nav("/list", "list", "List", 1, ["admin", "board"])

    def list_members(self) -> Union[str, Response]:
        return render_template(
            "list_members.html",
            persons=self.storage.session.query(Person)
            .order_by(Person.uid.desc())
            .all(),
        )
