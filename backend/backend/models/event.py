from datetime import datetime
from typing import List
from pydantic import BaseModel, validator

from .host import Host
from .ticket import Ticket

class EventIdentity(BaseModel):
    id: int

class BaseEvent(BaseModel):
    name: str
    description: str
    location: str
    start: datetime
    end: datetime

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

class Event(BaseEvent, EventIdentity):
    # Relationships
    tickets: List[Ticket] | None = None
    host_id: int | None = None
    host: Host | None = None

    # Authentication
    public_key: str | None = None
    private_key: str | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None