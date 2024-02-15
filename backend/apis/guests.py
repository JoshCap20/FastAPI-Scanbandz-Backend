from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import Guest, BaseGuest, GuestIdentity
from ..services import GuestService
from ..utils.dev_only import dev_only
from ..exceptions import GuestNotFoundException, TicketNotFoundException, EventNotFoundException, IllegalGuestOperationException

api = APIRouter(prefix="/api/guests")
openapi_tags = {
    "name": "Guests",
    "description": "Guest management.",
}

@api.post("/{event_id}/{ticket_id}/create", tags=["Guests"])
def create_guest(
    guest: BaseGuest,
    ticket_id: int,
    event_id: int,
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    try:
        guest_service.create_free_guest(guest=guest, ticket_id=ticket_id, event_id=event_id)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Guest created successfully."},
        )
    except (TicketNotFoundException, EventNotFoundException):
        raise HTTPException(status_code=404, detail="Ticket or Event not found")
    except IllegalGuestOperationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    