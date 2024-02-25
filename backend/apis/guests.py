from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse


from .authentication import registered_user
from ..models import Guest, BaseGuest, Host, UpdateGuest
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
    StripeCheckoutSessionException,
    HostPermissionError,
)

api = APIRouter(prefix="/api/guests")
openapi_tags = {
    "name": "Guests",
    "description": "Guest management.",
}


@api.post("/{event_id}/{ticket_id}/host-create", tags=["Guests"])
def host_create_guest(
    guest: BaseGuest,
    ticket_id: int,
    event_id: int,
    current_user: Host = Depends(registered_user),
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Create a new guest for the specified event and ticket on behalf of the host.

    Args:
        guest (BaseGuest): The guest information.
        ticket_id (int): The ID of the ticket.
        event_id (int): The ID of the event.
        current_user (Host): The injected current user.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message.

    Raises:
        HTTPException: If the ticket or event is not found.
    """
    try:
        guest = guest_service.create_guest_by_host(
            guest=guest, ticket_id=ticket_id, event_id=event_id, host=current_user
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Guest created successfully.", "id": guest.id},
        )
    except (TicketNotFoundException, EventNotFoundException):
        raise HTTPException(status_code=404, detail="Ticket or Event not found")
    except HostPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            content={"url": checkout},
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
    except StripeCheckoutSessionException:
        raise HTTPException(
            status_code=500, detail="Error creating Stripe checkout session"
        )


@api.put("/host-update", tags=["Guests"])
def update_guest_by_host(
    guest: UpdateGuest,
    current_user: Host = Depends(registered_user),
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Update a guest by the host.

    Args:
        guest_id (int): The ID of the guest.
        guest (BaseGuest): The updated guest information.
        current_user (Host): The injected current user.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message.

    Raises:
        HTTPException: If the guest is not found or the host does not have permission.
    """
    try:
        guest_service.update_guest_by_host(guest, current_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Guest updated successfully."},
        )
    except GuestNotFoundException:
        raise HTTPException(status_code=404, detail="Guest not found")
    except HostPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.get("/{event_key}/{guest_key}/retrieve", tags=["Guests"])
def retrieve_guest(
    event_key: str,
    guest_key: str,
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Retrieve a guest by event and ticket key.

    Args:
        event_key (str): The key of the event.
        guest_key (str): The key of the guest.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        Guest: The response containing the status code and message or guest information.

    Raises:
        HTTPException: If the guest is not found.
    """
    try:
        guest: Guest = guest_service.retrieve_guest_ticket(
            event_key=event_key, guest_key=guest_key
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "first_name": guest.first_name,
                "last_name": guest.last_name,
                "quantity": guest.quantity,
                "used_quantity": 1,
                "event_name": guest.event.name,
                "event_start": guest.event.start.isoformat(),
                "event_end": guest.event.end.isoformat(),
                "ticket_name": guest.ticket.name,
                "public_key": guest.public_key,
            },
        )

    except GuestNotFoundException:
        raise HTTPException(status_code=404, detail="Guest not found")


@api.get("/retrieve/{guest_id}", response_model=Guest, tags=["Guests"])
def host_retrieve_guest(
    guest_id: int,
    current_user: Host = Depends(registered_user),
    guest_service: GuestService = Depends(),
) -> Guest:
    """
    Retrieve a guest by id on behalf of the host.

    Args:
        guest_id (int): The ID of the guest.
        current_user (Host): The injected current user.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        Guest: The guest object.

    Raises:
        HTTPException: If the guest is not found or the host does not have permission.
    """
    try:
        return guest_service.retrieve_guest_by_host(guest_id, current_user)
    except HostPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except GuestNotFoundException:
        raise HTTPException(status_code=404, detail="Guest not found")


@api.get("/all", response_model=list[Guest], tags=["Guests"])
def get_host_guests(
    current_user: Host = Depends(registered_user),
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Retrieve all guests for the host.

    Args:
        current_user (registered_user): The host information.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        list[Guest]: The list of guests.
    """
    return guest_service.get_guests_by_host(current_user)


### DEV ONLY ###
@api.get("/admin-all", tags=["Dev"], response_model=list[Guest])
@dev_only
def get_all_guests(guest_service: GuestService = Depends()) -> list[Guest]:
    """
    Dev Only
    Retrieve all guests.

    Args:
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message or guest information.
    """
    return guest_service.all()


@api.get("/get-ticket-sample", tags=["Dev"])
@dev_only
def get_random_guest(guest_service: GuestService = Depends()) -> JSONResponse:
    """
    Dev Only
    Retrieve a random guest.

    Args:
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message or guest information.
    """
    guest: Guest = guest_service.all()[0]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"guest_key": guest.public_key, "event_key": guest.event.public_key},
    )
