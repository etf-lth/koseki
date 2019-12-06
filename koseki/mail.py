import logging
from koseki.db.types import Person, Fee

from flask import render_template

import smtplib
from email.mime.text import MIMEText


class Mailer:

    def __init__(self, app):
        self.app = app

    def send_mail(self, to, template, **kwargs):
        logging.info('send_mail to=%s, template=%s, args=%s' %
                     (to, template, kwargs))
        try:
            from_mail = self.app.config['EMAIL_FROM']

            if type(to) is Person:
                to = '%s %s <%s>' % (to.fname, to.lname, to.email)
                #logging.info('fulade fram mejladress "%s"' % to)

            msg = MIMEText(render_template(
                template, **kwargs), _charset='utf8')
            msg['To'] = to
            msg['From'] = from_mail
            msg['Subject'] = self.app.config['EMAIL_SUBJECT']

            s = smtplib.SMTP(self.app.config['SMTP_SERVER'])
            s.sendmail(from_mail, [to], msg.as_string())
            s.quit()
        except Exception as e:
            logging.exception('send_mail failed: %s' % e)
            pass
