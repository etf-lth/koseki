from apscheduler.scheduler import Scheduler
from koseki.db.types import Person, Fee
from koseki.mail import Mailer
from datetime import datetime, timedelta
import logging


class Updater:

    def __init__(self, app, storage):
        self.app = app
        self.storage = storage
        self.sched = Scheduler()

    def start(self):
        self.sched.start()
        self.sched.add_cron_job(self.update_members,
                                hour=7, minute=0, second=0)

    def update_members(self):
        with self.app.app_context():
            logging.info('Update members')
            members = self.storage.session.query(
                Person).filter(Person.state == 'active').all()

            for member in members:
                if self.storage.session.query(Fee).\
                        filter(Fee.uid == member.uid, Fee.start <= datetime.now(), Fee.end >= datetime.now()).count() < 1:
                    # Membership has expired
                    logging.info('Member %s %s no longer active' %
                                 (member.fname, member.lname))
                    member.state = 'expired'
                    self.storage.commit()

                    # Send mail to member and board
                    self.app.mailer.send_mail(
                        member, 'member_expired.mail', member=member)
                    self.app.mailer.send_mail(self.app.config['BOARD_EMAIL'],
                                              'board_member_expired.mail', member=member)
                else:
                    # Check expiration date
                    last_fee = self.storage.session.query(Fee).filter_by(
                        uid=member.uid).order_by(Fee.end.desc()).first()
                    days_left = (last_fee.end - datetime.now()).days

                    # Send reminder to member
                    if days_left == 14:
                        logging.info('Member %s %s has %d days left, sending reminder' % (
                            member.fname, member.lname, days_left))
                        self.app.mailer.send_mail(member, 'member_reminder.mail',
                                                  member=member, days_left=days_left)
