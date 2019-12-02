from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import start_session, destroy_session, nav, get_alternate_login
from koseki.db.types import Person
import hashlib

@app.route('/login', methods=['GET', 'POST'])
def login():
    alert = None
    if request.method == 'POST':
        person = storage.session.query(Person).filter_by(email=request.form['email']).scalar()
        if person and person.password == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
            start_session(person.uid)
            return redirect(request.form['redir'])
        else:
            alert = {'class': 'alert-error',
                    'title': 'Authentication error',
                    'message': 'The username or password is incorrect.'}

    return render_template('login.html', redir=request.args.get('redir',url_for('index')), alert=alert, alternate=get_alternate_login())

@app.route('/logout')
@nav('/logout','icon-off','Sign out',999)
def logout():
    destroy_session()
    return render_template('logout.html')
