from koseki import app, storage
from koseki.core import member_of
from koseki.db.types import Person
from flask import request, abort

allowed_ips = ('130.235.20.201','130.235.20.67','194.47.250.246')

@app.route('/salto/all')
def salto_all():
    if 'X-Real-IP' in request.headers and (not request.headers['X-Real-IP'] in allowed_ips):
        abort(403)
    out = ''
    for member in storage.session.query(Person).filter_by(state='active').all():
        if len(member.stil) < 1:
            continue
        out = out + member.stil + '\r\n'
    return out

@app.route('/salto/sales')
def salto_sales():
    if 'X-Real-IP' in request.headers and (not request.headers['X-Real-IP'] in allowed_ips):
        abort(403)
    out = ''
    for member in storage.session.query(Person).filter_by(state='active').all():
        if len(member.stil) < 1:
            continue
        if member_of('sales', member):
            out = out + member.stil + '\r\n'
    return out

@app.route('/salto/mek')
def salto_mek():
    if 'X-Real-IP' in request.headers and (not request.headers['X-Real-IP'] in allowed_ips):
        abort(403)
    out = ''
    for member in storage.session.query(Person).filter_by(state='active').all():
        if len(member.stil) < 1:
            continue
        if member_of('mek', member):
            out = out + member.stil + '\r\n'
    return out
