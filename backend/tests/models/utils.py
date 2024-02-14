from models.host import Host
from datetime import datetime

def create_host(id: int | None = None, first_name: str = "Test", last_name: str = "Host", phone_number: str = "1234567890", email: str = "test@gmail.com", password: str = "test1234567", stripe_id: str | None = None, is_active: bool | None = None, is_superuser: bool | None = None, created_at: datetime | None = None, updated_at: datetime | None = None):
    return Host(
        id=id,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        password=password,
        stripe_id=stripe_id,
        is_active=is_active,
        is_superuser=is_superuser,
        created_at=created_at,
        updated_at=updated_at
    )