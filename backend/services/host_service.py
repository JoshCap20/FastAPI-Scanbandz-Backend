from ..exceptions import (
    HostNotFoundException,
    InvalidCredentialsError,
    HostAlreadyExistsError,
)
from ..entities import HostEntity, EventEntity, GuestEntity, TicketEntity
from ..models import Host, BaseHost, LoginCredentials
from ..database import db_session

from datetime import datetime, timedelta
import bcrypt
from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, or_, and_, func


class HostService:
    _session: Session

    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def all(self) -> list[Host]:
        """
        Retrieves all hosts from the database.

        Returns:
            A list of Host objects representing all hosts in the database.
        """
        query = select(HostEntity)
        entities: Sequence[HostEntity] = self._session.scalars(query).all()
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> Host:
        """
        Retrieve a host by its ID.

        Args:
            id (int): The ID of the host to retrieve.

        Returns:
            Host: The host object.

        Raises:
            HostNotFoundException: If no host is found with the specified ID.
        """
        host_entity: HostEntity | None = self._session.get(HostEntity, id)

        if not host_entity:
            raise HostNotFoundException(f"Host not found with ID: {id}")

        return host_entity.to_model()

    def get_by_phone_number(self, key: str) -> Host:
        """
        Retrieves a host entity by phone number.

        Args:
            key (str): The phone number of the host.

        Returns:
            Host: The host entity.

        Raises:
            HostNotFoundException: If no host is found with the given phone number.
        """
        query = select(HostEntity).where(HostEntity.phone_number == key)
        host_entity: HostEntity | None = self._session.scalars(query).first()

        if not host_entity:
            raise HostNotFoundException(f"Host not found with phone number: {key}")

        return host_entity.to_model()

    def get_by_email(self, key: str) -> Host:
        """
        Retrieves a host by email.

        Args:
            key (str): The email of the host.

        Returns:
            Host: The host object.

        Raises:
            HostNotFoundException: If no host is found with the given email.
        """
        query = select(HostEntity).where(HostEntity.email == key)
        host_entity: HostEntity | None = self._session.scalars(query).first()

        if not host_entity:
            raise HostNotFoundException(f"Host not found with email: {key}")

        return host_entity.to_model()

    def create(self, host: BaseHost) -> Host:
        """
        Creates a new host.

        Args:
            host (BaseHost): The host object to be created.

        Returns:
            Host: The created host object.

        Raises:
            HostAlreadyExistsError: If the email or phone number is already being used.
            Exception: If an error occurs while creating the host.
        """
        # Check if email or phone number is already being used
        existing_host: HostEntity | None = (
            self._session.query(HostEntity)
            .filter(
                or_(
                    HostEntity.email == host.email,
                    HostEntity.phone_number == host.phone_number,
                )
            )
            .first()
        )

        if existing_host:
            raise HostAlreadyExistsError(
                "A host with the same email or phone number already exists."
            )

        host.password = self._hash_password(host.password)
        host_entity: HostEntity = HostEntity.from_base_model(host)
        # TODO: Add error handling for duplicate email or phone number
        try:
            self._session.add(host_entity)
            self._session.commit()
            return host_entity.to_model()
        except:
            self._session.rollback()
            raise Exception("An error occurred while creating the host.")

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hashes the given password using bcrypt.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies if the plain password matches the hashed password.

        Args:
            plain_password (str): The plain password to be verified.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def authenticate_user(self, credentials: LoginCredentials) -> Host:
        """
        Authenticates a user based on the provided credentials.

        Args:
            credentials (LoginCredentials): The login credentials of the user.

        Returns:
            tuple[int, str] | None: A tuple containing the user ID and phone number if the
            authentication is successful, or None if the authentication fails.

        Raises:
            InvalidCredentialsError: If the provided credentials are invalid.
        """
        try:
            user: Host = self.get_by_email(credentials.email)
        except HostNotFoundException:
            raise InvalidCredentialsError()

        if user and HostService._verify_password(credentials.password, user.password):
            return user
        raise InvalidCredentialsError()

    def get_upcoming_events(self, host: Host, limit: int = 5) -> list[dict[str, str]]:
        """
        Retrieves the upcoming events for a host.

        Args:
            host (Host): The host object.
            limit (int): The maximum number of events to retrieve.

        Returns:
            list[EventEntity]: A list of EventEntity objects representing the upcoming events.
        """
        query = (
            self._session.query(EventEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start > datetime.now(),
            )
            .order_by(EventEntity.start.asc())
            .limit(limit)
        )
        return [
            {
                "id": event.id,
                "name": event.name,
                "start": event.start.strftime("%m/%d/%Y"),
                "location": event.location,
                "tickets_sold": self.get_event_tickets_sold(event.id),
            }
            for event in query
        ]

    def get_event_tickets_sold(self, event_id: int) -> int:
        """
        Retrieves the number of tickets sold for a given event.

        Args:
            event_id (int): The ID of the event.

        Returns:
            int: The number of tickets sold.
        """
        query = (
            self._session.query(func.sum(TicketEntity.tickets_sold))
            .filter(TicketEntity.event_id == event_id)
            .scalar()
        )
        return query or 0

    def get_top_events(
        self, host: Host, start_date: datetime, end_date: datetime, limit: int = 4
    ) -> list[dict[str, int]]:
        # Returns top 3 events and tickets sold
        query = (
            self._session.query(EventEntity, func.sum(TicketEntity.tickets_sold))
            .join(TicketEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
            )
            .group_by(EventEntity.id)
            .order_by(func.sum(TicketEntity.tickets_sold).desc())
            .limit(3)
        )

        return [
            {"name": event.name, "tickets_sold": tickets_sold, "id": event.id}
            for event, tickets_sold in query
        ]

    def get_top_tickets(
        self, host: Host, start_date: datetime, end_date: datetime, limit: int = 3
    ) -> list[dict[str, int]]:
        # Returns top 3 tickets sold
        query = (
            self._session.query(TicketEntity)
            .join(EventEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
            )
            .order_by(TicketEntity.tickets_sold.desc())
            .limit(3)
        )

        return [
            {"name": ticket.name, "tickets_sold": ticket.tickets_sold}
            for ticket in query
        ]

    def get_dashboard_stats(self, host: Host, start_date: str, end_date: str) -> dict:
        """
        Returns dashboard stats for a given host within a specified time range.

        Args:
            host_id (int): The ID of the host.
            start_date (str): The start date of the time range. (Format: YYYY-MM-DD)
            end_date (str): The end date of the time range. (Format: YYYY-MM-DD)

        Returns:
            dict: A dictionary containing the number of upcoming events, total guests attended,
                total tickets sold, and total revenue within the time range.
        """
        # Convert start and end date strings to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Get count of events in timeframe
        events_count = (
            self._session.query(EventEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
            )
            .count()
        )

        # Get count of guests attended (where scan_timestamp is not null) in timeframe
        guests_attended_count = (
            self._session.query(GuestEntity)
            .join(EventEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
                GuestEntity.scan_timestamp.isnot(None),
            )
            .count()
        )

        # Get count of tickets sold
        tickets_sold_count = (
            self._session.query(func.sum(TicketEntity.tickets_sold))
            .join(EventEntity, TicketEntity.event_id == EventEntity.id)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
            )
            .scalar()
        ) or 0

        # Get total revenue
        revenue = (
            self._session.query(
                func.sum(TicketEntity.price * TicketEntity.tickets_sold)
            )
            .join(EventEntity)
            .filter(
                EventEntity.host_id == host.id,
                EventEntity.start >= start_date,
                EventEntity.start <= end_date,
            )
            .scalar()
            or 0
        )

        return {
            "events_count": events_count,
            "guests_attended": guests_attended_count,
            "tickets_sold": tickets_sold_count,
            "revenue": revenue,
            "top_events": self.get_top_events(host, start_date, end_date),
            "top_tickets": self.get_top_tickets(host, start_date, end_date),
            "upcoming_events": self.get_upcoming_events(host),
            "start_date": start_date.strftime("%m/%d/%Y"),
            "end_date": end_date.strftime("%m/%d/%Y"),
        }

    ### TESTING ONLY
    def set_stripe_id(self, host_id: int, stripe_id: str) -> Host:
        """
        Set the Stripe ID for a host.

        Args:
            host_id (int): The ID of the host.
            stripe_id (str): The Stripe ID to set.

        Returns:
            Host: The updated host object.
        """
        host: HostEntity | None = self._session.get(HostEntity, host_id)
        if not host:
            raise HostNotFoundException(f"No host found with ID: {host_id}")
        host.stripe_id = stripe_id
        self._session.commit()
        return host.to_model()

    def reset_password_request(self, email: str) -> None:
        """
        Send a password reset request to a host.

        Args:
            email (str): The email of the host.
        """
        host: HostEntity | None = (
            self._session.query(HostEntity).filter(HostEntity.email == email).first()
        )
        if host:
            # TODO: Send email with password reset link
            pass

        return None

    def reset_password(self, host_id: int, new_password: str) -> Host:
        """
        Reset the password for a host.

        Args:
            host_id (int): The ID of the host.
            new_password (str): The new password.

        Returns:
            Host: The updated host object.
        """
        host: HostEntity | None = self._session.get(HostEntity, host_id)
        if not host:
            raise HostNotFoundException(f"No host found with ID: {host_id}")
        host.password = self._hash_password(new_password)
        self._session.commit()
        return host.to_model()
