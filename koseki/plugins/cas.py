from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from xml.etree import ElementTree as ET
from koseki.core import start_session, alternate_login
from koseki.db.types import Person

import urllib.request
import urllib.parse
import urllib.error


@alternate_login
def cas_login():
    return {'text': 'Please sign in using CAS ' +
            'if you are a student or employee at Lund University.',
            'url': app.config['CAS_SERVER']+'/cas/login?service='+app.config['URL_BASE']+'/cas&renew=false',
            'button': 'Sign in using CAS'}


@app.route('/cas')
def cas_ticket():
    if 'ticket' not in request.args:
        # just pretend it failed
        return render_template('cas.html', error='cas-failed')

    ticket = request.args['ticket']

    try:
        u = urllib.request.urlopen(app.config['CAS_SERVER'] + '/cas/serviceValidate?renew=false&ticket=' + ticket + '&service=' + urllib.parse.quote_plus(app.config['URL_BASE']+'/cas'))
        response = u.read().decode('utf-8')
        u.close()
        root = ET.fromstring(response)
        if root[0].tag == '{http://www.yale.edu/tp/cas}authenticationSuccess':
            uid = root[0][0].text.strip()

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
    except urllib.error.URLError:
        # most likely cannot contact cas
        return render_template('cas.html', error='cas-url-error')
