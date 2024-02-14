from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class HostIdentity(BaseModel):
    id: int


class BaseHost(BaseModel):
    # General
    first_name: str
    last_name: str

    # Contact
    phone_number: str
    email: EmailStr

    # Authentication
    password: str

    @validator("password", pre=True, always=True)
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password should be at least 8 characters long")
        return password

    @validator("phone_number", pre=True, always=True)
    def validate_phone_number(cls, phone_number: str):
        if len(phone_number) != 10:
            # TODO: Add non-US phone number support
            raise ValueError("Phone number should be 10 characters long")

        if not phone_number.isdigit():
            raise ValueError("Phone number should only contain digits")

        return phone_number

    @validator("first_name", pre=True, always=True)
    def validate_first_name(cls, first_name: str):
        if len(first_name) < 1:
            raise ValueError("First name should be at least 1 character long")
        return first_name

    @validator("last_name", pre=True, always=True)
    def validate_last_name(cls, last_name: str):
        if len(last_name) < 1:
            raise ValueError("Last name should be at least 1 character long")
        return last_name


class Host(BaseHost, HostIdentity):
    # Stripe
    stripe_id: str | None = None

    # Metadata
    is_active: bool | None = None
    is_superuser: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# Public version of the Host model excluding sensitive and unnecessary fields
class HostPublic(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    stripe_id: str | None = None

    # Conditionally include fields
    def __init__(self, **data):
        include_stripe_id = data.pop("include_stripe_id", False)
        super().__init__(**data)
        if not include_stripe_id:
            self.stripe_id = None

    # Custom method to create an instance from a Host model
    @classmethod
    def from_host(cls, host: Host, include_stripe_id: bool = False) -> "HostPublic":
        return cls(
            id=host.id,
            first_name=host.first_name,
            last_name=host.last_name,
            email=host.email,
            stripe_id=host.stripe_id if include_stripe_id else None,
            include_stripe_id=include_stripe_id,  # Popped in init
        )
