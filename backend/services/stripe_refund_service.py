"""
Stripe payment service for creating checkout sessions.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
import stripe
from decimal import Decimal

from ..settings.config import STRIPE_SECRET_KEY
from .ticket_service import TicketService
from .guest_service import GuestService
from .receipt_service import ReceiptService
from ..exceptions import (
    StripeRefundException,
    ReceiptNotFoundException,
    HostPermissionError,
)


class StripeRefundService:
    _session: Session
    ticket_svc: TicketService
    guest_svc: GuestService
    receipt_svc: ReceiptService

    def __init__(
        self,
        receipt_svc: ReceiptService = Depends(ReceiptService),
    ):
        stripe.api_key = STRIPE_SECRET_KEY
        self.receipt_svc = receipt_svc
        
    def create_refund_for_guest(self, host_id: int, receipt_id: int, amount: Decimal) -> int:
        """
        Creates a refund for a guest and updates the guest entity with the refund ID.

        Args:
            guest_id (int): The ID of the guest to create a refund for.
            amount (Decimal): The amount to refund.

        Returns:
            int: The amount refunded in cents.

        Raises:
            StripeRefundException: If there is an error creating the refund, or if the refund amount is invalid.
            ReceiptNotFoundException: If no receipt is found with the specified ID.
            HostPermissionError: If the host does not have permission to refund the receipt.
        """
        try:
            receipt = self.receipt_svc.get_receipt_by_id(receipt_id)
        except ReceiptNotFoundException:
            raise ReceiptNotFoundException("Receipt not found")
        
        if host_id != receipt.host_id:
            raise HostPermissionError("Host does not have permission to refund this receipt")
        if amount > receipt.total_paid:
            raise StripeRefundException("Refund amount exceeds the total paid amount")
        if amount <= 0:
            raise StripeRefundException("Refund amount must be greater than 0")
        
        refund_amount = StripeRefundService._convert_to_cents(amount)
                
        try:
            refund = stripe.Refund.create(
                payment_intent=receipt.stripe_transaction_id,
                amount=refund_amount,
                reverse_transfer=True,
                metadata={"receipt_id": str(receipt.id)},
            )
        except stripe.StripeError as e:
            StripeRefundException(f"Error creating refund: {e}")
            
        return refund_amount
    
    @staticmethod
    def _convert_to_cents(amount: Decimal) -> int:
        """
        Convert the given amount from dollars to cents.

        Args:
            amount (Decimal): The amount to convert.

        Returns:
            int: The amount in cents.
        """
        return int(amount * 100)
    
    @staticmethod
    def _convert_to_dollars(amount: int) -> Decimal:
        """
        Convert the given amount from cents to dollars.

        Args:
            amount (int): The amount to convert.

        Returns:
            Decimal: The amount in dollars.
        """
        return Decimal(amount) / 100
    
    def handle_stripe_webhook_refund(
        self, payload: bytes, sig_header: str, stripe_endpoint_secret: str
    ) -> None:
        """
        Handles a Stripe webhook event for a refund.

        Args:
            payload (bytes): The payload of the webhook event.
            sig_header (str): The signature header of the webhook event.
            stripe_endpoint_secret (str): The secret key for the Stripe endpoint.

        Raises:
            StripeRefundException: If there is an error handling the webhook event.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_endpoint_secret
            )
        except ValueError as e:
            raise StripeRefundException(f"Error decoding webhook event: {e}")
        except stripe.SignatureVerificationError as e:
            raise StripeRefundException(f"Error verifying webhook signature: {e}")
        
        if event["type"] == "charge.refunded":
            refund = event["data"]["object"]["refunds"]["data"][0] # Get most recent refund
            receipt_id = refund["metadata"]["receipt_id"]
            amount_in_cents = refund["amount"]
            amount = StripeRefundService._convert_to_dollars(amount_in_cents)
            self.receipt_svc.create_refund_receipt(receipt_id, amount)
        else:
            raise StripeRefundException(f"Unhandled event type: {event['type']}")
        
