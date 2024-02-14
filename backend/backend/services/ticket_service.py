from ..exceptions import TicketNotFoundException, HostPermissionError
from ..entities import TicketEntity
from ..models import Ticket, Host
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

    def create(self, ticket: Ticket, host: Host) -> Ticket:
        """
        Create a new ticket.

        Args:
            ticket (Ticket): The ticket object to be created.
            host (Host): The host object who is creating the ticket.

        Returns:
            Ticket: The created ticket object.

        Raises:
            HostPermissionError: If the host does not have permission to create the ticket.
        """
        ticket_entity: TicketEntity = TicketEntity.from_model(ticket)
        
        if ticket_entity.event.host_id != host.id:
            raise HostPermissionError()
        
        self._session.add(ticket_entity)
        self._session.commit()
        return ticket_entity.to_model()

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
