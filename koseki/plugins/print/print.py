import logging
import os
import time

import cups
from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from koseki.plugin import KosekiPlugin
from werkzeug.utils import secure_filename


class PrintForm(FlaskForm):
    file = FileField("Select Document", validators=[FileRequired()])


class PrintPlugin(KosekiPlugin):
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def config(self) -> dict:
        return {"ALLOWED_EXTENSIONS": ("pdf")}

    def plugin_enable(self) -> None:
        self.cupsConn = cups.Connection()

    def create_blueprint(self) -> Blueprint:
        self.core.nav("/print", "print", "Print", 6)
        blueprint: Blueprint = Blueprint(
            "store", __name__, template_folder="./templates"
        )
        self.app.add_url_rule(
            "/print",
            None,
            self.core.require_session(self.print),
            methods=["GET", "POST"],
        )
        return blueprint

    def allowed_file(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in self.app.config["ALLOWED_EXTENSIONS"]
        )

    def print(self):
        form = PrintForm()
        alerts = []

        if form.validate_on_submit():
            # check if the post request has the file part
            if "file" not in request.files:
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "No file part",
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)
            file = request.files["file"]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == "":
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "No selected file",
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)
            if not file or not self.allowed_file(file.filename):
                alerts.append(
                    {
                        "class": "alert-danger",
                        "title": "Error",
                        "message": "That type of file is not allowed. Please try again or with a different file. At the moment only PDF files are supported.",
                    }
                )
                return render_template("print.html", form=form, alerts=alerts)

            # save file to harddrive
            filename = secure_filename(file.filename)
            filepath = os.path.join(
                self.app.config["UPLOAD_FOLDER"], filename + "_" + str(time.time())
            )
            file.save(filepath)

            # send file to printer
            self.cupsConn.printFile("printer1", filepath, "", {"media": "A4"})

            # log that a document has been printed
            logging.info(
                "Document %s printed by %s" % (form.file.name, self.core.current_user())
            )

            # show success message to user
            alerts.append(
                {
                    "class": "alert-success",
                    "title": "Success",
                    "message": "File has now been scheduled for printing." % (),
                }
            )
            form = PrintForm(None)

        return render_template("print.html", form=form, alerts=alerts)
