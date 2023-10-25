"""Definitions of SQLAlchemy table-backed object mappings called entities."""


from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from entities.ticket_entity import TicketEntity
from entities.event_entity import EventEntity
from settings.base import Base
from typing import Type
from models.guest import Guest
from utils.encryption_service import EncryptionService

class GuestEntity(Base):
    __tablename__ = "guests"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    # Contact
    phone_number: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True)

    # Ticket
    quantity: Mapped[int] = mapped_column(Integer)
    used_quantity: Mapped[int] = mapped_column(Integer)
    scan_timestamp: Mapped[datetime] = mapped_column(DateTime)

    # Relationships
    event: Mapped["EventEntity"] = relationship("EventEntity")
    ticket: Mapped["TicketEntity"] = relationship("TicketEntity")

    # Authentication
    public_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: EncryptionService.generate_uuid(),
    )
    private_key: Mapped[str] = mapped_column(
        String, index=True, unique=True, default=lambda: EncryptionService.generate_code()
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Methods

    @classmethod
    def from_model(cls: Type['GuestEntity'], model: Guest) -> 'GuestEntity':
        """
        Convert a Guest (Pydantic Model) to a GuestEntity (DB Model).
        """
        return cls(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            phone_number=model.phone_number,
            email=model.email,
            quantity=model.quantity,
            used_quantity=model.used_quantity,
            scan_timestamp=model.scan_timestamp,
            event=model.event,
            ticket=model.ticket,
            public_key=model.public_key,
            private_key=model.private_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def to_model(self) -> Guest:
        """
        Convert a GuestEntity (DB Model) to a Guest (Pydantic Model).
        """
        return Guest(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            email=self.email,
            quantity=self.quantity,
            used_quantity=self.used_quantity,
            scan_timestamp=self.scan_timestamp,
            event=self.event.to_model(),
            ticket=self.ticket.to_model(),
            public_key=self.public_key,
            private_key=self.private_key,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
