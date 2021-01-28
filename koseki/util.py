from typing import List
from koseki.db.storage import Storage
from flask import session

import logging
from koseki.db.types import Group, Person

class KosekiAlertType:
    DANGER = "alert-danger"
    SUCCESS = "alert-success"
    WARNING = "alert-warning"

class KosekiAlert:
    def __init__(self, type: str, title: str, message: str):
        self.type = type
        self.title = title
        self.message = message

class KosekiNavigationEntry:
    def __init__(self, uri: str, icon: str, title: str, weight: int, groups: List[str]):
        self.uri = uri
        self.icon = icon
        self.title = title
        self.weight = weight
        self.groups = groups

class KosekiUtil:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.navigation: List[KosekiNavigationEntry] = []
        self.alt_login = None

    def nav(self, uri, icon, title, weight=0, groups=None):
        self.navigation.append(KosekiNavigationEntry(uri, icon ,title, weight, groups))

    def calc_nav(self):
        nav: List[KosekiNavigationEntry] = []
        for n in self.navigation:
            if n.groups is None or sum(
                1 for group in n.groups if self.member_of(group)
            ) > 0:
                nav.append(n)
        session["nav"] = sorted(nav, key=lambda x: x.weight)

    def start_session(self, uid):
        session["uid"] = int(uid)
        session.permanent = True
        session.modified = True
        self.calc_nav()

    def destroy_session(self):
        session.pop("uid", None)

    def member_of_processor(self):
        return dict(member_of=self.member_of)

    def member_of(self, group, person=None):
        if person is None:
            person = self.current_user()
        if type(person) in (int, int):
            person = self.storage.query(Person).filter_by(uid=person).scalar()
        if type(group) == int:
            group = self.storage.query(Group).filter_by(gid=group).scalar()
        elif type(group) == str:
            group = self.storage.query(Group).filter_by(name=group).scalar()
        return sum(1 for x in person.groups if x.gid == group.gid)

    # TODO: move current_user to auth?
    def current_user(self):
        return session["uid"]

    def fetch_alerts(self) -> List[KosekiAlert]:
        alerts: List[KosekiAlert] = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def set_alerts(self, alerts: List[KosekiAlert]) -> None:
        session["alerts"] = alerts

    def get_alternate_login(self):
        return self.alt_login

    def alternate_login(self, alt):
        self.alt_login = alt()
        logging.info("Registered alternate login provider: %s" % self.alt_login)
