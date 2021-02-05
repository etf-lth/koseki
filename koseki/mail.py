import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Union

from flask import render_template

from koseki.db.types import Person


class KosekiMailer:
    def __init__(self, app):
        self.app = app

    def send_mail(self, to: Union[Person, str], template: str, **kwargs):
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

            logging.info(
                "send_mail to=%s, template=%s" % (
                    to_mail, template)
            )

            mimeType = "plain"
            if template.endswith("html"):
                mimeType = "html"

            msg.attach(MIMEText(
                render_template(template, **kwargs), mimeType, _charset="utf8"
            ))

            s = smtplib.SMTP(host=self.app.config["SMTP_SERVER"], port=self.app.config["SMTP_PORT"])
            if self.app.config["SMTP_USE_TLS"]:
                s.starttls()
            s.sendmail(from_mail, to_mail, msg.as_string())
            s.quit()
        except (Exception, ConnectionRefusedError) as e:
            logging.exception("send_mail failed: %s" % e)
            pass
