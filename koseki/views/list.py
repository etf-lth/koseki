from flask import url_for, render_template, session, redirect, escape, request
from koseki.db.types import Person


class ListView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/list",
            None,
            self.core.require_session(self.list_members, ["admin", "board"]),
        )
        self.core.nav("/list", "list", "List", 1, ["admin", "board"])

    def list_members(self):
        return render_template(
            "list_members.html",
            persons=self.storage.session.query(Person)
            .order_by(Person.uid.desc())
            .all(),
        )
