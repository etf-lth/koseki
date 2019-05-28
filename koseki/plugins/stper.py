from koseki import app, storage
from koseki.core import require_session, nav, current_user
from koseki.db.types import Person

import paho.mqtt.client as mqtt

from flask import request, abort, render_template

@app.route('/stper', methods=['GET','POST'])
@nav('/stper','icon-lock','Door',4,['admin','stper'])
@require_session(['admin','stper'])
def unlock():
    alerts = []

    user = storage.session.query(Person).filter_by(uid=current_user()).scalar()

    active = user.state == 'active'

    if active and 'open' in request.form:
        try:
            client = mqtt.Client()
            client.username_pw_set('koseki','rajrajraj')
            client.connect('localhost', 1883, 60)
            client.publish('/door','open')

            alerts.append({'class': 'alert-success',
                'title': 'Success',
                'message': 'Sent open request'})

        except Exception as e:
            alerts.append({'class': 'alert-error',
                'title': 'Error',
                'message': e})

    if not active:
        alerts.append({'class': 'alert-warning',
            'title': 'User not active',
            'message': 'Your membership is not active.'})

    return render_template('stper.html', alerts=alerts, active=active)
