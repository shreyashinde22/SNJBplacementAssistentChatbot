import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.gemini_service import GeminiService
from config import Config


def test_gemini_service_offline_fallback():
    """Test GeminiService returns intelligent offline fallback when API key is missing."""
    svc = GeminiService()
    svc.api_key = ""
    svc.client = None
    res = svc.generate_response("How to prepare for coding round?")
    assert res["success"] is True
    assert res["mode"] in ["offline_fallback", "knowledge_fallback"]
    assert "Aptitude" in res["reply"] or "Coding" in res["reply"] or "SNJB" in res["reply"] or "Verified" in res["reply"]


def test_gemini_service_mocked_live_call():
    """Test GeminiService handles live generation response structure correctly using mock."""
    svc = GeminiService()
    svc.api_key = "mock_valid_key_12345"
    
    mock_response = MagicMock()
    mock_response.text = "This is a mocked Gemini response for SNJB placement preparation."

    svc.client = MagicMock()
    svc.client.models.generate_content.return_value = mock_response

    res = svc.generate_response("Explain SNJB recruitment process")
    assert res["success"] is True
    assert res["reply"] == "This is a mocked Gemini response for SNJB placement preparation."
    assert res["mode"] == "gemini_live"
