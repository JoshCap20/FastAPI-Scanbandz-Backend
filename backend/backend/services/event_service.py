from ..entities.event_entity import EventEntity
from ..exceptions.event_exceptions import EventNotFoundException
from ..models import Event, BaseEvent, EventIdentity, Host
from ..database import db_session

from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class EventService:
    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Event]:
        query = select(EventEntity)
        entities: list[EventEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Event:
        event_entity: EventEntity = self._session.get(EventEntity, id)
        if event_entity:
            return event_entity.to_model()
        else:
            raise EventNotFoundException(id)

    def get_by_public_key(self, key: str) -> Event:
        query = select(EventEntity).where(EventEntity.public_key == key)
        event_entity: EventEntity = self._session.scalars(query).first()
        if event_entity:
            return event_entity.to_model()
        else:
            raise EventNotFoundException(key)

    def get_by_private_key(self, key: str) -> Event:
        query = select(EventEntity).where(EventEntity.private_key == key)
        event_entity: EventEntity = self._session.scalars(query).first()
        if event_entity:
            return event_entity.to_model()
        else:
            raise EventNotFoundException(key)

    def create(self, event: BaseEvent, host: Host) -> Event:
        event_entity: EventEntity = EventEntity.from_base_model(event, host.id)
        self._session.add(event_entity)
        self._session.commit()
        return event_entity.to_model()

    def delete(self, id: int) -> None:
        event_entity: EventEntity = self._session.get(EventEntity, id)
        if event_entity:
            self._session.delete(event_entity)
            self._session.commit()
        else:
            raise EventNotFoundException(id)
