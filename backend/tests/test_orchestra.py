import pytest
from fastapi.testclient import TestClient


def test_orchestra_status(client: TestClient):
    """Test Orchestra framework status endpoint."""
    response = client.get("/api/orchestra/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "operational"
    assert "active_agents" in data
    assert "running_tasks" in data
    assert "knowledge_graph" in data
    assert data["version"] == "1.0.0"


def test_knowledge_graph_stats(client: TestClient):
    """Test knowledge graph statistics endpoint."""
    response = client.get("/api/orchestra/knowledge-graph/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_nodes" in data
    assert "total_edges" in data
    assert "node_types" in data
    assert "edge_types" in data


def test_start_orchestra_agent(client: TestClient):
    """Test starting an Orchestra agent."""
    response = client.post(
        "/api/orchestra/agents/test_agent/start?agent_type=demo&task_type=extract_project_data",
        json={"project_id": "test_project"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["agent_id"] == "test_agent"
    assert data["status"] == "started"
    assert data["task_type"] == "extract_project_data"


def test_get_orchestra_agent_status(client: TestClient):
    """Test getting Orchestra agent status."""
    # First start an agent
    start_response = client.post(
        "/api/orchestra/agents/status_test_agent/start?agent_type=demo&task_type=extract_project_data",
        json={"project_id": "test_project"}
    )
    assert start_response.status_code == 200
    
    # Then get its status
    response = client.get("/api/orchestra/agents/status_test_agent/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["agent_id"] == "status_test_agent"
    assert data["status"] in ["running", "idle"]
    assert "capabilities" in data


def test_stop_orchestra_agent(client: TestClient):
    """Test stopping an Orchestra agent."""
    # First start an agent
    start_response = client.post(
        "/api/orchestra/agents/stop_test_agent/start?agent_type=demo&task_type=extract_project_data",
        json={"project_id": "test_project"}
    )
    assert start_response.status_code == 200
    
    # Then stop it
    response = client.post("/api/orchestra/agents/stop_test_agent/stop")
    assert response.status_code == 200
    
    data = response.json()
    assert data["agent_id"] == "stop_test_agent"
    assert data["status"] == "stopped"


def test_orchestrate_agents_parallel(client: TestClient):
    """Test parallel agent orchestration."""
    orchestration_data = {
        "strategy": "parallel",
        "project_id": "test_project",
        "agents": [
            {
                "agent_id": "agent1",
                "agent_type": "demo",
                "task_type": "extract_project_data",
                "parameters": {"project_id": "test_project"}
            },
            {
                "agent_id": "agent2", 
                "agent_type": "demo",
                "task_type": "extract_project_data",
                "parameters": {"project_id": "test_project"}
            }
        ]
    }
    
    response = client.post("/api/orchestra/orchestrate", json=orchestration_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "orchestration_id" in data
    assert data["status"] == "started"
    assert data["strategy"] == "parallel"
    assert data["agents_count"] == 2


def test_orchestrate_agents_sequential(client: TestClient):
    """Test sequential agent orchestration.""" 
    orchestration_data = {
        "strategy": "sequential",
        "project_id": "test_project",
        "agents": [
            {
                "agent_id": "seq_agent1",
                "agent_type": "demo",
                "task_type": "extract_project_data",
                "parameters": {"project_id": "test_project"}
            }
        ]
    }
    
    response = client.post("/api/orchestra/orchestrate", json=orchestration_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["strategy"] == "sequential"
    assert data["agents_count"] == 1


def test_generate_predictions(client: TestClient):
    """Test predictive analytics endpoint."""
    prediction_data = {
        "project_id": "test_project",
        "prediction_types": ["schedule_drift", "budget_variance"],
        "horizon_days": 30
    }
    
    response = client.post("/api/orchestra/predictions", json=prediction_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["project_id"] == "test_project"
    assert data["horizon_days"] == 30
    assert data["status"] == "completed"
    assert "predictions" in data


def test_temporal_context_query(client: TestClient):
    """Test temporal context query endpoint."""
    query_data = {
        "entity_id": "test_project",
        "entity_type": "project", 
        "context_window_hours": 24
    }
    
    response = client.post("/api/orchestra/temporal/query", json=query_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["entity_id"] == "test_project"
    assert data["entity_type"] == "project"
    assert data["context_window_hours"] == 24


def test_collaboration_insights(client: TestClient):
    """Test collaboration insights endpoint."""
    response = client.get("/api/orchestra/collaboration/insights")
    assert response.status_code == 200
    
    data = response.json()
    assert "collaboration_analysis" in data or "total_events_analyzed" in data


def test_pattern_detection(client: TestClient):
    """Test pattern detection endpoint."""
    response = client.post("/api/orchestra/patterns/detect?lookback_days=7")
    assert response.status_code == 200
    
    data = response.json()
    assert "patterns_detected" in data
    assert data["lookback_days"] == 7
    assert "patterns" in data


def test_daily_consolidation(client: TestClient):
    """Test daily data consolidation endpoint."""
    response = client.post("/api/orchestra/consolidation/daily")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "completed"
    assert "consolidation_results" in data


def test_invalid_agent_type(client: TestClient):
    """Test starting agent with invalid type."""
    response = client.post(
        "/api/orchestra/agents/invalid_agent/start?agent_type=invalid&task_type=test",
        json={}
    )
    assert response.status_code == 422  # Validation error


def test_stop_nonexistent_agent(client: TestClient):
    """Test stopping agent that doesn't exist."""
    response = client.post("/api/orchestra/agents/nonexistent/stop")
    assert response.status_code == 200  # Should handle gracefully
    
    data = response.json()
    assert data["agent_id"] == "nonexistent"