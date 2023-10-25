from datetime import datetime
from typing import List
from pydantic import BaseModel
from models.host import Host

from models.ticket import Ticket

class Event(BaseModel):
    # General
    id: int | None = None
    name: str
    description: str
    location: str # TODO: Add location class
    start: datetime 
    end: datetime

    # Relationships
    tickets: List[Ticket] | None = None
    host: Host | None = None

    # Authentication
    public_key: str | None = None
    private_key: str | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None

