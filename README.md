# 📖 Introduction
This project is a real-time task processing system designed to handle long-running tasks with live progress updates. Built using FastAPI, Celery, Redis, WebSockets, and Docker, this project showcases a scalable solution for managing asynchronous tasks and delivering their progress to clients in real-time. The system allows users to start a task, track its progress in real-time through a web interface, and reconnect to ongoing tasks even after disconnection. It's perfect for scenarios where you need to process time-consuming operations (e.g., data processing, file uploads) while keeping users informed about the status.

## Purpose
The goal of this project is to demonstrate how to:

- Process long-running tasks asynchronously using Celery.
- Store task states in Redis for reliability.
- Deliver real-time updates to clients via WebSockets.
- Ensure clients can reconnect and retrieve the latest task state.

## Target Audience
- Developers learning about asynchronous task processing and real-time communication involving websockets.
- Teams building applications requiring live updates for background jobs.

# 🛠️ Pre-requisites
Before setting up the project, ensure you have the following tools and knowledge:

## Software Requirements
- Docker and Docker Compose: To run the application in containers (version 20.10 or higher recommended).
- Python 3.9+: If you want to run the app without Docker or modify the code.
- Node.js (optional): To use wscat for WebSocket testing (npm install -g wscat).
- Git: To clone the repository.
- A modern web browser (e.g., Chrome, Firefox) to access the web interface.

## Knowledge Requirements
- Basic understanding of Python and JavaScript.
- Familiarity with Docker and containerized applications.
- Awareness of asynchronous programming and WebSockets (not mandatory but helpful).

## Hardware Requirements
- At least 2 GB of free RAM for Docker containers.
- Stable internet connection (for pulling Docker images).

# ⚙️ Setting Up
Follow these steps to set up and run the project on your machine. We'll use Docker to simplify the process, but I'll also include steps for running without Docker.

## 1. Clone the Repository
Clone the project to your local machine:

```bash
git clone <repository-url>
cd task-1
```

## 2. Set Up Docker (Recommended)
### Prerequisites
Ensure Docker and Docker Compose are installed:
```bash
docker --version
docker-compose --version
```

### Steps
Create a Dockerfile (if not already present):
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Create a docker-compose.yml:
```yaml
version: '3.8'
services:
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - PYTHONUNBUFFERED=1
  worker:
    build: .
    command: celery -A app.celery_config.celery_app worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
    environment:
      - PYTHONUNBUFFERED=1
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
```

Build and Run the Containers:
```bash
sudo docker-compose up --build
```

This starts three services: web (FastAPI), worker (Celery), and redis.
The FastAPI server will be accessible at http://127.0.0.1:8000.

### Note for WSL Users
If you're on Windows Subsystem for Linux (WSL), 127.0.0.1 might not work from your browser due to networking. Use your WSL IP instead:
```bash
ip addr show eth0 | grep inet
```
Replace 127.0.0.1 with the WSL IP (e.g., 172.18.0.1) in the browser.

## 3. Set Up Without Docker (Optional)

### For Local Development Without Docker

#### Steps

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Redis**:
   - Install and start Redis locally:
     ```bash
     sudo apt-get install redis-server
     sudo systemctl start redis
     ```
   - Or use Docker for Redis:
     ```bash
     docker run -d -p 6379:6379 redis:6-alpine
     ```

3. **Run the FastAPI Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Run the Celery Worker**:
   - Open a new terminal:
     ```bash
     celery -A app.celery_config.celery_app worker --loglevel=info
     ```

5. **Access the App**:
   - Open http://127.0.0.1:8000 in your browser.

# ✨ Features
This project includes the following features to ensure a robust and user-friendly experience:

## Asynchronous Task Processing:
Long-running tasks are processed in the background using Celery, preventing the main application from blocking.

## Real-Time Updates:
Task progress is updated live via WebSockets, showing stages like "PENDING," "STARTED," "PROCESSING," and "COMPLETED."

## Dual Task Option:
  - Start New Task: Initiate a new task with a unique ID.
  - Observe Existing Task: Monitor an ongoing task by entering its ID.

## Concurrent Task Monitoring:
Multiple tasks can be observed simultaneously at different tabs of the browser, with updates appended to the status display.

## Reliable State Management:
Task states are stored in Redis, ensuring data persistence even if the client disconnects.

