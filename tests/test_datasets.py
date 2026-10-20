"""Test dataset file existence, structured schema, and synthetic markings."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def test_incident_triage_datasets():
    it_dir = DATA_DIR / "incident_triage"
    for fname in ["historical_incidents.json", "runbooks.json", "log_snippets.json", "services_catalog.json"]:
        fpath = it_dir / fname
        assert fpath.exists(), f"Missing dataset: {fname}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data.get("synthetic") is True, f"{fname} must be marked synthetic"
            assert data.get("count", 0) > 0, f"{fname} must contain records"


def test_expense_reimbursement_datasets():
    er_dir = DATA_DIR / "expense_reimbursement"
    for fname in ["expense_claims.json", "policies.json", "employees.json", "historical_submissions.json"]:
        fpath = er_dir / fname
        assert fpath.exists(), f"Missing dataset: {fname}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data.get("synthetic") is True, f"{fname} must be marked synthetic"
            assert data.get("count", 0) > 0, f"{fname} must contain records"


def test_market_research_datasets():
    mr_dir = DATA_DIR / "market_research"
    for fname in ["competitors.json", "source_documents.json"]:
        fpath = mr_dir / fname
        assert fpath.exists(), f"Missing dataset: {fname}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data.get("synthetic") is True, f"{fname} must be marked synthetic"
            assert data.get("count", 0) > 0, f"{fname} must contain records"


def test_stable_identifiers():
    # Verify ID formatting conventions
    with open(DATA_DIR / "incident_triage" / "runbooks.json", "r", encoding="utf-8") as f:
        runbooks = json.load(f)["runbooks"]
        assert all(rb["runbook_id"].startswith("RB-") for rb in runbooks)

    with open(DATA_DIR / "expense_reimbursement" / "policies.json", "r", encoding="utf-8") as f:
        policies = json.load(f)["policies"]
        assert all(p["policy_id"].startswith("POL-EXP-") for p in policies)

    with open(DATA_DIR / "market_research" / "source_documents.json", "r", encoding="utf-8") as f:
        docs = json.load(f)["documents"]
        assert all(d["doc_id"].startswith("DOC-") for d in docs)
