from ..entities import EventEntity, TicketEntity, GuestEntity, HostEntity
from ..exceptions import (
    GuestNotFoundException,
    HostPermissionError,
    TicketNotFoundException,
    EventNotFoundException,
    IllegalGuestOperationException,
    TicketRegistrationClosedException,
    TicketRegistrationFullException,
)
from ..database import db_session
from ..models import Guest, Host, BaseGuest, Ticket, Event
from .stripe_payment_service import StripePaymentService

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, func


class GuestService:
    _session: Session
    payment_service: StripePaymentService

    def __init__(
        self,
        session: Session = Depends(db_session),
        stripe_payment_service: StripePaymentService = Depends(StripePaymentService),
    ):
        self._session = session
        self.payment_service = stripe_payment_service

    def all(self) -> list[Guest]:
        """
        Retrieves all guest entities from the database and returns them as a list of Guest models.

        Returns:
            list[Guest]: A list of Guest models representing the guest entities.
        """
        query = select(GuestEntity)
        entities: Sequence[GuestEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def retrieve_guest_ticket(self, event_key: str, ticket_key: str) -> Guest:
        """
        Retrieves a guest by event and ticket key.

        Args:
            event_key (str): The key of the event.
            ticket_key (str): The key of the ticket.

        Returns:
            Guest: The guest object.

        Raises:
            GuestNotFoundException: If no guest is found with the given event and ticket key.
        """
        query = (
            select(GuestEntity)
            .join(TicketEntity)
            .join(EventEntity)
            .where(
                EventEntity.public_key == event_key,
                TicketEntity.public_key == ticket_key,
            )
        )
        guest_entity: GuestEntity | None = self._session.scalars(query).first()

        if not guest_entity:
            raise GuestNotFoundException(
                f"No guest found with event key: {event_key} and ticket key: {ticket_key}"
            )

        return guest_entity.to_model()

    def get_by_id(self, id: int) -> Guest:
        """
        Retrieves a guest by their ID.

        Args:
            id (int): The ID of the guest to retrieve.

        Returns:
            Guest: The guest object.

        Raises:
            GuestNotFoundException: If no guest is found with the specified ID.
        """
        guest_entity: GuestEntity | None = self._session.get(GuestEntity, id)

        if not guest_entity:
            raise GuestNotFoundException(f"No guest found with ID: {id}")

        return guest_entity.to_model()

    def get_by_public_key(self, key: str) -> Guest:
        """
        Retrieves a guest by their public key.

        Args:
            key (str): The public key of the guest.

        Returns:
            Guest: The guest object corresponding to the public key.

        Raises:
            GuestNotFoundException: If no guest is found with the provided public key.
        """
        query = select(GuestEntity).where(GuestEntity.public_key == key)
        guest_entity: GuestEntity | None = self._session.scalars(query).first()

        if not guest_entity:
            raise GuestNotFoundException(f"No guest found with public key: {key}")

        return guest_entity.to_model()

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
            ticket_entity.tickets_sold += 1
            self._session.commit()
            return self.create_guest_from_base(guest=guest, ticket=ticket, event=event)
        return self.payment_service.create_checkout_session(
            guest=guest, ticket=ticket, event=event
        )

    def create_guest_from_base(
        self, guest: BaseGuest, ticket: Ticket, event: Event
    ) -> Guest:
        """
        Creates a new guest from a base guest, ticket, and event.

        Args:
            guest (BaseGuest): The base guest object.
            ticket (Ticket): The ticket object.
            event (Event): The event object.

        Returns:
            Guest: The created guest object.
        """
        entity: GuestEntity = GuestEntity.from_base_model(
            base_model=guest, ticket_id=ticket.id, event_id=event.id
        )
        self._session.add(entity)
        self._session.commit()
        return entity.to_model()

    def create(self, guest: Guest) -> Guest:
        """
        Creates a new guest in the database.

        Args:
            guest (Guest): The guest object to be created.

        Returns:
            Guest: The created guest object.
        """
        guest_entity: GuestEntity = GuestEntity.from_model(guest)
        self._session.add(guest_entity)
        self._session.commit()
        return guest_entity.to_model()

    def delete(self, id: int, host: Host) -> None:
        """
        Delete a guest by ID if the host has permission.

        Args:
            id (int): The ID of the guest to delete.
            host (Host): The host object representing the host.

        Raises:
            GuestNotFoundException: If no guest is found with the given ID.
            HostPermissionError: If the host does not have permission to delete the guest.
        """
        guest_entity: GuestEntity | None = self._session.get(GuestEntity, id)

        if not guest_entity:
            raise GuestNotFoundException(f"No guest found with ID: {id}")
        if guest_entity.event.host_id != host.id:
            raise HostPermissionError()

        self._session.delete(guest_entity)
        self._session.commit()
