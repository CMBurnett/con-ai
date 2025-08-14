from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime
import uuid

from models.agent import AgentState, AgentType
from api.websocket import manager, create_agent_update

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all construction platform agents."""

    def __init__(
        self, agent_id: str, agent_type: AgentType, config: Dict[str, Any] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config or {}

        # State management
        self.state = AgentState.IDLE
        self.progress = 0
        self.current_message = ""
        self.last_error = ""

        # Task management
        self.current_task_id: Optional[str] = None
        self.is_running = False
        self.should_stop = False

        # Callbacks
        self.on_status_change: Optional[Callable] = None

        logger.info(f"Initialized {self.agent_type} agent: {self.agent_id}")

    async def start(self, task_type: str, parameters: Dict[str, Any] = None) -> str:
        """Start the agent with a specific task."""
        if self.is_running:
            raise ValueError(f"Agent {self.agent_id} is already running")

        self.current_task_id = str(uuid.uuid4())
        self.is_running = True
        self.should_stop = False

        await self._update_status(AgentState.RUNNING, 0, f"Starting {task_type}")

        try:
            logger.info(f"Starting agent {self.agent_id} with task {task_type}")

            # Run the agent task
            result = await self._execute_task(task_type, parameters or {})

            if not self.should_stop:
                await self._update_status(
                    AgentState.COMPLETED, 100, "Task completed successfully"
                )
                logger.info(f"Agent {self.agent_id} completed task {task_type}")
            else:
                await self._update_status(AgentState.IDLE, 0, "Task stopped by user")
                logger.info(f"Agent {self.agent_id} stopped by user")

            return self.current_task_id

        except Exception as e:
            error_msg = f"Task failed: {str(e)}"
            self.last_error = error_msg
            await self._update_status(AgentState.ERROR, self.progress, error_msg)
            logger.error(f"Agent {self.agent_id} failed: {e}")
            raise
        finally:
            self.is_running = False
            self.current_task_id = None

    async def stop(self):
        """Stop the currently running agent."""
        if not self.is_running:
            logger.warning(f"Agent {self.agent_id} is not running")
            return

        logger.info(f"Stopping agent {self.agent_id}")
        self.should_stop = True
        await self._update_status(AgentState.IDLE, self.progress, "Stopping...")

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "state": self.state.value,
            "progress": self.progress,
            "current_message": self.current_message,
            "last_error": self.last_error,
            "is_running": self.is_running,
            "current_task_id": self.current_task_id,
            "config": self.config,
        }

    async def _update_status(
        self,
        state: AgentState,
        progress: int,
        message: str,
        data: Dict[str, Any] = None,
    ):
        """Update agent status and broadcast to WebSocket clients."""
        self.state = state
        self.progress = progress
        self.current_message = message

        # Create agent update message
        update = create_agent_update(
            agent_id=self.agent_id,
            status=state,
            progress=progress,
            message=message,
            data=data,
        )

        # Broadcast to WebSocket clients
        await manager.broadcast_agent_update(update)

        # Call status change callback if registered
        if self.on_status_change:
            try:
                await self.on_status_change(self, update)
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")

        logger.debug(
            f"Agent {self.agent_id} status: {state.value} ({progress}%) - {message}"
        )

    async def _update_progress(self, progress: int, message: str = None):
        """Update progress without changing state."""
        if message is None:
            message = self.current_message
        await self._update_status(self.state, progress, message)

    @abstractmethod
    async def _execute_task(
        self, task_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the specific task for this agent type.

        Args:
            task_type: The type of task to execute
            parameters: Task-specific parameters

        Returns:
            Task execution result

        Raises:
            NotImplementedError: If task_type is not supported
            Exception: If task execution fails
        """
        pass

    @abstractmethod
    async def _authenticate(self) -> bool:
        """
        Authenticate with the construction platform.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    async def _extract_data(
        self, data_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract data from the construction platform.

        Args:
            data_type: Type of data to extract (e.g., 'projects', 'rfis')
            parameters: Extraction parameters

        Returns:
            Extracted data
        """
        pass

    async def _check_should_stop(self):
        """Check if agent should stop and raise exception if so."""
        if self.should_stop:
            raise asyncio.CancelledError("Agent stopped by user")

    async def _sleep_with_stop_check(self, seconds: float):
        """Sleep while checking for stop signal."""
        end_time = asyncio.get_event_loop().time() + seconds
        while asyncio.get_event_loop().time() < end_time:
            await self._check_should_stop()
            await asyncio.sleep(min(0.1, end_time - asyncio.get_event_loop().time()))

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type}, state={self.state})>"
