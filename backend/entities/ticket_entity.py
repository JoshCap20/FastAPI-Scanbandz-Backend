from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Integer, String, DateTime, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Type

from .base import Base
from ..models import Ticket, BaseTicket, UpdateTicket, TicketPublic
from ..utils.encryption_service import EncryptionService


class TicketEntity(Base):
    __tablename__ = "tickets"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Settings
    max_quantity: Mapped[int] = mapped_column(
        Integer, nullable=True
    )  # Max ticket limit
    tickets_sold: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Number of tickets sold
    visibility: Mapped[bool] = mapped_column(Boolean)
    registration_active: Mapped[bool] = mapped_column(Boolean)

    # Relationships
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    event: Mapped["EventEntity"] = relationship("EventEntity", back_populates="tickets")
    guests: Mapped[list["GuestEntity"]] = relationship(
        "GuestEntity", back_populates="ticket"
    )

    ticket_receipts: Mapped[list["TicketReceiptEntity"]] = relationship(
        "TicketReceiptEntity", back_populates="ticket"
    )

    # Authentication
    public_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: EncryptionService.generate_uuid(),
    )
    private_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: EncryptionService.generate_code(),
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @classmethod
    def from_base_model(
        cls: Type["TicketEntity"], model: BaseTicket | UpdateTicket
    ) -> "TicketEntity":
        """
        Convert a BaseTicket (Pydantic Model) to a TicketEntity (DB Model).
        """
        return cls(
            name=model.name,
            description=model.description,
            price=model.price,
            max_quantity=model.max_quantity,
            visibility=model.visibility,
            registration_active=model.registration_active,
            event_id=model.event_id,
        )

    # Methods
    @classmethod
    def from_model(cls: Type["TicketEntity"], model: Ticket) -> "TicketEntity":
        """
        Convert a Ticket (Pydantic Model) to a TicketEntity (DB Model).
        """
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            max_quantity=model.max_quantity,
            visibility=model.visibility,
            registration_active=model.registration_active,
            event_id=model.event_id,
            public_key=model.public_key,
            private_key=model.private_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
            tickets_sold=model.tickets_sold,
        )

    def to_model(self) -> Ticket:
        """
        Convert a TicketEntity (DB Model) to a Ticket (Pydantic Model).
        """
        return Ticket(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            max_quantity=self.max_quantity,
            visibility=self.visibility,
            registration_active=self.registration_active,
            event_id=self.event_id,
            public_key=self.public_key,
            private_key=self.private_key,
            created_at=self.created_at,
            updated_at=self.updated_at,
            tickets_sold=self.tickets_sold,
        )

    def to_public_model(self) -> TicketPublic:
        return TicketPublic(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            max_quantity=self.max_quantity,
            visibility=self.visibility,
            registration_active=self.registration_active,
            event_id=self.event_id,
        )
