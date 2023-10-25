from exceptions.host_exceptions import HostNotFoundException
from exceptions.ticket_exceptions import TicketNotFoundException
from entities.host_entity import HostEntity
from models.host import Host
from settings.database import db_session
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class TicketService:

    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Host]:
        query = select(HostEntity)
        entities = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Host:
        host_entity = self._session.get(HostEntity, id)
        if host_entity:
            return host_entity.to_model()
        else:
            raise HostNotFoundException(f"Host not found with ID: {id}")
        
    def get_by_phone_number(self, key: str) -> Host:
        query = select(HostEntity).where(HostEntity.phone_number == key)
        host_entity = self._session.scalars(query).first()
        if host_entity:
            return host_entity.to_model()
        else:
            raise HostNotFoundException(f"Host not found with phone number: {key}")
        
    def get_by_email(self, key: str) -> Host:
        query = select(HostEntity).where(HostEntity.email == key)
        host_entity = self._session.scalars(query).first()
        if host_entity:
            return host_entity.to_model()
        else:
            raise HostNotFoundException(f"Host not found with email: {key}")

    def create(self, host: Host) -> Host:
        host_entity = HostEntity.from_model(host)
        self._session.add(host_entity)
        self._session.commit()
        return host_entity.to_model()

    def delete(self, id: int) -> None:
        host_entity = self._session.get(HostEntity, id)
        if host_entity:
            self._session.delete(host_entity)
            self._session.commit()
        else:
            raise TicketNotFoundException(f"Host not found with ID: {id}")