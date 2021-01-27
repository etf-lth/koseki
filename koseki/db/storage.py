from flask import g
from sqlalchemy.engine.base import Connection
from koseki.db.types import *
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.schema import MetaData


class Storage:
    def __init__(self, conn="sqlite:///koseki.db"):
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
        
        self.__migrate_person_table()

    @property
    def session(self) -> Session:
        try:
            return g.db
        except AttributeError:
            g.db = self.sm()
            return g.db

    def add(self, obj):
        self.session.add(obj)

    def delete(self, obj):
        self.session.delete(obj)

    def commit(self):
        self.session.commit()

    def query(self, obj) -> Query:
        return self.session.query(obj)

    def __migrate_person_table(self):
        with self.engine.connect() as con:
            con: Connection
            for column_name in [
                "address_line1",
                "address_line2",
                "city",
                "postcode",
                "region",
                "country",
                "phone_number",
            ]:
                con.execute(
                    """
                    IF NOT EXISTS( SELECT NULL
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE table_name = 'person'
                        AND table_schema = 'koseki'
                        AND column_name = '{columnname1}')  THEN
                            ALTER TABLE person ADD COLUMN {columnname2} varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL;
                    END IF;""".format(
                        columnname1=column_name,columnname2=column_name
                    )
                )

    def __insert_initial_values_group(self):
        self.add(Group("admin", "System Administrator"))
        self.add(Group("enroll", "Allow enrolling new members"))
        self.add(Group("accounter", "Allow registering fees"))
        self.add(Group("board", "Allow general browsing of members"))

