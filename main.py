"""Command-Line Interface for Agentic Workflow Optimizer (AWO) Target Workflows.

Commands:
  list            List available multi-agent workflows and their specifications.
  run-incident    Execute IT Incident Triage on a sample ticket.
  run-expense     Execute Employee Expense Reimbursement on a sample claim.
  run-market      Execute Market and Competitor Research on a sample query.
  live-smoke      Execute a lightweight live validation of all 3 workflows against Groq.
  launch-phoenix  Start the local Arize Phoenix tracing UI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from Agents.expense_reimbursement.workflow import run_expense_workflow
from Agents.incident_triage.workflow import run_incident_triage_workflow
from Agents.market_research.workflow import run_market_research_workflow
from common.agent_runner import print_run_summary
from common.settings import GROQ_MODEL, MANDATORY_MODEL
from common.tracing import launch_phoenix_server, setup_tracing


def get_sample_incident() -> dict:
    inc_path = BASE_DIR / "data" / "incident_triage" / "historical_incidents.json"
    if inc_path.exists():
        with open(inc_path, "r", encoding="utf-8") as f:
            incidents = json.load(f).get("incidents", [])
            if incidents:
                return incidents[0]
    return {
        "incident_id": "INC-SAMPLE-101",
        "title": "database-primary: PostgreSQL active connection pool reached 100% (250/250)",
        "service": "database-primary",
        "service_tier": "Tier-1",
        "category": "database_problem",
        "impact_users": 6500,
        "outage_minutes": 45,
        "symptoms": ["PostgreSQL active connection pool reached 100% (250/250)", "High p99 write latency"],
        "synthetic": True,
    }


def get_sample_expense() -> dict:
    exp_path = BASE_DIR / "data" / "expense_reimbursement" / "expense_claims.json"
    if exp_path.exists():
        with open(exp_path, "r", encoding="utf-8") as f:
            claims = json.load(f).get("claims", [])
            if claims:
                return claims[0]
    return {
        "claim_id": "CLM-SAMPLE-201",
        "employee_id": "EMP-401",
        "employee_name": "Elena Rostova",
        "department": "Engineering",
        "submission_date": "2026-09-12",
        "category": "Meals & Entertainment",
        "merchant": "The Grillhouse Steakhouse",
        "currency": "USD",
        "subtotal": 65.00,
        "tax": 5.77,
        "total": 70.77,
        "business_purpose": "Client technical architecture dinner",
        "receipt_text": "THE GRILLHOUSE - Date: 2026-09-12 - Total: $70.77",
        "synthetic": True,
    }


def get_sample_market_query() -> dict:
    return {
        "query": (
            "Compare CloudScale AI, DataPulse Systems, NexusOps Technologies, and Veloce Security "
            "across enterprise latency, pricing predictability, advertised vs actual SLAs, and on-prem readiness."
        ),
        "synthetic": True,
    }


def cmd_list(args):
    """List the three target workflows and their properties."""
    workflows = [
        {
            "name": "incident_triage",
            "agents_count": 7,
            "directory": "Agents/incident_triage/",
            "purpose": "Classify IT incidents, retrieve runbooks, correlate symptoms, estimate severity, and recommend remediation.",
            "execution": "Sequential (Intake -> Classification -> Runbook -> Symptom -> Severity -> Remediation -> Review)",
            "model": GROQ_MODEL,
        },
        {
            "name": "expense_reimbursement",
            "agents_count": 8,
            "directory": "Agents/expense_reimbursement/",
            "purpose": "Process expense claims, parse receipts, test arithmetic, enforce policies, detect duplicates, audit exceptions.",
            "execution": "Sequential (Receipt -> Normalize -> Category -> Amount -> Policy -> Duplicate -> Exception -> Review)",
            "model": GROQ_MODEL,
        },
        {
            "name": "market_research",
            "agents_count": 9,
            "directory": "Agents/market_research/",
            "purpose": "Research 4 enterprise competitors, correlate evidence, build comparison matrix, synthesize findings, fact-check citations.",
            "execution": "Sequential (Planning -> Profile -> Product -> Pricing -> Feedback -> Evidence -> Comparison -> Synthesis -> Fact-Check)",
            "model": GROQ_MODEL,
        },
    ]
    print("\n" + "=" * 70)
    print(" AGENTIC WORKFLOW OPTIMIZER (AWO) - TARGET WORKFLOWS")
    print("=" * 70)
    for wf in workflows:
        print(f"\n* Workflow: {wf['name']} ({wf['agents_count']} Agents)")
        print(f"  Directory: {wf['directory']}")
        print(f"  Purpose  : {wf['purpose']}")
        print(f"  Execution: {wf['execution']}")
        print(f"  Model    : {wf['model']} (Mandatory Groq fixed)")
    print("\n" + "=" * 70 + "\n")


def cmd_run_incident(args):
    setup_tracing()
    sample = get_sample_incident()
    print(f"\n[AWO] Running IT Incident Triage workflow (Ticket: {sample.get('incident_id')})...")
    result = run_incident_triage_workflow(sample)
    print_run_summary(result)


def cmd_run_expense(args):
    setup_tracing()
    sample = get_sample_expense()
    print(f"\n[AWO] Running Employee Expense Reimbursement workflow (Claim: {sample.get('claim_id')})...")
    result = run_expense_workflow(sample)
    print_run_summary(result)


def cmd_run_market(args):
    setup_tracing()
    sample = get_sample_market_query()
    print(f"\n[AWO] Running Market & Competitor Research workflow...")
    result = run_market_research_workflow(sample)
    print_run_summary(result)


def cmd_live_smoke(args):
    setup_tracing()
    print("\n" + "=" * 70)
    print(f" RUNNING LIVE SMOKE TESTS (Groq Model: {MANDATORY_MODEL})")
    print("=" * 70)
    
    target = args.workflow or "all"
    if target in ["all", "incident_triage"]:
        print("\n--> Testing Workflow 1: incident_triage (7 agents)...")
        res1 = run_incident_triage_workflow(get_sample_incident())
        print(f"    [Status: {res1.status}] Completed in {res1.total_duration_seconds:.2f}s across {res1.agent_count} agents.")
    
    if target in ["all", "expense_reimbursement"]:
        print("\n--> Testing Workflow 2: expense_reimbursement (8 agents)...")
        res2 = run_expense_workflow(get_sample_expense())
        print(f"    [Status: {res2.status}] Completed in {res2.total_duration_seconds:.2f}s across {res2.agent_count} agents.")
    
    if target in ["all", "market_research"]:
        print("\n--> Testing Workflow 3: market_research (9 agents)...")
        res3 = run_market_research_workflow(get_sample_market_query())
        print(f"    [Status: {res3.status}] Completed in {res3.total_duration_seconds:.2f}s across {res3.agent_count} agents.")

    print("\n" + "=" * 70)
    print(" Live smoke tests finished successfully.")
    print("=" * 70 + "\n")


def cmd_launch_phoenix(args):
    port = args.port or 6006
    print(f"[AWO] Launching local Arize Phoenix tracing server on port {port}...")
    launch_phoenix_server(port=port)
    print("Keep this terminal window open to preserve local tracing UI. Press Ctrl+C to exit.")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[AWO] Stopped Phoenix tracing server.")


def main():
    parser = argparse.ArgumentParser(description="Agentic Workflow Optimizer - Target Workflows CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    subparsers.add_parser("list", help="List available target workflows")

    p_inc = subparsers.add_parser("run-incident", help="Run IT Incident Triage workflow")
    p_inc.set_defaults(func=cmd_run_incident)

    p_exp = subparsers.add_parser("run-expense", help="Run Employee Expense Reimbursement workflow")
    p_exp.set_defaults(func=cmd_run_expense)

    p_mkt = subparsers.add_parser("run-market", help="Run Market and Competitor Research workflow")
    p_mkt.set_defaults(func=cmd_run_market)

    p_smoke = subparsers.add_parser("live-smoke", help="Run live smoke tests against Groq")
    p_smoke.add_argument("--workflow", choices=["incident_triage", "expense_reimbursement", "market_research", "all"], default="all")
    p_smoke.set_defaults(func=cmd_live_smoke)

    p_px = subparsers.add_parser("launch-phoenix", help="Start Arize Phoenix local tracing UI")
    p_px.add_argument("--port", type=int, default=6006, help="Port to run Phoenix UI on (default: 6006)")
    p_px.set_defaults(func=cmd_launch_phoenix)

    args = parser.parse_args()
    if args.command == "list" or not args.command:
        cmd_list(args)
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
