import json
import logging
from datetime import datetime
from typing import Optional, Type

from pyop.storage import StorageBase
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.schema import MetaData

from koseki.db.types import Base, Group, OIDCEntry, Person, PersonGroup


class Storage:
    def __init__(self, conn: str = "sqlite:///:memory:") -> None:
        sql_args = {
            "pool_recycle": 600,
            "pool_pre_ping": True,
        }
        if conn.startswith("mysql"):
            sql_args["pool_use_lifo"] = True
            sql_args["pool_size"] = 10
            sql_args["max_overflow"] = 20
            sql_args["pool_timeout"] = 3

        self.engine: Engine = create_engine(
            conn,
            **sql_args
        )

        metadata: MetaData = Base.metadata
        metadata.create_all(bind=self.engine)
        self._sessionmaker = sessionmaker(bind=self.engine)
        self._database: Optional[Session] = None

        self.__insert_initial_values()

    def close(self, error: Optional[Exception]) -> None:
        if error:
            logging.error(error)
        if self._database is not None:
            self._database.close()
            self._database = None

    @property
    def session(self) -> Session:
        if self._database is None:
            self._database = self._sessionmaker()
        return self._database

    def add(self, obj: Base) -> None:
        self.session.add(obj)

    def delete(self, obj: Base) -> None:
        self.session.delete(obj)

    def commit(self) -> None:
        self.session.commit()

    def query(self, obj: Type[Base]) -> Query:
        return self.session.query(obj)

    def __insert_initial_values(self) -> None:
        self.__insert_initial_values_group()
        self.__insert_initial_values_person()
        self.__insert_initial_values_person_group()
        self.commit()

    def __insert_initial_values_group(self) -> None:
        if self.session.query(Group).count() < 1:
            self.add(Group(name="admin", descr="System Administrator"))
            self.add(Group(name="enroll", descr="Allow enrolling new members"))
            self.add(Group(name="accounter", descr="Allow registering fees"))
            self.add(Group(name="board", descr="Allow general browsing of members"))

    def __insert_initial_values_person(self) -> None:
        # user: admin@example.com
        # pass: password
        if self.session.query(Person).count() < 1:
            self.add(
                Person(
                    uid=1,
                    fname="Admin",
                    lname="Testsson",
                    email="admin@example.com",
                    username="admin",
                    password="$argon2id$v=19$m=16,t=2,p=1$S1AwUjlDVXVnbFNBV2J3cg$ErwAfuI1RV2nl/B17lfQWg",
                )
            )  # pass: password

    def __insert_initial_values_person_group(self) -> None:
        if self.session.query(PersonGroup).count() < 1:
            self.add(PersonGroup(uid=1, gid=1))


class SQLWrapper(StorageBase):
    def __init__(self, storage: Storage, key_type: str, force_key_int: bool = False):
        self.storage = storage
        self._type = key_type
        self._force_key_int = force_key_int

    def __setitem__(self, key, value):
        entry = self.storage.session.query(OIDCEntry).filter_by(
            type=self._type, key=key).scalar()
        if not entry:
            self.storage.add(
                OIDCEntry(
                    type=self._type,
                    key=key,
                    value=json.dumps(value)
                )
            )
            self.storage.commit()
        else:
            entry.value = json.dumps(value)
            entry.last_modified = datetime.now()
            self.storage.commit()
        return value

    def __getitem__(self, key):
        entry = self.storage.session.query(OIDCEntry).filter_by(
            type=self._type, key=key).scalar()
        if not entry:
            raise KeyError(key)
        return json.loads(entry.value)

    def __delitem__(self, key):
        entry = self.storage.session.query(OIDCEntry).filter_by(
            type=self._type, key=key).scalar()
        if not entry:
            raise KeyError(key)
        self.storage.delete(entry)

    def __contains__(self, key):
        count = self.storage.session.query(OIDCEntry).filter_by(
            type=self._type, key=key).scalar()
        return bool(count)

    def items(self):
        for entry in self.storage.session.query(OIDCEntry).filter_by(type=self._type).all():
            if self._force_key_int:
                yield (int(entry.key), json.loads(entry.value))
            else:
                yield (entry.key, json.loads(entry.value))


class PersonWrapper(StorageBase):
    def __init__(self, storage: Storage):
        self.storage = storage

    def __setitem__(self, key, value):
        # Read-only interface: OIDC PersonWrapper not allowed to delete users
        raise NotImplementedError

    def __getitem__(self, key):
        person = self.storage.session.query(Person).filter_by(uid=key).scalar()
        if not person:
            raise KeyError(key)
        return vars(person)

    def __delitem__(self, key):
        # Read-only interface: OIDC PersonWrapper not allowed to delete users
        raise NotImplementedError

    def __contains__(self, key):
        count = self.storage.session.query(Person).filter_by(uid=key).scalar()
        return bool(count)

    def items(self):
        # for person in self.storage.session.query(Person).filter_by(state="active").all():
        for person in self.storage.session.query(Person).all():
            yield (person.uid, vars(person))
