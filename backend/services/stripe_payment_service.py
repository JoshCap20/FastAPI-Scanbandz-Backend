"""
Stripe payment service for creating checkout sessions.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
import stripe
from decimal import Decimal

from ..database import db_session
from ..settings.config import STRIPE_SECRET_KEY
from ..models import Ticket, Host, Event, BaseGuest, Guest, BaseTicketReceipt, BaseDonationRequest
from .ticket_service import TicketService
from .guest_service import GuestService
from .receipt_service import ReceiptService
from ..exceptions import (
    StripeCheckoutSessionException,
    HostStripeAccountNotFoundException,
    EventNotFoundException
)
from ..entities import DonationReceiptEntity, EventEntity


class StripePaymentService:
    _session: Session
    ticket_svc: TicketService
    guest_svc: GuestService
    receipt_svc: ReceiptService

    def __init__(
        self,
        session: Session = Depends(db_session),
        ticket_svc: TicketService = Depends(TicketService),
        guest_svc: GuestService = Depends(GuestService),
        receipt_svc: ReceiptService = Depends(ReceiptService),
    ):
        stripe.api_key = STRIPE_SECRET_KEY
        self._session = session
        self.ticket_svc = ticket_svc
        self.guest_svc = guest_svc
        self.receipt_svc = receipt_svc
        
    def create_donation_session(
        self, donation_request: BaseDonationRequest, event_id: int
    ) -> str:
        
        event = self._session.query(EventEntity).filter(EventEntity.id == event_id).first()
        
        if event is None:
            raise EventNotFoundException()
        
        host = event.host
        
        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()
        
        # TODO: Make the success and cancel urls method work for both this and checkout
        SUCCESS_URL: str = f"https://v2.scanbandz.com/payments/success?donation=true"
        CANCEL_URL: str = f"https://v2.scanbandz.com/payments/failure?donation=true"
        
        return self._get_stripe_donation(
            donation_amount=donation_request.donation_amount,
            event=event,
            host_stripe_id=host.stripe_id,
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            metadata={
                "guest_first_name": donation_request.first_name,
                "guest_last_name": donation_request.last_name,
                "guest_email": donation_request.email,
                "guest_phone_number": donation_request.phone_number,
                "event_id": event.id,
                "host_id": host.id,
                "host_stripe_id": host.stripe_id,
                "type": "donation"
            },
        )

        

    # TODO: Convert metadata to a model for validation
    def create_checkout_session(
        self, guest: BaseGuest, ticket: Ticket, event: Event
    ) -> str:
        """
        Creates a checkout session for purchasing tickets.

        Args:
            ticket_id (int): The ID of the ticket to be purchased.
            quantity (int): The quantity of tickets to be purchased.
            metadata (dict, optional): Additional metadata for the checkout session. Defaults to {}.

        Returns:
            str: The created checkout session url.

        Raises:
            TicketNotFoundException: If the ticket with the given ID does not exist.
            TicketRegistrationClosedException: If the ticket registration is closed.
            HostStripeAccountNotFoundException: If the host does not have a Stripe account.
            StripeCheckoutSessionException: If there is an error creating the checkout session.
        """
        host: Host = event.host

        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()

        SUCCESS_URL: str = self._get_success_link(event, ticket, guest.quantity)
        CANCEL_URL: str = self._get_cancel_link(event)

        return self._get_stripe_checkout(
            ticket=ticket,
            event=event,
            host_stripe_id=host.stripe_id,
            quantity=guest.quantity,
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            metadata={
                "guest_first_name": guest.first_name,
                "guest_last_name": guest.last_name,
                "guest_email": guest.email,
                "guest_phone_number": guest.phone_number,
                "event_id": event.id,
                "ticket_id": ticket.id,
                "quantity": guest.quantity,
                "host_id": host.id,
                "host_stripe_id": host.stripe_id,
                "unit_price": ticket.price,
                "type": "ticket"
            },
        )

    def _get_success_link(self, event: Event, ticket: Ticket, quantity: int) -> str:
        """
        Get the success link for the checkout session.

        Args:
            event (Event): The event object.
            ticket (Ticket): The ticket object.
            quantity (int): The quantity of tickets.

        Returns:
            str: The success link for the checkout session.
        """
        return f"https://v2.scanbandz.com/payments/success?event={event.public_key}"

    def _get_cancel_link(self, event: Event) -> str:
        """
        Get the cancel link for the checkout session.

        Args:
            event (Event): The event object.

        Returns:
            str: The cancel link for the checkout session.
        """
        return f"https://v2.scanbandz.com/payments/failure?event={event.public_key}"

    def _get_stripe_checkout(
        self,
        ticket: Ticket,
        event: Event,
        host_stripe_id: str,
        quantity: int,
        success_url: str,
        cancel_url: str,
        metadata: dict,
    ) -> str:
        """
        Creates a Stripe checkout session for a given ticket and event.

        Args:
            ticket (Ticket): The ticket object.
            event (Event): The event object.
            host_stripe_id (str): The Stripe account ID of the event host.
            quantity (int): The quantity of tickets to purchase.
            success_url (str): The URL to redirect to after successful payment.
            cancel_url (str): The URL to redirect to if payment is canceled.
            metadata (dict): Additional metadata to include in the checkout session.

        Returns:
            str: The created Stripe checkout session url.

        Raises:
            StripeCheckoutSessionException: If there is an error creating the checkout session.
        """
        price: int = self._convert_to_cents(ticket.price)
        fee: int = self._get_ticket_fee(ticket, quantity)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": event.name,
                                "description": ticket.name,
                            },
                            "unit_amount": price,
                        },
                        "quantity": quantity,
                    },
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Taxes & Fees",
                            },
                            "unit_amount": fee,
                        },
                        "quantity": quantity,
                    },
                ],
                mode="payment",
                metadata=metadata,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_intent_data={
                    "statement_descriptor": "Scanbz Event Ticket",
                    "transfer_data": {
                        "destination": host_stripe_id,
                        "amount": price * quantity,
                    },
                },
            )
            return checkout_session.url
        except stripe.StripeError as e:
            raise StripeCheckoutSessionException(str(e))
        
    def _get_stripe_donation(
        self,
        donation_amount: Decimal,
        event: Event,
        host_stripe_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict,
    ) -> str:
        
        price: int = self._convert_to_cents(donation_amount)
        fee: int = self._get_donation_fee(donation_amount)
        
        metadata["fee"] = fee
        
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": event.name,
                                "description": "Donation",
                            },
                            "unit_amount": price,
                        },
                        "quantity": 1,
                    },
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Taxes & Fees",
                            },
                            "unit_amount": fee,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                metadata=metadata,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_intent_data={
                    "statement_descriptor": "Scanbz Event Ticket",
                    "transfer_data": {
                        "destination": host_stripe_id,
                        "amount": price,
                    },
                },
            )
            return checkout_session.url
        except stripe.StripeError as e:
            raise StripeCheckoutSessionException(str(e))
        

    def _get_ticket_fee(self, ticket: Ticket, quantity: int) -> int:
        """
        Get the fee in cents for the given ticket and quantity.

        Args:
            ticket (Ticket): The ticket object.
            quantity (int): The quantity of tickets.

        Returns:
            int: The fee in cents.
        """
        fee: int = self._convert_to_cents(ticket.price * quantity * Decimal(0.05))
        if fee < 150:
            return 150
        return fee
    
    def _get_donation_fee(self, amount: Decimal) -> int:
        """
        Get the fee in cents for the donation.

        Args:
            amount (Decimal): The amount of the donation.

        Returns:
            int: The fee in cents.
        """
        # Fee is 3.1% plus 40 cents
        PERCENTAGE_FEE: Decimal = Decimal(0.031)
        FIXED_FEE: Decimal = Decimal(0.40)
        
        return self._convert_to_cents(amount * PERCENTAGE_FEE + FIXED_FEE)

    def _convert_to_cents(self, amount: Decimal) -> int:
        """
        Convert the given amount from dollars to cents.

        Args:
            amount (Decimal): The amount to convert.

        Returns:
            int: The amount in cents.
        """
        amount = Decimal(amount)
        return int(amount * 100)

    def _convert_to_dollars(self, amount: int) -> Decimal:
        """
        Convert the given amount from cents to dollars.

        Args:
            amount (int): The amount to convert.

        Returns:
            Decimal: The amount in dollars.
        """
        amount = int(amount)
        return Decimal(amount) / 100

    def is_valid_signature(
        self, payload: bytes, sig_header: str, stripe_endpoint_secret: str
    ) -> bool:
        """
        Verify the signature of a Stripe webhook request.

        Args:
            payload: The raw payload from the request body.
            sig_header: Stripe signature header from the request.
            stripe_endpoint_secret: The secret used for verifying webhook signature.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        try:
            stripe.Webhook.construct_event(payload, sig_header, stripe_endpoint_secret)
            return True
        except ValueError:
            # Invalid payload
            return False
        except stripe.SignatureVerificationError:
            # Invalid signature
            return False

    def handle_stripe_webhook_ticket_payment(
        self, payload: bytes, sig_header: str, stripe_endpoint_secret: str
    ) -> None:
        """
        Handle the Stripe webhook for ticket payments.

        Args:
            payload: The raw payload from the request body.
            sig_header: Stripe signature header from the request.
            stripe_endpoint_secret: The secret used for verifying webhook signature.

        Raises:
            ValueError: If the payload or signature are invalid.
            stripe.SignatureVerificationError: If the signature is invalid.
        """
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_endpoint_secret
        )
        # BELOW CODE IS FOR TESTING ONLY
        # try:
        #     event = json.loads(payload.decode("utf-8"))
        # except ValueError as e:
        #     print("Invalid payload")
        #     print(e)
        #     raise ValueError("Invalid payload")

        # Successfully constructed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            
            if session["metadata"]["type"] == "donation":
                return self._fulfill_donation(session)
            else:
                return self._fulfill_ticket_purchase(session)

        return None
    
    def _fulfill_donation(self, session: dict) -> None:
        # Create a DonationReceiptEntity
        metadata: dict = session["metadata"]
        total_price: Decimal = self._convert_to_dollars(session["amount_total"])
        fee: Decimal = self._convert_to_dollars(metadata["fee"])
        
        donation_receipt_entity = DonationReceiptEntity(
            first_name=metadata["guest_first_name"],
            last_name=metadata["guest_last_name"],
            email=metadata["guest_email"],
            phone=metadata["guest_phone_number"],
            event_id=metadata["event_id"],
            host_id=metadata["host_id"],
            total_price=total_price - fee,
            total_fee=fee,
            total_paid=total_price,
            stripe_account_id=metadata["host_stripe_id"],
            stripe_transaction_id=session["payment_intent"]
        )
        
        try:
            self._session.add(donation_receipt_entity)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e
        
        self.receipt_svc.send_donation_receipt(donation_receipt_entity)
        

    def _fulfill_ticket_purchase(self, session: dict) -> None:
        """
        Fulfill the purchase based on the checkout session.

        Args:
            session: The checkout session object from the Stripe event.
        """
        metadata: dict = session["metadata"]

        base_guest: BaseGuest = BaseGuest(
            first_name=metadata["guest_first_name"],
            last_name=metadata["guest_last_name"],
            phone_number=metadata["guest_phone_number"],
            email=metadata["guest_email"],
            quantity=metadata["quantity"],
        )

        guest: Guest = self.guest_svc.create_guest_from_base(
            guest=base_guest,
            ticket_id=metadata["ticket_id"],
            event_id=metadata["event_id"],
        )

        self.record_transaction(session=session, guest_id=guest.id)

    def record_transaction(self, session: dict, guest_id: int) -> None:
        """
        Record the transaction in the database and send a receipt to the guest.

        Args:
            session: The checkout session object from the Stripe event.
            guest_id: The ID of the guest who made the purchase.
        """
        metadata: dict = session["metadata"]
        charge_id: str = session["payment_intent"]
        
        total_price: Decimal = Decimal(metadata["unit_price"]) * Decimal(
            metadata["quantity"]
        )
        total_fee: Decimal = (
            Decimal(self._convert_to_dollars(session["amount_total"])) - total_price
        )

        base_ticket_receipt: BaseTicketReceipt = BaseTicketReceipt(
            guest_id=guest_id,
            event_id=metadata["event_id"],
            ticket_id=metadata["ticket_id"],
            host_id=metadata["host_id"],
            quantity=metadata["quantity"],
            unit_price=metadata["unit_price"],
            total_price=total_price,
            total_fee=total_fee,
            total_paid=self._convert_to_dollars(session["amount_total"]),
            stripe_account_id=metadata["host_stripe_id"],
            stripe_transaction_id=charge_id
        )

        self.receipt_svc.generate_ticket_receipt(base_ticket_receipt)