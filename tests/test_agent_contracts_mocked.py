"""Test end-to-end workflow execution contracts with mocked LLM responses.

Ensures the complete agent pipelines execute without consuming live Groq API tokens.
"""

from unittest.mock import MagicMock, patch
from Agents.incident_triage.workflow import run_incident_triage_workflow
from Agents.expense_reimbursement.workflow import run_expense_workflow
from Agents.market_research.workflow import run_market_research_workflow


@patch("crewai.Crew.kickoff")
def test_mocked_incident_triage_workflow(mock_kickoff):
    # Mock return value for crew kickoff
    mock_res = MagicMock()
    mock_res.raw = '{"status": "ok", "mocked_assessment": "Test validation completed"}'
    mock_kickoff.return_value = mock_res

    sample_incident = {
        "incident_id": "INC-TEST-001",
        "title": "Mock Auth Outage",
        "service": "auth-gateway",
        "service_tier": "Tier-1",
        "category": "authentication_issue",
        "impact_users": 1500,
        "outage_minutes": 25,
        "symptoms": ["OAuth token expired"],
        "synthetic": True,
    }

    result = run_incident_triage_workflow(sample_incident, run_id="test_mock_incident")
    assert result.status == "SUCCESS"
    assert result.agent_count == 7
    assert len(result.execution_order) == 7
    assert "review_agent" in result.agent_durations
    assert result.output["stages"]["intake"] != ""


@patch("crewai.Crew.kickoff")
def test_mocked_expense_workflow(mock_kickoff):
    mock_res = MagicMock()
    mock_res.raw = '{"decision": "ELIGIBLE", "mocked_audit": "Clean verification"}'
    mock_kickoff.return_value = mock_res

    sample_expense = {
        "claim_id": "CLM-TEST-001",
        "employee_id": "EMP-401",
        "employee_name": "Elena Rostova",
        "department": "Engineering",
        "submission_date": "2026-09-15",
        "category": "Meals & Entertainment",
        "merchant": "Bistro Bella Donna",
        "currency": "USD",
        "subtotal": 50.00,
        "tax": 4.50,
        "total": 54.50,
        "business_purpose": "Technical roadmap discussion",
        "receipt_text": "Bistro Bella Donna - Total: $54.50",
        "synthetic": True,
    }

    result = run_expense_workflow(sample_expense, run_id="test_mock_expense")
    assert result.status == "SUCCESS"
    assert result.agent_count == 8
    assert len(result.execution_order) == 8
    assert "review_agent" in result.agent_durations


@patch("crewai.Crew.kickoff")
def test_mocked_market_research_workflow(mock_kickoff):
    mock_res = MagicMock()
    mock_res.raw = '{"synthesis": "Mocked competitive report", "verified": true}'
    mock_kickoff.return_value = mock_res

    query_payload = {
        "query": "Evaluate CloudScale AI vs NexusOps Technologies for autonomous incident resolution.",
        "synthetic": True,
    }

    result = run_market_research_workflow(query_payload, run_id="test_mock_market")
    assert result.status == "SUCCESS"
    assert result.agent_count == 9
    assert len(result.execution_order) == 9
    assert "fact_check_agent" in result.agent_durations
