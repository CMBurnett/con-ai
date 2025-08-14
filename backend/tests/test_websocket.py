import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_websocket_connection(client: TestClient):
    """Test basic WebSocket connection."""
    with client.websocket_connect("/ws") as websocket:
        # Should receive welcome message
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "connection_established"
        assert "client_id" in message
        assert "timestamp" in message


def test_websocket_ping_pong(client: TestClient):
    """Test WebSocket ping/pong."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send ping
        websocket.send_text(json.dumps({"type": "ping"}))

        # Receive pong
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "pong"
        assert "timestamp" in message


def test_websocket_start_agent_command(client: TestClient):
    """Test WebSocket start agent command."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send start agent command
        command = {
            "type": "start_agent",
            "agent_id": "test-agent",
            "config": {"test": "value"},
        }
        websocket.send_text(json.dumps(command))

        # Receive acknowledgment
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "command_received"
        assert message["command"] == "start_agent"
        assert message["agent_id"] == "test-agent"
        assert "not implemented yet" in message["message"]


def test_websocket_stop_agent_command(client: TestClient):
    """Test WebSocket stop agent command."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send stop agent command
        command = {"type": "stop_agent", "agent_id": "test-agent"}
        websocket.send_text(json.dumps(command))

        # Receive acknowledgment
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "command_received"
        assert message["command"] == "stop_agent"
        assert message["agent_id"] == "test-agent"


def test_websocket_invalid_json(client: TestClient):
    """Test WebSocket with invalid JSON."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send invalid JSON
        websocket.send_text("invalid json")

        # Receive error
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "Invalid JSON format" in message["message"]


def test_websocket_unknown_message_type(client: TestClient):
    """Test WebSocket with unknown message type."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send unknown message type
        websocket.send_text(json.dumps({"type": "unknown_type"}))

        # Receive error
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "Unknown message type" in message["message"]


def test_websocket_missing_agent_id(client: TestClient):
    """Test WebSocket commands missing agent_id."""
    with client.websocket_connect("/ws") as websocket:
        # Skip welcome message
        websocket.receive_text()

        # Send start command without agent_id
        websocket.send_text(json.dumps({"type": "start_agent"}))

        # Receive error
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "agent_id is required" in message["message"]
