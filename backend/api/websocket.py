from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import logging
from datetime import datetime
import asyncio

from models.agent import AgentState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": datetime.now().isoformat(),
        }

        logger.info(
            f"WebSocket connected: {self.connection_data[websocket]['client_id']}"
        )

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "client_id": self.connection_data[websocket]["client_id"],
                "timestamp": datetime.now().isoformat(),
            },
            websocket,
        )

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            client_info = self.connection_data.get(websocket, {})
            client_id = client_info.get("client_id", "unknown")

            self.active_connections.remove(websocket)
            if websocket in self.connection_data:
                del self.connection_data[websocket]

            logger.info(f"WebSocket disconnected: {client_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return

        message_text = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_agent_update(self, agent_update: dict):
        """Broadcast an agent status update to all clients."""
        message = {
            "type": "agent_update",
            "data": agent_update,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat(),
                    },
                    websocket,
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_websocket_message(message: dict, websocket: WebSocket):
    """Handle incoming WebSocket messages from clients."""
    message_type = message.get("type")

    if message_type == "ping":
        # Heartbeat response
        await manager.send_personal_message(
            {"type": "pong", "timestamp": datetime.now().isoformat()}, websocket
        )

    elif message_type == "start_agent":
        agent_id = message.get("agent_id")
        config = message.get("config", {})

        if not agent_id:
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": "agent_id is required for start_agent command",
                    "timestamp": datetime.now().isoformat(),
                },
                websocket,
            )
            return

        # TODO: Implement agent starting logic
        # For now, send acknowledgment
        await manager.send_personal_message(
            {
                "type": "command_received",
                "command": "start_agent",
                "agent_id": agent_id,
                "message": "Agent start command received (not implemented yet)",
                "timestamp": datetime.now().isoformat(),
            },
            websocket,
        )

        logger.info(f"Received start_agent command for {agent_id}")

    elif message_type == "stop_agent":
        agent_id = message.get("agent_id")

        if not agent_id:
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": "agent_id is required for stop_agent command",
                    "timestamp": datetime.now().isoformat(),
                },
                websocket,
            )
            return

        # TODO: Implement agent stopping logic
        # For now, send acknowledgment
        await manager.send_personal_message(
            {
                "type": "command_received",
                "command": "stop_agent",
                "agent_id": agent_id,
                "message": "Agent stop command received (not implemented yet)",
                "timestamp": datetime.now().isoformat(),
            },
            websocket,
        )

        logger.info(f"Received stop_agent command for {agent_id}")

    else:
        await manager.send_personal_message(
            {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.now().isoformat(),
            },
            websocket,
        )


def create_agent_update(
    agent_id: str,
    status: AgentState,
    progress: int = 0,
    message: str = "",
    data: dict = None,
) -> dict:
    """Create a standardized agent update message."""
    return {
        "agentId": agent_id,
        "status": status.value,
        "progress": progress,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat(),
    }
