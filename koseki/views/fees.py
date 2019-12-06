from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, nav, current_user
from koseki.db.types import Person, Fee
from koseki.mail import send_mail

from flask_wtf import Form
from wtforms import TextField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Optional

from datetime import datetime, timedelta
import re
import logging

@app.route('/fees')
@nav('/fees','certificate','Fees',3,['admin','accounter'])
@require_session(['admin','accounter'])
def list_fees():
    return render_template('list_fees.html', fees=storage.session.query(Fee).order_by(Fee.registered.desc()).all())

class FeeForm(Form):

    uid = TextField('Member ID', validators=[DataRequired()])
    amount = DecimalField('Amount (SEK)')
    method = SelectField('Payment Method', choices=[('swish','Swish'),('cash','Cash'),('bankgiro','Bankgiro'),('creditcard','Credit card')])
    retro = DateField('Retroactive fee (Date)', validators=[Optional()])

@app.route('/fees/csv')
@require_session(['admin','accounter'])
def export_csv():
    return render_template('list_fees.csv', fees=storage.session.query(Fee).order_by(Fee.registered.desc()).all())

@app.route('/fees/register', methods=['GET','POST'])
@require_session(['admin','accounter'])
def register_fee():
    form = FeeForm()

    alerts = []

    if form.validate_on_submit():
        person = storage.session.query(Person).filter_by(uid=form.uid.data).scalar()

        if person is None:
            alerts.append({'class': 'alert-danger',
                'title': 'Error',
                'message': 'No such member "%s". Did you try the auto-complete feature?' % form.uid.data})
            return render_template('register_fee.html', form=form, alerts=alerts)

        if form.retro.data is not None:
            # Use user-supplied start date
            start = form.retro.data
        else:
            # Calculate period of validity
            last_fee = storage.session.query(Fee).filter_by(uid=person.uid).order_by(Fee.end.desc()).first()

            if last_fee and last_fee.end > datetime.now():
                logging.debug('Last fee: start=%s, end=%s' % (last_fee.start, last_fee.end))
                start = last_fee.end
            else:
                start = datetime.now()
        #end = start + timedelta(days=(3.65*int(form.amount.data)))
        end = start + timedelta(days=(1.825*int(form.amount.data)))

        # Store fee
        fee = Fee(uid=person.uid, registered_by=current_user(), amount=form.amount.data, start=start, end=end, method=form.method.data)
        storage.add(fee)
        storage.commit()

        logging.info('Registered %d SEK for %s %s' % (form.amount.data, person.fname, person.lname))

        # Check for user state changes
        if person.state != 'active' and storage.session.query(Fee).\
                filter(Fee.uid==person.uid, Fee.start<=datetime.now(), Fee.end>=datetime.now()).all():
            person.state = 'active'
            storage.commit()
            logging.info('%s %s is now active' % (person.fname, person.lname))
            send_mail(app.config['BOARD_EMAIL'], 'board_member_active.mail', member=person)
            send_mail(person, 'member_active.mail', member=person)

        alerts.append({'class': 'alert-success',
            'title': 'Success',
            'message': 'Registered %d SEK for %s %s' % (form.amount.data, person.fname, person.lname)})
        form = FeeForm(None)

    return render_template('register_fee.html', form=form, alerts=alerts)
