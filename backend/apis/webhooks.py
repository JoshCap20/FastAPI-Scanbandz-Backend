from fastapi import APIRouter, Depends, HTTPException, Request, status
from ..services import StripePaymentService

from ..settings.config import STRIPE_ENDPOINT_SECRET

api = APIRouter(prefix="/api/webhook")
openapi_tags = {
    "name": "Webhook",
    "description": "Handle webhooks.",
}


@api.post("/stripe-ticket-payments", tags=["Webhook"])
async def stripe_ticket_payments_webhook(
    request: Request, stripe_payment_service: StripePaymentService = Depends()
):
    """
    Handle Stripe webhooks for ticket payments.
    """
    payload: bytes = await request.body()
    sig_header: str | None = request.headers.get("Stripe-Signature")

    try:
        event = stripe_payment_service.handle_stripe_webhook_ticket_payment(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"received": True}
