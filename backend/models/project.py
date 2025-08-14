from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    JSON,
    Enum as SQLEnum,
    Numeric,
    Date,
)
from enum import Enum
from decimal import Decimal
from datetime import date
from typing import Optional

from .base import Base


class ProjectStatus(str, Enum):
    """Project execution status."""

    PLANNING = "planning"
    ACTIVE = "active"
    DELAYED = "delayed"
    COMPLETED = "completed"


class RFIStatus(str, Enum):
    """Request for Information status."""

    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"


class Priority(str, Enum):
    """Priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(Base):
    """Construction project from various platforms."""

    # Platform identification
    platform_id = Column(
        String(100), nullable=False, index=True
    )  # ID from source platform
    platform_type = Column(String(20), nullable=False)  # procore, autodesk, primavera

    # Project details
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    project_number = Column(String(50), nullable=True)

    # Status and timing
    status = Column(
        SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False
    )
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Financial
    budget_amount = Column(Numeric(15, 2), default=0)
    actual_cost = Column(Numeric(15, 2), default=0)

    # Location
    address = Column(Text, default="")
    city = Column(String(100), default="")
    state = Column(String(50), default="")
    zip_code = Column(String(20), default="")

    # Additional data from platform
    platform_data = Column(JSON, default=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "status": self.status.value if self.status else None,
                "budget_amount": float(self.budget_amount) if self.budget_amount else 0,
                "actual_cost": float(self.actual_cost) if self.actual_cost else 0,
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None,
            }
        )
        return data

    @property
    def budget_variance(self) -> float:
        """Calculate budget variance percentage."""
        if not self.budget_amount or self.budget_amount == 0:
            return 0.0
        return float((self.actual_cost - self.budget_amount) / self.budget_amount * 100)


class RFI(Base):
    """Request for Information tracking."""

    # Platform identification
    platform_id = Column(String(100), nullable=False, index=True)
    platform_type = Column(String(20), nullable=False)
    project_platform_id = Column(String(100), nullable=False)  # Reference to project

    # RFI details
    rfi_number = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")

    # Status and priority
    status = Column(SQLEnum(RFIStatus), default=RFIStatus.OPEN, nullable=False)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, nullable=False)

    # People
    submitter = Column(String(100), default="")
    assignee = Column(String(100), default="")

    # Timing
    due_date = Column(Date, nullable=True)
    response_date = Column(Date, nullable=True)

    # Additional data from platform
    platform_data = Column(JSON, default=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "status": self.status.value if self.status else None,
                "priority": self.priority.value if self.priority else None,
                "due_date": self.due_date.isoformat() if self.due_date else None,
                "response_date": (
                    self.response_date.isoformat() if self.response_date else None
                ),
            }
        )
        return data


class BudgetItem(Base):
    """Budget tracking for project cost items."""

    # Platform identification
    platform_id = Column(String(100), nullable=False, index=True)
    platform_type = Column(String(20), nullable=False)
    project_platform_id = Column(String(100), nullable=False)

    # Budget details
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), default="")
    description = Column(Text, default="")

    # Financial
    budgeted_amount = Column(Numeric(15, 2), default=0)
    actual_amount = Column(Numeric(15, 2), default=0)
    committed_amount = Column(Numeric(15, 2), default=0)

    # Unit information
    unit_type = Column(String(50), default="")  # e.g., "sq ft", "linear ft", "each"
    quantity = Column(Numeric(10, 2), default=0)
    unit_cost = Column(Numeric(10, 2), default=0)

    # Additional data from platform
    platform_data = Column(JSON, default=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "budgeted_amount": (
                    float(self.budgeted_amount) if self.budgeted_amount else 0
                ),
                "actual_amount": float(self.actual_amount) if self.actual_amount else 0,
                "committed_amount": (
                    float(self.committed_amount) if self.committed_amount else 0
                ),
                "quantity": float(self.quantity) if self.quantity else 0,
                "unit_cost": float(self.unit_cost) if self.unit_cost else 0,
            }
        )
        return data

    @property
    def variance_amount(self) -> float:
        """Calculate variance between budgeted and actual."""
        return float(self.actual_amount - self.budgeted_amount)

    @property
    def variance_percentage(self) -> float:
        """Calculate variance percentage."""
        if not self.budgeted_amount or self.budgeted_amount == 0:
            return 0.0
        return float(self.variance_amount / self.budgeted_amount * 100)
