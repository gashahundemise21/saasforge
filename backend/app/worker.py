import asyncio
from functools import wraps

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "saasforge_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)


def async_task(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


# Import tasks here so Celery registers them
import app.workers.tasks  # noqa
