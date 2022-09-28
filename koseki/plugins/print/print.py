import logging
import os
import time
from typing import Union

import cups  # type: ignore
from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm  # type: ignore
from flask_wtf.file import FileField, FileRequired  # type: ignore
from werkzeug.wrappers import Response

from koseki.plugin import KosekiPlugin
from koseki.util import KosekiAlert, KosekiAlertType


class PrintForm(FlaskForm):
    file = FileField("Select Document", validators=[FileRequired()])


class PrintPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {
            "UPLOAD_FOLDER": "./data",
            "ALLOWED_EXTENSIONS": ["pdf"]
        }

    def plugin_enable(self) -> None:
        if not os.path.exists(self.app.config["UPLOAD_FOLDER"]):
            os.makedirs(self.app.config["UPLOAD_FOLDER"])
        self.cups_conn = cups.Connection()  # pylint: disable=attribute-defined-outside-init

    def create_blueprint(self) -> Blueprint:
        self.util.nav("/print", "print", "Print", 6)
        blueprint: Blueprint = Blueprint(
            "print", __name__, template_folder="./templates"
        )
        blueprint.add_url_rule(
            "/print",
            None,
            self.auth.require_session(self.print),
            methods=["GET", "POST"],
        )
        return blueprint

    def allowed_file(self, filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in self.app.config["ALLOWED_EXTENSIONS"]
        )

    def print(self) -> Union[str, Response]:
        form = PrintForm()

        if form.validate_on_submit():
            # check if the post request has the file part
            if "file" not in request.files:
                self.util.alert(
                    KosekiAlert(KosekiAlertType.DANGER,
                                "Error", "No file part",)
                )
                return render_template("print.html", form=form)
            file = request.files["file"]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == "":
                self.util.alert(
                    KosekiAlert(KosekiAlertType.DANGER,
                                "Error", "No selected file",)
                )
                return render_template("print.html", form=form)
            if not file or not self.allowed_file(file.filename):
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Error",
                        """That type of file is not allowed.
                        Please try again or with a different file. Allowed files are: %s"""
                        % (", ".join(self.app.config["ALLOWED_EXTENSIONS"])),
                    )
                )
                return render_template("print.html", form=form)

            # save file to harddrive
            filename = "".join(
                [c for c in file.filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
            filepath = os.path.join(
                self.app.config["UPLOAD_FOLDER"], filename +
                "_" + str(time.time())
            )
            file.save(filepath)

            # send file to printer
            self.cups_conn.printFile("printer1", filepath, "", {"media": "A4"})

            # log that a document has been printed
            logging.info(
                "Document %s printed by %s",
                form.file.name, self.util.current_user()
            )

            # delete file after sending it to printer
            file.close()
            try:
                os.remove(filepath)

                logging.info(
                    "Deleted file after sending it to the printer."
                )
            except Exception as error:
                logging.warning(
                    """Failed to delete file after printing,
                    delete it manually from {project-root}/data."""
                )

            # show success message to user
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.SUCCESS,
                    "Success",
                    "File has now been scheduled for printing.",
                )
            )
            form = PrintForm(None)

        return render_template("print.html", form=form)
