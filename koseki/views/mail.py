from flask import render_template
from koseki.db.types import Person
from koseki.view import KosekiView


class MailView(KosekiView):
    def register(self):
        self.app.add_url_rule(
            "/mail",
            None,
            self.auth.require_session(
                self.list_mail, ["admin", "board", "pr", "m3", "krangare"]
            ),
        )
        self.util.nav(
            "/mail", "envelope", "Mail", 5, ["admin", "board", "pr", "m3", "krangare"]
        )

    def list_mail(self):
        return render_template(
            "list_mail.html",
            persons=self.storage.session.query(Person).filter_by(state="active").all(),
        )
