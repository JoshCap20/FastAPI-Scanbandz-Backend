"""Definitions of SQLAlchemy table-backed object mappings called entities."""

from typing import Type
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .host_entity import HostEntity
from .ticket_entity import TicketEntity
from .base import Base
from ..models import Event, BaseEvent, EventPublic
from ..utils.encryption_service import EncryptionService


class EventEntity(Base):
    __tablename__ = "events"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime] = mapped_column(DateTime)
    
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    tickets: Mapped[list["TicketEntity"]] = relationship(
        "TicketEntity", back_populates="event"
    )
    guests: Mapped[list["GuestEntity"]] = relationship(
        "GuestEntity", back_populates="event"
    )

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("hosts.id"))
    host: Mapped["HostEntity"] = relationship("HostEntity")

    # Authentication
    public_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: EncryptionService.generate_uuid(),
    )
    private_key: Mapped[str] = mapped_column(
        String,
        index=True,
        unique=True,
        default=lambda: EncryptionService.generate_code(),
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    ticket_receipts: Mapped[list["TicketReceiptEntity"]] = relationship(
        "TicketReceiptEntity", back_populates="event"
    )

    # Methods
    @classmethod
    def from_base_model(
        cls: Type["EventEntity"], model: BaseEvent, host_id: int
    ) -> "EventEntity":
        """
        Convert a BaseEvent (Pydantic Model) to a EventEntity (DB Model).
        """
        return cls(
            name=model.name,
            description=model.description,
            location=model.location,
            start=model.start,
            end=model.end,
            host_id=host_id,
            tickets=(
                [TicketEntity.from_base_model(ticket) for ticket in model.tickets]
                if model.tickets
                else []
            ),
            guests=[],
            ticket_receipts=[],
        )

    @classmethod
    def from_model(cls: Type["EventEntity"], model: Event) -> "EventEntity":
        """
        Convert a Event (Pydantic Model) to a EventEntity (DB Model).
        """
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            location=model.location,
            start=model.start,
            end=model.end,
            tickets=(
                [TicketEntity.from_model(ticket) for ticket in model.tickets]
                if model.tickets
                else None
            ),
            host=HostEntity.from_model(model.host),
            public_key=model.public_key,
            private_key=model.private_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self) -> Event:
        """
        Convert a EventEntity (DB Model) to a Event (Pydantic Model).
        """
        return Event(
            id=self.id,
            name=self.name,
            description=self.description,
            location=self.location,
            start=self.start,
            end=self.end,
            tickets=(
                [ticket.to_model() for ticket in self.tickets] if self.tickets else None
            ),
            host=self.host.to_model(),
            public_key=self.public_key,
            private_key=self.private_key,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_public_model(self) -> EventPublic:
        """
        Convert a EventEntity (DB Model) to a EventPublic (Pydantic Model).
        """
        return EventPublic(
            id=self.id,
            name=self.name,
            description=self.description,
            location=self.location,
            start=self.start,
            end=self.end,
            host=self.host.to_public_model(),
            public_key=self.public_key,
        )
