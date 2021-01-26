from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    DECIMAL,
    Unicode,
    VARCHAR,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()


class PersonGroup(Base):
    __tablename__ = "person_group"

    uid = Column(Integer, ForeignKey("person.uid"), primary_key=True)
    gid = Column(Integer, ForeignKey("group.gid"), primary_key=True)

    group = relationship("Group", backref="person_group")


class Group(Base):
    __tablename__ = "group"

    gid = Column(Integer, primary_key=True)
    name = Column(Unicode(32))
    descr = Column(Unicode(64))


class Fee(Base):
    __tablename__ = "fee"

    fid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("person.uid"))
    registered_by = Column(Integer, ForeignKey("person.uid"))
    amount = Column(Integer)
    registered = Column(DateTime, default=datetime.now)
    start = Column(DateTime)
    end = Column(DateTime)
    method = Column(Enum("swish", "cash", "bankgiro", "creditcard"), default="swish")


class Payment(Base):
    __tablename__ = "payment"

    pid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("person.uid"))
    registered_by = Column(Integer, ForeignKey("person.uid"))
    amount = Column(DECIMAL(10,2))
    registered = Column(DateTime, default=datetime.now)
    method = Column(
        Enum("swish", "cash", "bankgiro", "creditcard", "kiosk", "wordpress"),
        default="swish",
    )
    reason = Column(VARCHAR(length=255))


class Product(Base):
    __tablename__ = "product"

    pid = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=255))
    img_url = Column(VARCHAR(length=510))
    price = Column(DECIMAL(10,2))
    order = Column(Integer)


class Person(Base):
    __tablename__ = "person"

    uid = Column(Integer, primary_key=True)
    state = Column(Enum("pending", "active", "expired"), default="pending")
    fname = Column(Unicode(64))
    lname = Column(Unicode(64))
    email = Column(Unicode(64))
    stil = Column(Unicode(64))
    password = Column(Unicode(64))
    card_id = Column(Unicode(64))
    enrolled = Column(DateTime, default=datetime.now)
    enrolled_by = Column(Integer, ForeignKey("person.uid"))

    groups = relationship("PersonGroup", backref="person")
    fees = relationship(
        "Fee", primaryjoin="Fee.uid==Person.uid", order_by="desc(Fee.fid)"
    )
    payments = relationship(
        "Payment", primaryjoin="Payment.uid==Person.uid", order_by="desc(Payment.pid)"
    )

    @property
    def balance(self):
        return sum([p.amount for p in self.payments])

    @property
    def unpaid_payments(self):
        unpaids = []
        remainder = 0
        # person.fees sorts in descending ID-order, therefore the list is reversed to be chronological
        for payment in reversed(self.payments):
            if payment.amount == 0:
                continue
            if payment.amount < 0:
                # Add unpaid entry to list
                unpaids.append(payment)
                continue
            if payment.amount > 0:
                remainder += payment.amount
                # Check how many unpaids can be removed with this payment
                now_paids = []
                for unpaid in unpaids:
                    # Check if member has any leftover cash to remove this unpaid too
                    if remainder > -unpaid.amount:
                        remainder += unpaid.amount # Amount is negative
                        now_paids.append(unpaid)
                # Post-remove everything in batch in order to not mess up looping
                for paid in now_paids:
                    unpaids.remove(paid)
        return unpaids
