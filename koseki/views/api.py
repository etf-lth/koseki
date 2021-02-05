from flask import jsonify, request
from koseki.db.types import Person
from koseki.view import KosekiView
from sqlalchemy import or_, and_


class APIView(KosekiView):
    def register(self):
        self.app.add_url_rule(
            "/api/ac/members",
            None,
            self.auth.require_session(
                self.api_ac_members, ["admin", "accounter", "board"]
            ),
            methods=["GET"],
        )

    def api_ac_members(self):
        term = request.args.get("term", "")
        members = (
            self.storage.session.query(Person)
            .filter(or_(Person.fname.like(term + "%%"), Person.lname.like(term + "%%"),
            and_(Person.fname.like(term.split(" ")[0] + "%%"), Person.lname.like(term.split(" ")[-1] + "%%"))))
            .all()
        )
        return jsonify(
            data=[
                {"label": "%s %s" % (p.fname, p.lname), "value": p.uid} for p in members
            ]
        )
