from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from .ticket_receipt import TicketReceipt

class BaseRefundRequest(BaseModel):
    receipt_id: int
    amount: Decimal

class RefundReceipt(BaseModel):
    id: int
    ticket_receipt_id: int
    refund_amount: Decimal
    created_at: datetime