from datetime import datetime
from typing import List
from pydantic import BaseModel
from models.host import Host

from models.ticket import Ticket

class Event(BaseModel):
    # General
    id: int
    name: str
    description: str
    location: str # TODO: Add location class
    start: datetime 
    end: datetime

    # Relationships
    tickets: List[Ticket]
    host: Host

    # Authentication
    public_key: str
    private_key: str

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None