from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.orm import Session

from models.agent import Agent, AgentTask, AgentLog, AgentType, AgentState
from database import get_db
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agents and their execution."""

    def __init__(self):
        self.active_agents: Dict[str, BaseAgent] = {}
        self.agent_registry: Dict[AgentType, type] = {}

    def register_agent_class(self, agent_type: AgentType, agent_class: type):
        """Register an agent class for a specific type."""
        self.agent_registry[agent_type] = agent_class
        logger.info(
            f"Registered agent class {agent_class.__name__} for type {agent_type}"
        )

    async def get_agents(self, db: Session) -> List[Dict[str, Any]]:
        """Get all agents from database with current status."""
        agents = db.query(Agent).all()
        agent_list = []

        for agent in agents:
            agent_dict = agent.to_dict()

            # Add runtime status if agent is active
            if agent.agent_id in self.active_agents:
                runtime_agent = self.active_agents[agent.agent_id]
                agent_dict.update(
                    {
                        "runtime_status": await runtime_agent.get_status(),
                        "is_active": True,
                    }
                )
            else:
                agent_dict["is_active"] = False

            agent_list.append(agent_dict)

        return agent_list

    async def get_agent(self, agent_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get a specific agent by ID."""
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return None

        agent_dict = agent.to_dict()

        # Add runtime status if agent is active
        if agent_id in self.active_agents:
            runtime_agent = self.active_agents[agent_id]
            agent_dict.update(
                {"runtime_status": await runtime_agent.get_status(), "is_active": True}
            )
        else:
            agent_dict["is_active"] = False

        return agent_dict

    async def create_agent(
        self, agent_data: Dict[str, Any], db: Session
    ) -> Dict[str, Any]:
        """Create a new agent configuration."""
        agent = Agent(
            agent_id=agent_data["agent_id"],
            name=agent_data["name"],
            agent_type=AgentType(agent_data["agent_type"]),
            config=agent_data.get("config", {}),
            is_enabled=agent_data.get("is_enabled", True),
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        logger.info(f"Created agent: {agent.agent_id}")
        return agent.to_dict()

    async def update_agent(
        self, agent_id: str, agent_data: Dict[str, Any], db: Session
    ) -> Optional[Dict[str, Any]]:
        """Update an existing agent configuration."""
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return None

        # Update fields
        for field, value in agent_data.items():
            if hasattr(agent, field) and field != "agent_id":  # Don't allow ID changes
                setattr(agent, field, value)

        db.commit()
        db.refresh(agent)

        logger.info(f"Updated agent: {agent_id}")
        return agent.to_dict()

    async def delete_agent(self, agent_id: str, db: Session) -> bool:
        """Delete an agent configuration."""
        # Stop agent if running
        if agent_id in self.active_agents:
            await self.stop_agent(agent_id, db)

        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return False

        db.delete(agent)
        db.commit()

        logger.info(f"Deleted agent: {agent_id}")
        return True

    async def start_agent(
        self, agent_id: str, task_type: str, parameters: Dict[str, Any], db: Session
    ) -> str:
        """Start an agent with a specific task."""
        # Check if agent is already running
        if agent_id in self.active_agents:
            raise ValueError(f"Agent {agent_id} is already running")

        # Get agent configuration from database
        agent_config = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent_config:
            raise ValueError(f"Agent {agent_id} not found")

        if not agent_config.is_enabled:
            raise ValueError(f"Agent {agent_id} is disabled")

        # Get agent class
        agent_class = self.agent_registry.get(agent_config.agent_type)
        if not agent_class:
            raise ValueError(
                f"No agent class registered for type {agent_config.agent_type}"
            )

        # Create agent instance
        agent_instance = agent_class(agent_id=agent_id, config=agent_config.config)

        # Register status change callback
        agent_instance.on_status_change = self._on_agent_status_change

        # Add to active agents
        self.active_agents[agent_id] = agent_instance

        try:
            # Start the agent
            task_id = await agent_instance.start(task_type, parameters)

            # Create task record
            task = AgentTask(
                task_id=task_id,
                agent_id=agent_config.id,
                task_type=task_type,
                parameters=parameters,
                status=AgentState.RUNNING,
                started_at=agent_instance.current_message,
            )

            db.add(task)
            db.commit()

            logger.info(f"Started agent {agent_id} with task {task_id}")
            return task_id

        except Exception as e:
            # Remove from active agents if start failed
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
            raise

    async def stop_agent(self, agent_id: str, db: Session) -> bool:
        """Stop a running agent."""
        if agent_id not in self.active_agents:
            logger.warning(f"Agent {agent_id} is not running")
            return False

        agent_instance = self.active_agents[agent_id]
        await agent_instance.stop()

        # Remove from active agents
        del self.active_agents[agent_id]

        logger.info(f"Stopped agent {agent_id}")
        return True

    async def get_agent_tasks(self, agent_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get tasks for a specific agent."""
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return []

        tasks = db.query(AgentTask).filter(AgentTask.agent_id == agent.id).all()
        return [task.to_dict() for task in tasks]

    async def get_agent_logs(
        self, agent_id: str, db: Session, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get logs for a specific agent."""
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return []

        logs = (
            db.query(AgentLog)
            .filter(AgentLog.agent_id == agent.id)
            .order_by(AgentLog.created_at.desc())
            .limit(limit)
            .all()
        )

        return [log.to_dict() for log in logs]

    async def log_agent_activity(
        self,
        agent_id: str,
        level: str,
        action: str,
        message: str,
        task_id: str = None,
        platform_data: Dict[str, Any] = None,
        db: Session = None,
    ):
        """Log agent activity."""
        if not db:
            # Can't log without database session
            logger.warning("No database session provided for logging")
            return

        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            logger.error(f"Agent {agent_id} not found for logging")
            return

        log_entry = AgentLog(
            agent_id=agent.id,
            level=level,
            action=action,
            message=message,
            task_id=task_id,
            platform_data=platform_data or {},
        )

        db.add(log_entry)
        db.commit()

    async def _on_agent_status_change(self, agent: BaseAgent, update: Dict[str, Any]):
        """Callback for agent status changes."""
        # This can be used to update database, trigger other actions, etc.
        logger.debug(f"Agent {agent.agent_id} status changed: {update}")

    def get_active_agent_count(self) -> int:
        """Get the number of currently active agents."""
        return len(self.active_agents)

    def get_active_agent_ids(self) -> List[str]:
        """Get list of active agent IDs."""
        return list(self.active_agents.keys())


# Global agent service instance
agent_service = AgentService()
