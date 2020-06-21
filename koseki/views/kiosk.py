import logging
import re
from datetime import datetime, timedelta

from flask import abort, redirect, render_template, session, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Optional

from koseki.db.types import Fee, Person, Payment, Product


class KioskLoginForm(FlaskForm):

    password = PasswordField("Kiosk Password", validators=[DataRequired()])
    submit_login = SubmitField("Unlock Kiosk")


class KioskCardForm(FlaskForm):

    card_id = PasswordField("Student Card ID", validators=[DataRequired()])


class KioskProductForm(FlaskForm):

    product_id = HiddenField("Product ID", validators=[DataRequired()])


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
            "/kiosk/register", None, self.kiosk_register, methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/kiosk/products", None, self.kiosk_products, methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/kiosk/success", None, self.kiosk_success, methods=["GET", "POST"],
        )

    def kiosk_card(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        # Remove old user if they came here via "Logout" button
        if "kiosk_uid" in session:
            session.pop("kiosk_uid")
        if "kiosk_card" in session:
            session.pop("kiosk_card")

        alerts = self.core.fetch_alerts()
        form = KioskCardForm()

        if form.validate_on_submit():
            person = (
                self.storage.session.query(Person)
                .filter_by(card_id=form.card_id.data)
                .scalar()
            )
            if person:
                session["kiosk_uid"] = person.uid
                return redirect(url_for("kiosk_products"))
            else:
                alerts.append(
                    {
                        "class": "alert-warning",
                        "title": "Card not verified",
                        "message": "This is the first time you are using ETF Kiosk. Please verify by entering your student StiL/LUCAT.",
                    }
                )
                self.core.set_alerts(alerts)
                session["kiosk_card"] = form.card_id.data
                return redirect(url_for("kiosk_register"))

        return render_template("kiosk_card.html", form=form, alerts=alerts,)

    def kiosk_register(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        # Remove old user if they came here via "Logout" button
        if "kiosk_card" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.core.fetch_alerts()
        form = KioskCardForm()

        if form.validate_on_submit():
            person = (
                self.storage.session.query(Person)
                .filter_by(card_id=form.card_id.data)
                .scalar()
            )
            if person:
                session["kiosk_uid"] = person.uid
                return redirect(url_for("kiosk_products"))
            else:
                return redirect(url_for("kiosk_register"))

        return render_template("kiosk_register.html", form=form, alerts=alerts,)

    def kiosk_products(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        if "kiosk_uid" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.core.fetch_alerts()

        person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["kiosk_uid"])
            .scalar()
        )
        if not person:
            alerts.append(
                {
                    "class": "alert-danger",
                    "title": "Error",
                    "message": "Missing user %s" % (session["kiosk_uid"]),
                }
            )
            self.core.set_alerts(alerts)
            return redirect(url_for("kiosk_card"))

        form = KioskProductForm()

        if form.validate_on_submit():
            product = (
                self.storage.session.query(Product)
                .filter_by(pid=form.product_id.data)
                .scalar()
            )
            if product:
                # Store payment
                payment = Payment(
                    uid=person.uid,
                    registered_by=person.uid,
                    amount=-product.price,
                    method="kiosk",
                    reason="Bought %s for %d kr" % (product.name, product.price),
                )
                self.storage.add(payment)
                self.storage.commit()

                logging.info(
                    "Person %d bought %d for %d kr"
                    % (person.uid, product.pid, product.price)
                )
                alerts.append(
                    {
                        "class": "alert-success",
                        "title": "Successfully bought %s" % (product.name),
                        "message": "",
                    }
                )
                self.core.set_alerts(alerts)
                return redirect(url_for("kiosk_success"))
            else:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "Invalid product %s" % (form.product_id.data),
                    }
                )

        return render_template(
            "kiosk_products.html",
            form=form,
            alerts=alerts,
            person=person,
            products=self.storage.session.query(Product)
            .order_by(Product.order.asc())
            .all(),
        )

    def kiosk_success(self):
        if "kiosk_unlocked" not in session or session["kiosk_unlocked"] != True:
            return redirect(url_for("kiosk_login"))

        if "kiosk_uid" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.core.fetch_alerts()

        person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["kiosk_uid"])
            .scalar()
        )
        if not person:
            alerts.append(
                {
                    "class": "alert-danger",
                    "title": "Error",
                    "message": "Missing user %s" % (session["kiosk_uid"]),
                }
            )
            self.core.set_alerts(alerts)
            return redirect(url_for("kiosk_card"))

        if "kiosk_uid" in session:
            session.pop("kiosk_uid")
        return render_template("kiosk_success.html", person=person, alerts=alerts,)

    def kiosk_login(self):
        loginForm = KioskLoginForm()

        alerts = self.core.fetch_alerts()

        if loginForm.submit_login.data and loginForm.validate_on_submit():
            if loginForm.password.data == self.app.config["KIOSK_KEY"]:
                session["kiosk_unlocked"] = True
                return redirect(url_for("kiosk_card"))
            else:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "Invalid password. Login attempt has been logged.",
                    }
                )

        return render_template("kiosk_login.html", form=loginForm, alerts=alerts,)

    def kiosk_logout(self):
        if "kiosk_unlocked" in session:
            session.pop("kiosk_unlocked")
        return redirect(url_for("kiosk_login"))
