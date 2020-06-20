import logging
import re
from datetime import datetime, timedelta

from flask import abort, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Optional

from koseki.db.types import Fee, Person, Payment, Product


class ProductForm(FlaskForm):

    name = TextField("Product name", validators=[DataRequired()])
    img_url = TextField("Image URL", validators=[DataRequired()])
    price = IntegerField("Price (SEK)")
    order = IntegerField("Order")
    submitAdd = SubmitField("Add product")
    submitUpdate = SubmitField("Update product")
    submitDelete = SubmitField("Delete product")

class StoreView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule(
            "/store",
            None,
            self.core.require_session(self.products, ["admin", "board", "krangare"]),
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/store/product/<int:pid>",
            None,
            self.core.require_session(self.manage_product, ["admin", "board", "krangare"]),
            methods=["GET", "POST"],
        )
        self.core.nav(
            "/store", "shopping-basket", "Store", 4, ["admin", "board", "krangare"]
        )

    def products(self):
        productForm = ProductForm()

        alerts = []

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

            logging.info("Registered product %s #%d" % (productForm.name.data, product.pid))

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "Registered product %s #%d"
                    % (productForm.name.data, product.pid),
                }
            )
            productForm = ProductForm(None)

        return render_template(
            "product_list.html",
            form=productForm,
            alerts=alerts,
            products=self.storage.session.query(Product)
            .order_by(Product.order.asc())
            .all(),
        )
    
    def manage_product(self, pid):
        productForm = ProductForm()
        product = self.storage.session.query(Product).filter_by(pid=pid).scalar()
        if not product:
            raise abort(404)

        alerts = []

        if productForm.submitDelete.data and productForm.validate_on_submit():
            # Delete product
            self.storage.delete(product)
            self.storage.commit()

            logging.info("Deleted product %s #%d" % (productForm.name.data, product.pid))
            return redirect("/store")
        
        if productForm.submitUpdate.data and productForm.validate_on_submit():
            # Update product
            product.name = productForm.name.data
            product.img_url = productForm.img_url.data
            product.price = productForm.price.data
            product.order = productForm.order.data
            self.storage.commit()

            logging.info("Updated product %s #%d" % (productForm.name.data, product.pid))
            return redirect("/store")

        productForm.name.data = product.name
        productForm.img_url.data = product.img_url
        productForm.price.data = product.price
        productForm.order.data = product.order

        return render_template(
            "product_manage.html",
            form=productForm,
            alerts=alerts,
        )
