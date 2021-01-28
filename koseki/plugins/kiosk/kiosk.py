import logging

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Payment, Person, Product
from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType
from wtforms import HiddenField, PasswordField  # type: ignore
from wtforms.validators import DataRequired  # type: ignore


class KioskCardForm(FlaskForm):
    card_id = PasswordField("Student Card ID", validators=[DataRequired()])


class KioskRegisterForm(FlaskForm):
    student_id = HiddenField("Student ID", validators=[DataRequired()])


class KioskProductForm(FlaskForm):
    products_field = HiddenField("Products", validators=[DataRequired()])


class KioskPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "KIOSK_KEY": "123456",
        }

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint(
            "kiosk", __name__, template_folder="./templates"
        )
        blueprint.add_url_rule(
            "/kiosk", None, self.kiosk_login, methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/kiosk/logout", None, self.kiosk_logout, methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/kiosk/card", None, self.kiosk_card, methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/kiosk/register", None, self.kiosk_register, methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/kiosk/products", None, self.kiosk_products, methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/kiosk/success", None, self.kiosk_success, methods=["GET", "POST"],
        )
        return blueprint

    def kiosk_card(self):
        if (
            "kiosk_password" not in session
            or session["kiosk_password"] != self.app.config["KIOSK_KEY"]
        ):
            return redirect(url_for("kiosk_login"))

        # Remove old user if they came here via "Logout" button
        if "kiosk_uid" in session:
            session.pop("kiosk_uid")
        if "kiosk_card" in session:
            session.pop("kiosk_card")

        alerts = self.util.fetch_alerts()
        form = KioskCardForm()

        if form.validate_on_submit() and len(form.card_id.data) == 10:
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
                    KosekiAlert(
                        KosekiAlertType.WARNING,
                        "Card not verified",
                        "This is the first time you are using ETF Kiosk. Please verify by entering your student StiL/LUCAT.",
                    )
                )
                self.util.set_alerts(alerts)
                session["kiosk_card"] = form.card_id.data
                return redirect(url_for("kiosk_register"))

        return render_template("kiosk_card.html", form=form, alerts=alerts,)

    def kiosk_register(self):
        if (
            "kiosk_password" not in session
            or session["kiosk_password"] != self.app.config["KIOSK_KEY"]
        ):
            return redirect(url_for("kiosk_login"))

        # Remove old user if they came here via "Logout" button
        if "kiosk_card" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.util.fetch_alerts()
        form = KioskRegisterForm()

        if form.validate_on_submit():
            person: Person = (
                self.storage.session.query(Person)
                .filter_by(stil=form.student_id.data)
                .scalar()
            )
            if person:
                person.card_id = session.pop("kiosk_card")
                self.storage.commit()

                alerts.append(
                    KosekiAlert(
                        KosekiAlertType.SUCCESS,
                        "Card verified successfully",
                        "You can now use your student card in the Kiosk.",
                    )
                )
                self.util.set_alerts(alerts)
                return redirect(url_for("kiosk_card"))
            else:
                alerts.append(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Missing user account",
                        "Could not find user '%s'. Please contact an ETF board member."
                        % (form.student_id.data),
                    )
                )

        return render_template("kiosk_register.html", form=form, alerts=alerts,)

    def kiosk_products(self):
        if (
            "kiosk_password" not in session
            or session["kiosk_password"] != self.app.config["KIOSK_KEY"]
        ):
            return redirect(url_for("kiosk_login"))

        if "kiosk_uid" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.util.fetch_alerts()

        person: Person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["kiosk_uid"])
            .scalar()
        )
        if not person:
            alerts.append(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Error",
                    "Missing user %s" % (session["kiosk_uid"]),
                )
            )
            self.util.set_alerts(alerts)
            return redirect(url_for("kiosk_card"))

        form = KioskProductForm()
        product: Product

        if form.validate_on_submit():
            # Process form input
            productsInput = form.products_field.data.split(",")
            products = []
            productAmounts = []
            errorProcessing = False
            # Loop through each of the received products and its respective quantity
            for p in productsInput:
                productId = float(p.split(":")[0])
                productQty = int(p.split(":")[1])
                # Check if QTY is valid
                if productQty < 1 or productQty > 100:
                    alerts.append(
                        KosekiAlert(
                            KosekiAlertType.DANGER,
                            "Error",
                            "Invalid Quantity %s" % (productId),
                        )
                    )
                    errorProcessing = True

                # Fetch product and add if valid
                product = (
                    self.storage.session.query(Product)
                    .filter_by(pid=productId)
                    .scalar()
                )
                if product:
                    products.append(product)
                    productAmounts.append(productQty)
                else:
                    alerts.append(
                        KosekiAlert(
                            KosekiAlertType.DANGER,
                            "Error",
                            "Invalid product %s" % (productId),
                        )
                    )
                    errorProcessing = True
                    break

            if errorProcessing is not True:
                # Store payment
                for i in range(len(products)):
                    product = products[i]
                    for i in range(productAmounts[i]):
                        payment = Payment(
                            uid=person.uid,
                            registered_by=person.uid,
                            amount=-product.price,  # type: ignore
                            method="kiosk",
                            reason="Bought %s for %.2f kr"
                            % (product.name, product.price),  # type: ignore
                        )
                        self.storage.add(payment)
                        self.storage.commit()

                        logging.info(
                            "Person %d bought %d for %d kr"
                            % (person.uid, product.pid, product.price)  # type: ignore
                        )
                        alerts.append(
                            KosekiAlert(
                                KosekiAlertType.SUCCESS,
                                "Successfully bought %s" % (product.name),
                                "",
                            )
                        )
                self.util.set_alerts(alerts)
                return redirect(url_for("kiosk_success"))

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
        if (
            "kiosk_password" not in session
            or session["kiosk_password"] != self.app.config["KIOSK_KEY"]
        ):
            return redirect(url_for("kiosk_login"))

        if "kiosk_uid" not in session:
            return redirect(url_for("kiosk_card"))

        alerts = self.util.fetch_alerts()

        person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["kiosk_uid"])
            .scalar()
        )
        if not person:
            alerts.append(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Error",
                    "Missing user %s" % (session["kiosk_uid"]),
                )
            )
            self.util.set_alerts(alerts)
            return redirect(url_for("kiosk_card"))

        if "kiosk_uid" in session:
            session.pop("kiosk_uid")
        return render_template("kiosk_success.html", person=person, alerts=alerts,)

    def kiosk_login(self):
        if (
            "kiosk_password" in session
            and session["kiosk_password"] == self.app.config["KIOSK_KEY"]
        ):
            return redirect(url_for("kiosk_card"))

        alerts = self.util.fetch_alerts()

        if "User-Agent" in request.headers and request.headers.get(  # type: ignore
            "User-Agent"
        ).startswith("Kiosk"):
            if ("Key=" + self.app.config["KIOSK_KEY"]) in request.headers.get(  # type: ignore
                "User-Agent"
            ).split(
                " "
            ):
                session["kiosk_password"] = self.app.config["KIOSK_KEY"]
                return redirect(url_for("kiosk_card"))
            else:
                alerts.append(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "Invalid password. Login attempt has been logged.",
                    )
                )
        else:
            alerts.append(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Error",
                    "Invalid client. Access attempt has been logged.",
                )
            )

        return render_template("kiosk_login.html", alerts=alerts,)

    def kiosk_logout(self):
        if "kiosk_password" in session:
            session.pop("kiosk_password")
        return redirect(url_for("kiosk_login"))

