from ..entities import EventEntity, TicketEntity, GuestEntity
from ..exceptions import (
    TicketNotFoundException,
    EventNotFoundException,
    IllegalGuestOperationException,
    TicketRegistrationClosedException,
    TicketRegistrationFullException,
)
from ..database import db_session
from ..models import Guest, BaseGuest, Ticket, Event
from .stripe_payment_service import StripePaymentService
from .ticket_service import TicketService
from .guest_service import GuestService

from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, func


class TicketPaymentBridge:
    _session: Session
    payment_service: StripePaymentService
    ticket_service: TicketService
    guest_service: GuestService

    def __init__(
        self,
        session: Session = Depends(db_session),
        stripe_payment_service: StripePaymentService = Depends(StripePaymentService),
        ticket_service: TicketService = Depends(TicketService),
        guest_service: GuestService = Depends(GuestService),
    ):
        self._session = session
        self.payment_service = stripe_payment_service
        self.ticket_service = ticket_service
        self.guest_service = guest_service

    def create_guest(
        self, guest: BaseGuest, ticket_id: int, event_id: int
    ) -> Guest | str:
        """
        Creates a guest for a given ticket and event if free
        or creates a checkout session for a paid ticket.

        Args:
            guest (BaseGuest): The guest information.
            ticket_id (int): The ID of the ticket.
            event_id (int): The ID of the event.

        Returns:
            Guest | str: The created guest object or a checkout URL

        Raises:
            TicketNotFoundException: If the ticket with the given ID is not found.
            EventNotFoundException: If the event with the given ID is not found.
            IllegalGuestOperationException: If the ticket does not belong to the event.
            TicketRegistrationClosedException: If the ticket registration is closed.
            TicketRegistrationFullException: If the ticket registration is full.
        """
        ticket_entity: TicketEntity | None = self._session.get(TicketEntity, ticket_id)
        event_entity: EventEntity | None = self._session.get(EventEntity, event_id)

        if not ticket_entity:
            raise TicketNotFoundException()
        if not event_entity:
            raise EventNotFoundException(event_id)
        if ticket_entity.event_id != event_entity.id:
            raise IllegalGuestOperationException()
        if not ticket_entity.registration_active:
            raise TicketRegistrationClosedException()

        if ticket_entity.max_quantity:
            guest_count_query = select(func.count()).where(
                GuestEntity.ticket_id == ticket_entity.id
            )
            total_guests = self._session.execute(guest_count_query).scalar_one()

            if total_guests >= ticket_entity.max_quantity:
                raise TicketRegistrationFullException()

        ticket: Ticket = ticket_entity.to_model()
        event: Event = event_entity.to_model()

        if ticket.price <= 0:
            return self.guest_service.create_guest_from_base(
                guest=guest, ticket_id=ticket.id, event_id=event.id
            )
        return self.payment_service.create_checkout_session(
            guest=guest, ticket=ticket, event=event
        )
