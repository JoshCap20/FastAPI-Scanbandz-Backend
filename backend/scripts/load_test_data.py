# Load sample data into the database for testing purposes
from sqlalchemy.orm import Session

from ..models import BaseHost, BaseEvent, BaseTicket, BaseGuest
from ..entities import EventEntity, GuestEntity, TicketEntity, HostEntity, Base
from ..services import HostService

dummy_host_1 = BaseHost(
    first_name="Host 1",
    last_name="Doe",
    email="test1@gmail.com",
    phone_number="1234567890",
    password=HostService._hash_password("password123"),
)

dummy_host_2 = BaseHost(
    first_name="Jane",
    last_name="Host 2",
    email="test2@gmail.com",
    phone_number="1234567891",
    password=HostService._hash_password("password123"),
)

hosts: list[BaseHost] = [dummy_host_1, dummy_host_2]

dummy_event_1 = BaseEvent(
    name="Event 1",
    description="This is a test event",
    start="2022-01-01T00:00:00",
    end="2022-01-01T01:00:00",
    location="Test Location",
)

dummy_event_2 = BaseEvent(
    name="Event 2",
    description="This is another test event",
    start="2022-01-02T00:00:00",
    end="2022-01-02T01:00:00",
    location="Test Location 2",
)

dummy_event_3 = BaseEvent(
    name="Event 3",
    description="This is another test event",
    start="2022-01-03T00:00:00",
    end="2022-01-03T01:00:00",
    location="204 Cottage Lane",
)


events: list[BaseEvent] = [dummy_event_1, dummy_event_2, dummy_event_3]
host_1_events: list[BaseEvent] = events[:2]
host_2_events: list[BaseEvent] = events[2:]

dummy_ticket_1 = BaseTicket(
    name="Ticket 1 for Event 1 (Paid)",
    description="This is a test ticket",
    price=100,
    visibility=True,
    registration_active=True,
    event_id=1,
)

dummy_ticket_2 = BaseTicket(
    name="Ticket 2 for Event 1 (Free)",
    description="This is another test ticket that is free!",
    price=0,
    event_id=1,
    visibility=True,
    registration_active=True,
)

dummy_ticket_3 = BaseTicket(
    name="Ticket %$!Free for Event 2",
    description="This is another test ticket",
    price=0,
    event_id=2,
    visibility=True,
    registration_active=True,
)

dummy_ticket_4 = BaseTicket(
    name="Ticket 2 for Event 2 (Also free)",
    description="This is a test ticket",
    price=0,
    event_id=2,
    visibility=True,
    registration_active=True,
)

dummy_ticket_5 = BaseTicket(
    name="Ticket 3 for Event 2 (Paid)",
    description="This is a test ticket",
    price=52.20,
    event_id=2,
    visibility=True,
    registration_active=True,
)

tickets: list[BaseTicket] = [
    dummy_ticket_1,
    dummy_ticket_2,
    dummy_ticket_3,
    dummy_ticket_4,
    dummy_ticket_5,
]

dummy_guest_1 = BaseGuest(
    first_name="John",
    last_name="Doe",
    email="dummyguest1@gmail.com",
    phone_number="1234567890",
    quantity=1,
    used_quantity=0,
)

dummy_guest_2 = BaseGuest(
    first_name="Jane",
    last_name="Doe",
    email="dummyguest2@gmail.com",
    phone_number="1234567891",
    quantity=1,
    used_quantity=0,
)

dummy_guest_3 = BaseGuest(
    first_name="Johnathan",
    last_name="Doe",
    email="dummyguest3@gmail.com",
    phone_number="1234567892",
    quantity=10,
    used_quantity=2,
)

guests: list[BaseGuest] = [dummy_guest_1, dummy_guest_2, dummy_guest_3]


def insert_fake_hosts(session: Session):
    for host in hosts:
        host_entity = HostEntity.from_base_model(host)
        session.add(host_entity)
        session.commit()


def insert_fake_events(session: Session):
    for event in host_1_events:
        event_entity = EventEntity.from_base_model(event, host_id=1)
        session.add(event_entity)

    for event in host_2_events:
        event_entity = EventEntity.from_base_model(event, host_id=2)
        session.add(event_entity)

    session.commit()


def insert_fake_tickets(session: Session):
    for ticket in tickets:
        ticket_entity = TicketEntity.from_base_model(ticket)
        session.add(ticket_entity)
        session.commit()


def insert_fake_guests(session: Session):
    for guest in guests:
        guest_entity = GuestEntity.from_base_model(guest, ticket_id=1, event_id=1)
        session.add(guest_entity)
        session.commit()


if __name__ == "__main__":
    from ..database import engine

    session = Session(engine)
    insert_fake_hosts(session)
    insert_fake_events(session)
    insert_fake_tickets(session)
    insert_fake_guests(session)
    session.close()
    print("Sample data loaded successfully!")
