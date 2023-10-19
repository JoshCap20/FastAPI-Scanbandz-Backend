from pydantic import BaseModel

class Guest(BaseModel):
    # General
    id: int
    first_name: str
    last_name: str

    # Ticket
    quantity: int
    used_quantity: int
    scan_timestamp: str

    # Authentication
    public_key: str
    private_key: str
