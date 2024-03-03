from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .authentication import registered_user
from ..models import BaseHost, Host, ResetPasswordRequest
from ..exceptions import (
    HostStripeAccountCreationException,
    HostStripeAccountNotFoundException,
    HostAlreadyExistsError,
)
from ..services import HostService, StripeHostService
from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/hosts")
openapi_tags = {
    "name": "Hosts",
    "description": "Host management.",
}

## Frontend should have a method to automatically redirect when url is returned in content


@api.post("/register", tags=["Hosts"])
def register_host(
    new_host: BaseHost,
    host_service: HostService = Depends(),
    stripe_host_service: StripeHostService = Depends(),
) -> JSONResponse:
    try:
        host: Host = host_service.create(new_host)
    except HostAlreadyExistsError as e:
        detail = "An account with the provided email or phone number already exists."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    try:
        stripe_host_service.create_stripe_account_for_host(host.id)
    except HostStripeAccountCreationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Host registered successfully."},
    )


@api.post("/reset-password", tags=["Hosts"])
def reset_password_request(
    email: ResetPasswordRequest, host_service: HostService = Depends()
) -> JSONResponse:
    host_service.reset_password_request(email.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "An email has been sent to reset your password. Please check your inbox."
        },
    )


@api.get("/dashboard-stats", tags=["Hosts"])
def dashboard_stats(
    startDate: str,
    endDate: str,
    host_service: HostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    stats = host_service.get_dashboard_stats(current_user, startDate, endDate)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=stats,
    )


@api.get("/chart-data/revenue/{year}", tags=["Hosts"])
def revenue_chart_data(
    year: int,
    host_service: HostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    if year is None:
        year = 2023
    stats = host_service.get_revenue_year_chart_data(host=current_user, year=year)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=stats,
    )


# STRIPE ROUTES

# MOVE TO HOST REGISTRATION FOR NOW, WILL MOVE TO AFTER EMAIL VALIDATION
# @api.post("/stripe-initiate", tags=["Hosts"])
# def initiate_stripe(
#     stripe_host_service: StripeHostService = Depends(),
#     current_user: Host = Depends(registered_user),
# ) -> JSONResponse:
#     try:
#         stripe_host_service.create_stripe_account_for_host(current_user.id)
#     except HostStripeAccountCreationException as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )
#     return JSONResponse(
#         status_code=status.HTTP_201_CREATED,
#         content={"message": "Stripe onboarding initiated successfully."},
#     )


@api.get("/stripe-onboarding", tags=["Hosts"])
def stripe_onboarding(
    stripe_host_service: StripeHostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        onboarding_url: str = stripe_host_service.get_onboarding_link(current_user.id)
    except HostStripeAccountNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"url": onboarding_url},
    )


@api.get("/stripe-update", tags=["Hosts"])
def stripe_update(
    stripe_host_service: StripeHostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        update_url: str = stripe_host_service.get_update_link(current_user.id)
    except HostStripeAccountNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"url": update_url},
    )


@api.post("/stripe-status", tags=["Hosts"])
def stripe_status(
    stripe_host_service: StripeHostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        account_status: bool = stripe_host_service.is_account_enabled(current_user.id)
    except HostStripeAccountNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": account_status},
    )


@api.get("/stripe-link", tags=["Hosts"])
def stripe_login(
    stripe_host_service: StripeHostService = Depends(),
    current_user: Host = Depends(registered_user),
) -> JSONResponse:
    try:
        login_url: str = stripe_host_service.get_account_link(current_user.id)
    except HostStripeAccountNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"url": login_url},
    )


#### TESTING ROUTES ####


@api.get("/list", response_model=list[Host], tags=["Dev"])
@dev_only
def list_hosts(host_service: HostService = Depends()) -> list[Host]:
    return host_service.all()


@api.post("/set-stripe-id", tags=["Dev"])
@dev_only
def set_stripe_id(
    host_id: int,
    stripe_id: str,
    host_service: HostService = Depends(),
) -> JSONResponse:
    host_service.set_stripe_id(host_id, stripe_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Stripe account ID set successfully."},
    )


# @api.post("/reset-password", tags=["Dev"])
# @dev_only
# def reset_password(
#     host_id: int,
#     new_password: str,
#     host_service: HostService = Depends(),
# ) -> JSONResponse:
#     host_service.reset_password(host_id, new_password)
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": "Password reset successfully."},
#     )
