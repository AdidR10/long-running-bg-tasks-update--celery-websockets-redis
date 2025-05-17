# Celery task definitions
import time
from celery import Celery
from redis import Redis

# Initialize Celery (import from celery_config)
from app.celery_config import celery_app

# Initialize Redis client for state management
redis_client = Redis(host="localhost", port=6379, db=0)

@celery_app.task(bind=True)
def long_running_task(self, task_id: str):
    """Simulate a long-running task and update status in Redis."""
    stages = ["PENDING", "STARTED", "PROCESSING", "COMPLETED"]
    for i, stage in enumerate(stages):
        # Update task status in Redis
        redis_client.hset(f"task:{task_id}", "status", stage)
        redis_client.hset(f"task:{task_id}", "progress", i * 25)
        redis_client.hset(f"task:{task_id}", "timestamp", time.time())
        # Publish update to Redis Pub/Sub channel for WebSocket broadcasting
        redis_client.publish(f"task:{task_id}:updates", stage)
        # Simulate work
        time.sleep(5)
    return {"task_id": task_id, "status": "COMPLETED", "progress": 100}