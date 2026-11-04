import logging
from typing import Union

from flask import Blueprint, abort, redirect, render_template, url_for, session
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import SubmitField  # type: ignore
from wtforms import DecimalField, IntegerField, StringField
from wtforms.validators import DataRequired  # type: ignore

from koseki.db.types import Payment, Person, Product
from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType


class SwishPayForm(FlaskForm):
    amount = DecimalField("Amount", validators=[DataRequired()])
    submitPay = SubmitField("Pay")


class SwishPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "PAYMENT_DEBT_ENABLED": True,  # Override to enable Debt in Koseki
        }

    def create_blueprint(self) -> Blueprint:
        self.util.nav(
            "/swish", "money-bill", "Swish", 4
        )
        blueprint: Blueprint = Blueprint(
            "swish", __name__, template_folder="./templates"
        )
        blueprint.add_url_rule(
            "/swish",
            None,
            self.auth.require_session(
                self.swish, ["admin", "board", "krangare"]
            ),
            methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/swish/pay/<int:amount>",
            None,
            self.auth.require_session(
                self.manage_product, ["admin", "board", "krangare"]
            ),
            methods=["GET", "POST"],
        )
        return blueprint

    def swish(self) -> Union[str, Response]:
        person: Person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["uid"])
            .scalar()
        )

        if person.balance < 0:
            payment_form = SwishPayForm(amount=(abs(person.balance)))
        else:
            payment_form = SwishPayForm()

        if payment_form.submitPay.data and payment_form.validate_on_submit():
            # Create swish request
            self.create_swish_payment_request(payment_form.amount.data)
            return redirect(url_for("swish.swish"))

        return render_template("swish.html", person=person, form=payment_form)

    def create_swish_payment_request(self, amount: int):
        print(amount)

    def manage_product(self, amount: int) -> Union[str, Response]:
        person: Person = (
            self.storage.session.query(Person)
            .filter_by(uid=session["uid"])
            .scalar()
        )

        product_form = ProductForm(obj=product)

        if product_form.submitDelete.data and product_form.validate_on_submit():
            # Delete product
            self.storage.delete(product)
            self.storage.commit()

            logging.info(
                "Deleted product %s #%d", product_form.name.data, product.pid
            )
            return redirect(url_for("swish.list_products"))

        if product_form.submitUpdate.data and product_form.validate_on_submit():
            # Update product
            product_form.populate_obj(product)
            self.storage.commit()

            logging.info(
                "Updated product %s #%d", product_form.name.data, product.pid
            )
            return redirect(url_for("swish.list_products"))

        return render_template("store_manage_product.html", form=product_form)
