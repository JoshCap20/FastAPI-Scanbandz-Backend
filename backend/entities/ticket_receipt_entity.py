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


class TicketReceiptEntity(Base):
    __tablename__ = "ticket_receipts"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    guest_id: Mapped[int] = mapped_column(Integer, ForeignKey("guests.id"))
    guest: Mapped["GuestEntity"] = relationship(
        "GuestEntity", back_populates="ticket_receipts"
    )

    # Purchase Event Details
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    event: Mapped["EventEntity"] = relationship(
        "EventEntity", back_populates="ticket_receipts"
    )

    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"))
    ticket: Mapped["TicketEntity"] = relationship(
        "TicketEntity", back_populates="ticket_receipts"
    )

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("hosts.id"))
    host: Mapped["HostEntity"] = relationship(
        "HostEntity", back_populates="ticket_receipts"
    )

    # Purchase Financial Details
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Stripe Details
    stripe_account_id: Mapped[str] = mapped_column(String)
    stripe_transaction_id: Mapped[str] = mapped_column(String) # Use Stripe payment_intent ID

    # Associated Refunds
    refund_receipts: Mapped[list["RefundReceiptEntity"]] = relationship(
        "RefundReceiptEntity", back_populates="ticket_receipt"
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @classmethod
    def from_model(
        cls: Type["TicketReceiptEntity"], model: BaseTicketReceipt
    ) -> "TicketReceiptEntity":
        return cls(
            guest_id=model.guest_id,
            event_id=model.event_id,
            ticket_id=model.ticket_id,
            host_id=model.host_id,
            quantity=model.quantity,
            unit_price=model.unit_price,
            total_price=model.total_price,
            total_fee=model.total_fee,
            total_paid=model.total_paid,
            stripe_account_id=model.stripe_account_id,
            stripe_transaction_id=model.stripe_transaction_id,
        )

    def to_model(self) -> TicketReceipt:
        return TicketReceipt(
            id=self.id,
            guest_id=self.guest_id,
            event_id=self.event_id,
            ticket_id=self.ticket_id,
            guest=self.guest.to_base_model(),
            event=self.event.to_public_model(),
            ticket=self.ticket.to_public_model(),
            host=self.host.to_public_model(),
            host_id=self.host_id,
            quantity=self.quantity,
            unit_price=self.unit_price,
            total_price=self.total_price,
            total_fee=self.total_fee,
            total_paid=self.total_paid,
            stripe_account_id=self.stripe_account_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            stripe_transaction_id=self.stripe_transaction_id,
        )
