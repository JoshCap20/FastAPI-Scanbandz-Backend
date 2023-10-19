"""Definitions of SQLAlchemy table-backed object mappings called entities."""


from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from settings.base import Base
from typing import Self
from models.guest import Guest
from services.encryption_service import EncryptionService

class GuestEntity(Base):
    __tablename__ = "guests"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, index=True)
    last_name: Mapped[str] = mapped_column(String, index=True)

    # Ticket
    quantity: Mapped[int] = mapped_column(Integer, index=True)
    used_quantity: Mapped[int] = mapped_column(Integer, index=True)
    scan_timestamp: Mapped[str] = mapped_column(String, index=True)

    # Authentication
    public_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: EncryptionService.generate_uuid(),
    )
    private_key: Mapped[str] = mapped_column(
        String, index=True, default=lambda: EncryptionService.generate_code()
    )

    # Methods

    @classmethod
    def from_model(cls, model: Guest) -> Self:
        """
        Convert a Guest (Pydantic Model) to a GuestEntity (DB Model).
        """
        return cls(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            quantity=model.quantity,
            used_quantity=model.used_quantity,
            scan_timestamp=model.scan_timestamp,
            public_key=model.public_key,
            private_key=model.private_key,
        )
    
    def to_model(self) -> Guest:
        """
        Convert a GuestEntity (DB Model) to a Guest (Pydantic Model).
        """
        return Guest(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            quantity=self.quantity,
            used_quantity=self.used_quantity,
            scan_timestamp=self.scan_timestamp,
            public_key=self.public_key,
            private_key=self.private_key,
        )
