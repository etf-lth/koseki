from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request, abort
from koseki.core import require_session, member_of, current_user, nav
from koseki.db.types import Person, Fee

from flask_wtf import Form
from wtforms import TextField, SelectMultipleField
from wtforms.validators import DataRequired, Email

@app.route('/membership')
@nav('/membership','user','My membership',10)
@require_session()
def membership_general():
    person = storage.session.query(Person).filter_by(uid=current_user()).scalar()
    last_fee = storage.session.query(Fee).filter_by(uid=current_user()).order_by(Fee.end.desc()).first()
    return render_template('membership_general.html', person=person, last_fee=last_fee)

class EditForm(Form):

    fname = TextField('First name', validators=[DataRequired()])
    lname = TextField('Last name', validators=[DataRequired()])
    email = TextField('Email', validators=[Email()])
    stil = TextField('StiL')

@app.route('/membership/edit', methods=['GET', 'POST'])
@require_session()
def membership_edit():
    person = storage.session.query(Person).filter_by(uid=current_user()).scalar()
    form = EditForm(obj=person)

    alerts = []
    alerts.append({'class': 'alert-warning',
        'title': 'Note',
        'message': 'Profile editing is currently disabled'})

    if request.method == 'POST':
        alerts.append({'class': 'alert-danger',
            'title': 'Error',
            'message': 'Profile editing is currently disabled'})

    return render_template('membership_edit.html', person=person, form=form, alerts=alerts)
