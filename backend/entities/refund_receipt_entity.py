"""
These entities represent refunds for purchased tickets.
"""

from decimal import Decimal
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Type

from .base import Base
from ..models import TicketReceipt, BaseTicketReceipt


class RefundReceiptEntity(Base):
    __tablename__ = "refund_receipts"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    ticket_receipt_id: Mapped[int] = mapped_column(Integer, ForeignKey("ticket_receipts.id"))
    ticket_receipt: Mapped["TicketReceiptEntity"] = relationship(
        "TicketReceiptEntity", back_populates="refund_receipts"
    )
    
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))