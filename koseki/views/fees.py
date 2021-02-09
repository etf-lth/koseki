import logging
from datetime import datetime, timedelta
from typing import Union

from flask import render_template, request
from flask.helpers import url_for
from flask_wtf import FlaskForm  # type: ignore
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wtforms import SelectField  # type: ignore
from wtforms import IntegerField, SubmitField, TextField
from wtforms.validators import DataRequired  # type: ignore

from koseki.db.types import Fee, Payment, Person
from koseki.util import KosekiAlert, KosekiAlertType
from koseki.view import KosekiView


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
        validators=[DataRequired()]
    )
    submitFee = SubmitField("Register")


class PaymentForm(FlaskForm):
    uid = TextField("Member ID", validators=[DataRequired()])
    amount = IntegerField("Amount (SEK)", validators=[DataRequired()])
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
        validators=[DataRequired()]
    )
    reason = TextField("Reason", validators=[DataRequired()])
    submitPayment = SubmitField("Register")


class FeesView(KosekiView):
    def register(self) -> None:
        self.app.add_url_rule(
            "/fees",
            None,
            self.auth.require_session(self.list_fees, ["admin", "accounter"]),
        )
        self.app.add_url_rule(
            "/fees/csv",
            None,
            self.auth.require_session(self.export_csv, ["admin", "accounter"]),
        )
        self.app.add_url_rule(
            "/fees/register",
            None,
            self.auth.require_session(
                self.register_fee, ["admin", "accounter"]),
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            "/payments",
            None,
            self.auth.require_session(
                self.list_payments, ["admin", "accounter"]),
        )
        self.util.nav("/fees", "certificate", "Fees",
                      3, ["admin", "accounter"])

    def list_fees(self) -> Union[str, Response]:
        return render_template(
            "list_fees.html",
            fees=self.storage.session.query(
                Fee).order_by(Fee.fid.desc()).all(),
        )

    def list_payments(self) -> Union[str, Response]:
        return render_template(
            "list_payments.html",
            payments=self.storage.session.query(Payment)
            .order_by(Payment.pid.desc())
            .all(),
        )

    def export_csv(self) -> Union[str, Response]:
        return render_template(
            "list_fees.csv",
            fees=self.storage.session.query(
                Fee).order_by(Fee.fid.desc()).all(),
        )

    def register_fee(self) -> Union[str, Response]:
        fee_form = FeeForm()
        payment_form = PaymentForm()

        if "submitFee" in request.form and fee_form.validate():
            payment_form = PaymentForm(None)  # Clear the other form
            person = (
                self.storage.session.query(Person)
                .filter_by(uid=fee_form.uid.data)
                .scalar()
            )

            if person is None:
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        'No such member "%s". Did you try the auto-complete feature?'
                        % fee_form.uid.data,
                    )
                )
                return redirect(url_for("register_fee"))

            # Calculate period of validity
            last_fee: Fee = (
                self.storage.session.query(Fee)
                .filter_by(uid=person.uid)
                .order_by(Fee.end.desc())
                .first()
            )

            if last_fee and last_fee.end > datetime.now():  # type: ignore
                logging.debug(
                    "Last fee: start=%s, end=%s",
                    last_fee.start, last_fee.end
                )
                start: datetime = last_fee.end  # type: ignore
            else:
                start = datetime.now()
            # end = start + timedelta(days=(3.65*int(form.amount.data)))
            end = start + timedelta(days=(1.825 * int(fee_form.amount.data)))

            # Store fee
            fee = Fee(
                uid=person.uid,
                registered_by=self.util.current_user(),
                amount=fee_form.amount.data,
                start=start,
                end=end,
                method=fee_form.method.data,
            )
            self.storage.add(fee)
            self.storage.commit()

            logging.info(
                "Registered fee %d SEK for %d",
                fee_form.amount.data, person.uid
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
                logging.info("%s %s is now active", person.fname, person.lname)
                self.mail.send_mail(
                    self.app.config["ORG_EMAIL"],
                    "mail/board_member_active.html",
                    member=person,
                )
                self.mail.send_mail(
                    person, "member_active.mail", member=person)

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Registered fee %d SEK for %s %s"
                    % (fee_form.amount.data, person.fname, person.lname),
                )
            )
            fee_form = FeeForm(None)

        elif "submitPayment" in request.form and payment_form.validate():
            fee_form = FeeForm(None)  # Clear the other form
            person = (
                self.storage.session.query(Person)
                .filter_by(uid=payment_form.uid.data)
                .scalar()
            )

            if person is None:
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        'No such member "%s". Did you try the auto-complete feature?'
                        % payment_form.uid.data,
                    )
                )
                return redirect(url_for("register_fee"))

            # Store payment
            payment = Payment(
                uid=person.uid,
                registered_by=self.util.current_user(),
                amount=payment_form.amount.data,
                method=payment_form.method.data,
                reason=payment_form.reason.data,
            )
            self.storage.add(payment)
            self.storage.commit()

            logging.info(
                "Registered payment %d SEK for %d",
                payment_form.amount.data, person.uid
            )

            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "Registered payment %d SEK for %s %s"
                    % (payment_form.amount.data, person.fname, person.lname),
                )
            )
            payment_form = PaymentForm(None)

        return render_template(
            "register_fee.html", feeForm=fee_form, paymentForm=payment_form
        )
