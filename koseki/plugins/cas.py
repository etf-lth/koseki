import urllib.error
import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

from flask import escape, redirect, render_template, request, session, url_for

from koseki.db.types import Person


class CASPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule("/cas", None, self.cas_ticket)

    def cas_login(self):
        return {
            "text": "Please sign in using LU "
            + "if you are a student or employee at Lund University.",
            "url": self.app.config["CAS_SERVER"]
            + "/cas/login?service="
            + self.app.config["URL_BASE"]
            + "/cas&renew=false",
            "button": "Sign in with LU",
        }

    def cas_ticket(self):
        if "ticket" not in request.args:
            # just pretend it failed
            return render_template("cas.html", error="cas-failed")

        ticket = request.args["ticket"]

        try:
            u = urllib.request.urlopen(
                self.app.config["CAS_SERVER"]
                + "/cas/serviceValidate?renew=false&ticket="
                + ticket
                + "&service="
                + urllib.parse.quote_plus(self.app.config["URL_BASE"] + "/cas")
            )
            response = u.read().decode("utf-8")
            u.close()
            root = ET.fromstring(response)
            if root[0].tag == "{http://www.yale.edu/tp/cas}authenticationSuccess":
                uid = root[0][0].text.strip()

                person = self.storage.session.query(Person).filter_by(stil=uid).scalar()
                if person:
                    # valid user, move along
                    self.core.start_session(person.uid)
                    return redirect(url_for("index"))
                else:
                    # authenticated by cas but unknown to us
                    return render_template("cas.html", error="unknown-uid")
            else:
                # cas failed
                return render_template("cas.html", error="cas-failed")
        except urllib.error.URLError:
            # most likely cannot contact cas
            return render_template("cas.html", error="cas-url-error")
