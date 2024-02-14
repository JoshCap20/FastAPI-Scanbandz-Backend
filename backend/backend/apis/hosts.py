from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ..models import BaseHost
from ..services.host_service import HostService

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
        host = host_service.create(host)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # except Exception as e:
    #     # TODO: Create specific exception for Host already exists
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Host already exists")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Host registered successfully."},
    )
