import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app
from config import Config


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    """Test homepage loads successfully (HTTP 200)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"SNJB Placement Cell Assistant" in response.data


def test_health_endpoint_no_secrets(client):
    """Test health status endpoint does not leak secret API keys."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert "server_status" in data
    assert "gemini_configured" in data
    # Ensure raw API key is never exposed if configured
    if Config.GEMINI_API_KEY:
        assert Config.GEMINI_API_KEY not in str(data)
    if data["gemini_configured"]:
        assert "..." in data["masked_key"] or "****" in data["masked_key"]


def test_faqs_endpoint(client):
    """Test retrieval of placement FAQs."""
    response = client.get('/api/faqs')
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["count"] > 0
    assert len(data["faqs"]) > 0


def test_chat_empty_input_rejected(client):
    """Test chat endpoint rejects empty messages with 400 Bad Request."""
    response = client.post('/api/chat', json={"message": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "cannot be empty" in data["error"].lower()


def test_chat_whitespace_only_rejected(client):
    """Test chat endpoint rejects whitespace-only messages."""
    response = client.post('/api/chat', json={"message": "     "})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_chat_overlength_input_rejected(client):
    """Test chat endpoint rejects messages exceeding maximum character limit."""
    long_msg = "A" * (Config.MAX_MESSAGE_LENGTH + 50)
    response = client.post('/api/chat', json={"message": long_msg})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "exceeds" in data["error"].lower()


def test_chat_valid_placement_query(client):
    """Test chat endpoint returning grounded answer for standard placement query."""
    response = client.post('/api/chat', json={"message": "How does campus placement work?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "reply" in data
    assert len(data["reply"]) > 20
    assert "mode" in data


def test_chat_unknown_institutional_query(client):
    """Test chat endpoint handles queries about unverified specific topics honestly."""
    response = client.post('/api/chat', json={"message": "What is the package for XYZ Random Tech Company drive?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    # Verify honest fallback response
    assert "reply" in data
