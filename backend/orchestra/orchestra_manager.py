"""
Orchestra Framework Manager

Provides a wrapper around the Orchestra framework that maintains compatibility
with the existing agent API while adding multi-agent orchestration capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Using mock Orchestra framework since mainframe-orchestra is not available
# In production, this would be: from mainframe_orchestra import Orchestra, Agent as OrchestraAgent


class MockOrchestra:
    """Mock Orchestra framework for development."""

    async def start(self):
        pass

    async def stop(self):
        pass


class MockOrchestraAgent:
    """Mock Orchestra agent for development."""

    def __init__(self, name: str):
        self.name = name
        self.status = "idle"

    async def execute_task(self, task_context):
        return {
            "status": "completed",
            "message": f"Mock execution of {task_context.get('task_type')}",
        }

    async def stop(self):
        self.status = "stopped"


# Use mock implementations
Orchestra = MockOrchestra
OrchestraAgent = MockOrchestraAgent

# Define AgentType enum locally since we removed legacy models
from enum import Enum

class AgentType(Enum):
    """Agent types for Orchestra framework."""
    PROCORE = "procore"
    AUTODESK = "autodesk" 
    PRIMAVERA = "primavera"
    MSPROJECT = "msproject"
    DEMO = "demo"

from api.websocket import ConnectionManager
from orchestra.temporal.knowledge_graph import TemporalKnowledgeGraph

logger = logging.getLogger(__name__)


class OrchestraManager:
    """Manages Orchestra framework integration and agent orchestration."""

    def __init__(self, websocket_manager: ConnectionManager):
        self.orchestra = Orchestra()
        self.websocket_manager = websocket_manager
        self.knowledge_graph = TemporalKnowledgeGraph()
        self.active_agents: Dict[str, OrchestraAgent] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize the Orchestra framework and load agents."""
        try:
            await self.orchestra.start()
            await self.knowledge_graph.initialize()
            logger.info("Orchestra framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Orchestra framework: {e}")
            raise

    async def start_agent(
        self,
        agent_id: str,
        agent_type: AgentType,
        task_type: str,
        parameters: Dict[str, Any] = None,
    ) -> str:
        """Start an Orchestra-powered agent with the given task."""
        try:
            # Create Orchestra agent based on type
            orchestra_agent = await self._create_orchestra_agent(agent_type, agent_id)

            # Store the agent
            self.active_agents[agent_id] = orchestra_agent

            # Create task for agent execution
            task = asyncio.create_task(
                self._run_agent_task(agent_id, task_type, parameters or {})
            )
            self.agent_tasks[agent_id] = task

            # Broadcast agent start
            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "running",
                    "progress": 0,
                    "message": f"Started {agent_type.value} agent with task: {task_type}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Store in knowledge graph
            await self.knowledge_graph.store_agent_event(
                agent_id, "start", {"task_type": task_type, "parameters": parameters}
            )

            return f"Agent {agent_id} started with task {task_type}"

        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "error",
                    "progress": 0,
                    "message": f"Failed to start agent: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            raise

    async def stop_agent(self, agent_id: str) -> str:
        """Stop a running Orchestra agent."""
        try:
            if agent_id in self.agent_tasks:
                task = self.agent_tasks[agent_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self.agent_tasks[agent_id]

            if agent_id in self.active_agents:
                orchestra_agent = self.active_agents[agent_id]
                await orchestra_agent.stop()
                del self.active_agents[agent_id]

            # Broadcast agent stop
            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "idle",
                    "progress": 0,
                    "message": f"Agent {agent_id} stopped",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Store in knowledge graph
            await self.knowledge_graph.store_agent_event(agent_id, "stop", {})

            return f"Agent {agent_id} stopped successfully"

        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            raise

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the current status of an Orchestra agent."""
        if agent_id in self.active_agents:
            orchestra_agent = self.active_agents[agent_id]
            return {
                "agent_id": agent_id,
                "status": "running" if agent_id in self.agent_tasks else "idle",
                "orchestra_status": (
                    orchestra_agent.status
                    if hasattr(orchestra_agent, "status")
                    else "unknown"
                ),
                "capabilities": getattr(orchestra_agent, "capabilities", []),
                "current_task": getattr(orchestra_agent, "current_task", None),
            }
        else:
            return {
                "agent_id": agent_id,
                "status": "idle",
                "orchestra_status": "not_running",
                "capabilities": [],
                "current_task": None,
            }

    async def orchestrate_agents(self, orchestration_plan: Dict[str, Any]) -> str:
        """Orchestrate multiple agents working together on a complex task."""
        try:
            orchestration_id = (
                f"orchestration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Extract agents and their tasks from the plan
            agent_configs = orchestration_plan.get("agents", [])
            coordination_strategy = orchestration_plan.get("strategy", "sequential")

            logger.info(
                f"Starting orchestration {orchestration_id} with {len(agent_configs)} agents"
            )

            # Create and start agents based on strategy
            if coordination_strategy == "parallel":
                await self._orchestrate_parallel(orchestration_id, agent_configs)
            elif coordination_strategy == "sequential":
                await self._orchestrate_sequential(orchestration_id, agent_configs)
            elif coordination_strategy == "collaborative":
                await self._orchestrate_collaborative(orchestration_id, agent_configs)
            else:
                raise ValueError(
                    f"Unknown orchestration strategy: {coordination_strategy}"
                )

            # Store orchestration in knowledge graph
            await self.knowledge_graph.store_orchestration_event(
                orchestration_id, "start", orchestration_plan
            )

            return orchestration_id

        except Exception as e:
            logger.error(f"Failed to orchestrate agents: {e}")
            raise

    async def _create_orchestra_agent(
        self, agent_type: AgentType, agent_id: str
    ) -> OrchestraAgent:
        """Create an Orchestra agent based on the agent type."""
        from .agents.construction_agent import ConstructionAgent

        # Map agent types to Orchestra agent classes
        agent_classes = {
            AgentType.PROCORE: ConstructionAgent,
            AgentType.AUTODESK: ConstructionAgent,
            AgentType.PRIMAVERA: ConstructionAgent,
            AgentType.DEMO: ConstructionAgent,
        }

        agent_class = agent_classes.get(agent_type, ConstructionAgent)

        # Create agent with construction-specific tools
        agent = agent_class(
            name=f"{agent_type.value}_{agent_id}",
            platform=agent_type.value,
            agent_id=agent_id,
        )

        return agent

    async def _run_agent_task(
        self, agent_id: str, task_type: str, parameters: Dict[str, Any]
    ):
        """Run a task for a specific agent."""
        try:
            orchestra_agent = self.active_agents[agent_id]

            # Create task context
            task_context = {
                "task_type": task_type,
                "parameters": parameters,
                "agent_id": agent_id,
                "start_time": datetime.now().isoformat(),
            }

            # Update progress
            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "running",
                    "progress": 25,
                    "message": f"Executing {task_type} task",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Execute the task through Orchestra
            result = await orchestra_agent.execute_task(task_context)

            # Update progress to completion
            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "completed",
                    "progress": 100,
                    "message": f"Task {task_type} completed successfully",
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Store result in knowledge graph
            await self.knowledge_graph.store_task_result(
                agent_id, task_type, result, parameters
            )

            logger.info(f"Agent {agent_id} completed task {task_type}")

        except Exception as e:
            logger.error(f"Agent {agent_id} failed task {task_type}: {e}")

            await self.websocket_manager.broadcast_agent_update(
                {
                    "agentId": agent_id,
                    "status": "error",
                    "progress": 0,
                    "message": f"Task {task_type} failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Store error in knowledge graph
            await self.knowledge_graph.store_agent_event(
                agent_id, "error", {"task_type": task_type, "error": str(e)}
            )

    async def _orchestrate_parallel(
        self, orchestration_id: str, agent_configs: List[Dict]
    ):
        """Orchestrate agents to run in parallel."""
        tasks = []
        for config in agent_configs:
            agent_id = config["agent_id"]
            agent_type = AgentType(config["agent_type"])
            task_type = config["task_type"]
            parameters = config.get("parameters", {})

            task = asyncio.create_task(
                self.start_agent(agent_id, agent_type, task_type, parameters)
            )
            tasks.append(task)

        # Wait for all agents to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _orchestrate_sequential(
        self, orchestration_id: str, agent_configs: List[Dict]
    ):
        """Orchestrate agents to run sequentially."""
        for config in agent_configs:
            agent_id = config["agent_id"]
            agent_type = AgentType(config["agent_type"])
            task_type = config["task_type"]
            parameters = config.get("parameters", {})

            await self.start_agent(agent_id, agent_type, task_type, parameters)

            # Wait for current agent to complete before starting next
            if agent_id in self.agent_tasks:
                await self.agent_tasks[agent_id]

    async def _orchestrate_collaborative(
        self, orchestration_id: str, agent_configs: List[Dict]
    ):
        """Orchestrate agents to collaborate on shared tasks."""
        # Create shared workspace for collaboration
        workspace = {
            "orchestration_id": orchestration_id,
            "shared_data": {},
            "communication_channel": f"collab_{orchestration_id}",
        }

        # Start all agents with shared workspace
        for config in agent_configs:
            agent_id = config["agent_id"]
            agent_type = AgentType(config["agent_type"])
            task_type = config["task_type"]
            parameters = config.get("parameters", {})
            parameters["workspace"] = workspace

            await self.start_agent(agent_id, agent_type, task_type, parameters)

    async def shutdown(self):
        """Shutdown the Orchestra manager and cleanup resources."""
        try:
            # Stop all running agents
            for agent_id in list(self.active_agents.keys()):
                await self.stop_agent(agent_id)

            # Shutdown Orchestra
            await self.orchestra.stop()

            # Cleanup knowledge graph
            await self.knowledge_graph.close()

            logger.info("Orchestra manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during Orchestra manager shutdown: {e}")
