from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Type

from .base import Base
from ..models import Host, BaseHost


class HostEntity(Base):
    __tablename__ = "hosts"

    # General
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    # Contact
    phone_number: Mapped[str] = mapped_column(String, index=True, unique=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)

    # Authentication
    password: Mapped[str] = mapped_column(String)
    stripe_id: Mapped[str] = mapped_column(String, nullable=True)

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    events: Mapped[list["EventEntity"]] = relationship(
        "EventEntity", back_populates="host"
    )

    @classmethod
    def from_base_model(cls: Type["HostEntity"], model: BaseHost) -> "HostEntity":
        """
        Convert a BaseHost (Pydantic Model) to a HostEntity (DB Model).
        """
        return cls(
            first_name=model.first_name,
            last_name=model.last_name,
            phone_number=model.phone_number,
            email=model.email,
            password=model.password,
            stripe_id=None,
            is_active=False,
            is_superuser=False,
        )

    @classmethod
    def from_model(cls: Type["HostEntity"], model: Host) -> "HostEntity":
        """
        Convert a Host (Pydantic Model) to a HostEntity (DB Model).
        """
        return cls(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            phone_number=model.phone_number,
            email=model.email,
            password=model.password,
            stripe_id=model.stripe_id,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self) -> Host:
        """
        Convert a HostEntity (DB Model) to a Host (Pydantic Model).
        """
        return Host(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            email=self.email,
            password=self.password,
            stripe_id=self.stripe_id,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
