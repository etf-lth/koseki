from datetime import datetime
from typing import Reversible

from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer, Unicode, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()


class PersonGroup(Base):
    __tablename__: str = "person_group"

    uid = Column(Integer, ForeignKey("person.uid"), primary_key=True)
    gid = Column(Integer, ForeignKey("group.gid"), primary_key=True)

    group = relationship("Group", backref="person_group")


class Group(Base):
    __tablename__: str = "group"

    gid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(32), unique=True)
    descr = Column(Unicode(64))


class Fee(Base):
    __tablename__: str = "fee"

    fid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid = Column(Integer, ForeignKey("person.uid"))
    registered_by = Column(Integer, ForeignKey("person.uid"))
    amount = Column(Integer, nullable=False)
    registered = Column(DateTime, default=datetime.now)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    method = Column(Enum("swish", "cash", "bankgiro",
                         "creditcard"), default="swish")


class Payment(Base):
    __tablename__: str = "payment"

    pid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid = Column(Integer, ForeignKey("person.uid"), nullable=False)
    registered_by = Column(Integer, ForeignKey("person.uid"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    registered = Column(DateTime, default=datetime.now)
    method = Column(
        Enum("swish", "cash", "bankgiro", "creditcard", "kiosk", "wordpress"),
        default="swish",
    )
    reason = Column(Unicode(length=255))


class Product(Base):
    __tablename__: str = "product"

    pid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(255))
    img_url = Column(Text())
    price = Column(DECIMAL(10, 2), nullable=False)
    order = Column(Integer, default=0, nullable=False)


class Person(Base):
    __tablename__: str = "person"

    uid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    state = Column(Enum("pending", "active", "expired"), default="pending")
    fname = Column(Unicode(64))
    lname = Column(Unicode(64))
    email = Column(Unicode(64))
    username = Column(Unicode(64))
    password = Column(Text())
    enrolled = Column(DateTime, default=datetime.now)
    enrolled_by = Column(Integer, ForeignKey("person.uid"))
    card_id = Column(Unicode(64))  # Plugin: Kiosk
    address_line1 = Column(Unicode(64))
    address_line2 = Column(Unicode(64))
    city = Column(Unicode(64))
    postcode = Column(Unicode(64))
    region = Column(Unicode(64))
    country = Column(Unicode(64))
    phone_number = Column(Unicode(64))

    groups: Reversible[PersonGroup] = relationship(
        "PersonGroup", backref="person")
    fees: Reversible[Fee] = relationship(
        "Fee", primaryjoin="Fee.uid==Person.uid", order_by="desc(Fee.fid)"
    )
    payments: Reversible[Payment] = relationship(
        "Payment", primaryjoin="Payment.uid==Person.uid", order_by="desc(Payment.pid)"
    )

    @property
    def balance(self) -> float:
        return sum([p.amount for p in self.payments])

    @property
    def unpaid_payments(self) -> list[Payment]:
        unpaids: list[Payment] = []
        remainder: float = 0
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
                        remainder += unpaid.amount  # Amount is negative
                        now_paids.append(unpaid)
                # Post-remove everything in batch in order to not mess up looping
                for paid in now_paids:
                    unpaids.remove(paid)
        return unpaids

    # Note: This is *not* a @property
    def reduce_empty_to_null(self) -> None:
        if self.username == "":
            self.username = None
        if self.address_line1 == "":
            self.address_line1 = None
        if self.address_line2 == "":
            self.address_line2 = None
        if self.city == "":
            self.city = None
        if self.postcode == "":
            self.postcode = None
        if self.region == "":
            self.region = None
        if self.country == "":
            self.country = None
        if self.phone_number == "":
            self.phone_number = None


class Metric(Base):
    __tablename__: str = "metric"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column(Unicode(length=255), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
