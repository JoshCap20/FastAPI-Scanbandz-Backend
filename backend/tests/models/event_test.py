from models.event import Event
from datetime import datetime, timedelta
import pytest
from .utils import create_host

def test_new_event():
    event = Event(
        name="Test Event",
        description="Test description",
        location="Test location",
        start=datetime.now(),
        end=datetime.now(),
    )
    assert event.name == "Test Event"
    assert event.description == "Test description"
    assert event.location == "Test location"

def test_new_event_with_host():
    host = create_host()
    event = Event(
        name="Test Event",
        description="Test description",
        location="Test location",
        start=datetime.now(),
        end=datetime.now(),
        host=host
    )
    assert event.name == "Test Event"
    assert event.description == "Test description"
    assert event.location == "Test location"
    assert event.host == host

def test_event_end_before_start_validation():
    with pytest.raises(ValueError):
        Event(
            name="Test Event",
            description="Test description",
            location="Test location",
            start=datetime.now(),
            end=datetime.now() - timedelta(days=1),
        )

def test_event_name_validation_blank():
    with pytest.raises(ValueError):
        Event(
            name="",
            description="Test description",
            location="Test location",
            start=datetime.now(),
            end=datetime.now(),
        )

def test_event_name_validation_long():
    with pytest.raises(ValueError):
        Event(
            name="a" * 101,
            description="Test description",
            location="Test location",
            start=datetime.now(),
            end=datetime.now(),
        )

