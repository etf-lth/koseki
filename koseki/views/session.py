import logging
import random
import string
from typing import Union

from flask import redirect, render_template, request, url_for
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import PasswordField, SubmitField, TextField  # type: ignore
from wtforms.validators import DataRequired, Email  # type: ignore

from koseki.db.types import Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView


class LoginForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(
        "Email required"), Email("Invalid email")])
    password = PasswordField("Password", validators=[
                             DataRequired("Password required")])
    submit_login = SubmitField("Sign in")


class ResetPasswordForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(
        "Email required"), Email("Invalid email")])
    submit_reset = SubmitField("Reset password")


class SessionView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule("/reset-password", None, self.reset_password,
                              methods=["GET", "POST"])
        self.app.add_url_rule("/login", None, self.login,
                              methods=["GET", "POST"])
        self.app.add_url_rule("/logout", None, self.logout)
        self.util.nav("/logout", "power-off", "Sign out", 999)

    def reset_password(self) -> Union[str, Response]:
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

                logging.info("Reset password for %s %s", person.fname, person.lname)
                self.mail.send_mail(
                    person, "mail/reset_password.html", member=person, new_pass=new_pass)

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Reset email sent",
                    "If that email exists in the membership database, then an email has been sent to that address.",
                )
            )

        return render_template(
            "reset_password.html",
            form_reset_password=form_reset_password,
        )

    def login(self) -> Union[str, Response]:
        form_login = LoginForm()

        if form_login.validate_on_submit():
            person = (
                self.storage.session.query(Person)
                .filter_by(email=form_login.email.data)
                .scalar()
            )
            if (
                person
                and self.auth.verify_password(person.password, form_login.password.data)
            ):
                self.util.start_session(person.uid)
                return redirect(request.form["redir"])
            else:
                self.util.alert(
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
            sso_providers=self.util.get_alternate_logins(),
        )

    def logout(self) -> Union[str, Response]:
        self.util.destroy_session()
        return render_template("logout.html")
