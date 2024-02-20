from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse


from .authentication import registered_user
from ..models import Guest, BaseGuest
from ..services import GuestService
from ..utils.dev_only import dev_only
from ..exceptions import (
    GuestNotFoundException,
    TicketNotFoundException,
    EventNotFoundException,
    IllegalGuestOperationException,
    TicketRegistrationClosedException,
    HostStripeAccountNotFoundException,
    TicketRegistrationFullException,
)

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
    """
    Create a new guest for the specified event and ticket.

    Args:
        guest (BaseGuest): The guest information.
        ticket_id (int): The ID of the ticket.
        event_id (int): The ID of the event.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message or checkout URL.

    Raises:
        HTTPException: If the ticket or event is not found, the ticket registration is full or closed, or the host does not have a Stripe account.
    """
    try:
        checkout = guest_service.create_guest(
            guest=guest, ticket_id=ticket_id, event_id=event_id
        )
        if isinstance(checkout, Guest):
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Guest created successfully.", "id": checkout.id},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"checkout_url": checkout},
        )
    except (TicketNotFoundException, EventNotFoundException):
        raise HTTPException(status_code=404, detail="Ticket or Event not found")
    except TicketRegistrationFullException:
        raise HTTPException(status_code=400, detail="Ticket registration is full")
    except TicketRegistrationClosedException:
        raise HTTPException(status_code=400, detail="Ticket registration is closed")
    except HostStripeAccountNotFoundException:
        raise HTTPException(
            status_code=400, detail="Host does not have a Stripe account"
        )
    except IllegalGuestOperationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
