from datetime import datetime
from pydantic import BaseModel, Field

class Event(BaseModel):
    # General
    id: int
    name: str
    description: str
    location: str # TODO: Add location class
    start: datetime 
    end: datetime

    # Relationships
    # tickets: Ticket TODO: Add ticket model
    # host: Host TODO: Add host model

    # Authentication
    public_key: str
    private_key: str

    # Metadata
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)