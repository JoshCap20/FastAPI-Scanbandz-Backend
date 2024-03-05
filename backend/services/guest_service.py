from ..entities import EventEntity, TicketEntity, GuestEntity
from ..exceptions import (
    GuestNotFoundException,
    HostPermissionError,
    EventNotFoundException,
)
from ..database import db_session
from ..models import Guest, Host, BaseGuest, UpdateGuest
from .ticket_service import TicketService
from .communication_service import CommunicationService

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, func


class GuestService:
    _session: Session
    ticket_service: TicketService
    communication_service: CommunicationService

    def __init__(
        self,
        session: Session = Depends(db_session),
        ticket_service: TicketService = Depends(TicketService),
        communication_service: CommunicationService = Depends(CommunicationService),
    ):
        self._session = session
        self.ticket_service = ticket_service
        self.communication_service = communication_service

    def all(self) -> list[Guest]:
        """
        Retrieves all guest entities from the database and returns them as a list of Guest models.

        Returns:
            list[Guest]: A list of Guest models representing the guest entities.
        """
        query = select(GuestEntity)
        entities: Sequence[GuestEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def retrieve_guest_ticket(self, event_key: str, guest_key: str) -> Guest:
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
            .join(EventEntity)
            .where(EventEntity.public_key == event_key)
            .where(GuestEntity.public_key == guest_key)
        )
        guest_entity: GuestEntity | None = self._session.scalars(query).first()

        if not guest_entity:
            raise GuestNotFoundException(
                f"No guest found with event key: {event_key} and guest key: {guest_key}"
            )

        return guest_entity.to_model()

    def update_guest_by_host(self, guest: UpdateGuest, host: Host) -> Guest:
        """
        Updates a guest by ID on behalf of the host.

        Args:
            guest (UpdateGuest): The guest information to update.
            host (Host): The host object representing the host.

        Returns:
            Guest: The updated guest object.

        Raises:
            GuestNotFoundException: If no guest is found with the given ID.
            HostPermissionError: If the host does not have permission to update the guest.
        """
        guest_entity: GuestEntity | None = self._session.get(GuestEntity, guest.id)

        if not guest_entity:
            raise GuestNotFoundException(f"No guest found with ID: {guest.id}")
        if guest_entity.event.host_id != host.id:
            raise HostPermissionError()

        guest_entity.first_name = guest.first_name
        guest_entity.last_name = guest.last_name
        guest_entity.email = guest.email
        guest_entity.quantity = guest.quantity
        guest_entity.ticket_id = guest.ticket_id
        guest_entity.event_id = guest.event_id
        guest_entity.used_quantity = guest.used_quantity
        self._session.commit()
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

    def create_guest_by_host(
        self, guest: BaseGuest, ticket_id: int, event_id: int, host: Host
    ) -> Guest:
        """
        Creates a new guest from a base guest, ticket, and event.

        Args:
            guest (BaseGuest): The base guest object.
            ticket (Ticket): The ticket object.
            event (Event): The event object.
            host (Host): The host object representing the host.

        Returns:
            Guest: The created guest object.
        """
        event: EventEntity | None = self._session.get(EventEntity, event_id)
        ticket: TicketEntity | None = self._session.get(TicketEntity, ticket_id)

        if event.host.id != host.id:
            raise HostPermissionError()

        if not event or not ticket:
            raise EventNotFoundException(event_id)

        return self.create_guest_from_base(
            guest=guest, ticket_id=ticket.id, event_id=event.id
        )

    def create_guest_from_base(
        self, guest: BaseGuest, ticket_id: int, event_id: int
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
            base_model=guest, ticket_id=ticket_id, event_id=event_id
        )

        self._session.add(entity)
        self._session.commit()

        self.ticket_service.increase_ticket_sold_count(ticket_id, guest.quantity)

        model: Guest = entity.to_model()
        self.send_ticket(model)

        return model

    def send_ticket(self, guest: Guest) -> None:
        """
        Sends a ticket to the guest.

        Args:
            guest (Guest): The guest object.
        """
        self.communication_service.send_guest_ticket_link(guest)

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

    def get_guests_by_host(
        self, host: Host, filters: None | dict[str, str | None] = None
    ) -> list[Guest]:
        """
        Retrieves all guests belonging to the host.

        Args:
            host (Host): The host object representing the host.

        Returns:
            list[Guest]: A list of guest objects belonging to the host.
        """
        query: list[tuple[int, str]] = (
            select(GuestEntity).join(EventEntity).where(EventEntity.host_id == host.id)
        )
        if filters:
            query = self._apply_filters(query, filters)
        entities: Sequence[GuestEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def _apply_filters(self, query, filters: dict):
        if "searchEvent" in filters and filters["searchEvent"]:
            query = query.where(EventEntity.name.ilike(f"%{filters['searchEvent']}%"))
        if "searchTicket" in filters and filters["searchTicket"]:
            query = query.where(TicketEntity.name.ilike(f"%{filters['searchTicket']}%"))
        if "searchEventID" in filters and filters["searchEventID"]:
            query = query.where(EventEntity.id == filters["searchEventID"])
        if "searchTicketID" in filters and filters["searchTicketID"]:
            query = query.join(TicketEntity, TicketEntity.id == GuestEntity.ticket_id)
            query = query.where(TicketEntity.id == filters["searchTicketID"])
        if "searchEmail" in filters and filters["searchEmail"]:
            query = query.where(GuestEntity.email.ilike(f"%{filters['searchEmail']}%"))
        if "searchPhoneNumber" in filters and filters["searchPhoneNumber"]:
            query = query.where(
                GuestEntity.phone_number.ilike(f"%{filters['searchPhoneNumber']}%")
            )
        if "searchAttended" in filters and filters["searchAttended"] == "attended":
            query = query.where(GuestEntity.used_quantity > 0)
        if "searchAttended" in filters and filters["searchAttended"] == "not attended":
            query = query.where(GuestEntity.used_quantity == 0)
        if "searchName" in filters and filters["searchName"]:
            query = query.where(
                func.concat(GuestEntity.first_name, " ", GuestEntity.last_name).ilike(
                    f"%{filters['searchName']}%"
                )
            )

        return query

    def retrieve_guest_by_host(self, guest_id: int, host: Host) -> Guest:
        """
        Retrieves a guest by ID on behalf of the host.

        Args:
            guest_id (int): The ID of the guest.
            host (Host): The host object representing the host.

        Returns:
            Guest: The guest object.

        Raises:
            GuestNotFoundException: If no guest is found with the given ID.
            HostPermissionError: If the host does not have permission to retrieve the guest.
        """
        guest_entity: GuestEntity | None = self._session.get(GuestEntity, guest_id)

        if not guest_entity:
            raise GuestNotFoundException(f"No guest found with ID: {guest_id}")
        if guest_entity.event.host_id != host.id:
            raise HostPermissionError()

        return guest_entity.to_model()

    def validate_guest_ticket(self, event_key: str, guest_key: str) -> Guest:
        """
        Validates a guest ticket by event and ticket key.

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
            .join(EventEntity)
            .where(EventEntity.public_key == event_key)
            .where(GuestEntity.public_key == guest_key)
        )
        guest_entity: GuestEntity | None = self._session.scalars(query).first()

        if not guest_entity:
            raise GuestNotFoundException(
                f"No guest found with event key: {event_key} and guest key: {guest_key}"
            )

        return guest_entity.to_model()
