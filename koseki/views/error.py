from koseki import app, storage
from flask import url_for, render_template, session, redirect, escape, request
from koseki.db.types import Person


@app.errorhandler(400)
def error_bad_request(error):
    return render_template('error.html', code=400, codename="Bad Request",
                           message='The browser sent an invalid request, unable to be understood by the server.'), 400


@app.errorhandler(403)
def error_forbidden(error):
    return render_template('error.html', code=403, codename="Forbidden",
                           message='You do not have permission to access this page.'), 403


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error.html', code=404, codename="Not Found",
                           message='The requested page or resource was not found.'), 404
