from datetime import datetime
from pydantic import BaseModel, validator

from .host import Host, HostPublic
from .ticket import Ticket, TicketPublic, BaseTicket, UpdateTicket


class EventIdentity(BaseModel):
    id: int


class BaseEvent(BaseModel):
    name: str
    description: str
    location: str
    start: datetime
    end: datetime
    tickets: list[BaseTicket] | None = None

    @validator("end")
    def validate_end(cls, end: datetime, values: dict):
        if "start" in values and end < values["start"]:
            raise ValueError("End time must be after start time")
        return end

    @validator("name", pre=True, always=True)
    def validate_name(cls, name: str):
        if len(name) < 1:
            raise ValueError("Name should be at least 1 character long")
        if len(name) > 90:
            raise ValueError("Name should be at most 100 characters long")
        return name


class UpdateEvent(BaseEvent):
    id: int
    tickets: list[UpdateTicket] | None = None


class Event(BaseEvent, EventIdentity):
    # Relationships
    tickets: list[Ticket] | None = None
    host: Host

    # Authentication
    public_key: str | None = None
    private_key: str | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    # Additional
    image_url: str | None = None


# Public version of the Event model excluding sensitive and unnecessary fields
class EventPublic(BaseModel):
    id: int
    name: str
    description: str
    location: str
    start: datetime
    end: datetime
    host: HostPublic | None = None
    public_key: str | None = None
    tickets: list[TicketPublic] | None = None
    image_url: str | None = None

    @classmethod
    def from_event(cls, event: Event) -> "EventPublic":
        """
        Create an EventPublic instance from an Event model instance or dict.
        """
        tickets: list[TicketPublic] | None = (
            [
                TicketPublic.from_ticket(ticket)
                for ticket in event.tickets
                if ticket.visibility
            ]
            if event.tickets
            else None
        )
        return cls(
            id=event.id,
            name=event.name,
            description=event.description,
            location=event.location,
            start=event.start,
            end=event.end,
            tickets=tickets,
            host=(HostPublic.from_host(event.host) if event.host else None),
            public_key=event.public_key,
            image_url=event.image_url if event.image_url else None,
        )
