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


### DEVELOPMENT ONLY ###
@api.get("/dev-all", response_model=list[TicketReceipt], tags=["Dev"])
@dev_only
def dev_all_receipts(receipt_service: ReceiptService = Depends()) -> JSONResponse:
    receipts = receipt_service.dev_all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=receipts,
    )
