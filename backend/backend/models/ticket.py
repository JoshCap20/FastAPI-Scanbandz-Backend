from decimal import Decimal
from pydantic import BaseModel, validator
from datetime import datetime

class Ticket(BaseModel):
    # General
    id: int | None = None
    name: str
    description: str | None = None
    price: Decimal

    # Settings
    max_quantity: int
    used_quantity: int
    visibility: bool
    registration_active: bool

    # Relationships
    event_id: int
    
    # Authentication
    public_key: str | None = None
    private_key: str | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator("price", pre=True, always=True)
    def validate_price(cls, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price






