from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from .event import Event
from .ticket import Ticket

class GuestIdentity(BaseModel):
    id: int

class BaseGuest(BaseModel):
    # General
    first_name: str
    last_name: str

    # Contact
    phone_number: str | None = None# TODO: Add phone number class
    email: EmailStr | None = None

    # Ticket
    quantity: int = 1
    used_quantity: int = 0
    scan_timestamp: datetime | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator("phone_number", pre=True, always=True)
    def validate_phone_number(cls, phone_number):
        if len(phone_number) != 10:
            # TODO: Add non-US phone number support
            raise ValueError("Phone number should be 10 characters long")
        return phone_number
    
    @validator("first_name", pre=True, always=True)
    def validate_first_name(cls, first_name):
        if len(first_name) < 1:
            raise ValueError("First name should be at least 1 character long")
        return first_name
    
    @validator("last_name", pre=True, always=True)
    def validate_last_name(cls, last_name):
        if len(last_name) < 1:
            raise ValueError("Last name should be at least 1 character long")
        return last_name

class Guest(BaseGuest):
    # Relationships
    event: Event
    ticket: Ticket

    # Authentication
    public_key: str
    private_key: str

