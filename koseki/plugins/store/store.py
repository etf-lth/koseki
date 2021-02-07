import logging
from typing import Union

from flask import Blueprint, abort, redirect, render_template, url_for
from flask_wtf import FlaskForm  # type: ignore
from koseki.db.types import Product
from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType
from werkzeug.wrappers import Response
from wtforms import SubmitField  # type: ignore
from wtforms import DecimalField, IntegerField, TextField
from wtforms.validators import DataRequired  # type: ignore


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
        productForm = ProductForm()

        if productForm.submitAdd.data and productForm.validate_on_submit():
            # Store product
            product = Product(
                name=productForm.name.data,
                img_url=productForm.img_url.data,
                price=productForm.price.data,
                order=productForm.order.data,
            )
            self.storage.add(product)
            self.storage.commit()

            logging.info(
                "Registered product %s #%d" % (
                    productForm.name.data, product.pid)
            )

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Registered product %s #%d" % (
                        productForm.name.data, product.pid),
                )
            )
            productForm = ProductForm(None)

        return render_template(
            "store_list_products.html",
            form=productForm,
            products=self.storage.session.query(Product)
            .order_by(Product.order.asc())
            .all(),
        )

    def manage_product(self, pid: int) -> Union[str, Response]:
        product = self.storage.session.query(
            Product).filter_by(pid=pid).scalar()
        if not product:
            raise abort(404)

        productForm = ProductForm(obj=product)

        if productForm.submitDelete.data and productForm.validate_on_submit():
            # Delete product
            self.storage.delete(product)
            self.storage.commit()

            logging.info(
                "Deleted product %s #%d" % (productForm.name.data, product.pid)
            )
            return redirect(url_for("store.list_products"))

        if productForm.submitUpdate.data and productForm.validate_on_submit():
            # Update product
            productForm.populate_obj(product)
            self.storage.commit()

            logging.info(
                "Updated product %s #%d" % (productForm.name.data, product.pid)
            )
            return redirect(url_for("store.list_products"))

        return render_template("store_manage_product.html", form=productForm)
