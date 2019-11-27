from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'

    uid = Column(Integer, primary_key = True)
    state = Column(Enum('pending','active','expired'), default='pending')
    fname = Column(Unicode(64))
    lname = Column(Unicode(64))
    email = Column(Unicode(64))
    stil = Column(Unicode(64))
    password = Column(Unicode(64))
    enrolled = Column(DateTime, default=datetime.now)
    lchange = Column(DateTime, default=datetime.now)
    enrolled_by = Column(Integer, ForeignKey('person.uid'))

    groups = relationship('PersonGroup', backref='person')
    fees = relationship('Fee', primaryjoin="Fee.uid==Person.uid")

    #def __init__(self, uid, fname, lname, email):
    #    self.uid = uid
    #    self.fname = fname
    #    self.lname = lname
    #    self.email = email

class PersonGroup(Base):
    __tablename__ = 'person_group'

    uid = Column(Integer, ForeignKey('person.uid'), primary_key = True)
    gid = Column(Integer, ForeignKey('group.gid'), primary_key = True)

    group = relationship('Group', backref='person_group')

class Group(Base):
    __tablename__ = 'group'

    gid = Column(Integer, primary_key = True)
    name = Column(Unicode(32))
    descr = Column(Unicode(64))

class Fee(Base):
    __tablename__ = 'fee'

    fid = Column(Integer, primary_key = True)
    uid = Column(Integer, ForeignKey('person.uid'))
    registered_by = Column(Integer, ForeignKey('person.uid'))
    amount = Column(Integer)
    registered = Column(DateTime, default=datetime.now)
    start = Column(DateTime)
    end = Column(DateTime)
    method = Column(Enum('swish','cash','bankgiro','creditcard'), default='swish')
