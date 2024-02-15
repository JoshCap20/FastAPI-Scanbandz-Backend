from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import Event, BaseEvent, Host, EventPublic
from ..services import EventService
from ..utils.dev_only import dev_only
from ..exceptions import EventNotFoundException, HostPermissionError

api = APIRouter(prefix="/api/events")
openapi_tags = {
    "name": "Events",
    "description": "Event management.",
}


@api.post("/new", tags=["Events"])
def new_event(
    event_details: BaseEvent,
    event_service: EventService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    event: Event = event_service.create(event_details, current_user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Event created successfully."},
    )


@api.put("/update/{event_id}", tags=["Events"])
def update_event(
    event_id: int,
    event_details: BaseEvent,
    event_service: EventService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        event: Event = event_service.update(event_id, event_details, current_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Event updated successfully."},
        )
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except HostPermissionError:
        raise HTTPException(status_code=403, detail="Invalid permission to update event")


@api.get("/get/{event_id}", response_model=EventPublic, tags=["Events"])
def get_public_event(
    event_id: int, event_service: EventService = Depends()
) -> EventPublic:
    try:
        event: Event = event_service.get_by_id(event_id)
        return EventPublic.from_event(event)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")


@api.get("/list", response_model=list[Event], tags=["Events"])
@dev_only
def list_events(event_service: EventService = Depends()) -> list[Event]:
    return event_service.all()
