from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import Ticket, BaseTicket, Host, UpdateTicket
from ..services import TicketService
from ..utils.dev_only import dev_only
from ..exceptions import (
    EventNotFoundException,
    HostPermissionError,
    TicketNotFoundException,
)

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
        ticket: Ticket = ticket_service.create(ticket=ticket_details, host=current_user)
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
    baseTicket: UpdateTicket,
    ticket_service: TicketService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        ticket: Ticket = ticket_service.update(ticket=baseTicket, host=current_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Ticket updated successfully."},
        )
    except TicketNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except HostPermissionError:
        raise HTTPException(status_code=403, detail="Invalid permissions")


@api.get("/all", tags=["Tickets"], response_model=list[Ticket])
def get_host_tickets(
    name: str | None = None,
    price: float | None = None,
    max_quantity: int | None = None,
    visibility: bool | None = None,
    registration_active: bool | None = None,
    tickets_sold: int | None = None,
    event_id: int | None = None,
    id: int | None = None,
    ticket_service: TicketService = Depends(),
    current_user: Host = Depends(registered_user),
) -> list[Ticket]:
    filters: dict[str, str | float | bool | None] = {
        "name": name,
        "price": price,
        "max_quantity": max_quantity,
        "visibility": visibility,
        "registration_active": registration_active,
        "tickets_sold": tickets_sold,
        "event_id": event_id,
        "id": id,
    }
    return ticket_service.get_tickets_by_host(filters=filters, host=current_user)


@api.get("/list", response_model=list[Ticket], tags=["Tickets"])
@dev_only
def list_tickets(ticket_service: TicketService = Depends()) -> list[Ticket]:
    return ticket_service.all()
