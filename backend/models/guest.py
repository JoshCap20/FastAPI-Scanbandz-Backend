from pydantic import BaseModel, Field
from datetime import datetime

from models.event import Event
from models.ticket import Ticket

class Guest(BaseModel):
    # General
    id: int
    first_name: str
    last_name: str

    # Contact
    phone_number: str # TODO: Add phone number class
    email: str

    # Ticket
    quantity: int
    used_quantity: int
    scan_timestamp: datetime

    # Relationships
    event: Event
    ticket: Ticket

    # Authentication
    public_key: str
    private_key: str

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None