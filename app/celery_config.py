# Celery configuration
from celery import Celery

# Configure Celery with Redis as broker and backend
celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # Track task start events
    task_acks_late=True,     # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reschedule tasks if worker dies
    broker_connection_retry_on_startup=True,
)   