from flask import request, jsonify
from sqlalchemy import or_

from koseki.db.types import Person


class APIView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/api/ac/members",
            None,
            self.core.require_session(
                self.api_ac_members, ["admin", "accounter", "board"]
            ),
            methods=["GET"],
        )

    def api_ac_members(self):
        term = request.args.get("term", "")
        members = (
            self.storage.session.query(Person)
            .filter(or_(Person.fname.like(term + "%%"), Person.lname.like(term + "%%")))
            .all()
        )
        return jsonify(
            data=[
                {"label": "%s %s" % (p.fname, p.lname), "value": p.uid} for p in members
            ]
        )
