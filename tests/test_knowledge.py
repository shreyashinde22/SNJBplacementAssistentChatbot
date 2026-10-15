import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.knowledge_service import KnowledgeService


@pytest.fixture
def knowledge_svc():
    return KnowledgeService()


def test_knowledge_base_loading(knowledge_svc):
    """Test FAQs and verified documents are indexed on startup."""
    assert len(knowledge_svc.faqs) >= 5
    assert len(knowledge_svc.documents) >= 1


def test_faq_search_match(knowledge_svc):
    """Test searching for placement documents checklist finds matching FAQ."""
    results = knowledge_svc.search_knowledge("What documents should I prepare for interview?")
    assert len(results) > 0
    top_result = results[0]
    assert top_result["score"] > 0.2
    assert "resume" in top_result["content"].lower() or "documents" in top_result["content"].lower()


def test_document_policy_search_match(knowledge_svc):
    """Test searching for placement policy rules matches verified policy text."""
    results = knowledge_svc.search_knowledge("attendance percentage for placement policy")
    assert len(results) > 0
    match_sources = [r["source"] for r in results]
    assert any("policy" in src.lower() or "faq" in src.lower() for src in match_sources)


def test_no_match_returns_empty_or_low_score(knowledge_svc):
    """Test irrelevant query returns low or empty matches."""
    results = knowledge_svc.search_knowledge("quantum mechanics astrophysics space voyage")
    # Irrelevant topics should produce no strong matches (>0.15 score filter)
    assert len(results) == 0 or all(r["score"] <= 0.25 for r in results)
