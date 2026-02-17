from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager
from app.services.redis_broker import broker
import asyncio

# 1. Background Task Manager (Lifespan)
# This runs BEFORE the app starts accepting requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the "Listener" task in the background
    # This listens to the "global_chat" channel on Redis
    task = asyncio.create_task(broker.subscribe("global_chat"))
    yield
    # Clean up when app shuts down
    task.cancel()

# 2. Initialize App
app = FastAPI(lifespan=lifespan)

# 3. The WebSocket Endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # A. Accept the connection
    await manager.connect(websocket)
    
    try:
        while True:
            # B. Wait for message from Client (You)
            data = await websocket.receive_text()
            
            # C. Publish to Redis (The "Cloud")
            # Instead of sending directly to other users, we send to Redis.
            # Redis then tells the Background Task (on all servers) to broadcast it.
            message = {"user": f"User {client_id}", "content": data}
            await broker.publish("global_chat", message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Optional: Notify others that user left
        await broker.publish("global_chat", {"user": "System", "content": f"User {client_id} left."})

# 4. Health Check (for AWS Load Balancer)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}