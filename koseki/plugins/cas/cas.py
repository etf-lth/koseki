import urllib.error
import urllib.parse
import urllib.request
from typing import Union
from xml.etree import ElementTree as ET

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from koseki.db.types import Person
from koseki.plugin import KosekiPlugin


class CASPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "CAS_SERVER": "https://ldpv3.acme.nu/idp/profile",
            "USER_USERNAME_ENABLED": True,
        }

    def plugin_enable(self) -> None:
        self.util.alternate_login("Sign in with LU", self.cas_login)

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint("cas", __name__)
        blueprint.add_url_rule("/cas", None, self.cas_ticket)
        return blueprint

    def cas_login(self, redir: str) -> dict:
        service = self.app.config["URL_BASE"] + "/cas?redir=" + urllib.parse.quote(redir, safe="")
        return {
            "text": "If you are a student or employee at Lund University, please sign in with your LU account.",
            "url": self.app.config["CAS_SERVER"]
            + "/cas/login?service="
            + urllib.parse.quote_plus(service)
            + "&renew=false",
            "button": "Sign in with LU",
            "color": "#875e29",
        }

    def cas_ticket(self) -> Union[str, Response]:
        if "ticket" not in request.args:
            # just pretend it failed
            return render_template("cas.html", error="cas-failed")

        ticket = request.args["ticket"]
        redir = request.args.get("redir", url_for("index"))

        if not self.util.is_safe_redir(redir):
            return render_template("cas.html", error="bad-redir")

        service = self.app.config["URL_BASE"] + "/cas?redir=" + urllib.parse.quote(redir, safe="")

        try:
            response = urllib.request.urlopen(
                self.app.config["CAS_SERVER"]
                + "/cas/serviceValidate?renew=false&ticket="
                + ticket
                + "&service="
                + urllib.parse.quote_plus(service)
            )
            contents = response.read().decode("utf-8")
            response.close()
            root = ET.fromstring(contents)
            if root[0].tag == "{http://www.yale.edu/tp/cas}authenticationSuccess":
                uid = root[0][0].text.strip()  # type: ignore

                person = self.storage.session.query(
                    Person).filter_by(username=uid).scalar()
                if person:
                    # valid user, move along
                    self.util.start_session(person.uid)
                    return redirect(redir)
                else:
                    # authenticated by cas but unknown to us
                    return render_template("cas.html", error="unknown-uid")
            else:
                # cas failed
                return render_template("cas.html", error="cas-failed")
        except urllib.error.URLError:
            # most likely cannot contact cas
            # TODO: move cas.html to plugin folder
            return render_template("cas.html", error="cas-url-error")
