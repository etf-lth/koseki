from typing import Optional, Type

from koseki.db.types import *
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.schema import MetaData


class Storage:
    def __init__(self, conn: str = "sqlite:///koseki.db") -> None:
        self.engine: Engine = create_engine(
            conn,
            pool_recycle=600,
            pool_use_lifo=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=3,
        )

        m: MetaData = Base.metadata
        m.create_all(bind=self.engine)
        self.sm = sessionmaker(bind=self.engine)
        self.db: Optional[Session] = None

        self.__insert_initial_values()

    def close(self, error: Optional[Exception]) -> None:
        if self.db is not None:
            self.db.close()
            self.db = None

    @property
    def session(self) -> Session:
        if self.db is None:
            self.db = self.sm()
        return self.db

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
