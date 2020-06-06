from flask import url_for, render_template, session, redirect, escape, request, abort
from koseki.db.types import Person, Fee

from flask_wtf import FlaskForm
from wtforms import TextField, SelectMultipleField
from wtforms.validators import DataRequired, Email


class EditForm(FlaskForm):

    fname = TextField("First name", validators=[DataRequired()])
    lname = TextField("Last name", validators=[DataRequired()])
    email = TextField("Email", validators=[Email()])
    stil = TextField("StiL")


class MembershipView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/membership", None, self.core.require_session(self.membership_general)
        )
        self.app.add_url_rule(
            "/membership/edit",
            None,
            self.core.require_session(self.membership_edit),
            methods=["GET", "POST"],
        )
        self.core.nav("/membership", "user", "My membership", 10)

    def membership_general(self):
        person = (
            self.storage.session.query(Person)
            .filter_by(uid=self.core.current_user())
            .scalar()
        )
        last_fee = (
            self.storage.session.query(Fee)
            .filter_by(uid=self.core.current_user())
            .order_by(Fee.end.desc())
            .first()
        )
        return render_template(
            "membership_general.html", person=person, last_fee=last_fee
        )

    def membership_edit(self):
        person = (
            self.storage.session.query(Person)
            .filter_by(uid=self.core.current_user())
            .scalar()
        )
        form = EditForm(obj=person)

        alerts = []
        alerts.append(
            {
                "class": "alert-warning",
                "title": "Note",
                "message": "Profile editing is currently disabled",
            }
        )

        if request.method == "POST":
            alerts.append(
                {
                    "class": "alert-danger",
                    "title": "Error",
                    "message": "Profile editing is currently disabled",
                }
            )

        return render_template(
            "membership_edit.html", person=person, form=form, alerts=alerts
        )
