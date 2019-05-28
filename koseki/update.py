from koseki import app, storage, sched
from koseki.db.types import Person, Fee
from koseki.mail import send_mail
from datetime import datetime, timedelta
import logging

@sched.cron_schedule(hour=07, minute=00, second=0)
def update_members():
    with app.app_context():
        logging.info('Update members')
        members = storage.session.query(Person).filter(Person.state == 'active').all()

        for member in members:
            if storage.session.query(Fee).\
                    filter(Fee.uid==member.uid, Fee.start<=datetime.now(), Fee.end>=datetime.now()).count() < 1:
                # Membership has expired
                logging.info('Member %s %s no longer active' % (member.fname, member.lname))
                member.state = 'expired'
                storage.commit()

                # Send mail to member and board
                send_mail(member, 'member_expired.mail', member=member)
                send_mail(app.config['BOARD_EMAIL'], 'board_member_expired.mail', member=member)
            else:
                # Check expiration date
                last_fee = storage.session.query(Fee).filter_by(uid=member.uid).order_by(Fee.end.desc()).first()
                days_left = (last_fee.end - datetime.now()).days

                # Send reminder to member
                if days_left == 14:
                    logging.info('Member %s %s has %d days left, sending reminder' % (member.fname, member.lname, days_left))
                    send_mail(member, 'member_reminder.mail', member=member, days_left=days_left) 
