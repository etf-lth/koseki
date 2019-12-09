
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, member_of, current_user, nav
from koseki.db.types import Person
from koseki.db.types import PersonGroup
from datetime import datetime


class IndexView:

    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule('/', None, self.index)
        self.core.nav('/', 'home', 'Home', -999)

    @require_session()
    def index(self):
        if member_of('admin') or member_of('board'):
            active = self.storage.session.query(
                Person).filter_by(state='active').count()
            pending = self.storage.session.query(
                Person).filter_by(state='pending').count()
            enrolled = self.storage.session.query(Person).filter(
                Person.enrolled >= datetime.now().replace(month=1, day=1)).count()
            return render_template('overview.html', active=active, pending=pending, enrolled=enrolled)
        else:
            return render_template('home.html')
