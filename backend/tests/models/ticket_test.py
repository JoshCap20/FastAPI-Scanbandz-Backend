import pytest
from decimal import Decimal
from datetime import datetime
from models.ticket import Ticket

def test_new_ticket():
    ticket = Ticket(
        name="Test Ticket",
        price=Decimal("10.00"),
        max_quantity=100,
        used_quantity=0,
        visibility=True,
        registration_active=True,
        event_id=1
    )
    assert ticket.name == "Test Ticket"
    assert ticket.price == Decimal("10.00")
    assert ticket.max_quantity == 100
    assert ticket.used_quantity == 0
    assert ticket.visibility == True
    assert ticket.registration_active == True
    assert ticket.event_id == 1

def test_ticket_price_validation():
    with pytest.raises(ValueError):
        Ticket(
            name="Test Ticket",
            price=Decimal("-10.00"),
            max_quantity=100,
            used_quantity=0,
            visibility=True,
            registration_active=True,
            event_id=1
        )