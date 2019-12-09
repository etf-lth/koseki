from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, current_user, nav
from koseki.db.types import Person

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email

import logging


class EnrollForm(Form):

    fname = TextField('First name', validators=[DataRequired()])
    lname = TextField('Last name', validators=[DataRequired()])
    email = TextField('Email', validators=[Email()])
    stil = TextField('StiL')


class AddView:

    def __init__(self, app, core, storage, mailer):
        self.app = app
        self.core = core
        self.storage = storage
        self.mailer = mailer

    def register(self):
        self.app.add_url_rule(
            '/enroll', None, self.enroll_member, methods=['GET', 'POST'])
        self.core.nav('/enroll', 'plus-circle', 'Enroll',
                      2, ['admin', 'board', 'enroll'])

    @require_session(['admin', 'board', 'enroll'])
    def enroll_member(self):
        form = EnrollForm()
        alerts = []

        if form.validate_on_submit():
            if self.storage.session.query(Person).filter_by(email=form.email.data).scalar():
                alerts.append({'class': 'alert-danger',
                               'title': 'Error',
                               'message': 'The specified email %s is already in use!' % form.email.data})
            elif form.stil.data and self.storage.session.query(Person).filter_by(stil=form.stil.data).scalar():
                alerts.append({'class': 'alert-danger',
                               'title': 'Error',
                               'message': 'The specified StiL %s is already in use!' % form.stil.data})
            else:
                person = Person(enrolled_by=current_user())
                form.populate_obj(person)
                self.storage.add(person)
                self.storage.commit()

                logging.info('Enrolled %s %s' % (person.fname, person.lname))

                self.mailer.send_mail(
                    person, 'member_enrolled.mail', member=person)
                self.mailer.send_mail(
                    self.app.config['BOARD_EMAIL'], 'board_member_enrolled.mail', member=person)

                msg = [{'class': 'alert-success',
                        'title': 'Success',
                        'message': '%s %s was successfully enrolled' % (form.fname.data, form.lname.data)}]
                return render_template('message.html', messages=msg)

        return render_template('enroll_member.html', form=form, alerts=alerts)
