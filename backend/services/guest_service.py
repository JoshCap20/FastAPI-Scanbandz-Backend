from backend.entities.event_entity import EventEntity
from backend.entities.ticket_entity import TicketEntity
from ..exceptions import (
    GuestNotFoundException,
    HostPermissionError,
    TicketNotFoundException,
    EventNotFoundException,
    IllegalGuestOperationException,
)
from ..database import db_session
from ..entities import GuestEntity
from ..models import Guest, Host, BaseGuest, Ticket, Event

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class GuestService:
    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Guest]:
        """
        Retrieves all guest entities from the database and returns them as a list of Guest models.

        Returns:
            list[Guest]: A list of Guest models representing the guest entities.
        """
        query = select(GuestEntity)
        entities: Sequence[GuestEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

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

    def create_free_guest(
        self, guest: BaseGuest, ticket_id: int, event_id: int
    ) -> Guest:
        """
        Creates a guest for a free ticket and event.

        Args:
            guest (BaseGuest): The guest information.
            ticket_id (int): The ID of the ticket.
            event_id (int): The ID of the event.

        Returns:
            Guest: The created guest.

        Raises:
            TicketNotFoundException: If the ticket is not found.
            EventNotFoundException: If the event is not found.
            IllegalGuestOperationException: If the ticket has a price or the event is not the same as the ticket's event.
        """
        ticket: TicketEntity | None = self._session.get(TicketEntity, ticket_id)
        event: EventEntity | None = self._session.get(EventEntity, event_id)

        if not ticket:
            raise TicketNotFoundException()
        if not event:
            raise EventNotFoundException(event_id)

        if ticket.event_id != event.id:
            raise IllegalGuestOperationException()
        if ticket.price > 0:
            raise IllegalGuestOperationException()

        entity: GuestEntity = GuestEntity.from_base_model(
            base_model=guest, ticket_id=ticket_id, event_id=event_id
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
