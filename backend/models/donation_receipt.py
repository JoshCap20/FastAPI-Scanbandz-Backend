from pydantic import BaseModel, EmailStr, validator
from decimal import Decimal

class BaseDonationRequest(BaseModel):
    # General
    first_name: str
    last_name: str

    # Contact
    phone_number: str | None = None  # TODO: Add phone number class
    email: EmailStr | None = None
    
    donation_amount: Decimal