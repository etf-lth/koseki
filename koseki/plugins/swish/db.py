from datetime import datetime
from typing import Reversible

from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer, Unicode, Text

from db.types import Base

# Plugin: Swish
class SwishPaymentRequest(Base):
    __tablename__: str = "swish_payment_request"

    uuid = Column(Unicode(length=32), primary_key=True, nullable=False)
    payer = Column(Integer, ForeignKey("person.uid"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)    
    initalized = Column(DateTime, default=datetime.now)