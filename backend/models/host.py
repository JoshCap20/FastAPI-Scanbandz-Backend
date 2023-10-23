from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime

class Host(BaseModel):
    # General
    id: int
    first_name: str
    last_name: str

    # Contact
    phone_number: str
    email: str

    # Authentication
    password: str
    stripe_id: str | None = None

    # Metadata
    is_active: bool | None = True
    is_superuser: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
