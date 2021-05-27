import base64
import hashlib
import logging
from datetime import datetime
from typing import Optional, Tuple

from flask import session
from flask.app import Flask
from flask.globals import request
from requests.utils import requote_uri

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.db.types import Person
from koseki.mail import KosekiMailer


class KosekiAlertType:
    DANGER = "alert-danger"
    SUCCESS = "alert-success"
    WARNING = "alert-warning"


class KosekiAlert(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, category: str, title: str, message: str):
        dict.__init__(self, category=category, title=title, message=message)
        self.category: str
        self.title: str
        self.message: str


class KosekiNavigationEntry(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, uri: str, icon: str, title: str, weight: int, groups: Optional[list[str]]):
        dict.__init__(self, uri=uri, icon=icon, title=title,
                      weight=weight, groups=groups)
        self.uri: str
        self.icon: str
        self.title: str
        self.weight: int
        self.groups: Optional[list[str]]


class KosekiUtil:
    def __init__(self, app: Flask, auth: KosekiAuth, storage: Storage, mail: KosekiMailer):
        self.app = app
        self.auth = auth
        self.storage = storage
        self.mail = mail
        self.navigation: list[KosekiNavigationEntry] = []
        self.alt_login: list[dict] = []

    def nav(self, uri: str, icon: str, title: str, weight: int = 0,
        groups: Optional[list[str]] = None) -> None:
        self.navigation.append(KosekiNavigationEntry(
            uri, icon, title, weight, groups))

    def calc_nav(self) -> None:
        nav_list: list[KosekiNavigationEntry] = []
        for nav in self.navigation:
            if nav.groups is None or sum(
                1 for group in nav.groups if self.auth.member_of(group)
            ) > 0:
                nav_list.append(nav)
        session["nav"] = sorted(nav_list, key=lambda x: x.weight)

    def start_session(self, uid: int) -> None:
        session["uid"] = uid
        session["permanent"] = True
        session["modified"] = True
        self.calc_nav()

    def current_user(self) -> int:
        return session["uid"]

    def destroy_session(self) -> None:
        session.pop("uid", None)

    def gravatar(self, mail: str) -> str:
        return (
            "//gravatar.com/avatar/" +
            hashlib.md5(mail.encode("utf-8")).hexdigest()
        )

    def format_date(self, value: datetime, date_format: str = "%Y-%m-%d") -> str:
        return value.strftime(date_format)

    def uid_to_name(self, uid: int) -> str:
        person = self.storage.session.query(
            Person).filter_by(uid=uid).scalar()
        return "%s %s" % (person.fname, person.lname) if person else "Nobody"

    def alert(self, alert: KosekiAlert) -> None:
        if "alerts" not in session:
            session["alerts"] = []
        session["alerts"].append(alert)

    def render_alerts(self) -> list[KosekiAlert]:
        if not request:
            return []
        alerts: list[KosekiAlert] = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def get_alternate_logins(self) -> list[dict]:
        return self.alt_login

    def alternate_login(self, alt: dict) -> None:
        self.alt_login.append(alt)
        logging.info("Registered alternate login provider: %s", alt["button"])

    def generate_swish_code(self, amount: float, message: str) -> str:
        if amount < 0:
            return "ERROR_CODE:NEGATIVE_AMOUNT"

        res = "C%s;%.2f;%s;0;%.0f" % (
            self.app.config["PAYMENT_METHOD_SWISH"], amount,
            requote_uri(message), datetime.timestamp(datetime.now()))

        res += "#" + \
            self.auth.hash_password(res + self.app.config["SECRET_KEY"])

        return str(base64.urlsafe_b64encode(res.encode("utf-8")), "utf-8")

    def validate_swish_code(self, code: str) -> Tuple[bool, Optional[str]]:
        code = str(base64.urlsafe_b64decode(code.encode("utf-8")), "utf-8")
        code_parts = code.split("#")
        if len(code_parts) != 2:
            return False, None

        message = code_parts[0]
        signature = code_parts[1]
        if not self.auth.verify_password(signature, message + self.app.config["SECRET_KEY"]):
            return False, None

        return True, message
    
    def send_debt_mail(self) -> None:
        with self.app.app_context():
            logging.info("Checking debt and sending emails")
            # This could probably be made more efficient with a .filter() on balance, but
            # difficult right now to implement as SQLAlchy wouldn't know how to structure
            # the SQL query due to .balance being a @property.
            members = self.storage.session.query(Person).all()

            for member in members:
                if len(member.email) == 0:
                    logging.warning("Member %s %s (%d) has no email.", member.fname, member.lname, member.uid)
                    continue
                if member.balance >= 0:
                    continue

                logging.info(
                    "Member %s %s (%d) has %d unpaid payments, sending reminder",
                    member.fname, member.lname, member.uid, len(member.unpaid_payments)
                )
                self.mail.send_mail(
                    member, "mail/unpaid_payments.html", member=member
                )
