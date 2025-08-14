from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    Boolean,
)
from sqlalchemy.orm import relationship
from enum import Enum
from typing import Optional, Dict, Any

from .base import Base


class AgentType(str, Enum):
    """Available agent types for construction platforms."""

    PROCORE = "procore"
    AUTODESK = "autodesk"
    PRIMAVERA = "primavera"
    DEMO = "demo"


class AgentState(str, Enum):
    """Agent execution states."""

    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"


class Agent(Base):
    """Agent configuration and status."""

    agent_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    status = Column(SQLEnum(AgentState), default=AgentState.IDLE, nullable=False)

    # Configuration
    config = Column(JSON, default=dict)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Status tracking
    progress = Column(Integer, default=0)  # 0-100
    current_message = Column(Text, default="")
    last_error = Column(Text, default="")

    # Relationships
    tasks = relationship(
        "AgentTask", back_populates="agent", cascade="all, delete-orphan"
    )
    logs = relationship(
        "AgentLog", back_populates="agent", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary with relationships."""
        data = super().to_dict()
        data.update(
            {
                "agent_type": self.agent_type.value if self.agent_type else None,
                "status": self.status.value if self.status else None,
            }
        )
        return data

    def get_latest_task(self) -> Optional["AgentTask"]:
        """Get the most recent task for this agent."""
        if self.tasks:
            return max(self.tasks, key=lambda t: t.created_at)
        return None


class AgentTask(Base):
    """Individual task execution by an agent."""

    task_id = Column(String(50), unique=True, index=True, nullable=False)
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)

    # Task details
    task_type = Column(
        String(50), nullable=False
    )  # e.g., "extract_projects", "sync_data"
    parameters = Column(JSON, default=dict)

    # Execution status
    status = Column(SQLEnum(AgentState), default=AgentState.IDLE, nullable=False)
    progress = Column(Integer, default=0)
    result = Column(JSON, default=dict)
    error_message = Column(Text, default="")

    # Timing
    started_at = Column(String, nullable=True)  # ISO timestamp
    completed_at = Column(String, nullable=True)  # ISO timestamp

    # Relationships
    agent = relationship("Agent", back_populates="tasks")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = super().to_dict()
        data["status"] = self.status.value if self.status else None
        return data


class AgentLog(Base):
    """Audit log for agent activities."""

    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)

    # Log details
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    action = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)

    # Context
    task_id = Column(String(50), nullable=True)
    platform_data = Column(JSON, default=dict)  # Platform-specific context

    # Relationships
    agent = relationship("Agent", back_populates="logs")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return super().to_dict()
