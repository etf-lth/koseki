import logging
import os
import time

import cups
from flask import escape, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from koseki.db.types import Fee, Person


class PrintForm(FlaskForm):
    file = FileField("Select Document", validators=[FileRequired()])


class PrintView:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage
        self.cupsConn = cups.Connection()
        self.ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    def register(self):
        self.app.add_url_rule(
            "/print",
            None,
            self.core.require_session(self.print),
            methods=["GET", "POST"],
        )
        self.core.nav("/print", "print", "Print", 5)

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def print(self):
        form = PrintForm()
        alerts = []

        if form.validate_on_submit():
            # check if the post request has the file part
            if 'file' not in request.files:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": 'No file part',
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": 'No selected file',
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)
            if not file or not self.allowed_file(file.filename):
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": 'That type of file is not allowed. Please try again or with a different file. Only PDF and DOCX is supported at the moment.',
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)
            
            # save file to harddrive
            filename = secure_filename(file.filename)
            filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename + "_" + str(time.time()))
            file.save(filepath)

            # send file to printer
            self.cupsConn.printFile("printer1", filepath, "", {"media": "A4"})

            # log that a document has been printed
            logging.info(
                "Document %s printed by %s"
                % (form.file.name, self.core.current_user())
            )

            # show success message to user
            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "File has now been scheduled for printing."
                    % (),
                }
            )
            form = PrintForm(None)

        return render_template("print.html", form=form, alerts=alerts)
