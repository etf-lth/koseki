import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from flask import render_template

from koseki.db.types import Person


class KosekiMailer:
    def __init__(self, app):
        self.app = app

    def send_mail(self, to, template, **kwargs):
        try:
            from_mail = self.app.config["EMAIL_FROM"]
            if type(to) is Person:
                to = "%s %s <%s>" % (to.fname, to.lname, to.email)

            logging.info(
                "send_mail to=%s, template=%s, args=%s" % (to, template, kwargs)
            )

            mimeType = "plain"
            if template.endswith("html"):
                mimeType = "html"

            msg = MIMEText(
                render_template(template, **kwargs), mimeType, _charset="utf8"
            )
            msg["To"] = Header(to, "utf-8")
            msg["From"] = Header(from_mail, "utf-8")
            msg["Subject"] = Header(self.app.config["EMAIL_SUBJECT"], "utf-8")

            s = smtplib.SMTP(self.app.config["SMTP_SERVER"])
            s.sendmail(from_mail, [to], msg.as_string())
            s.quit()
        except (Exception, ConnectionRefusedError) as e:
            logging.exception("send_mail failed: %s" % e)
            pass
