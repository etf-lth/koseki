import logging
import re
from datetime import datetime, timedelta

from flask import abort, redirect, render_template, session, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Optional

from koseki.db.types import Fee, Person, Payment, Product


class KioskLoginForm(FlaskForm):

    password = PasswordField("Kiosk Password", validators=[DataRequired()])
    submitLogin = SubmitField("Unlock Kiosk")


class KioskCardForm(FlaskForm):

    cardId = PasswordField("Student Card ID", validators=[DataRequired()])


class KioskView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/kiosk", None, self.kiosk_login, methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/kiosk/card", None, self.kiosk_card, methods=["GET", "POST"],
        )

    def kiosk_card(self):
        cardForm = KioskCardForm()

        alerts = []

        if cardForm.validate_on_submit():
            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "dt %s" % (cardForm.cardId.data),
                }
            )

        return render_template("kiosk_card.html", form=cardForm, alerts=alerts,)

    def kiosk_login(self):
        loginForm = KioskLoginForm()

        alerts = []

        if loginForm.submitLogin.data and loginForm.validate_on_submit():
            if loginForm.password.data == self.app.config["KIOSK_KEY"]:
                session["kiosk_unlock"] = True
                return redirect(url_for("kiosk_card"))
            else:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "Invalid password. Login attempt logged.",
                    }
                )

        return render_template("kiosk_login.html", form=loginForm, alerts=alerts,)
