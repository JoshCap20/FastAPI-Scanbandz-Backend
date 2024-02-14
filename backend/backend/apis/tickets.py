from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .authentication import registered_user
from ..models import Ticket, BaseTicket, Host
from ..services import TicketService
from ..utils.dev_only import dev_only
from ..exceptions import EventNotFoundException, HostPermissionError, TicketNotFoundException

api = APIRouter(prefix="/api/tickets")
openapi_tags = {
    "name": "Tickets",
    "description": "Ticket management.",
}


@api.post("/new", tags=["Tickets"])
def new_ticket(
    ticket_details: BaseTicket,
    ticket_service: TicketService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        ticket: Ticket = ticket_service.create(ticket_details, current_user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Ticket created successfully."},
        )
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except HostPermissionError:
        raise HTTPException(status_code=403, detail="Invalid permissions")
    
@api.put("/update", tags=["Tickets"])
def update_ticket(
    ticket_id: int,
    ticket_details: BaseTicket,
    ticket_service: TicketService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        ticket: Ticket = ticket_service.update(ticket_id, ticket_details, current_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Ticket updated successfully."},
        )
    except TicketNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except HostPermissionError:
        raise HTTPException(status_code=403, detail="Invalid permissions")

@api.get("/list", response_model=list[Ticket], tags=["Tickets"])
@dev_only
def list_tickets(ticket_service: TicketService = Depends()) -> list[Ticket]:
    return ticket_service.all()