## Client Reconnection:
Clients can reconnect to an ongoing task and retrieve the latest state, thanks to Redis storage and WebSocket reconnection logic.

## Simple Web Interface:
A minimal HTML page (index.html) allows users to start tasks and view progress in real-time.

## Dockerized Deployment:
The entire application runs in Docker containers for easy setup and scalability.

## Error Handling:
Basic error handling in the client (JavaScript) and server (FastAPI) ensures users are informed of issues like WebSocket errors.

## Logging:
Detailed logs from Celery and FastAPI help with debugging and monitoring.

# 📂 Project Structure
Here's an overview of the project's file structure to help you navigate the codebase:

```
task-1/
│
├── app/
│   ├── __init__.py           # Marks the app directory as a Python package
│   ├── main.py              # FastAPI application with WebSocket and task endpoints
│   ├── celery_config.py     # Celery configuration and app initialization
│   ├── tasks.py             # Celery task definitions (e.g., long_running_task)
│   └── index.html           # Web interface for starting tasks and viewing updates
│
├── Dockerfile               # Docker configuration for building the app image
├── docker-compose.yml       # Docker Compose configuration for multi-container setup
├── README.md                # Project documentation (this file)
└── requirements.txt         # Python dependencies
```

## File Details
- **app/main.py**: Contains the FastAPI application, including:
  - The root endpoint (/) to serve index.html.
  - The /start-task endpoint to initiate tasks.
  - The /ws/task/{task_id} WebSocket endpoint for real-time updates.
- **app/celery_config.py**: Sets up the Celery app with Redis as the broker and result backend.
- **app/tasks.py**: Defines the long_running_task that simulates a long-running process with stages.
- **app/index.html**: A simple HTML page with JavaScript to start tasks and display progress via WebSocket.
- **docker-compose.yml**: Orchestrates the web, worker, and redis services with port mapping (8000:8000).

# 🏗️ System Architecture
The system is designed as a distributed application with components interacting to process tasks and deliver updates. Here's a high-level overview:

## Components
### FastAPI Server (web service):
- Handles HTTP and WebSocket requests.
- Serves the web interface (index.html).
- Initiates tasks by sending them to Celery.
- Listens for Redis Pub/Sub messages and forwards updates to clients via WebSocket.

### Celery Worker (worker service):
- Processes tasks asynchronously in the background.
- Updates task states in Redis and publishes updates to Redis Pub/Sub.

### Redis (redis service):
- Acts as the message broker for Celery (task queue).
- Stores task states (status, progress, timestamp) for persistence.
- Uses Pub/Sub to broadcast task updates to the FastAPI server.

### Client (Browser):
- Displays the web interface (index.html).
- Starts tasks via HTTP requests and receives real-time updates via WebSocket.

## Architecture Diagram (Conceptual)
```
[Client (Browser)] <--> [FastAPI Server (WebSocket/HTTP)]
        |                        |
        |                        |
        |                  [Celery Worker]
        |                        |
        |                        |
       [Redis (Broker/State/PubSub)]
```

- Client <--> FastAPI: HTTP (/start-task) to initiate tasks, WebSocket (/ws/task/{task_id}) for updates.
- FastAPI <--> Celery: FastAPI sends tasks to Celery via Redis.
- Celery <--> Redis: Celery updates task states in Redis and publishes updates.
- FastAPI <--> Redis: FastAPI listens to Redis Pub/Sub to get updates and forwards them to the client.

# 🔄 Entire Workflow

## 1. User Interaction
- The user accesses http://127.0.0.1:8000, loading index.html.
- Options:
  - **Start New Task**: Click "Start New Task" to initiate a task.
  - **Observe Existing Task**: Enter a task_id and click "Observe Task" to monitor an ongoing task.

## 2. Starting a New Task
- **Client (index.html)**:
  - Sends a POST request to /start-task.
- **FastAPI (main.py)**:
  - Generates a task_id (e.g., e2f62903-48f4-4ae1-b607-15608c935a50).
  - Initializes Redis with status: PENDING, progress: 0.
  - Triggers long_running_task.delay(task_id).
  - Returns task_id to the client.
- **Client**:
  - Displays Current Task ID: <task_id>.
  - Connects to ws://127.0.0.1:8000/ws/task/<task_id>.

