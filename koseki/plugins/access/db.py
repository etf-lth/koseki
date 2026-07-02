from sqlalchemy import Column, ForeignKey, Integer, Unicode, UniqueConstraint
from sqlalchemy.orm import relationship

from koseki.db.types import Base

class Accesskey(Base):
    __tablename__: str = "accesskey"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    key = Column(Unicode(), unique=True)
    descr = Column(Unicode())

    rules = relationship("AccessRule", back_populates="key", cascade="all, delete-orphan")

class AccessRuleGroup(Base):
    __tablename__: str = "access_rule_group"

    rule_id = Column(Integer, ForeignKey("access_rule.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey("group.gid", ondelete="CASCADE"), primary_key=True)

    rule = relationship("AccessRule", back_populates="rule_groups")

class AccessRule(Base):
    __tablename__: str = "access_rule"

    __table_args__ = (
        UniqueConstraint("kid", "endpoint", name="uq_accesskey_endpoint"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    kid = Column(Integer, ForeignKey("accesskey.id", ondelete="CASCADE"))

    key = relationship("Accesskey", back_populates="rules")
    rule_groups = relationship("AccessRuleGroup", back_populates="rule", cascade="all, delete-orphan")
    groups = relationship("Group", secondary="access_rule_group")

    endpoint = Column(Unicode())
    attribute = Column(Unicode())
    descr = Column(Unicode())
