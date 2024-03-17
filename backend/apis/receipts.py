from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import Host, TicketReceipt
from ..services import HostService, ReceiptService
from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/receipts")
openapi_tags = {"name": "Receipts", "description": "Receipt management."}


@api.get("/tickets", tags=["Receipts"], response_model=list[TicketReceipt])
def get_host_ticket_receipts(
    current_user: Host = Depends(registered_user),
    receipt_service: ReceiptService = Depends(),
) -> list[TicketReceipt]:
    return receipt_service.get_receipts_by_host(current_user)

@api.get("/{id}", tags=["Receipts"], response_model=TicketReceipt)
def get_receipt_by_id(
    id: int,
    receipt_service: ReceiptService = Depends(),
    current_user: Host = Depends(registered_user),
) -> TicketReceipt:
    try:
        receipt: TicketReceipt = receipt_service.get_receipt_by_id(id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )
        
    if receipt.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Host does not have permission to view this receipt",
        )
        
    return receipt

### DEVELOPMENT ONLY ###
@api.get("/dev-all", response_model=list[TicketReceipt], tags=["Dev"])
@dev_only
def dev_all_receipts(receipt_service: ReceiptService = Depends()):
    receipts = receipt_service.dev_all()
    return [receipt.to_model() for receipt in receipts]
