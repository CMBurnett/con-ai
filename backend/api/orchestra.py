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


@router.post("/export")
async def export_orchestra_data(
    data_types: List[str],
    date_range: Dict[str, str],
    include_analytics: bool = False,
    include_predictions: bool = False,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Export Orchestra analytics data."""
    try:
        # Get temporal analytics data from knowledge graph
        temporal_data = {}
        if "temporalAnalytics" in data_types:
            temporal_data = await orchestra_manager.knowledge_graph.get_temporal_analytics()
        
        # Get collaboration insights
        collaboration_data = {}
        if "collaborationInsights" in data_types:
            collaboration_data = await orchestra_manager.knowledge_graph.get_collaboration_insights()
        
        # Get detected patterns
        patterns_data = {}
        if "patterns" in data_types:
            patterns_data = await orchestra_manager.knowledge_graph.detect_patterns(lookback_days=30)
        
        # Get predictions if requested
        predictions_data = {}
        if include_predictions and "predictions" in data_types:
            # Get predictions for all active projects
            predictions_data = await orchestra_manager.knowledge_graph.get_predictions_data()
        
        export_data = {
            "temporal_analytics": temporal_data,
            "collaboration_insights": collaboration_data,
            "patterns": patterns_data,
            "predictions": predictions_data,
            "export_metadata": {
                "exported_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
                "version": "1.0.0",
                "knowledge_graph_stats": {
                    "nodes": orchestra_manager.knowledge_graph.graph.number_of_nodes(),
                    "edges": orchestra_manager.knowledge_graph.graph.number_of_edges(),
                }
            }
        }
        
        return export_data
        
    except Exception as e:
        logger.error(f"Orchestra data export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/data/tables")
async def get_table_data(
    table_type: str,
    page: int = 1,
    page_size: int = 10,
    search: str = None,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Get paginated table data for the data tables view."""
    try:
        # Handle different table types
        if table_type == 'temporalData':
            # Get knowledge graph data
            nodes = []
            edges = []
            for node, data in orchestra_manager.knowledge_graph.graph.nodes(data=True):
                nodes.append({
                    'id': node,
                    'node_type': data.get('node_type', 'unknown'),
                    'entity_name': data.get('entity_name', node),
                    'attributes': data,
                    'created_at': data.get('created_at', '2024-01-01T00:00:00Z'),
                })
            
            for u, v, data in orchestra_manager.knowledge_graph.graph.edges(data=True):
                edges.append({
                    'from_node': u,
                    'to_node': v,
                    'relationship_type': data.get('relationship_type', 'connected_to'),
                    'weight': data.get('weight', 1.0),
                    'confidence': data.get('confidence', 0.8),
                })
            
            # Combine nodes and edges for temporal data view
            combined_data = [
                {'type': 'node', **node} for node in nodes
            ] + [
                {'type': 'edge', **edge} for edge in edges
            ]
            
            # Apply search filter if provided
            if search:
                combined_data = [
                    item for item in combined_data
                    if search.lower() in str(item.get('entity_name', '')).lower() or
                       search.lower() in str(item.get('relationship_type', '')).lower()
                ]
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_data = combined_data[start:end]
            
            return {
                'data': paginated_data,
                'total': len(combined_data),
                'page': page,
                'page_size': page_size,
                'total_pages': (len(combined_data) + page_size - 1) // page_size,
            }
            
        elif table_type == 'predictions':
            # Get prediction results
            predictions_data = await orchestra_manager.knowledge_graph.get_predictions_data()
            return {
                'data': predictions_data.get('predictions', []),
                'total': len(predictions_data.get('predictions', [])),
                'page': page,
                'page_size': page_size,
            }
            
        elif table_type == 'patterns':
            # Get detected patterns
            patterns = await orchestra_manager.knowledge_graph.detect_patterns(lookback_days=30)
            return {
                'data': patterns,
                'total': len(patterns),
                'page': page,
                'page_size': page_size,
            }
        
        else:
            return {
                'data': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'message': f'Table type {table_type} not supported',
            }
            
    except Exception as e:
        logger.error(f"Table data fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Table data fetch failed: {str(e)}")


@router.get("/data/search")
async def search_all_tables(
    query: str,
    tables: str = "all",  # comma-separated list of table types
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Search across all data tables."""
    try:
        results = []
        
        # Search in temporal data
        if "all" in tables or "temporalData" in tables:
            nodes = []
            for node, data in orchestra_manager.knowledge_graph.graph.nodes(data=True):
                if query.lower() in str(data.get('entity_name', '')).lower():
                    nodes.append({
                        'table': 'temporalData',
                        'type': 'node',
                        'id': node,
                        'match': data.get('entity_name', node),
                        'data': data,
                    })
            results.extend(nodes)
        
        return {
            'query': query,
            'results': results,
            'total_results': len(results),
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/data/export-table")
async def export_table_data(
    table_type: str,
    format: str = "json",
    filters: Dict[str, Any] = None,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Export specific table data in various formats."""
    try:
        # Get all data for the specified table
        table_data = await get_table_data(
            table_type=table_type,
            page=1,
            page_size=10000,  # Large page size to get all data
            orchestra_manager=orchestra_manager
        )
        
        export_data = {
            'table_type': table_type,
            'exported_at': "2024-01-01T00:00:00Z",  # Would use actual timestamp
            'format': format,
            'total_records': table_data['total'],
            'data': table_data['data'],
        }
        
        return export_data
        
    except Exception as e:
        logger.error(f"Table export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Table export failed: {str(e)}")


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
