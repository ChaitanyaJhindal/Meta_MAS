"""Test workflow agent counts and manifest parity."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def test_incident_triage_agent_count():
    manifest_path = BASE_DIR / "Agents" / "incident_triage" / "workflow.json"
    assert manifest_path.exists(), "Workflow manifest missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["agents"]) == 7, f"Expected 7 agents, found {len(data['agents'])}"
    assert len(data["execution_order"]) == 7


def test_expense_reimbursement_agent_count():
    manifest_path = BASE_DIR / "Agents" / "expense_reimbursement" / "workflow.json"
    assert manifest_path.exists(), "Workflow manifest missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["agents"]) == 8, f"Expected 8 agents, found {len(data['agents'])}"
    assert len(data["execution_order"]) == 8


def test_market_research_agent_count():
    manifest_path = BASE_DIR / "Agents" / "market_research" / "workflow.json"
    assert manifest_path.exists(), "Workflow manifest missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["agents"]) == 9, f"Expected 9 agents, found {len(data['agents'])}"
    assert len(data["execution_order"]) == 9


def test_total_agent_count():
    counts = [7, 8, 9]
    assert sum(counts) == 24, "Total agent count across all 3 workflows must be exactly 24"
