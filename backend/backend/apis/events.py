from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from ..models import Event, BaseEvent
from ..entities import HostEntity
from ..services.event_service import EventService
from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/events")
openapi_tags = {
    "name": "Events",
    "description": "Event management.",
}


@api.post("/new", tags=["Events"])
def new_event(
    event: BaseEvent, event_service: EventService = Depends()
) -> JSONResponse:
    event: Event = event_service.create(event)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Event created successfully."},
    )


@api.get("/list", response_model=list[Event], tags=["Events"])
@dev_only
def list_events(event_service: EventService = Depends()) -> list[Event]:
    return event_service.all()
