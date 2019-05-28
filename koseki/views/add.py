from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, current_user, nav
from koseki.db.types import Person
from koseki.mail import send_mail

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email

import logging

class EnrollForm(Form):

    fname = TextField('First name', validators=[DataRequired()])
    lname = TextField('Last name', validators=[DataRequired()])
    email = TextField('Email', validators=[Email()])
    stil = TextField('StiL')


@app.route('/enroll', methods=['GET', 'POST'])
@nav('/enroll','icon-plus-sign','Enroll', 2, ['admin','board','enroll'])
@require_session(['admin','board','enroll'])
def enroll_member():
    form = EnrollForm()
    alerts = []

    if form.validate_on_submit():
        if storage.session.query(Person).filter_by(email=form.email.data).scalar():
            alerts.append({'class': 'alert-error',
                'title': 'Error',
                'message': 'The specified email %s is already in use!' % form.email.data})
        elif form.stil.data and storage.session.query(Person).filter_by(stil=form.stil.data).scalar():
            alerts.append({'class': 'alert-error',
                'title': 'Error',
                'message': 'The specified StiL %s is already in use!' % form.stil.data})
        else:
            person = Person(enrolled_by=current_user())
            form.populate_obj(person)
            storage.add(person)
            storage.commit()

            logging.info('Enrolled %s %s' % (person.fname, person.lname))

            send_mail(person, 'member_enrolled.mail', member=person)
            send_mail(app.config['BOARD_EMAIL'], 'board_member_enrolled.mail', member=person)

            msg = [{'class': 'alert-success',
                'title': 'Success',
                'message': '%s %s was successfully enrolled' % (form.fname.data, form.lname.data)}]
            return render_template('message.html', messages=msg)

    return render_template('enroll_member.html', form=form, alerts=alerts)
