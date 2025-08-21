from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Union
import json
import logging
from datetime import datetime
import asyncio

# Define AgentState enum locally since we removed legacy models
from enum import Enum

# Import Orchestra components
from orchestra.agents.construction_agent import ConstructionAgent
from orchestra.agents.email_agent import EmailAgent
from orchestra.tools.construction_tools import MSProjectTools

class AgentState(Enum):
    """Agent states for WebSocket updates."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

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

        # Start real Orchestra agent execution
        try:
            await start_orchestra_agent(agent_id, message, websocket)
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": f"Failed to start agent {agent_id}: {str(e)}",
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

        # Stop real Orchestra agent execution
        try:
            await stop_orchestra_agent(agent_id, websocket)
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": f"Failed to stop agent {agent_id}: {str(e)}",
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


# Global storage for active agents
active_agents: Dict[str, ConstructionAgent] = {}
agent_tasks: Dict[str, asyncio.Task] = {}


async def start_orchestra_agent(agent_id: str, message: Dict[str, Any], websocket: WebSocket):
    """Start an Orchestra construction agent with real browser automation."""
    try:
        agent_type = message.get("agent_type", "msproject")
        task_type = message.get("task_type", "extract_project_data")
        config = message.get("config", {})
        
        logger.info(f"Starting Orchestra agent {agent_id} of type {agent_type}")
        
        # Send initial status update
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.RUNNING, 0, "Initializing agent..."),
            websocket
        )
        
        # Create appropriate agent based on type
        if agent_type == "email":
            # Create email agent
            agent = EmailAgent(
                name=f"Email Agent {agent_id}",
                agent_id=agent_id
            )
            
            # Initialize email agent with configuration
            email_config = config.get("email_config", {})
            init_success = await agent.initialize(email_config)
            if not init_success:
                raise Exception("Failed to initialize email agent")
            
        else:
            # Create browser-based construction agent
            if agent_type == "msproject":
                platform = "msproject"
            elif agent_type == "procore":
                platform = "procore"
            elif agent_type == "autodesk":
                platform = "autodesk"
            elif agent_type == "primavera":
                platform = "primavera"
            else:
                platform = "demo"
            
            # Create and initialize agent
            agent = ConstructionAgent(
                name=f"{platform.title()} Agent {agent_id}",
                platform=platform,
                agent_id=agent_id
            )
        
        # Store active agent
        active_agents[agent_id] = agent
        
        # Create task context for execution
        task_context = {
            "task_type": task_type,
            "parameters": {
                "project_id": config.get("projectId", "demo-project"),
                "data_types": config.get("extractionType", ["all"]),
                **config
            }
        }
        
        # Start agent execution in background task
        task = asyncio.create_task(
            execute_agent_with_progress(agent, task_context, agent_id, websocket)
        )
        agent_tasks[agent_id] = task
        
        # Send confirmation
        await manager.send_personal_message(
            {
                "type": "agent_started",
                "agent_id": agent_id,
                "agent_type": agent_type,
                "task_type": task_type,
                "message": f"Agent {agent_id} started successfully",
                "timestamp": datetime.now().isoformat(),
            },
            websocket
        )
        
        logger.info(f"Orchestra agent {agent_id} started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start Orchestra agent {agent_id}: {e}")
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.ERROR, 0, f"Failed to start: {str(e)}"),
            websocket
        )
        raise


async def stop_orchestra_agent(agent_id: str, websocket: WebSocket):
    """Stop a running Orchestra agent."""
    try:
        # Cancel running task if exists
        if agent_id in agent_tasks:
            task = agent_tasks[agent_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del agent_tasks[agent_id]
        
        # Clean up agent
        if agent_id in active_agents:
            agent = active_agents[agent_id]
            
            # Clean up based on agent type
            if isinstance(agent, EmailAgent):
                await agent.stop()
            elif hasattr(agent, 'tools') and 'msproject' in agent.tools:
                # Close browser if it exists
                ms_project_tool = agent.tools['msproject']
                if hasattr(ms_project_tool, 'browser'):
                    await ms_project_tool.browser.close()
            
            del active_agents[agent_id]
        
        # Send status update
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.IDLE, 0, "Agent stopped"),
            websocket
        )
        
        await manager.send_personal_message(
            {
                "type": "agent_stopped",
                "agent_id": agent_id,
                "message": f"Agent {agent_id} stopped successfully",
                "timestamp": datetime.now().isoformat(),
            },
            websocket
        )
        
        logger.info(f"Orchestra agent {agent_id} stopped successfully")
        
    except Exception as e:
        logger.error(f"Failed to stop Orchestra agent {agent_id}: {e}")
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.ERROR, 0, f"Failed to stop: {str(e)}"),
            websocket
        )
        raise


async def execute_agent_with_progress(
    agent: Union[ConstructionAgent, EmailAgent], 
    task_context: Dict[str, Any], 
    agent_id: str, 
    websocket: WebSocket
):
    """Execute agent task with real-time progress updates."""
    try:
        # Update progress: Starting
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.RUNNING, 10, "Connecting to platform..."),
            websocket
        )
        
        # Handle different agent types
        if isinstance(agent, EmailAgent):
            # Email agent execution
            await manager.send_personal_message(
                create_agent_update(agent_id, AgentState.RUNNING, 25, "Connecting to email server..."),
                websocket
            )
            
            # Connect to email
            if hasattr(agent.email_tools, 'connect'):
                connected = await agent.email_tools.connect()
                if not connected:
                    await manager.send_personal_message(
                        create_agent_update(agent_id, AgentState.ERROR, 25, "Email connection failed - check credentials"),
                        websocket
                    )
                    return
        
        elif hasattr(agent, 'platform') and agent.platform == "msproject":
            ms_project_tool = MSProjectTools()
            agent.tools["msproject"] = ms_project_tool
            
            # Initialize browser
            await ms_project_tool.browser.start()
            
            # Update progress: Authenticating
            await manager.send_personal_message(
                create_agent_update(agent_id, AgentState.RUNNING, 25, "Authenticating with Microsoft Project..."),
                websocket
            )
            
            # Check authentication (use existing session)
            authenticated = await ms_project_tool.authenticate()
            if not authenticated:
                await manager.send_personal_message(
                    create_agent_update(agent_id, AgentState.ERROR, 25, "Authentication failed - please sign in to Microsoft Project"),
                    websocket
                )
                return
        
        # Update progress: Executing task
        task_message = "Executing email processing task..." if isinstance(agent, EmailAgent) else "Executing data extraction task..."
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.RUNNING, 50, task_message),
            websocket
        )
        
        # Execute the actual task
        result = await agent.execute_task(task_context)
        
        # Update progress: Processing results
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.RUNNING, 80, "Processing extracted data..."),
            websocket
        )
        
        # Send results with appropriate data based on agent type
        if isinstance(agent, EmailAgent):
            extracted_count = result.get("construction_emails", 0) if result else 0
            completion_message = f"Email processing completed - {extracted_count} construction emails found"
        else:
            extracted_count = len(result.get("extracted_data", {}).get("projects", [])) if result else 0
            completion_message = "Task completed successfully"
        
        await manager.send_personal_message(
            create_agent_update(
                agent_id, 
                AgentState.COMPLETED, 
                100, 
                completion_message,
                {
                    "result": result,
                    "extracted_items": extracted_count
                }
            ),
            websocket
        )
        
        logger.info(f"Agent {agent_id} task completed successfully")
        
    except asyncio.CancelledError:
        logger.info(f"Agent {agent_id} task was cancelled")
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.IDLE, 0, "Task cancelled"),
            websocket
        )
    except Exception as e:
        logger.error(f"Agent {agent_id} task failed: {e}")
        await manager.send_personal_message(
            create_agent_update(agent_id, AgentState.ERROR, 0, f"Task failed: {str(e)}"),
            websocket
        )
    finally:
        # Clean up based on agent type
        if agent_id in active_agents:
            current_agent = active_agents[agent_id]
            
            if isinstance(current_agent, EmailAgent):
                # Clean up email agent
                try:
                    await current_agent.stop()
                except Exception as e:
                    logger.error(f"Error stopping email agent: {e}")
            
            elif hasattr(current_agent, 'tools'):
                # Clean up browser-based agent
                agent_tools = current_agent.tools
                if 'msproject' in agent_tools:
                    try:
                        await agent_tools['msproject'].browser.close()
                    except Exception as e:
                        logger.error(f"Error closing browser: {e}")
