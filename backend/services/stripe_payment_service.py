"""
Stripe payment service for creating checkout sessions.
"""

import stripe
from decimal import Decimal
from fastapi import Depends

from ..settings.config import STRIPE_SECRET_KEY
from ..models import Ticket, Host, Event
from .ticket_service import TicketService
from .event_service import EventService
from ..exceptions import (
    TicketRegistrationClosedException,
    StripeCheckoutSessionException,
    HostStripeAccountNotFoundException,
)


class StripePaymentService:
    ticket_service: TicketService
    event_service: EventService

    def __init__(
        self,
        ticket_service: TicketService = Depends(TicketService),
        event_service: EventService = Depends(EventService),
    ):
        stripe.api_key = STRIPE_SECRET_KEY
        self.ticket_service = ticket_service
        self.event_service = event_service

    def create_checkout_session(
        self, ticket_id: int, quantity: int, metadata: dict = {}
    ) -> stripe.checkout.Session:
        """
        Creates a checkout session for purchasing tickets.

        Args:
            ticket_id (int): The ID of the ticket to be purchased.
            quantity (int): The quantity of tickets to be purchased.
            metadata (dict, optional): Additional metadata for the checkout session. Defaults to {}.

        Returns:
            stripe.checkout.Session: The created checkout session.

        Raises:
            TicketNotFoundException: If the ticket with the given ID does not exist.
            TicketRegistrationClosedException: If the ticket registration is closed.
            HostStripeAccountNotFoundException: If the host does not have a Stripe account.
        """

        ticket: Ticket = self.ticket_service.get_by_id(ticket_id)
        event: Event = self.event_service.get_by_id(ticket.event_id)
        host: Host = event.host

        if not ticket.registration_active:
            raise TicketRegistrationClosedException()
        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()

        SUCCESS_URL: str = self._get_success_link(event, ticket, quantity)
        CANCEL_URL: str = self._get_cancel_link(event)

        return self._get_stripe_checkout(
            ticket=ticket,
            event=event,
            host_stripe_id=host.stripe_id,
            quantity=quantity,
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            metadata=metadata,
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
        return f"https://tickets.scanbandz.com/success?event={event.name}&ticket={ticket.name}&quantity={quantity}"

    def _get_cancel_link(self, event: Event) -> str:
        """
        Get the cancel link for the checkout session.

        Args:
            event (Event): The event object.

        Returns:
            str: The cancel link for the checkout session.
        """
        return f"https://tickets.scanbandz.com/cancel?event={event.name}"

    def _get_stripe_checkout(
        self,
        ticket: Ticket,
        event: Event,
        host_stripe_id: str,
        quantity: int,
        success_url: str,
        cancel_url: str,
        metadata: dict,
    ) -> stripe.checkout.Session:
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
            stripe.checkout.Session: The created Stripe checkout session.

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
                        "amount": price * quantity,
                    },
                },
            )

            return checkout_session
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

    def _convert_to_cents(self, amount: Decimal) -> int:
        """
        Convert the given amount to cents.

        Args:
            amount (Decimal): The amount to convert.

        Returns:
            int: The amount in cents.
        """
        return int(amount * 100)
