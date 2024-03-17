from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import Host, TicketReceipt, BaseRefundRequest, RefundReceipt
from ..services import StripeRefundService, ReceiptService
from ..utils.dev_only import dev_only
from ..exceptions import ReceiptNotFoundException, HostPermissionError, StripeRefundException

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

@api.get("/refunds/{id}", tags=["Receipts", "Refunds"], response_model=list[RefundReceipt])
def get_refunds_by_receipt_id(
    id: int,
    receipt_service: ReceiptService = Depends(),
    current_user: Host = Depends(registered_user),
) -> list[RefundReceipt]:
    # TODO: Add security to this endpoint
    return receipt_service.get_refunds_by_receipt_id(id)

@api.post("/refund", tags=["Receipts", "Refunds", "Stripe"])
def refund_receipt(
    refund: BaseRefundRequest,
    current_user: Host = Depends(registered_user),
    refund_svc: StripeRefundService = Depends(),
) -> JSONResponse:
    try:
        refund_amount: str = refund_svc.create_refund_for_guest(
            host_id=current_user.id, receipt_id=refund.receipt_id, amount=refund.amount
        )
    except ReceiptNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )
    except HostPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Host does not have permission to refund this receipt",
        )
    except StripeRefundException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"amount": str(refund_amount)},
    )

### DEVELOPMENT ONLY ###
@api.get("/dev-all", response_model=list[TicketReceipt], tags=["Dev"])
@dev_only
def dev_all_receipts(receipt_service: ReceiptService = Depends()):
    receipts = receipt_service.dev_all()
    return [receipt.to_model() for receipt in receipts]
