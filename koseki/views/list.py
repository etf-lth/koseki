from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.core import require_session, nav
from koseki.db.types import Person

@app.route('/list')
@nav('/list','list','List',1,['admin','board'])
@require_session(['admin','board'])
def list_members():
    return render_template('list_members.html', persons=storage.session.query(Person).all())

