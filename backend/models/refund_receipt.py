from pydantic import BaseModel
from decimal import Decimal

class BaseRefundRequest(BaseModel):
    receipt_id: int
    amount: Decimal
