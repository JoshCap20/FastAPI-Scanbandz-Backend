"""
Model for ticket_receipt table that represents a ticket purchase receipt.
"""

from decimal import Decimal
from pydantic import BaseModel, validator
from datetime import datetime
from .guest import BaseGuest
from .event import EventPublic
from .ticket import TicketPublic
from .host import HostPublic


class BaseTicketReceipt(BaseModel):
    guest_id: int
    event_id: int
    ticket_id: int
    host_id: int

    quantity: int
    unit_price: Decimal
    total_price: Decimal # what host gets
    total_fee: Decimal # added fee on top
    total_paid: Decimal # total_price + total_fee

    stripe_account_id: str


class TicketReceipt(BaseTicketReceipt):
    id: int
    guest: BaseGuest
    event: EventPublic
    ticket: TicketPublic
    host: HostPublic
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator("quantity")
    def quantity_must_be_positive(cls, v: int):
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @validator("total_price")
    def total_price_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("total_price must be positive")
        return v

    @validator("total_fee")
    def total_fee_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("total_fee must be positive")
        return v

    @validator("total_paid")
    def total_paid_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("total_paid must be positive")
        return v

    @validator("unit_price")
    def unit_price_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("unit_price must be positive")
        return v

    @validator("stripe_account_id")
    def stripe_account_id_must_not_be_empty(cls, v: str):
        if len(v) == 0:
            raise ValueError("stripe_account_id must not be empty")
        return v
