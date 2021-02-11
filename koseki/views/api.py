import logging
from typing import Union
from urllib.parse import unquote

import requests
from flask import jsonify, request
from sqlalchemy import and_, or_
from werkzeug.exceptions import abort
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
        self.app.add_url_rule(
            "/api/swish/<string:code>",
            None,
            self.auth.require_session(self.api_swish),
            methods=["GET"],
        )

    def api_ac_members(self) -> Union[str, Response]:
        term = request.args.get("term")
        if term is None:
            return jsonify(data=[])
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

    def api_swish(self, code: str) -> Union[str, Response]:
        # return self.util.generate_swish_code(100, "Test")
        signed, message = self.util.validate_swish_code(code)
        if not signed:
            logging.warning("Refusing invalid QR-code : %s", code)
            abort(400, "Invalid Swish QR Code.")
        if message is None:
            logging.fatal("Signed QR Code Message contained no message: %s", code)
            abort(500, "The Signed Message contained no message.")

        parts = message.split(";")

        lock_mask: int = int(parts[3])
        data = dict(
            format="png",
            size=500,
            transparent=True,
            border=1,
            message={
                "value": unquote(parts[2]),
                "editable": lock_mask & (1 << 2)},
            amount={
                "value": parts[1],
                "editable": lock_mask & (1 << 1)},
            payee={
                "value": parts[0].lstrip("C"),
                "editable": lock_mask & (1 << 0)},
        )
        headers = {"Content-type": "application/json"}
        response = requests.post(
            "https://mpc.getswish.net/qrg-swish/api/v1/prefilled",
            headers=headers,
            json=data,
        )
        return Response(response.content, mimetype=response.headers["Content-Type"])
