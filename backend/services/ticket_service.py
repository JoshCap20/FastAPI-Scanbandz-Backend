from ..exceptions import (
    TicketNotFoundException,
    HostPermissionError,
    EventNotFoundException,
)
from ..entities import TicketEntity, EventEntity, GuestEntity
from ..models import Ticket, Host, BaseTicket, UpdateTicket
from ..database import db_session

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class TicketService:
    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Ticket]:
        """
        Retrieve all tickets from the database.

        Returns:
            A list of Ticket objects representing all the tickets in the database.
        """
        query = select(TicketEntity)
        entities: Sequence[TicketEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Ticket:
        """
        Retrieves a ticket by its ID.

        Args:
            id (int): The ID of the ticket to retrieve.

        Returns:
            Ticket: The ticket object.

        Raises:
            TicketNotFoundException: If no ticket is found with the specified ID.
        """
        ticket_entity: TicketEntity | None = self._session.get(TicketEntity, id)

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with ID: {id}")

        return ticket_entity.to_model()

    def get_by_public_key(self, key: str) -> Ticket:
        """
        Retrieves a ticket by its public key.

        Args:
            key (str): The public key of the ticket.

        Returns:
            Ticket: The ticket object.

        Raises:
            TicketNotFoundException: If no ticket is found with the given public key.
        """
        query = select(TicketEntity).where(TicketEntity.public_key == key)
        ticket_entity: TicketEntity | None = self._session.scalars(query).first()

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with public key: {key}")

        return ticket_entity.to_model()

    def get_by_private_key(self, key: str) -> Ticket:
        """
        Retrieves a ticket by its private key.

        Args:
            key (str): The private key of the ticket.

        Returns:
            Ticket: The ticket object.

        Raises:
            TicketNotFoundException: If no ticket is found with the given private key.
        """
        query = select(TicketEntity).where(TicketEntity.private_key == key)
        ticket_entity: TicketEntity | None = self._session.scalars(query).first()

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with private key: {key}")

        return ticket_entity.to_model()

    def create(self, ticket: BaseTicket, host: Host) -> Ticket:
        """
        Create a new ticket.

        Args:
            ticket (Ticket): The ticket object to be created.
            host (Host): The host object who is creating the ticket.

        Returns:
            Ticket: The created ticket object.

        Raises:
            HostPermissionError: If the host does not have permission to create the ticket.
            EventNotFoundException: If the event with the specified ID from the ticket is not found.
        """
        ticket_entity: TicketEntity = TicketEntity.from_base_model(ticket)
        event_entity: EventEntity | None = self._session.get(
            EventEntity, ticket.event_id
        )

        if not event_entity:
            raise EventNotFoundException(f"Event not found with ID: {ticket.event_id}")

        if event_entity.host_id != host.id:
            raise HostPermissionError()

        try:
            self._session.add(ticket_entity)
            self._session.commit()
            return ticket_entity.to_model()
        except:
            self._session.rollback()
            raise Exception("Error creating ticket")

    def update(self, ticket: UpdateTicket, host: Host) -> Ticket:
        """
        Update a ticket with the given ID.

        Args:
            id (int): The ID of the ticket to be updated.
            ticket (BaseTicket): The updated ticket object.
            host (Host): The host object representing the user performing the update.

        Returns:
            Ticket: The updated ticket object.

        Raises:
            TicketNotFoundException: If no ticket is found with the given ID.
            HostPermissionError: If the host does not have permission to update the ticket.
        """
        ticket_entity: TicketEntity | None = self._session.get(TicketEntity, ticket.id)

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with ID: {ticket.id}")

        if ticket_entity.event.host_id != host.id:
            raise HostPermissionError()

        ticket_entity.name = ticket.name
        ticket_entity.description = ticket.description if ticket.description else ""
        ticket_entity.price = ticket.price
        ticket_entity.max_quantity = ticket.max_quantity
        ticket_entity.visibility = ticket.visibility
        ticket_entity.registration_active = ticket.registration_active
        if ticket.event_id != ticket_entity.event_id:
            ticket_entity.event_id = ticket.event_id
            self._ticket_event_id_changes(ticket_entity.id, ticket.event_id)

        try:
            self._session.commit()
            return ticket_entity.to_model()
        except:
            self._session.rollback()
            raise Exception("Error updating ticket")

    def _ticket_event_id_changes(self, ticket_id: int, event_id: int) -> None:
        """
        Update the event_id of a ticket entity and associated guest tickets.

        Args:
            ticket_id (int): The ID of the ticket to be updated.
            event_id (int): The new event ID.

        Returns:
            None
        """
        query = select(GuestEntity).where(GuestEntity.ticket_id == ticket_id)
        guests: list[GuestEntity] = self._session.scalars(query).all()

        for guest in guests:
            guest.event_id = event_id

        return

    def delete(self, id: int, host: Host) -> None:
        """
        Deletes a ticket with the given ID if the host has permission.

        Args:
            id (int): The ID of the ticket to be deleted.
            host (Host): The host object representing the user performing the deletion.

        Raises:
            TicketNotFoundException: If no ticket is found with the given ID.
            HostPermissionError: If the host does not have permission to delete the ticket.
        """
        ticket_entity: TicketEntity | None = self._session.get(TicketEntity, id)

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with ID: {id}")

        if ticket_entity.event.host_id != host.id:
            raise HostPermissionError()

        self._session.delete(ticket_entity)
        self._session.commit()

    def get_tickets_by_host(
        self, host: Host, filters: dict[str, str | float | bool | None] = None
    ) -> list[Ticket]:
        """
        Retrieve all tickets hosted by the current user.

        Args:
            filters (dict): The filters to apply to the ticket search.
            host (Host): The host object representing the user performing the search.

        Returns:
            list[Ticket]: The list of tickets hosted by the current user.
        """
        query = (
            select(TicketEntity).join(EventEntity).where(EventEntity.host_id == host.id)
        )

        if filters:
            query = self._apply_filters(query, filters)

        entities: Sequence[TicketEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities] if entities else []

    def _apply_filters(self, query, filters: dict):
        if "id" in filters and filters["id"]:
            query = query.where(TicketEntity.id == filters["id"])
            return query
        if "name" in filters and filters["name"]:
            query = query.where(TicketEntity.name.ilike(f"%{filters['name']}%"))
        if "price" in filters and filters["price"]:
            query = query.where(TicketEntity.price >= filters["price"])
        if "max_quantity" in filters and filters["max_quantity"]:
            query = query.where(TicketEntity.max_quantity >= filters["max_quantity"])
        if "visibility" in filters and filters["visibility"] is not None:
            query = query.where(TicketEntity.visibility == filters["visibility"])
        if (
            "registration_active" in filters
            and filters["registration_active"] is not None
        ):
            query = query.where(
                TicketEntity.registration_active == filters["registration_active"]
            )
        if "tickets_sold" in filters and filters["tickets_sold"]:
            query = query.where(TicketEntity.tickets_sold >= filters["tickets_sold"])
        if "event_id" in filters and filters["event_id"]:
            query = query.where(TicketEntity.event_id == filters["event_id"])

        return query

    def increase_ticket_sold_count(self, ticket_id: int, quantity: int) -> None:
        """
        Increase the ticket sold count by the given quantity.

        Args:
            ticket_id (int): The ID of the ticket to be updated.
            quantity (int): The quantity of tickets sold.

        Returns:
            None
        """
        ticket_entity: TicketEntity | None = self._session.get(TicketEntity, ticket_id)

        if not ticket_entity:
            raise TicketNotFoundException(f"Ticket not found with ID: {ticket_id}")

        ticket_entity.tickets_sold += quantity

        try:
            self._session.commit()
            return
        except:
            self._session.rollback()
            raise Exception("Error updating ticket sold count")

    def get_all_tickets_id_and_name_by_event_key(self, event_key: str) -> list[dict]:
        """
        Retrieve all tickets' id and name for a given event key.

        Args:
            event_key (str): The public key of the event.

        Returns:
            list[dict]: A list of dictionaries containing the ticket ID and name.
        """
        query = (
            select(TicketEntity.id, TicketEntity.name)
            .join(EventEntity)
            .where(EventEntity.public_key == event_key)
        )
        result = self._session.execute(query).all()

        tickets = [{"id": row[0], "name": row[1]} for row in result] if result else []
        return tickets
