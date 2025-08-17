"""
Temporal Intelligence Database Models

SQLAlchemy models for storing temporal data, knowledge graphs, and analytics.
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Float,
    Integer,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()


class EventType(Enum):
    """Types of temporal events that can be tracked."""

    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    AGENT_ERROR = "agent_error"
    TASK_EXECUTION = "task_execution"
    DATA_EXTRACTION = "data_extraction"
    ORCHESTRATION = "orchestration"
    PATTERN_DETECTION = "pattern_detection"
    PREDICTION = "prediction"
    DATA_CONSOLIDATION = "data_consolidation"


class TemporalEvent(Base):
    """Store temporal events for knowledge graph construction."""

    __tablename__ = "temporal_events"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False)
    agent_id = Column(String(50), nullable=False)
    project_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Event-specific data
    event_data = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)

    # Relationships and dependencies
    parent_event_id = Column(
        String(50), ForeignKey("temporal_events.id"), nullable=True
    )
    related_events = relationship("TemporalEvent", backref="parent", remote_side=[id])

    # Performance metrics
    duration_seconds = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_data": self.event_data,
            "context": self.context,
            "parent_event_id": self.parent_event_id,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class KnowledgeNode(Base):
    """Represent nodes in the knowledge graph."""

    __tablename__ = "knowledge_nodes"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_type = Column(String(50), nullable=False)  # project, agent, task, entity
    entity_id = Column(
        String(100), nullable=False
    )  # External ID (project_id, agent_id, etc.)
    entity_name = Column(String(200), nullable=True)

    # Node properties
    properties = Column(JSON, nullable=True)
    attributes = Column(JSON, nullable=True)

    # Temporal information
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    edges = relationship(
        "KnowledgeEdge", foreign_keys="KnowledgeEdge.from_node_id", backref="from_node"
    )

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "node_type": self.node_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "properties": self.properties,
            "attributes": self.attributes,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
        }


class KnowledgeEdge(Base):
    """Represent relationships between knowledge graph nodes."""

    __tablename__ = "knowledge_edges"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_node_id = Column(String(50), ForeignKey("knowledge_nodes.id"), nullable=False)
    to_node_id = Column(String(50), ForeignKey("knowledge_nodes.id"), nullable=False)

    # Relationship properties
    relationship_type = Column(
        String(100), nullable=False
    )  # contains, depends_on, collaborates_with
    weight = Column(Float, default=1.0)
    confidence = Column(Float, default=1.0)

    # Temporal properties
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    interaction_count = Column(Integer, default=1)

    # Metadata (using edge_metadata to avoid SQLAlchemy conflict)
    edge_metadata = Column(JSON, nullable=True)

    # Relationships
    to_node = relationship("KnowledgeNode", foreign_keys=[to_node_id])

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_interaction": (
                self.last_interaction.isoformat() if self.last_interaction else None
            ),
            "interaction_count": self.interaction_count,
            "edge_metadata": self.edge_metadata,
        }


class PatternAnalysis(Base):
    """Store detected patterns and their analytics."""

    __tablename__ = "pattern_analyses"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String(100), nullable=False)
    pattern_name = Column(String(200), nullable=False)

    # Pattern characteristics
    description = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False)
    frequency = Column(Integer, default=1)

    # Time-based properties
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_occurrence = Column(DateTime, default=datetime.utcnow)
    detection_window_days = Column(Integer, default=30)

    # Pattern data
    pattern_data = Column(JSON, nullable=True)
    supporting_events = Column(JSON, nullable=True)  # List of event IDs
    affected_entities = Column(JSON, nullable=True)  # List of entity IDs

    # Analytics
    trend_direction = Column(
        String(20), nullable=True
    )  # increasing, decreasing, stable
    seasonal_component = Column(Boolean, default=False)
    anomaly_indicator = Column(Boolean, default=False)

    # Predictive indicators
    predictive_power = Column(Float, nullable=True)
    correlation_strength = Column(Float, nullable=True)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "pattern_type": self.pattern_type,
            "pattern_name": self.pattern_name,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "frequency": self.frequency,
            "first_detected": (
                self.first_detected.isoformat() if self.first_detected else None
            ),
            "last_occurrence": (
                self.last_occurrence.isoformat() if self.last_occurrence else None
            ),
            "detection_window_days": self.detection_window_days,
            "pattern_data": self.pattern_data,
            "supporting_events": self.supporting_events,
            "affected_entities": self.affected_entities,
            "trend_direction": self.trend_direction,
            "seasonal_component": self.seasonal_component,
            "anomaly_indicator": self.anomaly_indicator,
            "predictive_power": self.predictive_power,
            "correlation_strength": self.correlation_strength,
        }


class PredictionResult(Base):
    """Store predictive analytics results."""

    __tablename__ = "prediction_results"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_type = Column(String(100), nullable=False)
    target_entity_id = Column(String(100), nullable=False)
    target_entity_type = Column(String(50), nullable=False)

    # Prediction details
    predicted_value = Column(JSON, nullable=False)
    confidence_interval = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=False)

    # Time horizon
    prediction_horizon_days = Column(Integer, nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=True)

    # Model information
    model_type = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    training_data_size = Column(Integer, nullable=True)
    feature_importance = Column(JSON, nullable=True)

    # Validation
    actual_value = Column(JSON, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    validated_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "prediction_type": self.prediction_type,
            "target_entity_id": self.target_entity_id,
            "target_entity_type": self.target_entity_type,
            "predicted_value": self.predicted_value,
            "confidence_interval": self.confidence_interval,
            "confidence_score": self.confidence_score,
            "prediction_horizon_days": self.prediction_horizon_days,
            "prediction_date": (
                self.prediction_date.isoformat() if self.prediction_date else None
            ),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "model_type": self.model_type,
            "model_version": self.model_version,
            "training_data_size": self.training_data_size,
            "feature_importance": self.feature_importance,
            "actual_value": self.actual_value,
            "accuracy_score": self.accuracy_score,
            "validated_at": (
                self.validated_at.isoformat() if self.validated_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ConsolidationCycle(Base):
    """Track data consolidation cycles and their results."""

    __tablename__ = "consolidation_cycles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    cycle_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    cycle_date = Column(DateTime, nullable=False)

    # Processing metrics
    events_processed = Column(Integer, default=0)
    patterns_detected = Column(Integer, default=0)
    predictions_generated = Column(Integer, default=0)

    # Performance metrics
    processing_time_seconds = Column(Float, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    insights_generated = Column(Integer, default=0)

    # Results
    consolidation_results = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    anomalies_detected = Column(JSON, nullable=True)

    # Status
    status = Column(String(20), default="completed")  # running, completed, failed
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "cycle_type": self.cycle_type,
            "cycle_date": self.cycle_date.isoformat() if self.cycle_date else None,
            "events_processed": self.events_processed,
            "patterns_detected": self.patterns_detected,
            "predictions_generated": self.predictions_generated,
            "processing_time_seconds": self.processing_time_seconds,
            "data_quality_score": self.data_quality_score,
            "insights_generated": self.insights_generated,
            "consolidation_results": self.consolidation_results,
            "recommendations": self.recommendations,
            "anomalies_detected": self.anomalies_detected,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
