from backend.exceptions.guest_exceptions import GuestNotFoundException
from settings.database import db_session
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from entities.guest_entity import GuestEntity
from models.guest import Guest


class GuestService:

    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Guest]:
        query = select(GuestEntity)
        entities = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Guest:
        guest_entity = self._session.get(GuestEntity, id)
        if guest_entity:
            return guest_entity.to_model()
        else:
            raise GuestNotFoundException(f"No guest found with ID: {id}")
        
    def get_by_public_key(self, key: str) -> Guest:
        query = select(GuestEntity).where(GuestEntity.public_key == key)
        guest_entity = self._session.scalars(query).first()
        if guest_entity:
            return guest_entity.to_model()
        else:
            raise GuestNotFoundException(f"No guest found with public key: {key}")


    def create(self, guest: Guest) -> Guest:
        raise NotImplementedError()

    def delete(self, guest: Guest) -> None:
        raise NotImplementedError()
