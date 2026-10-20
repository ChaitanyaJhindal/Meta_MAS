"""Shared execution metrics recorder and runner helper.

Saves structured execution results into runs/ and formats human-readable
console summaries for each workflow execution.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class WorkflowExecutionResult:
    workflow_name: str
    run_id: str
    status: str  # "SUCCESS" | "FAILED"
    execution_order: List[str] = field(default_factory=list)
    agent_durations: Dict[str, float] = field(default_factory=dict)
    total_duration_seconds: float = 0.0
    agent_count: int = 0
    llm_call_count: int = 0
    token_usage: Dict[str, Any] = field(default_factory=lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "is_available": False,
    })
    estimated_cost_usd: Optional[float] = None
    cost_estimation_label: str = "Unavailable (requires real-time provider token billing callback)"
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RunMetricsTracker:
    """Thread-safe real-time LLM call and token consumption accumulator."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.llm_call_count = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def record_usage(self, prompt: int, completion: int, total: int):
        self.llm_call_count += 1
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += total

    def snapshot(self) -> Dict[str, Any]:
        prompt_rate = 0.59 / 1_000_000
        completion_rate = 0.79 / 1_000_000
        cost = (self.prompt_tokens * prompt_rate) + (self.completion_tokens * completion_rate)
        has_calls = self.llm_call_count > 0
        return {
            "llm_call_count": self.llm_call_count,
            "token_usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
                "is_available": has_calls,
            },
            "estimated_cost_usd": round(cost, 6) if has_calls else None,
            "cost_estimation_label": (
                f"Estimated (${cost:.6f} USD at standard $0.59/$0.79 per 1M tokens)"
                if has_calls else "No live LLM calls recorded"
            ),
        }


ACTIVE_TRACKER = RunMetricsTracker()



def generate_run_id(prefix: str = "run") -> str:
    """Generate a clean timestamped correlation run ID."""
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"{prefix}_{now_str}_{short_uuid}"


def save_run_result(result: WorkflowExecutionResult) -> Path:
    """Persist the workflow run result as structured JSON and append to JSONL summary."""
    run_file = RUNS_DIR / f"{result.workflow_name}_{result.run_id}.json"
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)

    # Append single-line summary to runs_summary.jsonl
    summary_file = RUNS_DIR / "runs_summary.jsonl"
    summary_entry = {
        "timestamp": result.timestamp,
        "run_id": result.run_id,
        "workflow": result.workflow_name,
        "status": result.status,
        "agent_count": result.agent_count,
        "duration_seconds": round(result.total_duration_seconds, 3),
        "error": result.error,
    }
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary_entry) + "\n")

    return run_file


def print_run_summary(result: WorkflowExecutionResult):
    """Print a clean, structured console summary of the workflow execution."""
    divider = "=" * 68
    subdivider = "-" * 68
    print(f"\n{divider}")
    print(f" WORKFLOW EXECUTION SUMMARY: {result.workflow_name.upper()}")
    print(divider)
    print(f" Run ID           : {result.run_id}")
    print(f" Status           : {'[SUCCESS]' if result.status == 'SUCCESS' else '[FAILED]'}")
    print(f" Total Duration   : {result.total_duration_seconds:.2f}s")
    print(f" Agents Executed  : {result.agent_count}")
    print(f" Execution Order  : {' -> '.join(result.execution_order)}")
    print(subdivider)
    print(" Agent Execution Durations:")
    for agent, dur in result.agent_durations.items():
        print(f"   * {agent:<28} : {dur:.2f}s")
    print(subdivider)
    print(f" Token Usage      : {result.token_usage.get('total_tokens', 'N/A')} tokens")
    print(f" Estimated Cost   : {result.cost_estimation_label}")
    if result.error:
        print(subdivider)
        print(f" Error Details    : {result.error}")
    print(subdivider)
    print(" Structured Output Preview:")
    out_str = json.dumps(result.output, indent=2)
    preview_lines = out_str.splitlines()[:20]
    for line in preview_lines:
        print(f"   {line}")
    if len(out_str.splitlines()) > 20:
        print("   ... [truncated in preview, full output saved to run artifact]")
    print(divider + "\n")
