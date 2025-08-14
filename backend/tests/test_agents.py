import pytest
from fastapi.testclient import TestClient


def test_get_agents_empty(client: TestClient):
    """Test getting agents when none exist."""
    response = client.get("/api/agents/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_agent(client: TestClient, sample_agent_data):
    """Test creating a new agent."""
    response = client.post("/api/agents/", json=sample_agent_data)
    assert response.status_code == 201

    data = response.json()
    assert data["agent_id"] == sample_agent_data["agent_id"]
    assert data["name"] == sample_agent_data["name"]
    assert data["agent_type"] == sample_agent_data["agent_type"]
    assert data["is_enabled"] == sample_agent_data["is_enabled"]
    assert "created_at" in data
    assert "updated_at" in data


def test_create_duplicate_agent(client: TestClient, sample_agent_data):
    """Test creating agent with duplicate ID fails."""
    # Create first agent
    response = client.post("/api/agents/", json=sample_agent_data)
    assert response.status_code == 201

    # Try to create duplicate
    response = client.post("/api/agents/", json=sample_agent_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_agent(client: TestClient, sample_agent_data):
    """Test getting a specific agent."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Get agent
    agent_id = sample_agent_data["agent_id"]
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_id"] == agent_id
    assert data["is_active"] == False  # Not running


def test_get_nonexistent_agent(client: TestClient):
    """Test getting agent that doesn't exist."""
    response = client.get("/api/agents/nonexistent")
    assert response.status_code == 404


def test_update_agent(client: TestClient, sample_agent_data):
    """Test updating an agent."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Update agent
    agent_id = sample_agent_data["agent_id"]
    update_data = {"name": "Updated Test Agent", "is_enabled": False}

    response = client.put(f"/api/agents/{agent_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["is_enabled"] == update_data["is_enabled"]
    assert data["agent_type"] == sample_agent_data["agent_type"]  # Unchanged


def test_update_nonexistent_agent(client: TestClient):
    """Test updating agent that doesn't exist."""
    update_data = {"name": "Updated Name"}
    response = client.put("/api/agents/nonexistent", json=update_data)
    assert response.status_code == 404


def test_delete_agent(client: TestClient, sample_agent_data):
    """Test deleting an agent."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Delete agent
    agent_id = sample_agent_data["agent_id"]
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 204

    # Verify agent is gone
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_agent(client: TestClient):
    """Test deleting agent that doesn't exist."""
    response = client.delete("/api/agents/nonexistent")
    assert response.status_code == 404


def test_get_agent_status(client: TestClient, sample_agent_data):
    """Test getting agent status."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Get status
    agent_id = sample_agent_data["agent_id"]
    response = client.get(f"/api/agents/{agent_id}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_id"] == agent_id
    assert "basic_info" in data
    assert "is_active" in data
    assert data["is_active"] == False


def test_get_agent_tasks(client: TestClient, sample_agent_data):
    """Test getting agent tasks."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Get tasks (should be empty)
    agent_id = sample_agent_data["agent_id"]
    response = client.get(f"/api/agents/{agent_id}/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_agent_logs(client: TestClient, sample_agent_data):
    """Test getting agent logs."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Get logs (should be empty)
    agent_id = sample_agent_data["agent_id"]
    response = client.get(f"/api/agents/{agent_id}/logs")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_id"] == agent_id
    assert data["logs"] == []
    assert data["total_logs"] == 0


def test_agents_overview(client: TestClient, sample_agent_data):
    """Test getting agents overview."""
    # Get overview when empty
    response = client.get("/api/agents/status/overview")
    assert response.status_code == 200

    data = response.json()
    assert data["total_agents"] == 0
    assert data["active_agents"] == 0

    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Get overview with one agent
    response = client.get("/api/agents/status/overview")
    assert response.status_code == 200

    data = response.json()
    assert data["total_agents"] == 1
    assert data["active_agents"] == 0  # Not running
    assert "status_breakdown" in data
    assert "agent_types" in data


def test_start_agent_not_implemented(client: TestClient, sample_agent_data):
    """Test starting agent (not fully implemented yet)."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Try to start agent
    agent_id = sample_agent_data["agent_id"]
    start_data = {"task_type": "test_task", "parameters": {"test": "value"}}

    response = client.post(f"/api/agents/{agent_id}/start", json=start_data)
    # This will fail because no agent class is registered for demo type
    assert response.status_code == 400


def test_stop_agent_not_running(client: TestClient, sample_agent_data):
    """Test stopping agent that's not running."""
    # Create agent
    create_response = client.post("/api/agents/", json=sample_agent_data)
    assert create_response.status_code == 201

    # Stop agent (not running)
    agent_id = sample_agent_data["agent_id"]
    response = client.post(f"/api/agents/{agent_id}/stop")
    assert response.status_code == 200

    data = response.json()
    assert "was not running" in data["message"]
