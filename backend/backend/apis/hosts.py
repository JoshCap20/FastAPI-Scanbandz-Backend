from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from ..models import BaseHost, Host
from ..entities import HostEntity
from ..services.host_service import HostService
from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/hosts")
openapi_tags = {
    "name": "Hosts",
    "description": "Host management.",
}


@api.post("/register", tags=["Hosts"])
def register_host(
    host: BaseHost, host_service: HostService = Depends()
) -> JSONResponse:
    try:
        host: Host = host_service.create(host)
    except IntegrityError as e:
        detail = "An account with the provided email or phone number already exists."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Host registered successfully."},
    )


@api.get("/list", response_model=list[Host], tags=["Hosts"])
@dev_only
def list_hosts(host_service: HostService = Depends()) -> list[Host]:
    return host_service.all()
