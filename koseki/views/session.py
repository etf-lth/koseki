import logging
import random
import string

from flask import redirect, render_template, request, url_for
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView
from wtforms import PasswordField, SubmitField, TextField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore


class LoginForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit_login = SubmitField("Sign in")


class ResetPasswordForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(), Email()])
    submit_reset = SubmitField("Reset password")


class SessionView(KosekiView):
    def register(self):
        self.app.add_url_rule("/reset-password", None, self.reset_password,
                              methods=["GET", "POST"])
        self.app.add_url_rule("/login", None, self.login,
                              methods=["GET", "POST"])
        self.app.add_url_rule("/logout", None, self.logout)
        self.util.nav("/logout", "power-off", "Sign out", 999)

    def reset_password(self):
        alerts: list[KosekiAlert] = []

        form_reset_password = ResetPasswordForm()

        if form_reset_password.validate_on_submit():
            person: Person = (
                self.storage.session.query(Person)
                .filter_by(email=form_reset_password.email.data)
                .scalar()
            )

            if person:
                new_pass = ''.join(
                    (random.choice(string.ascii_letters) for i in range(20)))

                person.password = self.auth.hash_password(new_pass)
                self.storage.commit()

                logging.info("Reset password for %s %s" %
                             (person.fname, person.lname))
                self.mail.send_mail(
                    person, "mail/reset_password.html", member=person, new_pass=new_pass)

            alerts.append(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Reset email sent",
                    "If that email exists in the membership database, then an email has been sent to that address.",
                )
            )

        return render_template(
            "reset_password.html",
            form_reset_password=form_reset_password,
            alerts=alerts,
        )

    def login(self):
        alerts: list[KosekiAlert] = []

        form_login = LoginForm()

        if form_login.validate_on_submit():
            person = (
                self.storage.session.query(Person)
                .filter_by(email=form_login.email.data)
                .scalar()
            )
            if (
                person
                and self.auth.verify_password(person, form_login.password.data)
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
            form_login=form_login,
            alerts=alerts,
            sso_providers=[self.util.get_alternate_login()],
        )

    def logout(self):
        self.util.destroy_session()
        return render_template("logout.html")
