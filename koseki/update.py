import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from flask import Flask

from koseki.db.storage import Storage
from koseki.db.types import Fee, Person
from koseki.mail import KosekiMailer


class Updater:
    def __init__(self, app: Flask, storage: Storage, mail: KosekiMailer):
        self.app = app
        self.storage = storage
        self.mail = mail
        self.__sched = BackgroundScheduler()

    def start(self):
        self.__sched.start()
        self.__sched.add_job(self.__update_members, "cron", hour=4, minute=0, second=0)
        self.__sched.add_job(
            self.__send_debt_mail,
            "cron",
            month="*/3",
            day=28,
            hour=5,
            minute=0,
            second=0,
        )

    def __update_members(self):
        with self.app.app_context():
            logging.info("Update members")
            members = (
                self.storage.session.query(Person)
                .filter(Person.state == "active")
                .all()
            )

            for member in members:
                if (
                    self.storage.session.query(Fee)
                    .filter(
                        Fee.uid == member.uid,
                        Fee.start <= datetime.now(),
                        Fee.end >= datetime.now(),
                    )
                    .count()
                    < 1
                ):
                    # Membership has expired
                    logging.info(
                        "Member %s %s no longer active" % (member.fname, member.lname)
                    )
                    member.state = "expired"
                    self.storage.commit()

                    # Send mail to member and board
                    self.mail.send_mail(
                        member, "member_expired.mail", member=member
                    )
                    self.mail.send_mail(
                        self.app.config["ORG_EMAIL"],
                        "mail/board_member_expired.html",
                        member=member,
                    )
                else:
                    # Check expiration date
                    last_fee: Fee = (
                        self.storage.session.query(Fee)
                        .filter_by(uid=member.uid)
                        .order_by(Fee.end.desc())
                        .scalar()
                    )
                    days_left = (last_fee.end - datetime.now()).days  # type: ignore # TODO

                    # Send reminder to member
                    if days_left == 14:
                        logging.info(
                            "Member %s %s has %d days left, sending reminder"
                            % (member.fname, member.lname, days_left)
                        )
                        self.mail.send_mail(
                            member,
                            "member_reminder.mail",
                            member=member,
                            days_left=days_left,
                        )

    def __send_debt_mail(self):
        with self.app.app_context():
            logging.info("Checking debt and sending emails")
            # This could probably be made more efficient with a .filter() on balance, but
            # difficult right now to implement as SQLAlchy wouldn't know how to structure
            # the SQL query due to .balance being a @property.
            members = self.storage.session.query(Person).all()

            for member in members:
                if member.balance >= 0:
                    continue

                logging.info(
                    "Member %s %s has %d unpaid payments, sending reminder"
                    % (member.fname, member.lname, len(member.unpaid_payments))
                )
                self.mail.send_mail(
                    member, "mail/unpaid_payments.html", member=member
                )
