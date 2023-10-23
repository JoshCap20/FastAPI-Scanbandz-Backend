from pydantic import BaseModel
from datetime import datetime

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
    # event: Event TODO: Add event model
    # tickets: Ticket TODO: Add ticket model

    # Authentication
    public_key: str
    private_key: str

    # Metadata
    created_at: datetime
