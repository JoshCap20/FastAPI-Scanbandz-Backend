import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from ..settings.env import getenv
from ..services import HostService
from ..exceptions import InvalidCredentialsError, HostNotFoundException
from ..models import Host, LoginCredentials

from ..utils.dev_only import dev_only

api = APIRouter(prefix="/api/auth")
openapi_tags = {
    "name": "Authentication",
    "description": "APIs for authenticating users and managing user sessions",
}

_JWT_SECRET = getenv("JWT_SECRET")
_JWT_ALGORITHM = "HS256"


def registered_user(
    host_service: HostService = Depends(),
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer()),
) -> Host:
    """Returns the authenticated user or raises a 401 HTTPException if the user is not authenticated."""
    if token:
        try:
            auth_info = jwt.decode(
                token.credentials, _JWT_SECRET, algorithms=[_JWT_ALGORITHM]
            )
            user = host_service.get_by_id(auth_info["user_id"])
            if user:
                return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    raise HTTPException(status_code=401, detail="Unauthorized")


@api.post("/login", tags=["Authentication"], response_model=dict[str, str])
def authenticate_user(
    credentials: LoginCredentials, host_service: HostService = Depends()
) -> dict[str, str]:
    # Delegate login logic to the UserService
    try:
        user_id, phone_number = host_service.authenticate_user(credentials)  # type: ignore
    except (InvalidCredentialsError, HostNotFoundException):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create a JWT token with the user's id and phone number
    token = jwt.encode(
        {
            "user_id": user_id,
            "phone_number": phone_number,
            "exp": datetime.utcnow() + timedelta(days=1),
        },
        _JWT_SECRET,
        algorithm=_JWT_ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}


@api.get("/protected", tags=["Authentication"])
@dev_only
def protected_route(current_user: Host = Depends(registered_user)):
    # This is a protected route example for testing purposes
    return {"message": "You are authorized to access this route", "user": current_user}
