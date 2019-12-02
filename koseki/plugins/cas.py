from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import start_session, alternate_login
from koseki.db.types import Person

import urllib.request, urllib.parse, urllib.error

@alternate_login
def cas_login():
    return {'text': 'Please sign in using CAS '+
            'if you are a student or employee at Lund University.',
            'url': app.config['CAS_SERVER']+'/cas/login?service='+app.config['URL_BASE']+'/cas&renew=true',
            'button': 'Sign in using CAS'}

@app.route('/cas')
def cas_ticket():
    ticket = request.args['ticket']

    alert = None

    u = urllib.request.urlopen(app.config['CAS_SERVER']+'/cas/validate?ticket='+ticket+'&service='+app.config['URL_BASE']+'/cas')
    response = u.readline()
    if response == "yes\n":
        uid = u.readline().strip()
        u.close()

        person = storage.session.query(Person).filter_by(stil=uid).scalar()
        if person:
            # valid user, move along
            start_session(person.uid)
            return redirect(url_for('index'))
        else:
            # authenticated by cas but unknown to us
            return render_template('cas.html', error='unknown-uid')
    else:
        # cas failed
        return render_template('cas.html', error='cas-failed')
