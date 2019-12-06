from koseki import app, storage
from koseki.core import require_session, nav
from koseki.db.types import Person
from flask import render_template

@app.route('/mail')
@nav('/mail','envelope','Mail',4,['admin','board','pr','m3','krangare'])
@require_session(['admin','board','pr','m3','krangare'])
def mail():
    return render_template('list_mail.html', persons=storage.session.query(Person).filter_by(state='active').all())
