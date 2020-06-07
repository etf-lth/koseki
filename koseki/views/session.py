
import hashlib

from flask import escape, redirect, render_template, request, session, url_for

from koseki.db.types import Person


class SessionView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def register(self):
        self.app.add_url_rule("/login", None, self.login, methods=['GET', 'POST'])
        self.app.add_url_rule("/logout", None, self.logout)
        self.core.nav("/logout", "power-off", "Sign out", 999)

    def login(self):
        alert = None
        if request.method == 'POST':
            person = self.storage.session.query(Person).filter_by(email=request.form['email']).scalar()
            if person and person.password == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                self.core.start_session(person.uid)
                return redirect(request.form['redir'])
            else:
                alert = {'class': 'alert-danger',
                        'title': 'Authentication error',
                        'message': 'The username or password is incorrect.'}

        return render_template('login.html', redir=request.args.get('redir',url_for('index')), alert=alert, alternate=self.core.get_alternate_login())

    def logout(self):
        self.core.destroy_session()
        return render_template('logout.html')
