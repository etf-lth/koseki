import logging
from typing import Union

from flask import Blueprint, abort, redirect, render_template, url_for
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.wrappers import Response
from wtforms import SubmitField  # type: ignore
from wtforms import DecimalField, IntegerField, TextField
from wtforms.validators import DataRequired  # type: ignore

from koseki.db.types import Product
from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType


class ProductForm(FlaskForm):
    name = TextField("Product name", validators=[DataRequired()])
    img_url = TextField("Image URL", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    order = IntegerField("Order", validators=[DataRequired()])
    submitAdd = SubmitField("Add product")
    submitUpdate = SubmitField("Update product")
    submitDelete = SubmitField("Delete product")


class StorePlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "PAYMENT_DEBT_ENABLED": True,  # Override to enable Debt in Koseki
        }

    def create_blueprint(self) -> Blueprint:
        self.util.nav(
            "/store", "shopping-basket", "Store", 4, [
                "admin", "board", "krangare"]
        )
        blueprint: Blueprint = Blueprint(
            "store", __name__, template_folder="./templates"
        )
        blueprint.add_url_rule(
            "/store",
            None,
            self.auth.require_session(
                self.list_products, ["admin", "board", "krangare"]
            ),
            methods=["GET", "POST"],
        )
        blueprint.add_url_rule(
            "/store/product/<int:pid>",
            None,
            self.auth.require_session(
                self.manage_product, ["admin", "board", "krangare"]
            ),
            methods=["GET", "POST"],
        )
        return blueprint

    def list_products(self) -> Union[str, Response]:
        product_form = ProductForm()

        if product_form.submitAdd.data and product_form.validate_on_submit():
            # Store product
            product = Product(
                name=product_form.name.data,
                img_url=product_form.img_url.data,
                price=product_form.price.data,
                order=product_form.order.data,
            )
            self.storage.add(product)
            self.storage.commit()

            logging.info(
                "Registered product %s #%d",
                product_form.name.data, product.pid
            )

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Registered product %s #%d" % (
                        product_form.name.data, product.pid),
                )
            )
            product_form = ProductForm(None)

        return render_template(
            "store_list_products.html",
            form=product_form,
            products=self.storage.session.query(Product)
            .order_by(Product.order.asc())
            .all(),
        )

    def manage_product(self, pid: int) -> Union[str, Response]:
        product = self.storage.session.query(
            Product).filter_by(pid=pid).scalar()
        if not product:
            raise abort(404)

        product_form = ProductForm(obj=product)

        if product_form.submitDelete.data and product_form.validate_on_submit():
            # Delete product
            self.storage.delete(product)
            self.storage.commit()

            logging.info(
                "Deleted product %s #%d", product_form.name.data, product.pid
            )
            return redirect(url_for("store.list_products"))

        if product_form.submitUpdate.data and product_form.validate_on_submit():
            # Update product
            product_form.populate_obj(product)
            self.storage.commit()

            logging.info(
                "Updated product %s #%d", product_form.name.data, product.pid
            )
            return redirect(url_for("store.list_products"))

        return render_template("store_manage_product.html", form=product_form)
