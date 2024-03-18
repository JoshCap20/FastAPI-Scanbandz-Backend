"""
Represents a ticket purchase receipt by a guest for a host's event ticket.
"""

from decimal import Decimal
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Type

from .base import Base
from ..models import TicketReceipt, BaseTicketReceipt
from .refund_receipt_entity import RefundReceiptEntity


class DonationReceiptEntity(Base):
    __tablename__ = "donation_receipts"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    
    
    # Purchase Event Details
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    event: Mapped["EventEntity"] = relationship("EventEntity")

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("hosts.id"))
    host: Mapped["HostEntity"] = relationship("HostEntity")

    # Purchase Financial Details
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Stripe Details
    stripe_account_id: Mapped[str] = mapped_column(String)
    stripe_transaction_id: Mapped[str] = mapped_column(String) # Use Stripe payment_intent ID

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )