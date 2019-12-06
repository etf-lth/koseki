from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, member_of, current_user, nav
from koseki.db.types import Person
from koseki.db.types import PersonGroup
from datetime import datetime

@app.route('/')
@nav('/','home','Home',-999)
@require_session()
def index():
    if storage.session.query(Person).count() < 1:
        storage.add(Person(fname='Test', lname='Testsson',
            email='test@example.com', password='5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8')) # pass: password
        storage.add(PersonGroup(uid=1, gid=1))
        storage.commit()
    if member_of('admin') or member_of('board'):
        active = storage.session.query(Person).filter_by(state='active').count()
        pending = storage.session.query(Person).filter_by(state='pending').count()
        enrolled = storage.session.query(Person).filter(Person.enrolled >= datetime.now().replace(month=1, day=1)).count()
        return render_template('overview.html', active=active, pending=pending, enrolled=enrolled)
    else:
        return render_template('home.html')

