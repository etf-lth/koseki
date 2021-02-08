from typing import Union

from flask import jsonify, request
from sqlalchemy import and_, or_
from werkzeug.wrappers import Response

from koseki.db.types import Person
from koseki.view import KosekiView


class APIView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/api/ac/members",
            None,
            self.auth.require_session(
                self.api_ac_members, ["admin", "accounter", "board"]
            ),
            methods=["GET"],
        )

    def api_ac_members(self) -> Union[str, Response]:
        term = request.args.get("term", "")
        members = (
            self.storage.session.query(Person)
            .filter(or_(
                Person.fname.like(term + "%%"), Person.lname.like(term + "%%"),
                and_(
                    Person.fname.like(term.split(" ")[0] + "%%"),
                    Person.lname.like(term.split(" ")[-1] + "%%"),
                ),
            ))
            .all()
        )
        res: Response = jsonify(
            data=[
                {"label": "%s %s" % (p.fname, p.lname), "value": p.uid} for p in members
            ]
        )
        return res
