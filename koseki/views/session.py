import hashlib
from koseki.util import KosekiAlert, KosekiAlertType

from flask import redirect, render_template, request, url_for
from koseki.db.types import Person
from koseki.view import KosekiView


class SessionView(KosekiView):
    def register(self):
        self.app.add_url_rule("/login", None, self.login, methods=["GET", "POST"])
        self.app.add_url_rule("/logout", None, self.logout)
        self.util.nav("/logout", "power-off", "Sign out", 999)

    def login(self):
        alerts: list[KosekiAlert] = []
        if request.method == "POST":
            person = (
                self.storage.session.query(Person)
                .filter_by(email=request.form["email"])
                .scalar()
            )
            if (
                person
                and person.password
                == hashlib.sha1(request.form["password"].encode("utf-8")).hexdigest()
            ):
                self.util.start_session(person.uid)
                return redirect(request.form["redir"])
            else:
                alerts.append(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Authentication error",
                        "The username or password is incorrect.",
                    )
                )

        return render_template(
            "login.html",
            redir=request.args.get("redir", url_for("index")),
            alerts=alerts,
            alternate=self.util.get_alternate_login(),
        )

    def logout(self):
        self.util.destroy_session()
        return render_template("logout.html")
