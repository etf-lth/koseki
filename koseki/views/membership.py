from flask import render_template, request
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Fee, Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView
from wtforms import TextField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore


class EditForm(FlaskForm):
    fname = TextField("First name", validators=[DataRequired()])
    lname = TextField("Last name", validators=[DataRequired()])
    email = TextField("Email", validators=[Email()])
    stil = TextField("StiL")


class MembershipView(KosekiView):
    def register(self):
        self.app.add_url_rule(
            "/membership", None, self.auth.require_session(
                self.membership_general)
        )
        self.app.add_url_rule(
            "/membership/edit",
            None,
            self.auth.require_session(self.membership_edit),
            methods=["GET", "POST"],
        )
        self.util.nav("/membership", "user", "My membership", 100)

    def membership_general(self):
        person = (
            self.storage.session.query(Person)
            .filter_by(uid=self.util.current_user())
            .scalar()
        )
        last_fee = (
            self.storage.session.query(Fee)
            .filter_by(uid=self.util.current_user())
            .order_by(Fee.end.desc())
            .first()
        )
        return render_template(
            "membership_general.html", person=person, last_fee=last_fee
        )

    def membership_edit(self):
        person = (
            self.storage.session.query(Person)
            .filter_by(uid=self.util.current_user())
            .scalar()
        )
        form = EditForm(obj=person)

        alerts: list[KosekiAlert] = []
        alerts.append(
            KosekiAlert(
                KosekiAlertType.WARNING,
                "Note",
                "Profile editing is currently disabled",
            )
        )

        if request.method == "POST":
            alerts.append(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Error",
                    "Profile editing is currently disabled",
                )
            )

        return render_template(
            "membership_edit.html", person=person, form=form, alerts=alerts
        )
