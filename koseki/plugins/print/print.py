import logging
import os
import time
from typing import List

import cups  # type: ignore
from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm  # type: ignore
from flask_wtf.file import FileField, FileRequired  # type: ignore
from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType
from werkzeug.utils import secure_filename


class PrintForm(FlaskForm):
    file = FileField("Select Document", validators=[FileRequired()])


class PrintPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {"ALLOWED_EXTENSIONS": ("pdf")}

    def plugin_enable(self) -> None:
        self.cupsConn = cups.Connection()

    def create_blueprint(self) -> Blueprint:
        self.util.nav("/print", "print", "Print", 6)
        blueprint: Blueprint = Blueprint(
            "store", __name__, template_folder="./templates"
        )
        blueprint.add_url_rule(
            "/print",
            None,
            self.auth.require_session(self.print),
            methods=["GET", "POST"],
        )
        return blueprint

    def allowed_file(self, filename: str):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in self.app.config["ALLOWED_EXTENSIONS"]
        )

    def print(self):
        form = PrintForm()
        alerts: List[KosekiAlert] = []

        if form.validate_on_submit():
            # check if the post request has the file part
            if "file" not in request.files:
                alerts.append(
                    KosekiAlert(KosekiAlertType.DANGER, "Error", "No file part",)
                )
                return render_template("print.html", form=form, alerts=alerts)
            file = request.files["file"]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == "":
                alerts.append(
                    KosekiAlert(KosekiAlertType.DANGER, "Error", "No selected file",)
                )
                return render_template("print.html", form=form, alerts=alerts)
            if not file or not self.allowed_file(file.filename):
                alerts.append(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        "That type of file is not allowed. Please try again or with a different file. At the moment only PDF files are supported.",
                    )
                )  # TODO: Don't hardcode PDF-only, make it use the env var instead
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
                "Document %s printed by %s" % (form.file.name, self.util.current_user())
            )

            # show success message to user
            alerts.append(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "File has now been scheduled for printing.",
                )
            )
            form = PrintForm(None)

        return render_template("print.html", form=form, alerts=alerts)
