"""
Temporal Knowledge Graph

Provides storage, querying, and analysis of temporal construction data
using a graph-based approach for pattern recognition and insights.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

import networkx as nx
from sqlalchemy import create_engine, and_, or_, desc, func
from sqlalchemy.orm import sessionmaker, Session
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np

from orchestra.temporal.models import (
    Base,
    TemporalEvent,
    KnowledgeNode,
    KnowledgeEdge,
    PatternAnalysis,
    PredictionResult,
    ConsolidationCycle,
)

logger = logging.getLogger(__name__)


class TemporalKnowledgeGraph:
    """Manages temporal knowledge graph for construction intelligence."""

    def __init__(self, database_url: str = "sqlite:///temporal_knowledge.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.graph = nx.DiGraph()  # NetworkX graph for analysis

    async def initialize(self):
        """Initialize the knowledge graph database and structures."""
        try:
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Load existing graph structure
            await self._load_graph_from_database()

            logger.info("Temporal knowledge graph initialized")

        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph: {e}")
            raise

    async def store_agent_event(
        self,
        agent_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        project_id: str = None,
    ):
        """Store an agent event in the temporal knowledge graph."""
        try:
            with self.SessionLocal() as db:
                event = TemporalEvent(
                    event_type=event_type,
                    agent_id=agent_id,
                    project_id=project_id,
                    event_data=event_data,
                    timestamp=datetime.utcnow(),
                )

                db.add(event)
                db.commit()

                # Update knowledge graph
                await self._update_graph_with_event(event)

                logger.debug(f"Stored agent event: {agent_id} - {event_type}")

        except Exception as e:
            logger.error(f"Failed to store agent event: {e}")
            raise

    async def store_task_result(
        self,
        agent_id: str,
        task_type: str,
        result: Dict[str, Any],
        parameters: Dict[str, Any],
    ):
        """Store task execution result with context."""
        try:
            event_data = {
                "task_type": task_type,
                "result": result,
                "parameters": parameters,
                "success": result.get("status") != "error",
            }

            await self.store_agent_event(
                agent_id=agent_id,
                event_type="task_execution",
                event_data=event_data,
                project_id=parameters.get("project_id"),
            )

            # Extract and store entities from result
            await self._extract_entities_from_result(agent_id, task_type, result)

        except Exception as e:
            logger.error(f"Failed to store task result: {e}")
            raise

    async def store_orchestration_event(
        self, orchestration_id: str, event_type: str, orchestration_data: Dict[str, Any]
    ):
        """Store orchestration events for multi-agent coordination tracking."""
        try:
            with self.SessionLocal() as db:
                event = TemporalEvent(
                    event_type=f"orchestration_{event_type}",
                    agent_id=orchestration_id,
                    event_data=orchestration_data,
                    timestamp=datetime.utcnow(),
                )

                db.add(event)
                db.commit()

                # Update orchestration relationships in graph
                await self._update_orchestration_graph(
                    orchestration_id, orchestration_data
                )

        except Exception as e:
            logger.error(f"Failed to store orchestration event: {e}")
            raise

    async def detect_patterns(self, lookback_days: int = 30) -> List[Dict[str, Any]]:
        """Detect patterns in temporal data using machine learning."""
        try:
            patterns = []

            # Pattern detection strategies
            patterns.extend(await self._detect_temporal_patterns(lookback_days))
            patterns.extend(await self._detect_collaboration_patterns(lookback_days))
            patterns.extend(await self._detect_performance_patterns(lookback_days))
            patterns.extend(await self._detect_anomalies(lookback_days))

            # Store detected patterns
            for pattern in patterns:
                await self._store_pattern(pattern)

            logger.info(
                f"Detected {len(patterns)} patterns in {lookback_days} days of data"
            )
            return patterns

        except Exception as e:
            logger.error(f"Failed to detect patterns: {e}")
            return []

    async def query_temporal_context(
        self, entity_id: str, entity_type: str, context_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Query temporal context around a specific entity."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=context_window_hours)

            with self.SessionLocal() as db:
                # Get events related to entity
                events = (
                    db.query(TemporalEvent)
                    .filter(
                        and_(
                            or_(
                                TemporalEvent.agent_id == entity_id,
                                TemporalEvent.project_id == entity_id,
                            ),
                            TemporalEvent.timestamp >= start_time,
                            TemporalEvent.timestamp <= end_time,
                        )
                    )
                    .order_by(TemporalEvent.timestamp)
                    .all()
                )

                # Get knowledge graph context
                node_context = await self._get_node_context(entity_id, entity_type)

                # Analyze temporal patterns
                temporal_analysis = await self._analyze_temporal_sequence(events)

                return {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "context_window_hours": context_window_hours,
                    "events_count": len(events),
                    "events": [event.to_dict() for event in events],
                    "node_context": node_context,
                    "temporal_analysis": temporal_analysis,
                    "generated_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to query temporal context: {e}")
            return {}

    async def get_collaboration_insights(
        self, project_id: str = None
    ) -> Dict[str, Any]:
        """Get insights about agent collaboration patterns."""
        try:
            with self.SessionLocal() as db:
                # Query collaboration events
                query = db.query(TemporalEvent).filter(
                    TemporalEvent.event_type.in_(
                        ["orchestration_start", "task_execution"]
                    )
                )

                if project_id:
                    query = query.filter(TemporalEvent.project_id == project_id)

                events = query.order_by(desc(TemporalEvent.timestamp)).limit(1000).all()

                # Analyze collaboration patterns
                collaboration_analysis = await self._analyze_collaboration_patterns(
                    events
                )

                # Get network metrics
                network_metrics = await self._calculate_network_metrics()

                return {
                    "project_id": project_id,
                    "collaboration_analysis": collaboration_analysis,
                    "network_metrics": network_metrics,
                    "total_events_analyzed": len(events),
                    "generated_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to get collaboration insights: {e}")
            return {}

    async def predict_project_outcomes(self, project_id: str) -> Dict[str, Any]:
        """Generate predictions for project outcomes based on temporal patterns."""
        try:
            # Get project historical data
            historical_data = await self._get_project_historical_data(project_id)

            # Generate predictions using different models
            predictions = {}

            if historical_data:
                predictions["schedule_drift"] = await self._predict_schedule_drift(
                    historical_data
                )
                predictions["budget_variance"] = await self._predict_budget_variance(
                    historical_data
                )
                predictions["quality_issues"] = await self._predict_quality_issues(
                    historical_data
                )
                predictions["collaboration_effectiveness"] = (
                    await self._predict_collaboration_effectiveness(historical_data)
                )

            # Store predictions
            for prediction_type, prediction_data in predictions.items():
                await self._store_prediction(
                    project_id, prediction_type, prediction_data
                )

            return {
                "project_id": project_id,
                "predictions": predictions,
                "prediction_confidence": self._calculate_overall_confidence(
                    predictions
                ),
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to predict project outcomes: {e}")
            return {}

    async def consolidate_daily_data(self) -> Dict[str, Any]:
        """Perform daily data consolidation and pattern detection."""
        try:
            start_time = datetime.utcnow()
            cycle_date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)

            with self.SessionLocal() as db:
                cycle = ConsolidationCycle(
                    cycle_type="daily", cycle_date=cycle_date, status="running"
                )
                db.add(cycle)
                db.commit()

                # Consolidation tasks
                results = {}

                # Pattern detection
                patterns = await self.detect_patterns(lookback_days=1)
                cycle.patterns_detected = len(patterns)

                # Data quality assessment
                quality_score = await self._assess_data_quality()
                cycle.data_quality_score = quality_score

                # Graph analysis
                graph_metrics = await self._update_graph_analytics()
                results["graph_metrics"] = graph_metrics

                # Generate insights
                insights = await self._generate_daily_insights()
                cycle.insights_generated = len(insights)
                results["insights"] = insights

                # Cleanup old data
                cleanup_results = await self._cleanup_old_data()
                results["cleanup"] = cleanup_results

                # Complete cycle
                cycle.status = "completed"
                cycle.completed_at = datetime.utcnow()
                cycle.processing_time_seconds = (
                    cycle.completed_at - start_time
                ).total_seconds()
                cycle.consolidation_results = results

                db.commit()

                logger.info(
                    f"Daily consolidation completed in {cycle.processing_time_seconds:.2f}s"
                )
                return results

        except Exception as e:
            logger.error(f"Daily consolidation failed: {e}")
            # Mark cycle as failed
            if "cycle" in locals():
                cycle.status = "failed"
                cycle.error_message = str(e)
                db.commit()
            raise

    async def _load_graph_from_database(self):
        """Load existing knowledge graph from database."""
        try:
            with self.SessionLocal() as db:
                # Load nodes
                nodes = db.query(KnowledgeNode).all()
                for node in nodes:
                    self.graph.add_node(
                        node.id,
                        node_type=node.node_type,
                        entity_id=node.entity_id,
                        entity_name=node.entity_name,
                        properties=node.properties or {},
                        attributes=node.attributes or {},
                    )

                # Load edges
                edges = db.query(KnowledgeEdge).all()
                for edge in edges:
                    self.graph.add_edge(
                        edge.from_node_id,
                        edge.to_node_id,
                        relationship_type=edge.relationship_type,
                        weight=edge.weight,
                        confidence=edge.confidence,
                        edge_metadata=edge.edge_metadata or {},
                    )

                logger.info(
                    f"Loaded knowledge graph: {len(nodes)} nodes, {len(edges)} edges"
                )

        except Exception as e:
            logger.error(f"Failed to load graph from database: {e}")

    async def _update_graph_with_event(self, event: TemporalEvent):
        """Update knowledge graph structure based on new event."""
        try:
            # Create or update agent node
            agent_node_id = await self._ensure_node(
                "agent", event.agent_id, f"Agent {event.agent_id}"
            )

            # Create project node if applicable
            if event.project_id:
                project_node_id = await self._ensure_node(
                    "project", event.project_id, f"Project {event.project_id}"
                )

                # Create agent-project relationship
                await self._ensure_edge(agent_node_id, project_node_id, "works_on", 1.0)

            # Update graph analytics
            await self._update_node_analytics(agent_node_id, event)

        except Exception as e:
            logger.error(f"Failed to update graph with event: {e}")

    async def _ensure_node(
        self, node_type: str, entity_id: str, entity_name: str
    ) -> str:
        """Ensure a node exists in both database and NetworkX graph."""
        try:
            with self.SessionLocal() as db:
                node = (
                    db.query(KnowledgeNode)
                    .filter(
                        and_(
                            KnowledgeNode.node_type == node_type,
                            KnowledgeNode.entity_id == entity_id,
                        )
                    )
                    .first()
                )

                if not node:
                    node = KnowledgeNode(
                        node_type=node_type,
                        entity_id=entity_id,
                        entity_name=entity_name,
                        properties={},
                        attributes={},
                    )
                    db.add(node)
                    db.commit()

                    # Add to NetworkX graph
                    self.graph.add_node(
                        node.id,
                        node_type=node_type,
                        entity_id=entity_id,
                        entity_name=entity_name,
                        properties={},
                        attributes={},
                    )

                return node.id

        except Exception as e:
            logger.error(f"Failed to ensure node: {e}")
            return None

    async def _ensure_edge(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        weight: float = 1.0,
    ):
        """Ensure an edge exists between two nodes."""
        try:
            with self.SessionLocal() as db:
                edge = (
                    db.query(KnowledgeEdge)
                    .filter(
                        and_(
                            KnowledgeEdge.from_node_id == from_node_id,
                            KnowledgeEdge.to_node_id == to_node_id,
                            KnowledgeEdge.relationship_type == relationship_type,
                        )
                    )
                    .first()
                )

                if edge:
                    # Update existing edge
                    edge.interaction_count += 1
                    edge.last_interaction = datetime.utcnow()
                    edge.weight = min(edge.weight + 0.1, 2.0)  # Strengthen relationship
                else:
                    # Create new edge
                    edge = KnowledgeEdge(
                        from_node_id=from_node_id,
                        to_node_id=to_node_id,
                        relationship_type=relationship_type,
                        weight=weight,
                        confidence=1.0,
                    )
                    db.add(edge)

                db.commit()

                # Update NetworkX graph
                self.graph.add_edge(
                    from_node_id,
                    to_node_id,
                    relationship_type=relationship_type,
                    weight=edge.weight,
                    confidence=edge.confidence,
                    edge_metadata=edge.edge_metadata or {},
                )

        except Exception as e:
            logger.error(f"Failed to ensure edge: {e}")

    async def _detect_temporal_patterns(
        self, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect temporal patterns in agent behavior."""
        patterns = []

        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=lookback_days)

            with self.SessionLocal() as db:
                events = (
                    db.query(TemporalEvent)
                    .filter(TemporalEvent.timestamp >= start_time)
                    .order_by(TemporalEvent.timestamp)
                    .all()
                )

                # Group events by hour to detect time-based patterns
                hourly_activity = {}
                for event in events:
                    hour = event.timestamp.hour
                    if hour not in hourly_activity:
                        hourly_activity[hour] = 0
                    hourly_activity[hour] += 1

                # Detect peak activity hours
                if hourly_activity:
                    peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
                    avg_activity = sum(hourly_activity.values()) / len(hourly_activity)

                    if peak_hour[1] > avg_activity * 1.5:
                        patterns.append(
                            {
                                "pattern_type": "temporal_peak",
                                "pattern_name": f"Peak activity at hour {peak_hour[0]}",
                                "confidence_score": 0.8,
                                "pattern_data": {
                                    "peak_hour": peak_hour[0],
                                    "peak_activity": peak_hour[1],
                                    "average_activity": avg_activity,
                                },
                            }
                        )

                # Detect daily patterns
                daily_activity = {}
                for event in events:
                    day = event.timestamp.strftime("%A")
                    if day not in daily_activity:
                        daily_activity[day] = 0
                    daily_activity[day] += 1

                if daily_activity:
                    most_active_day = max(daily_activity.items(), key=lambda x: x[1])
                    avg_daily = sum(daily_activity.values()) / len(daily_activity)

                    if most_active_day[1] > avg_daily * 1.3:
                        patterns.append(
                            {
                                "pattern_type": "daily_peak",
                                "pattern_name": f"High activity on {most_active_day[0]}",
                                "confidence_score": 0.75,
                                "pattern_data": {
                                    "peak_day": most_active_day[0],
                                    "peak_activity": most_active_day[1],
                                    "average_daily": avg_daily,
                                },
                            }
                        )

        except Exception as e:
            logger.error(f"Failed to detect temporal patterns: {e}")

        return patterns

    async def close(self):
        """Close database connections and cleanup resources."""
        try:
            if self.engine:
                self.engine.dispose()
            logger.info("Knowledge graph connections closed")
        except Exception as e:
            logger.error(f"Error closing knowledge graph: {e}")

    # Additional helper methods would be implemented here...
    # (Due to length constraints, showing key methods only)
