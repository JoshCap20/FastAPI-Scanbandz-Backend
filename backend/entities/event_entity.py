"""Definitions of SQLAlchemy table-backed object mappings called entities."""

from calendar import c
from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from settings.base import Base
from typing import Type
from models.event import Event
from services.encryption_service import EncryptionService

class EventEntity(Base):
    __tablename__ = "events"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime] = mapped_column(DateTime)

    # Relationships
    # tickets: Ticket TODO: Add ticket model
    # host: Host TODO: Add host model

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
    def from_model(cls: Type['EventEntity'], model: Event) -> 'EventEntity':
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
            public_key=self.public_key,
            private_key=self.private_key,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )