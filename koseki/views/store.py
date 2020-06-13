import logging
import re
from datetime import datetime, timedelta

from flask import escape, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from koseki.db.types import Fee, Person, Payment, Product


class StoreForm(FlaskForm):

    name = TextField("Product name", validators=[DataRequired()])
    img_url = TextField("Image URL", validators=[DataRequired()])
    price = IntegerField("Price (SEK)")
    order = IntegerField("Order")
    submit = SubmitField("Add product")


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
            "/store/kiosk", None, self.core.require_session(self.kiosk_mode),
        )
        self.core.nav(
            "/store", "shopping-basket", "Store", 4, ["admin", "board", "krangare"]
        )

    def kiosk_mode(self):
        return render_template(
            "list_fees.csv",
            fees=self.storage.session.query(Fee).order_by(Fee.fid.desc()).all(),
        )

    def products(self):
        form = StoreForm()

        alerts = []

        if form.validate_on_submit():
            # Store product
            product = Product(
                name=form.name.data,
                img_url=form.img_url.data,
                price=form.price.data,
                order=form.order.data,
            )
            self.storage.add(product)
            self.storage.commit()

            logging.info(
                "Registered product %s #%d"
                % (form.name.data, product.pid)
            )

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "Registered product %s #%d"
                    % (form.name.data, product.pid),
                }
            )
            form = StoreForm(None)

        return render_template(
            "products.html",
            form=form,
            alerts=alerts,
            products=self.storage.session.query(Product)
            .order_by(Product.pid.desc())
            .all(),
        )
