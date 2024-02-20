from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from ..models import BaseHost, Host
from ..services import HostService
from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/hosts")
openapi_tags = {
    "name": "Hosts",
    "description": "Host management.",
}


@api.post("/register", tags=["Hosts"])
def register_host(
    new_host: BaseHost, host_service: HostService = Depends()
) -> JSONResponse:
    try:
        host: Host = host_service.create(new_host)
    except IntegrityError as e:
        detail = "An account with the provided email or phone number already exists."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Host registered successfully."},
    )


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


@api.post("/reset-password", tags=["Dev"])
@dev_only
def reset_password(
    host_id: int,
    new_password: str,
    host_service: HostService = Depends(),
) -> JSONResponse:
    host_service.reset_password(host_id, new_password)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset successfully."},
    )
