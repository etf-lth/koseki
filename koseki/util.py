from koseki.db.storage import Storage
from flask import session

import logging
from koseki.db.types import Group, Person


class KosekiUtil:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.navigation: list = [] # TODO make more detailed
        self.alt_login = None

    def nav(self, uri, icon, title, weight=0, groups=None):
        self.navigation.append(
            {
                "uri": uri,
                "icon": icon,
                "title": title,
                "groups": groups,
                "weight": weight,
            }
        )

    def calc_nav(self):
        nav = []
        for n in self.navigation:
            if n["groups"] is None or sum(
                1 for group in n["groups"] if self.member_of(group)
            ) > 0:
                nav.append(n)
        session["nav"] = sorted(nav, key=lambda x: x["weight"])

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

    def fetch_alerts(self):
        alerts = session.pop("alerts", [])
        session["alerts"] = []
        return alerts

    def set_alerts(self, alerts) -> None:
        session["alerts"] = alerts

    def get_alternate_login(self):
        return self.alt_login

    def alternate_login(self, alt):
        self.alt_login = alt()
        logging.info("Registered alternate login provider: %s" % self.alt_login)
