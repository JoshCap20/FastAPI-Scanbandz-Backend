from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from ..services import StripePaymentService, StripeRefundService, ReceiptService

from ..settings import STRIPE_ENDPOINT_SECRET, STRIPE_REFUND_ENDPOINT_SECRET

api = APIRouter(prefix="/api/webhook")
openapi_tags = {
    "name": "Webhook",
    "description": "Handle webhooks.",
}


async def process_payment_in_background(
    stripe_payment_service: StripePaymentService, payload: bytes, sig_header: str
):
    # Logic to process payment in the background
    stripe_payment_service.handle_stripe_webhook_ticket_payment(
        payload, sig_header, STRIPE_ENDPOINT_SECRET
    )
    
async def process_refund_in_background(
    stripe_refund_service: StripeRefundService, payload: bytes, sig_header: str
):
    # Logic to process refund in the background
    stripe_refund_service.handle_stripe_webhook_refund(payload, sig_header, STRIPE_REFUND_ENDPOINT_SECRET)

@api.post("/stripe-refunds", tags=["Webhook"])
async def stripe_refunds_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    stripe_refund_service: StripeRefundService = Depends(),
):
    """
    Handle Stripe webhooks for refunds.
    """
    payload: bytes = await request.body()
    sig_header: str | None = request.headers.get("Stripe-Signature")

    # Add the background task
    background_tasks.add_task(
        process_refund_in_background, stripe_refund_service, payload, sig_header
    )

    return {"received": True}

@api.post("/stripe-ticket-payments", tags=["Webhook"])
async def stripe_ticket_payments_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    stripe_payment_service: StripePaymentService = Depends(),
):
    """
    Handle Stripe webhooks for ticket payments.
    """
    payload: bytes = await request.body()
    sig_header: str | None = request.headers.get("Stripe-Signature")

    if not stripe_payment_service.is_valid_signature(
        payload, sig_header, STRIPE_ENDPOINT_SECRET
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature or payload",
        )

    # Add the background task
    background_tasks.add_task(
        process_payment_in_background, stripe_payment_service, payload, sig_header
    )

    return {"received": True}
