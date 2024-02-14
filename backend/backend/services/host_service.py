from ..exceptions import (
    HostNotFoundException,
    TicketNotFoundException,
    InvalidCredentialsError,
)
from ..entities.host_entity import HostEntity
from ..models import Host, BaseHost, HostIdentity, LoginCredentials
from ..database import db_session

import bcrypt
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class HostService:

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

    def create(self, host: BaseHost) -> Host:
        host.password = self._hash_password(host.password)
        host_entity = HostEntity.from_base_model(host)
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

    @staticmethod
    def _hash_password(password: str) -> str:
        # Hashing the password
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        # Verifying the password
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def authenticate_user(
        self, credentials: LoginCredentials
    ) -> tuple[int, str] | None:
        """
        Authenticate a user with the given credentials.

        Parameters:
            credentials (LoginCredentials): User credentials.

        Returns:
            tuple[int, str] | None: a tuple containing the user's ID and phone number
                if the user is authenticated, None otherwise.
        """
        user: Host = self.get_by_email(credentials.email)
        if user and HostService._verify_password(credentials.password, user.password):
            return user.id, user.phone_number  # type: ignore
        raise InvalidCredentialsError()
