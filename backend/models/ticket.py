from decimal import Decimal
from typing import Union
from pydantic import BaseModel, validator
from datetime import datetime


class TicketIdentity(BaseModel):
    id: int


class BaseTicket(BaseModel):
    # General
    name: str
    description: str | None = None
    price: Decimal

    # Settings
    max_quantity: int | None = None
    visibility: bool  # Publicly visible (i.e. General Admission, not VIP)
    registration_active: bool  # Can be purchased

    # Relationships
    event_id: int


class UpdateTicket(BaseTicket):
    id: int


class Ticket(BaseTicket, TicketIdentity):
    # Authentication
    public_key: str | None = None
    private_key: str | None = None

    # Metadata
    tickets_sold: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator("price", pre=True, always=True)
    def validate_price(cls, price: Decimal) -> Decimal:
        price: Decimal = Decimal(price)
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price


# Public version of the Ticket model excluding sensitive and unnecessary fields
class TicketPublic(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    registration_active: bool
    event_id: int
    sold_out: bool = False

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> "TicketPublic":
        """
        Create a TicketPublic instance from a Ticket model instance or dict.
        """
        sold_out = (
            ticket.max_quantity is not None
            and ticket.tickets_sold >= ticket.max_quantity
        )
        return cls(
            id=ticket.id,
            name=ticket.name,
            description=ticket.description,
            price=ticket.price,
            registration_active=ticket.registration_active,
            event_id=ticket.event_id,
            sold_out=sold_out,
        )
