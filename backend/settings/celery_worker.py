from celery import Celery
from .config import MODE, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Celery instance for handling background tasks
celery_app = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.autodiscover_tasks(['backend.communication'])