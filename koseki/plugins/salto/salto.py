from flask import Blueprint
from koseki.db.types import Person
from koseki.plugin import KosekiPlugin


class SaltoPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "SALTO_ALLOWED_IPS": ["130.235.20.201", "130.235.20.67", "194.47.250.246"],
            "USER_USERNAME_ENABLED": True, # Override to enable Debt in Koseki
        }

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint("salto", __name__)
        blueprint.add_url_rule("/salto/all", None, self.salto_all)
        blueprint.add_url_rule("/salto/sales", None, self.salto_sales)
        blueprint.add_url_rule("/salto/mek", None, self.salto_mek)
        return blueprint

    def salto_all(self) -> str:
        # if "X-Real-IP" in request.headers and (
        #    not request.headers["X-Real-IP"] in self.app.config["SALTO_ALLOWED_IPS"]
        # ):
        #    abort(403)
        out: str = ""
        member: Person
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.username is None or len(member.username) < 1:
                continue
            out = out + member.username + "\r\n"
        return out

    def salto_sales(self) -> str:
        #if "X-Real-IP" in request.headers and (
        #    not request.headers["X-Real-IP"] in self.app.config["SALTO_ALLOWED_IPS"]
        #):
        #    abort(403)
        out: str = ""
        member: Person
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.username is None or len(member.username) < 1:
                continue
            if self.util.member_of("sales", member):
                out = out + member.username + "\r\n"
        return out

    def salto_mek(self) -> str:
        #if "X-Real-IP" in request.headers and (
        #    not request.headers["X-Real-IP"] in self.app.config["SALTO_ALLOWED_IPS"]
        #):
        #    abort(403)
        out: str = ""
        for member in (
            self.storage.session.query(Person).filter_by(state="active").all()
        ):
            if member.username is None or len(member.username) < 1:
                continue
            if self.util.member_of("mek", member):
                out = out + member.username + "\r\n"
        return out
