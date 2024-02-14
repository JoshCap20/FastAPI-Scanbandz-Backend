from fastapi import APIRouter

from ..settings.logging import AsyncLogger

api = APIRouter(prefix="/api/webhook", tags=["webhooks"])
openapi_tags = {
    "name": "Webhook",
    "description": "Handle webhooks.",
}

@api.get("/")
async def sample():
    await AsyncLogger.log_info("webhooks", "Hello World")
    return [{"username": "Foo"}, {"username": "Bar"}]