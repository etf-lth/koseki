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
            "/kiosk/logout", None, self.kiosk_logout, methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/kiosk/card", None, self.kiosk_card, methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/kiosk/products", None, self.kiosk_products, methods=["GET", "POST"],
        )

    def kiosk_card(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        # Remove old user if they came here via "Logout" button
        if "kiosk_uid" in session:
            session.pop("kiosk_uid")

        cardForm = KioskCardForm()
        alerts = self.core.fetch_alerts()

        if cardForm.validate_on_submit():
            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "dt %s" % (cardForm.cardId.data),
                }
            )
            self.core.set_alerts(alerts)
            return redirect(url_for("kiosk_products"))

        return render_template("kiosk_card.html", form=cardForm, alerts=alerts,)

    def kiosk_products(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        cardForm = KioskCardForm()
        alerts = self.core.fetch_alerts()

        if cardForm.validate_on_submit():
            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "dt %s" % (cardForm.cardId.data),
                }
            )

        return render_template(
            "kiosk_products.html",
            form=cardForm,
            alerts=alerts,
            products=self.storage.session.query(Product)
            .order_by(Product.order.asc())
            .all(),
        )

    def kiosk_login(self):
        loginForm = KioskLoginForm()

        alerts = self.core.fetch_alerts()

        if loginForm.submitLogin.data and loginForm.validate_on_submit():
            if loginForm.password.data == self.app.config["KIOSK_KEY"]:
                session["kiosk_unlocked"] = True
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

    def kiosk_logout(self):
        session["kiosk_unlocked"] = False
        return redirect(url_for("kiosk_login"))
