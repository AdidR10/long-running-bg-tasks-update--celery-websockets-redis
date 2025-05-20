# FastAPI app with WebSocket and HTTP endpoints
import uuid
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from redis import Redis
import aioredis
from app.tasks import long_running_task
import time

app = FastAPI()

# Initialize Redis client
redis_client = Redis(host="redis", port=6379, db=0)

# Store active WebSocket connections
active_connections = {}

@app.get("/")
async def get_index():
    return FileResponse("app/index.html")

@app.post("/start-task")
async def start_task():
    """Start a long-running task and return task ID."""
    task_id = str(uuid.uuid4())
    # Initialize task state in Redis
    redis_client.hset(f"task:{task_id}", mapping={
        "status": "PENDING",
        "progress": 0,
        "timestamp": str(time.time())
    })                         
    # Trigger Celery task
    long_running_task.delay(task_id)
    return JSONResponse({"task_id": task_id})

@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """Handle WebSocket connection for task updates."""
    await websocket.accept()
    # Store WebSocket connection
    if task_id not in active_connections:
        active_connections[task_id] = []
    active_connections[task_id].append(websocket)

    # Create Redis Pub/Sub client
    redis_pubsub = aioredis.Redis.from_url("redis://redis:6379/0")
    pubsub = redis_pubsub.pubsub()
    await pubsub.subscribe(f"task:{task_id}:updates")

    try:
        # Send current task state
        task_state = redis_client.hgetall(f"task:{task_id}")
        if task_state:
            await websocket.send_json({
                "task_id": task_id,
                "status": task_state.get(b"status", b"").decode(),
                "progress": int(task_state.get(b"progress", b"0").decode()),
                "timestamp": float(task_state.get(b"timestamp", b"0").decode())
            })

        # Listen for Redis Pub/Sub updates
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Fetch updated state from Redis
                task_state = redis_client.hgetall(f"task:{task_id}")
                await websocket.send_json({
                    "task_id": task_id,
                    "status": task_state.get(b"status", b"").decode(),
                    "progress": int(task_state.get(b"progress", b"0").decode()),
                    "timestamp": float(task_state.get(b"timestamp", b"0").decode())
                })
        # long_running_task.delay(task_id)
    except WebSocketDisconnect:
        # Remove WebSocket on disconnect
        active_connections[task_id].remove(websocket)
        if not active_connections[task_id]:
            del active_connections[task_id]
    finally:
        # Clean up Redis Pub/Sub
        await pubsub.unsubscribe(f"task:{task_id}:updates")
        await redis_pubsub.close()