from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi import FastAPI
from authentication.auth_api import verify_token
import logging
from .agent import ask_openai
import time
import uuid
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

router = APIRouter()

# Dictionary to store active WebSocket connections for each user
active_connections = {}

class ConnectionManager:
    def __init__(self):
        # Key: user_id, Value: List of WebSocket connections
        self.active_connections = {}  # Store multiple connections for the same user_id

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        connection_id = str(uuid.uuid4())  # Generate a unique connection ID for each WebSocket
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][connection_id] = websocket  # Store the WebSocket with the connection_id
        return connection_id

    def disconnect(self, user_id: str, connection_id: str):
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]  # Remove the user entry if no connections remain

    async def send_personal_message(self, message: str, user_id: str, connection_id: str):
        websocket = self.active_connections.get(user_id, {}).get(connection_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for websocket in connections.values():
                await websocket.send_text(message)


manager = ConnectionManager()

'''
FIXME: When two browser windows opened with the same user session, sometimes the response from app can go to wrong window.
'''

@router.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str):
    try:
        # Verify the token and get the user ID
        payload = verify_token(token)
        logger.info(f"Token validated for user {user_id}")

        # Connect user and store the connection ID
        connection_id = await manager.connect(websocket, user_id)
        
        try:
            while True:
                start_time = time.perf_counter()

                # Receive message
                data = await websocket.receive_text()
                logger.debug(f"Message received from {user_id} on connection {connection_id}: {data}")

                # Process user message
                response = ask_openai(data)

                end_time = time.perf_counter()
                elapsed_time_ms = (end_time - start_time) * 1000
                logger.info(f"Response time for user {user_id} on connection {connection_id}: {elapsed_time_ms:.3f} ms")

                # Send the response back to the specific connection
                await manager.send_personal_message(f"{response}", user_id, connection_id)

        except WebSocketDisconnect:
            manager.disconnect(user_id, connection_id)
            logger.info(f"User {user_id} disconnected from connection {connection_id}.")

    except ValueError as ve:
        logger.error(f"Invalid token for user {user_id}: {ve}")
        await websocket.close(code=1008, reason="Invalid authentication token")

    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        await websocket.close(code=1011, reason="Internal server error")