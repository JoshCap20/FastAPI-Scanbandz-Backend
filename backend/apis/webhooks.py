from fastapi import APIRouter, Depends, HTTPException, status

from settings.logging import AsyncLogger

router = APIRouter(
    prefix="/wh",
    tags=["webhooks"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def sample():
    await AsyncLogger.log_info("webhooks", "Hello World")
    return [{"username": "Foo"}, {"username": "Bar"}]