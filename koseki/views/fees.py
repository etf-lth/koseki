import logging
import re
from datetime import datetime, timedelta

from flask import escape, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, TextField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

from koseki.db.types import Fee, Person, Payment


class FeeForm(FlaskForm):

    uid = TextField("Member ID", validators=[DataRequired()])
    amount = IntegerField("Amount (SEK)")
    method = SelectField(
        "Payment Method",
        choices=[
            ("swish", "Swish"),
            ("cash", "Cash"),
            ("bankgiro", "Bankgiro"),
            ("creditcard", "Credit card"),
        ],
    )
    retro = DateField("Retroactive fee (Date)", validators=[Optional()])
    submitFee = SubmitField("Register")

class PaymentForm(FlaskForm):

    uid = TextField("Member ID", validators=[DataRequired()])
    amount = IntegerField("Amount (SEK)")
    method = SelectField(
        "Payment Method",
        choices=[
            ("swish", "Swish"),
            ("cash", "Cash"),
            ("bankgiro", "Bankgiro"),
            ("creditcard", "Credit card"),
            ("Kiosk", "Fridge Kiosk"),
            ("wordpress", "Wordpress"),
        ],
    )
    reason = TextField("Reason", validators=[DataRequired()])
    submitPayment = SubmitField("Register")

class FeesView:
    def __init__(self, app, core, storage, mailer):
        self.app = app
        self.core = core
        self.storage = storage
        self.mailer = mailer

    def register(self):
        self.app.add_url_rule(
            "/fees",
            None,
            self.core.require_session(self.list_fees, ["admin", "accounter"]),
        )
        self.app.add_url_rule(
            "/fees/csv",
            None,
            self.core.require_session(self.export_csv, ["admin", "accounter"]),
        )
        self.app.add_url_rule(
            "/fees/register",
            None,
            self.core.require_session(self.register_fee, ["admin", "accounter"]),
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/payments",
            None,
            self.core.require_session(self.list_payments, ["admin", "accounter"]),
        )
        self.core.nav("/fees", "certificate", "Fees", 3, ["admin", "accounter"])

    def list_fees(self):
        return render_template(
            "list_fees.html",
            fees=self.storage.session.query(Fee).order_by(Fee.fid.desc()).all(),
        )

    def list_payments(self):
        return render_template(
            "list_payments.html",
            payments=self.storage.session.query(Payment).order_by(Payment.pid.desc()).all(),
        )

    def export_csv(self):
        return render_template(
            "list_fees.csv",
            fees=self.storage.session.query(Fee).order_by(Fee.fid.desc()).all(),
        )

    def register_fee(self):
        feeForm = FeeForm()
        paymentForm = PaymentForm()

        alerts = []

        if feeForm.submitFee.data and feeForm.validate_on_submit():
            person = (
                self.storage.session.query(Person).filter_by(uid=feeForm.uid.data).scalar()
            )

            if person is None:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": 'No such member "%s". Did you try the auto-complete feature?'
                        % feeForm.uid.data,
                    }
                )
                return render_template("register_fee.html", form=feeForm, alerts=alerts)

            if feeForm.retro.data is not None:
                # Use user-supplied start date
                start = feeForm.retro.data
            else:
                # Calculate period of validity
                last_fee = (
                    self.storage.session.query(Fee)
                    .filter_by(uid=person.uid)
                    .order_by(Fee.end.desc())
                    .first()
                )

                if last_fee and last_fee.end > datetime.now():
                    logging.debug(
                        "Last fee: start=%s, end=%s" % (last_fee.start, last_fee.end)
                    )
                    start = last_fee.end
                else:
                    start = datetime.now()
            # end = start + timedelta(days=(3.65*int(form.amount.data)))
            end = start + timedelta(days=(1.825 * int(feeForm.amount.data)))

            # Store fee
            fee = Fee(
                uid=person.uid,
                registered_by=self.core.current_user(),
                amount=feeForm.amount.data,
                start=start,
                end=end,
                method=feeForm.method.data,
            )
            self.storage.add(fee)
            self.storage.commit()

            logging.info(
                "Registered fee %d SEK for %d"
                % (feeForm.amount.data, person.pid)
            )

            # Check for user state changes
            if (
                person.state != "active"
                and self.storage.session.query(Fee)
                .filter(
                    Fee.uid == person.uid,
                    Fee.start <= datetime.now(),
                    Fee.end >= datetime.now(),
                )
                .all()
            ):
                person.state = "active"
                self.storage.commit()
                logging.info("%s %s is now active" % (person.fname, person.lname))
                self.mailer.send_mail(
                    self.app.config["BOARD_EMAIL"],
                    "board_member_active.mail",
                    member=person,
                )
                self.mailer.send_mail(person, "member_active.mail", member=person)

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "Registered fee %d SEK for %s %s"
                    % (feeForm.amount.data, person.fname, person.lname),
                }
            )
            feeForm = FeeForm(None)


        elif paymentForm.submitPayment.data and paymentForm.validate_on_submit():
            person = (
                self.storage.session.query(Person).filter_by(uid=feeForm.uid.data).scalar()
            )

            if person is None:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": 'No such member "%s". Did you try the auto-complete feature?'
                        % paymentForm.uid.data,
                    }
                )
                return render_template("register_fee.html", form=paymentForm, alerts=alerts)

            # Store payment
            payment = Payment(
                uid=person.uid,
                registered_by=self.core.current_user(),
                amount=paymentForm.amount.data,
                method=paymentForm.method.data,
                reason=paymentForm.reason.data,
            )
            self.storage.add(payment)
            self.storage.commit()

            logging.info(
                "Registered payment %d SEK for %d"
                % (feeForm.amount.data, person.pid)
            )

            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "Registered payment %d SEK for %s %s"
                    % (feeForm.amount.data, person.fname, person.lname),
                }
            )
            paymentForm = PaymentForm(None)

        return render_template("register_fee.html", feeForm=feeForm, paymentForm=paymentForm, alerts=alerts)
