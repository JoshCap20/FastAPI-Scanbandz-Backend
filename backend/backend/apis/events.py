from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .authentication import registered_user
from ..models import Event, BaseEvent, Host, EventPublic
from ..entities import HostEntity
from ..services.event_service import EventService
from ..utils.dev_only import dev_only
from ..exceptions import EventNotFoundException

api = APIRouter(prefix="/api/events")
openapi_tags = {
    "name": "Events",
    "description": "Event management.",
}


@api.post("/new", tags=["Events"])
def new_event(
    event: BaseEvent, event_service: EventService = Depends(), current_user: Host = Depends(registered_user)
) -> JSONResponse:
    event: Event = event_service.create(event, current_user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Event created successfully."},
    )
    
@api.get("/get/{event_id}", response_model=EventPublic, tags=["Events"])
def get_event(event_id: int, event_service: EventService = Depends()) -> EventPublic:
    try:
        event: Event = event_service.get_by_id(event_id)
        return EventPublic.from_event(event)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")


@api.get("/list", response_model=list[Event], tags=["Events"])
@dev_only
def list_events(event_service: EventService = Depends()) -> list[Event]:
    return event_service.all()
