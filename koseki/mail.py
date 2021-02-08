import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Union

from flask import render_template
from flask.app import Flask

from koseki.db.types import Person


class KosekiMailer:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def send_mail(self, to: Union[Person, str],  # type: ignore
                  template: str, **kwargs) -> bool:
        try:
            msg = MIMEMultipart()

            from_mail = self.app.config["EMAIL_FROM"]
            to_mail: str

            if isinstance(to, Person):
                to_mail = str(to.email)
                msg["To"] = formataddr(
                    (str(Header("%s %s" % (to.fname, to.lname), 'utf-8')), to_mail))
            elif isinstance(to, str):
                to_mail = to
                msg["To"] = Header(to_mail, "utf-8")
            else:
                raise TypeError("Mail target was neither string nor Person")

            msg["From"] = Header(from_mail, "utf-8")
            msg["Subject"] = Header(self.app.config["EMAIL_SUBJECT"], "utf-8")

            logging.info("send_mail to=%s, template=%s", to_mail, template)

            mime_type = "plain"
            if template.endswith("html"):
                mime_type = "html"

            msg.attach(MIMEText(
                render_template(template, **kwargs), mime_type, _charset="utf8"
            ))

            mail_client = smtplib.SMTP(
                host=self.app.config["SMTP_SERVER"], port=self.app.config["SMTP_PORT"])
            if self.app.config["SMTP_USE_TLS"]:
                mail_client.starttls()
            mail_client.sendmail(from_mail, to_mail, msg.as_string())
            mail_client.quit()
            return True
        except (smtplib.SMTPException, ConnectionRefusedError) as error:
            logging.exception("send_mail failed: %s", error)
            return False
