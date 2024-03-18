from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse


from .authentication import registered_user
from ..models import Guest, BaseGuest, Host, UpdateGuest, GuestValidation, BaseDonationRequest
from ..services import GuestService, TicketPaymentBridge, StripePaymentService
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
    NoAvailableTicketsException,
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

@api.post("/donate/{event_id}", tags=["Guests", "Stripe"])
def guest_donation(
    donation_request: BaseDonationRequest,
    event_id: int,
    stripe_payment_svc: StripePaymentService = Depends(),
) -> JSONResponse:
    """
    Create a new guest for the specified event and ticket.

    Args:
        guest (BaseGuest): The guest information.
        event_id (int): The ID of the event.
        stripe_payment_svc (StripePaymentService): The injected stripe payment service dependency.
        
    Returns:
        JSONResponse: The response containing the checkout URL.

    Raises:
        HTTPException: If the event is not found, or the host does not have a Stripe account.
    """
    try:
        checkout: str = stripe_payment_svc.create_donation_session(donation_request=donation_request, event_id=event_id)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found")
    except HostStripeAccountNotFoundException:
        raise HTTPException(
            status_code=400, detail="Host does not have a Stripe account"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StripeCheckoutSessionException:
        raise HTTPException(
            status_code=500, detail="Error creating Stripe checkout session"
        )
        
    return JSONResponse(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        content={"url": checkout},
    )
    
    

@api.post("/{event_id}/{ticket_id}/create", tags=["Guests", "Stripe"])
def create_guest(
    guest: BaseGuest,
    ticket_id: int,
    event_id: int,
    ticket_payment_bridge: TicketPaymentBridge = Depends(TicketPaymentBridge),
) -> JSONResponse:
    """
    Create a new guest for the specified event and ticket.

    Args:
        guest (BaseGuest): The guest information.
        ticket_id (int): The ID of the ticket.
        event_id (int): The ID of the event.
        ticket_payment_bridge (TicketPaymentBridge): The injected ticket payment bridge dependency.

    Returns:
        JSONResponse: The response containing the status code and message or checkout URL.

    Raises:
        HTTPException: If the ticket or event is not found, the ticket registration is full or closed, or the host does not have a Stripe account.
    """
    try:
        checkout = ticket_payment_bridge.create_guest(
            guest=guest, ticket_id=ticket_id, event_id=event_id
        )
        if isinstance(checkout, Guest):
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Guest created successfully.", "id": checkout.id},
            )
        return JSONResponse(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
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


@api.post("/validate", tags=["Guests", "Scan"])
def scan_guest_ticket(
    guestValidation: GuestValidation,
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Validate a guest ticket by scanning the QR code.

    Args:
        GuestValidation (GuestValidation): The guest and event keys.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        JSONResponse: The response containing the status code and message.

    Raises:
        HTTPException: If the guest is not found.
    """
    try:
        guest_service.validate_guest_ticket(guestValidation=guestValidation)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Ticket scanned successfully."},
        )
    except GuestNotFoundException:
        raise HTTPException(status_code=404, detail="Guest not found")
    except NoAvailableTicketsException:
        raise HTTPException(status_code=400, detail="No available tickets")


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
        JSONResponse: The response containing the status code and message or guest information.

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
                "used_quantity": guest.used_quantity,
                "event_name": guest.event.name,
                "event_start": guest.event.start.isoformat(),
                "event_end": guest.event.end.isoformat(),
                "ticket_name": guest.ticket.name,
                "public_key": guest.public_key,
                "ticket_id": guest.ticket.id,
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
        return guest_service.retrieve_guest_as_host(guest_id, current_user)
    except HostPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except GuestNotFoundException:
        raise HTTPException(status_code=404, detail="Guest not found")


@api.get("/all", tags=["Guests"])
def get_host_guests(
    searchEvent: str | None = None,
    searchAttended: str | None = None,
    searchName: str | None = None,
    searchTicket: str | None = None,
    searchPhoneNumber: str | None = None,
    searchEmail: str | None = None,
    searchEventID: int | None = None,
    searchTicketID: int | None = None,
    current_user: Host = Depends(registered_user),
    guest_service: GuestService = Depends(),
) -> JSONResponse:
    """
    Retrieve all guests or those matching filter for the host.

    TODO: Pagination

    Args:
        filters (optional): The filters to apply to the query.
        current_user (registered_user): The host information.
        guest_service (GuestService): The injected guest service dependency.

    Returns:
        list[Guest]: The list of guests.
    """
    # TODO: Move to pydantic model, add pagination
    filters: dict[str, str | None] = {
        "searchEvent": searchEvent,
        "searchAttended": searchAttended,
        "searchName": searchName,
        "searchTicket": searchTicket,
        "searchPhoneNumber": searchPhoneNumber,
        "searchEmail": searchEmail,
        "searchEventID": searchEventID,
        "searchTicketID": searchTicketID,
    }

    # FOR BULK SEARCH ONLY RETURN: id, first_name, last_name, phone_number, email, quantity, used_quantity, event_id, ticket_id, scan_timestamp, ticket_name, event_name
    guests: list[Guest] = guest_service.get_guests_by_host(current_user, filters)

    return [
        {
            "id": guest.id,
            "first_name": guest.first_name,
            "last_name": guest.last_name,
            "phone_number": guest.phone_number,
            "email": guest.email,
            "quantity": guest.quantity,
            "used_quantity": guest.used_quantity,
            "event_id": guest.event.id,
            "ticket_id": guest.ticket.id,
            "scan_timestamp": (guest.scan_timestamp if guest.scan_timestamp else None),
            "ticket_name": guest.ticket.name,
            "event_name": guest.event.name,
        }
        for guest in guests
    ]


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
