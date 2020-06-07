import sqlalchemy
from .types import *
from flask import g

class Storage:

    def __init__(self, conn = 'sqlite:///koseki.db'):
        self.engine = sqlalchemy.create_engine(conn, pool_recycle=600, pool_use_lifo=True, pool_pre_ping=True, pool_size=10, max_overflow=20, pool_timeout=3)
        Base.metadata.create_all(self.engine)
        self.sm = sqlalchemy.orm.sessionmaker(bind=self.engine)

    @property
    def session(self):
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
