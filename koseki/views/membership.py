import logging

from flask import render_template, request
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Fee, Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView
from wtforms import PasswordField, SubmitField, TextField  # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo  # type: ignore


class EditEmailForm(FlaskForm):
    email1 = TextField("Email", validators=[DataRequired(), Email()])
    email2 = TextField("Repeat Email", validators=[DataRequired(), Email(),
                                                   EqualTo('email1', message='Emails do not match')])
    submit_email = SubmitField("Save")


class EditPasswordForm(FlaskForm):
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(
    ), EqualTo('password1', message='Passwords must match')])
    submit_password = SubmitField("Save")


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
        person: Person = (
            self.storage.session.query(Person)
            .filter_by(uid=self.util.current_user())
            .scalar()
        )

        alerts: list[KosekiAlert] = []

        form_email = EditEmailForm()
        form_password = EditPasswordForm()

        if "submit_email" in request.form and form_email.validate():
            person.email = form_email.email1.data
            self.storage.commit()
            logging.info("Changed email for %s %s" %
                         (person.fname, person.lname))

            alerts.append(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Email updated",
                    "Your email address has now been changed to %s." % (
                        form_email.email1.data),
                )
            )

        if "submit_password" in request.form and form_password.validate():
            person.password = self.auth.hash_password(
                form_password.password1.data)
            self.storage.commit()
            logging.info("Changed password for %s %s" %
                         (person.fname, person.lname))

            alerts.append(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Password changed",
                    "Your password has now been changed.",
                )
            )

        return render_template(
            "membership_edit.html", person=person, form_email=form_email, form_password=form_password, alerts=alerts
        )
