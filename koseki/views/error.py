from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.db.types import Person

@app.errorhandler(404)
def error_not_found(error):
    return render_template('error.html', error=error,
            message='The requested resouce was not found.'), 404

@app.errorhandler(403)
def error_not_found(error):
    return render_template('error.html', error=error,
            message='You do not have permission to access this content.'), 403
