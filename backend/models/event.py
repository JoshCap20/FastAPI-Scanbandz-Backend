from datetime import datetime
from typing import List
from pydantic import BaseModel, validator
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

    @validator("end")
    def validate_end(cls, end, values):
        if "start" in values and end < values["start"]:
            raise ValueError("End time must be after start time")
        return end
    
    @validator("name", pre=True, always=True)
    def validate_name(cls, name):
        if len(name) < 1:
            raise ValueError("Name should be at least 1 character long")
        if len(name) > 90:
            raise ValueError("Name should be at most 100 characters long")
        return name
