from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, member_of, current_user, nav
from koseki.db.types import Person
from datetime import datetime

@app.route('/')
@nav('/','icon-home','Home',-999)
@require_session()
def index():
    if member_of('admin') or member_of('board'):
        active = storage.session.query(Person).filter_by(state='active').count()
        pending = storage.session.query(Person).filter_by(state='pending').count()
        enrolled = storage.session.query(Person).filter(Person.enrolled >= datetime.now().replace(month=1, day=1)).count()
        return render_template('overview.html', active=active, pending=pending, enrolled=enrolled)
    else:
        return render_template('home.html')

