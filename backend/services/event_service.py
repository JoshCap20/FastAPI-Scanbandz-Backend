from ..entities.event_entity import EventEntity, TicketEntity
from ..exceptions import EventNotFoundException, HostPermissionError
from ..models import Event, BaseEvent, Host, UpdateEvent
from ..database import db_session

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class EventService:
    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    ## CORE FUNCTIONALITY

    def all(self) -> list[Event]:
        """
        Retrieve all events from the database.

        Returns:
            A list of Event objects.
        """
        query = select(EventEntity)
        entities: Sequence[EventEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Event:
        """
        Retrieve an event by its ID.

        Args:
            id (int): The ID of the event to retrieve.

        Returns:
            Event: The event object.

        Raises:
            EventNotFoundException: If the event with the specified ID is not found.
        """
        event_entity: EventEntity | None = self._session.get(EventEntity, id)

        if not event_entity:
            raise EventNotFoundException(id)

        return event_entity.to_model()

    def get_by_public_key(self, key: str) -> Event:
        """
        Retrieves an event by its public key.

        Args:
            key (str): The public key of the event.

        Returns:
            Event: The event object corresponding to the public key.

        Raises:
            EventNotFoundException: If no event is found with the given public key.
        """
        query = select(EventEntity).where(EventEntity.public_key == key)
        event_entity: EventEntity | None = self._session.scalars(query).first()

        if not event_entity:
            raise EventNotFoundException(key)

        return event_entity.to_model()

    def get_by_private_key(self, key: str) -> Event:
        """
        Retrieves an event by its private key.

        Args:
            key (str): The private key of the event.

        Returns:
            Event: The event object corresponding to the private key.

        Raises:
            EventNotFoundException: If no event is found with the given private key.
        """
        query = select(EventEntity).where(EventEntity.private_key == key)
        event_entity: EventEntity | None = self._session.scalars(query).first()

        if not event_entity:
            raise EventNotFoundException(key)

        return event_entity.to_model()

    def create(self, event: BaseEvent, host: Host) -> Event:
        """
        Create a new event.

        Args:
            event (BaseEvent): The event object to be created.
            host (Host): The host of the event.

        Returns:
            Event: The created event object.
        """
        event_entity: EventEntity = EventEntity.from_base_model(event, host.id)
        self._session.add(event_entity)
        self._session.commit()
        return event_entity.to_model()

    def update(self, id: int, event: UpdateEvent, host: Host) -> Event:
        """
        Update an event with the given ID.

        Args:
            id (int): The ID of the event to update.
            event (BaseEvent): The updated event data.
            host (Host): The host of the event.

        Returns:
            Event: The updated event.

        Raises:
            EventNotFoundException: If the event with the given ID does not exist.
            HostPermissionError: If the host does not have permission to update the event.
        """
        event_entity: EventEntity | None = self._session.get(EventEntity, id)

        # Check if the event exists
        if not event_entity:
            raise EventNotFoundException(id)

        # # Check if the host matches
        if event_entity.host_id != host.id:
            raise HostPermissionError()

        # Update the event entity with new data
        event_entity.name = event.name
        event_entity.description = event.description
        event_entity.location = event.location
        event_entity.start = event.start
        event_entity.end = event.end

        # Update any child tickets
        for ticket in event.tickets:
            if ticket.id == 0:
                ticket.event_id = event_entity.id
                ticket_entity: TicketEntity = TicketEntity.from_base_model(ticket)
                self._session.add(ticket_entity)
            else:
                ticket_entity: TicketEntity | None = self._session.get(
                    TicketEntity, ticket.id
                )
            ticket_entity.name = ticket.name
            ticket_entity.description = ticket.description
            ticket_entity.price = ticket.price
            ticket_entity.max_quantity = ticket.max_quantity
            ticket_entity.visibility = ticket.visibility
            ticket_entity.registration_active = ticket.registration_active

        self._session.commit()

        return event_entity.to_model()

    def delete(self, id: int, host: Host) -> None:
        """
        Delete an event and its associated tickets from the database.

        Args:
            id (int): The ID of the event to be deleted.
            host (Host): The host object representing the user attempting to delete the event.

        Raises:
            EventNotFoundException: If the event with the specified ID does not exist.
            HostPermissionError: If the user does not have permission to delete the event.

        Returns:
            None
        """
        event_entity: EventEntity | None = self._session.get(EventEntity, id)
        tickets: list[TicketEntity] = event_entity.tickets if event_entity else []

        if not event_entity:
            raise EventNotFoundException(id)

        if event_entity.host_id != host.id:
            raise HostPermissionError()

        for ticket in tickets:
            self._session.delete(ticket)

        self._session.delete(event_entity)
        self._session.commit()

    ### END CORE FUNCTIONALITY

    def get_events_by_host(self, host: Host) -> list[Event]:
        """
        Retrieve all events hosted by a given user.

        Args:
            host (Host): The host object representing the user.

        Returns:
            list[Event]: A list of Event objects hosted by the user.
        """
        query = select(EventEntity).where(EventEntity.host_id == host.id)
        entities: Sequence[EventEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities] if entities else []
