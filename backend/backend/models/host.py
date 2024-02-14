from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

class Host(BaseModel):
    # General
    id: int | None = None
    first_name: str
    last_name: str

    # Contact
    phone_number: str
    email: EmailStr

    # Authentication
    password: str
    stripe_id: str | None = None

    # Metadata
    is_active: bool | None = None
    is_superuser: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator("password", pre=True, always=True)
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password should be at least 8 characters long")
        return password
    
    @validator("phone_number", pre=True, always=True)
    def validate_phone_number(cls, phone_number):
        if len(phone_number) != 10:
            # TODO: Add non-US phone number support
            raise ValueError("Phone number should be 10 characters long")
        
        if not phone_number.isdigit():
            raise ValueError("Phone number should only contain digits")
        
        return phone_number
    
    @validator("first_name", pre=True, always=True)
    def validate_first_name(cls, first_name):
        if len(first_name) < 1:
            raise ValueError("First name should be at least 1 character long")
        return first_name
    
    @validator("last_name", pre=True, always=True)
    def validate_last_name(cls, last_name):
        if len(last_name) < 1:
            raise ValueError("Last name should be at least 1 character long")
        return last_name
