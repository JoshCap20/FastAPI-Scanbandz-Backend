from pydantic import BaseModel
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
    is_active: bool | None = None
    is_superuser: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
