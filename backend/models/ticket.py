from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class Ticket(BaseModel):
    # General
    id: int
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
    public_key: str
    private_key: str

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None