## 3. Observing an Existing Task
- **Client**:
  - Enters a task_id and clicks "Observe Task".
  - Displays Current Task ID: <entered_task_id>.
  - Connects to ws://127.0.0.1:8000/ws/task/<entered_task_id>.
- **FastAPI**:
  - Accepts the WebSocket and sends the current Redis state.

## 4. Task Processing
- **Celery Worker (tasks.py)**:
  - Executes long_running_task for 20 seconds (4 stages, 5 seconds each).
  - Updates Redis with stages ("STARTED," "PROCESSING," "CONCLUDING," "COMPLETED") and progress (25%, 50%, 75%, 100%).
  - Publishes each stage to Redis Pub/Sub.
  - Logs progress to console (e.g., i: 0, stage: STARTED).

## 5. Real-Time Updates
- **FastAPI**:
  - Listens to Redis Pub/Sub (task:{task_id}:updates).
  - Sends updates to the client via WebSocket when the current task_id matches.
- **Client**:
  - Appends updates to the status div (e.g., "Task: <task_id>, Status: PROCESSING, Progress: 50%").
  - Scrolls to the latest update.

## 6. Disconnection and Reconnection
- If the WebSocket closes (e.g., server restart):
  - Client displays "Disconnected from <task_id>. Reconnecting..."
  - Reconnects after 5 seconds to the same task_id.
  - Redis ensures the latest state is available for reconnection.

## 7. Task Completion
- Task finishes with "COMPLETED, 100%," and the client sees the final update.

# 📝 Usage

## Starting a New Task
1. Open http://127.0.0.1:8000 in your browser.
2. Click "Start New Task" button.
3. Note the task_id displayed and watch updates:

```
Current Task ID: e2f62903-48f4-4ae1-b607-15608c935a50
Task: e2f62903-48f4-4ae1-b607-15608c935a50, Status: STARTED, Progress: 25%
Task: e2f62903-48f4-4ae1-b607-15608c935a50, Status: PROCESSING, Progress: 50%
...
```

## Observing an Existing Task
1. Start a task and note its task_id.
2. Enter the task_id in the input field.
3. Click "Observe Task" to see its current and future updates.

## Concurrent Monitoring
- Start multiple tasks or observe different task_ids.
- Updates for each task are appended to the status display.
- Each task progress is tracked independently.

# 🧪 Testing

## Test Scenarios

### New Task:
- Start a task and verify all stages appear.

### Existing Task:
- Observe a running task with its task_id and check updates.

### Reconnection:
- Stop the web service (docker-compose stop web) during a task.
- Verify "Disconnected. Reconnecting..." and reconnection after 5 seconds.
- Restart the service (sudo docker-compose start web) and verify if updates are showing as it was supposed to.

### Concurrency:
- Start two tasks and observe both sets of updates.

## Tools for Testing

### Browser Console: 
- Check for WebSocket errors (right-click > Inspect > Console).

### Docker Logs: 
- Debug with:
  ```bash
  docker-compose logs
  ```

### Redis CLI: 
- Inspect task states:
  ```bash
  docker exec -it task-1-redis-1 redis-cli
  HGETALL task:<task_id>
  ```

# 🐞 Troubleshooting

## Common Issues

### No Updates:
- **Symptom**: task_id appears, but no progress.
- **Fix**: Ensure worker and redis are running (`docker ps`).

### WebSocket Errors:
- **Symptom**: "WebSocket error" in console.
- **Fix**: Verify 127.0.0.1:8000 or use WSL IP if needed.

### Task Not Starting:
- **Symptom**: No task_id or errors.
- **Fix**: Check main.py logs and ensure Celery is active.

## Debugging Tips
- Add print statements in tasks.py for task stages.
- Use browser "Network" tab to monitor WebSocket.

# 🚀 Future Improvements
- **Persistent Task List**: Display a list of past and current tasks.
- **Progress Bar**: Add a visual progress bar in index.html.
- **Authentication**: Secure task initiation with user login.
- **Custom Task Duration**: Allow users to set task length.
- **Error Recovery**: Enhance reconnection with retry logic.

# 📚 Resources
- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryproject.org/)
- [Redis](https://redis.io/)
- [Docker Compose](https://docs.docker.com/compose/)

# 🤝 Contributing
1. Fork the repository.
2. Create a branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push and submit a pull request.

# 📧 Contact
For support, contact adidra10@gmail.com

# ⚖️ License
MIT License. See LICENSE file for details.