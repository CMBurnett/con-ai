from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from database import get_db
from services.agent_service import agent_service
from models.agent import AgentType, AgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# Pydantic models for request/response
class AgentCreate(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    agent_type: AgentType = Field(..., description="Type of construction platform")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Agent configuration"
    )
    is_enabled: bool = Field(True, description="Whether agent is enabled")


class AgentUpdate(BaseModel):
    name: str = Field(None, description="Human-readable agent name")
    config: Dict[str, Any] = Field(None, description="Agent configuration")
    is_enabled: bool = Field(None, description="Whether agent is enabled")


class AgentStartRequest(BaseModel):
    task_type: str = Field(..., description="Type of task to execute")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Task parameters"
    )


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    status: str
    config: Dict[str, Any]
    is_enabled: bool
    is_active: bool
    progress: int = 0
    current_message: str = ""
    last_error: str = ""
    created_at: str
    updated_at: str


class TaskResponse(BaseModel):
    task_id: str
    agent_id: int
    task_type: str
    parameters: Dict[str, Any]
    status: str
    progress: int
    result: Dict[str, Any]
    error_message: str
    started_at: str = None
    completed_at: str = None
    created_at: str
    updated_at: str


@router.get("/", response_model=List[AgentResponse])
async def get_agents(db: Session = Depends(get_db)):
    """Get all agents with their current status."""
    try:
        agents = await agent_service.get_agents(db)
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agents",
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent by ID."""
    try:
        agent = await agent_service.get_agent(agent_id, db)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent",
        )


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent."""
    try:
        # Check if agent ID already exists
        existing_agent = await agent_service.get_agent(agent_data.agent_id, db)
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with ID {agent_data.agent_id} already exists",
            )

        agent = await agent_service.create_agent(agent_data.dict(), db)
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent",
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str, agent_data: AgentUpdate, db: Session = Depends(get_db)
):
    """Update an existing agent."""
    try:
        # Only include non-None fields
        update_data = {k: v for k, v in agent_data.dict().items() if v is not None}

        agent = await agent_service.update_agent(agent_id, update_data, db)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent",
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent."""
    try:
        success = await agent_service.delete_agent(agent_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete agent",
        )


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str, request: AgentStartRequest, db: Session = Depends(get_db)
):
    """Start an agent with a specific task."""
    try:
        task_id = await agent_service.start_agent(
            agent_id, request.task_type, request.parameters, db
        )
        return {
            "message": f"Agent {agent_id} started successfully",
            "task_id": task_id,
            "agent_id": agent_id,
            "task_type": request.task_type,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start agent",
        )


@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str, db: Session = Depends(get_db)):
    """Stop a running agent."""
    try:
        success = await agent_service.stop_agent(agent_id, db)
        if not success:
            return {
                "message": f"Agent {agent_id} was not running",
                "agent_id": agent_id,
            }
        return {
            "message": f"Agent {agent_id} stopped successfully",
            "agent_id": agent_id,
        }
    except Exception as e:
        logger.error(f"Error stopping agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop agent",
        )


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    """Get detailed status of a specific agent."""
    try:
        agent = await agent_service.get_agent(agent_id, db)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        return {
            "agent_id": agent_id,
            "basic_info": agent,
            "is_active": agent.get("is_active", False),
            "runtime_status": agent.get("runtime_status"),
            "active_agents_count": agent_service.get_active_agent_count(),
            "active_agents": agent_service.get_active_agent_ids(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent status",
        )


@router.get("/{agent_id}/tasks", response_model=List[TaskResponse])
async def get_agent_tasks(agent_id: str, db: Session = Depends(get_db)):
    """Get all tasks for a specific agent."""
    try:
        tasks = await agent_service.get_agent_tasks(agent_id, db)
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent tasks",
        )


@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: str, limit: int = 100, db: Session = Depends(get_db)
):
    """Get logs for a specific agent."""
    try:
        logs = await agent_service.get_agent_logs(agent_id, db, limit)
        return {
            "agent_id": agent_id,
            "logs": logs,
            "total_logs": len(logs),
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error getting logs for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent logs",
        )


# Global status endpoints
@router.get("/status/overview")
async def get_agents_overview(db: Session = Depends(get_db)):
    """Get overview of all agents."""
    try:
        agents = await agent_service.get_agents(db)

        status_counts = {}
        for agent in agents:
            status = agent.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_agents": len(agents),
            "active_agents": agent_service.get_active_agent_count(),
            "status_breakdown": status_counts,
            "agent_types": list(set(agent.get("agent_type") for agent in agents)),
            "active_agent_ids": agent_service.get_active_agent_ids(),
        }
    except Exception as e:
        logger.error(f"Error getting agents overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agents overview",
        )
