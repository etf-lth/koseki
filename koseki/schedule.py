import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from flask import Flask

from koseki.db.storage import Storage
from koseki.db.types import Fee, Person
from koseki.mail import KosekiMailer
from koseki.util import KosekiUtil


class KosekiScheduler:
    def __init__(self, app: Flask, storage: Storage, mail: KosekiMailer, util: KosekiUtil):
        self.app = app
        self.storage = storage
        self.mail = mail
        self.util = util
        self.__sched = BackgroundScheduler()
        self.add_job = self.__sched.add_job

    def start(self) -> None:
        self.__sched.start()
        self.__sched.add_job(self.__update_members, "cron",
                             hour=4, minute=13, second=0)
        if self.app.config["PAYMENT_DEBT_ENABLED"]:
            self.__sched.add_job(
                self.util.send_debt_mail,
                "cron",
                month="*/3",
                day=28,
                hour=5,
                minute=24,
                second=0,
            )

    def __update_members(self) -> None:
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
                        "Member %s %s no longer active",
                        member.fname, member.lname
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
                        .order_by(Fee.end.desc()).first()
                    )
                    days_left = (last_fee.end - datetime.now()).days

                    # Send reminder to member
                    if days_left == 14:
                        logging.info(
                            "Member %s %s has %d days left, sending reminder",
                            member.fname, member.lname, days_left
                        )
                        self.mail.send_mail(
                            member,
                            "member_reminder.mail",
                            member=member,
                            days_left=days_left,
                        )