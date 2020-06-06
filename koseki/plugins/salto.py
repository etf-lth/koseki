from koseki.core import member_of
from koseki.db.types import Person
from flask import request, abort


class SaltoPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage
        self.allowed_ips = ("130.235.20.201", "130.235.20.67", "194.47.250.246")

    def register(self):
        self.app.add_url_rule("/salto/all", None, self.salto_all)
        self.app.add_url_rule("/salto/sales", None, self.salto_sales)
        self.app.add_url_rule("/salto/mek", None, self.salto_mek)

    def salto_all(self):
        if "X-Real-IP" in request.headers and (
            not request.headers["X-Real-IP"] in self.allowed_ips
        ):
            abort(403)
        out = ""
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.stil is None or len(member.stil) < 1:
                continue
            out = out + member.stil + "\r\n"
        return out

    def salto_sales(self):
        if "X-Real-IP" in request.headers and (
            not request.headers["X-Real-IP"] in self.allowed_ips
        ):
            abort(403)
        out = ""
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.stil is None or len(member.stil) < 1:
                continue
            if member_of("sales", member):
                out = out + member.stil + "\r\n"
        return out

    def salto_mek(self):
        if "X-Real-IP" in request.headers and (
            not request.headers["X-Real-IP"] in self.allowed_ips
        ):
            abort(403)
        out = ""
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.stil is None or len(member.stil) < 1:
                continue
            if member_of("mek", member):
                out = out + member.stil + "\r\n"
        return out
