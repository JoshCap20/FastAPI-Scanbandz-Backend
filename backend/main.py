from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .apis import webhooks, hosts, events, authentication, tickets, guests, receipts
from .exceptions import HostPermissionError, InvalidCredentialsError
from .settings.config import MODE

description = """
This is the core v2 Scanbandz API. It is a RESTful API that provides endpoints for managing events, tickets, guests, and receipts. It also provides endpoints for user authentication and webhooks for handling Stripe payments. The API is designed to be used by both the host and guest frontends. 
"""

# Metadata to improve the usefulness of OpenAPI Docs /docs API Explorer
app = FastAPI(
    title="Scanbandz v2 API",
    version="0.2",
    description=description,
    openapi_tags=[
        webhooks.openapi_tags,
        hosts.openapi_tags,
        events.openapi_tags,
        authentication.openapi_tags,
        tickets.openapi_tags,
        guests.openapi_tags,
        receipts.openapi_tags,
    ],
)

# Allowed origins for CORS
origins = [
    "https://v2.scanbandz.com",  # Guest Frontend
    "https://v2.host.scanbandz.com",  # Host Frontend
    "https://scanbandz.com",  # Included for future domain use
]

if MODE == "development":
    origins.append("http://localhost:4200")  # Local Host Frontend
    origins.append("http://localhost:4201")  # Local Guest Frontend


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    expose_headers=["Authorization"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
api_files = [webhooks, hosts, events, authentication, tickets, guests, receipts]

for api_file in api_files:
    app.include_router(api_file.api)


# Application-wide exception handling middleware for commonly encountered API Exceptions
@app.exception_handler(HostPermissionError)
def permission_exception_handler(request: Request, e: HostPermissionError):
    return JSONResponse(status_code=404, content={"message": str(e)})


@app.exception_handler(InvalidCredentialsError)
def invalid_credentials_exception_handler(request: Request, e: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"message": str(e)})
