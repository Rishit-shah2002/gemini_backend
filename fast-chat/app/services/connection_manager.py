from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # List to store active connections in memory
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_local(self, message: str):
        """
        Sends a message ONLY to clients connected to THIS server instance.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Handle broken pipes (client disconnected abruptly)
                pass

# Global instance
manager = ConnectionManager()