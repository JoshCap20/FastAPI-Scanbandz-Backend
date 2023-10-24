from backend.exceptions.ticket_exceptions import TicketNotFoundException
from entities.ticket_entity import TicketEntity
from models.ticket import Ticket
from settings.database import db_session
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class TicketService:

    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Ticket]:
        query = select(TicketEntity)
        entities = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Ticket:
        ticket_entity = self._session.get(TicketEntity, id)
        if ticket_entity:
            return ticket_entity.to_model()
        else:
            raise TicketNotFoundException(f"Ticket not found with ID: {id}")
        
    def get_by_public_key(self, key: str) -> Ticket:
        query = select(TicketEntity).where(TicketEntity.public_key == key)
        ticket_entity = self._session.scalars(query).first()
        if ticket_entity:
            return ticket_entity.to_model()
        else:
            raise TicketNotFoundException(f"Ticket not found with public key: {key}")
        
    def get_by_private_key(self, key: str) -> Ticket:
        query = select(TicketEntity).where(TicketEntity.private_key == key)
        ticket_entity = self._session.scalars(query).first()
        if ticket_entity:
            return ticket_entity.to_model()
        else:
            raise TicketNotFoundException(f"Ticket not found with private key: {key}")

    def create(self, ticket: Ticket) -> Ticket:
        ticket_entity = TicketEntity.from_model(ticket)
        self._session.add(ticket_entity)
        self._session.commit()
        return ticket_entity.to_model()

    def delete(self, id: int) -> None:
        ticket_entity = self._session.get(TicketEntity, id)
        if ticket_entity:
            self._session.delete(ticket_entity)
            self._session.commit()
        else:
            raise TicketNotFoundException(f"Ticket not found with ID: {id}")