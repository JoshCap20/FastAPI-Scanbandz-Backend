from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .apis import webhooks, hosts, events, authentication
from .exceptions import HostPermissionError

description = """
This is the Scanbandz API.
"""

# Metadata to improve the usefulness of OpenAPI Docs /docs API Explorer
app = FastAPI(
    title="Scanbandz API",
    version="0.0.1",
    description=description,
    openapi_tags=[
        webhooks.openapi_tags,
        hosts.openapi_tags,
        events.openapi_tags,
        authentication.openapi_tags,
    ],
)

origins = [
    "http://localhost:8000",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    expose_headers=["Authorization"],
    allow_methods=["*"],
    allow_headers=["*"],
)

feature_apis = [webhooks, hosts, events, authentication]

for feature_api in feature_apis:
    app.include_router(feature_api.api)


# Application-wide exception handling middleware for commonly encountered API Exceptions
@app.exception_handler(HostPermissionError)
def permission_exception_handler(request: Request, e: HostPermissionError):
    return JSONResponse(status_code=404, content={"message": str(e)})
