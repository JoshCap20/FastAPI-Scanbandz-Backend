from settings.database import db_session
from sqlalchemy.orm import Session
from fastapi import Depends

class GuestService:

    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self):
        raise NotImplementedError()
        # query = select(GuestEntity)
        # entities = self._session.scalars(query).all()
        # return [entity.to_model() for entity in entities]

    def get(self, id: int):
        raise NotImplementedError()
    
    def create(self, guest):
        raise NotImplementedError()
    
    def update(self, guest):
        raise NotImplementedError()
    
    def delete(self, guest: int):
        raise NotImplementedError()