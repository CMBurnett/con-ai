"""
Orchestra API Endpoints

Provides REST API endpoints for Orchestra framework management,
multi-agent orchestration, and temporal intelligence.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

from orchestra.orchestra_manager import AgentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestra", tags=["orchestra"])


class OrchestrationRequest(BaseModel):
    """Request model for orchestrating multiple agents."""

    strategy: str = "sequential"  # parallel, sequential, collaborative
    agents: List[Dict[str, Any]]
    project_id: Optional[str] = None
    description: Optional[str] = None


class PredictionRequest(BaseModel):
    """Request model for generating predictions."""

    project_id: str
    prediction_types: List[str] = [
        "schedule_drift",
        "budget_variance",
        "quality_issues",
    ]
    horizon_days: int = 30


class TemporalQueryRequest(BaseModel):
    """Request model for temporal context queries."""

    entity_id: str
    entity_type: str = "project"
    context_window_hours: int = 24


def get_orchestra_manager(request: Request):
    """Dependency to get Orchestra manager from app state."""
    if not hasattr(request.app.state, "orchestra_manager"):
        raise HTTPException(status_code=500, detail="Orchestra manager not initialized")
    return request.app.state.orchestra_manager


@router.post("/orchestrate")
async def orchestrate_agents(
    request: OrchestrationRequest, orchestra_manager=Depends(get_orchestra_manager)
):
    """Orchestrate multiple agents for complex tasks."""
    try:
        orchestration_plan = {
            "strategy": request.strategy,
            "agents": request.agents,
            "project_id": request.project_id,
            "description": request.description or "Multi-agent orchestration",
        }

        orchestration_id = await orchestra_manager.orchestrate_agents(
            orchestration_plan
        )

        return {
            "orchestration_id": orchestration_id,
            "status": "started",
            "strategy": request.strategy,
            "agents_count": len(request.agents),
            "message": f"Orchestration {orchestration_id} started successfully",
        }

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.post("/agents/{agent_id}/start")
async def start_orchestra_agent(
    agent_id: str,
    agent_type: AgentType,
    task_type: str,
    parameters: Dict[str, Any] = None,
    orchestra_manager=Depends(get_orchestra_manager),
):
    """Start an Orchestra-powered agent."""
    try:
        result = await orchestra_manager.start_agent(
            agent_id=agent_id,
            agent_type=agent_type,
            task_type=task_type,
            parameters=parameters or {},
        )

        return {
            "agent_id": agent_id,
            "status": "started",
            "task_type": task_type,
            "message": result,
        }

    except Exception as e:
        logger.error(f"Failed to start Orchestra agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/agents/{agent_id}/stop")
async def stop_orchestra_agent(
    agent_id: str, orchestra_manager=Depends(get_orchestra_manager)
):
    """Stop an Orchestra agent."""
    try:
        result = await orchestra_manager.stop_agent(agent_id)

        return {"agent_id": agent_id, "status": "stopped", "message": result}

    except Exception as e:
        logger.error(f"Failed to stop Orchestra agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")


@router.get("/agents/{agent_id}/status")
async def get_orchestra_agent_status(
    agent_id: str, orchestra_manager=Depends(get_orchestra_manager)
):
    """Get status of an Orchestra agent."""
    try:
        status = await orchestra_manager.get_agent_status(agent_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get Orchestra agent status for {agent_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/predictions")
async def generate_predictions(
    request: PredictionRequest, orchestra_manager=Depends(get_orchestra_manager)
):
    """Generate predictive analytics for a project."""
    try:
        predictions = await orchestra_manager.knowledge_graph.predict_project_outcomes(
            request.project_id
        )

        return {
            "project_id": request.project_id,
            "predictions": predictions,
            "horizon_days": request.horizon_days,
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/temporal/query")
async def query_temporal_context(
    request: TemporalQueryRequest, orchestra_manager=Depends(get_orchestra_manager)
):
    """Query temporal context for an entity."""
    try:
        context = await orchestra_manager.knowledge_graph.query_temporal_context(
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            context_window_hours=request.context_window_hours,
        )

        return context

    except Exception as e:
        logger.error(f"Temporal query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Temporal query failed: {str(e)}")


@router.get("/collaboration/insights")
async def get_collaboration_insights(
    project_id: Optional[str] = None, orchestra_manager=Depends(get_orchestra_manager)
):
    """Get collaboration insights and patterns."""
    try:
        insights = await orchestra_manager.knowledge_graph.get_collaboration_insights(
            project_id
        )
        return insights

    except Exception as e:
        logger.error(f"Collaboration insights failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Collaboration insights failed: {str(e)}"
        )


@router.post("/patterns/detect")
async def detect_patterns(
    lookback_days: int = 30, orchestra_manager=Depends(get_orchestra_manager)
):
    """Detect patterns in temporal data."""
    try:
        patterns = await orchestra_manager.knowledge_graph.detect_patterns(
            lookback_days
        )

        return {
            "patterns_detected": len(patterns),
            "lookback_days": lookback_days,
            "patterns": patterns,
        }

    except Exception as e:
        logger.error(f"Pattern detection failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Pattern detection failed: {str(e)}"
        )


@router.post("/consolidation/daily")
async def trigger_daily_consolidation(orchestra_manager=Depends(get_orchestra_manager)):
    """Trigger daily data consolidation cycle."""
    try:
        results = await orchestra_manager.knowledge_graph.consolidate_daily_data()

        return {"status": "completed", "consolidation_results": results}

    except Exception as e:
        logger.error(f"Daily consolidation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Daily consolidation failed: {str(e)}"
        )


@router.get("/knowledge-graph/stats")
async def get_knowledge_graph_stats(orchestra_manager=Depends(get_orchestra_manager)):
    """Get knowledge graph statistics."""
    try:
        # This would get actual stats from the knowledge graph
        stats = {
            "total_nodes": orchestra_manager.knowledge_graph.graph.number_of_nodes(),
            "total_edges": orchestra_manager.knowledge_graph.graph.number_of_edges(),
            "node_types": {},
            "edge_types": {},
            "last_updated": "2024-01-01T00:00:00Z",  # Placeholder
        }

        # Count node types
        for node, data in orchestra_manager.knowledge_graph.graph.nodes(data=True):
            node_type = data.get("node_type", "unknown")
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

        # Count edge types
        for u, v, data in orchestra_manager.knowledge_graph.graph.edges(data=True):
            edge_type = data.get("relationship_type", "unknown")
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        return stats

    except Exception as e:
        logger.error(f"Knowledge graph stats failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Knowledge graph stats failed: {str(e)}"
        )


@router.get("/status")
async def get_orchestra_status(orchestra_manager=Depends(get_orchestra_manager)):
    """Get overall Orchestra framework status."""
    try:
        return {
            "status": "operational",
            "active_agents": len(orchestra_manager.active_agents),
            "running_tasks": len(orchestra_manager.agent_tasks),
            "knowledge_graph": {
                "nodes": orchestra_manager.knowledge_graph.graph.number_of_nodes(),
                "edges": orchestra_manager.knowledge_graph.graph.number_of_edges(),
            },
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Orchestra status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
