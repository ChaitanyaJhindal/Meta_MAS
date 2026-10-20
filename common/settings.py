"""Centralized settings, Groq API key distribution, and configuration validation.

Strict constraints enforced:
1. Groq API keys: Only keys 8 to 14 are utilized, assigned individually per agent role.
2. Model: Strictly openai/gpt-oss-120b. Startup validation aborts if any other model is set.
3. Observability: Phoenix tracing endpoint and project definitions.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import dotenv_values, load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load raw env dict to preserve and strip whitespace accurately
raw_env = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
load_dotenv(ENV_PATH)

# Supported key pool: Strictly keys 8 through 14
ALLOWED_KEY_NAMES = [f"GROQ_API_KEY_{i}" for i in range(8, 15)]

GROQ_KEYS_POOL: Dict[str, str] = {}
for key_name in ALLOWED_KEY_NAMES:
    # Prefer raw_env stripped, fallback to os.environ stripped
    val = raw_env.get(key_name) or os.getenv(key_name) or ""
    val = val.strip()
    if val:
        GROQ_KEYS_POOL[key_name] = val

# Fallback primary key if single key needed
DEFAULT_GROQ_KEY = (
    GROQ_KEYS_POOL.get("GROQ_API_KEY_8")
    or (os.getenv("GROQ_API_KEY") or "").strip()
    or (list(GROQ_KEYS_POOL.values())[0] if GROQ_KEYS_POOL else "")
)

# Mandatory model constraint
MANDATORY_MODEL = "openai/gpt-oss-120b"
configured_model = (os.getenv("GROQ_MODEL") or MANDATORY_MODEL).strip()
if configured_model != MANDATORY_MODEL:
    raise ValueError(
        f"Invalid model configuration: '{configured_model}'. "
        f"All workflows must strictly use '{MANDATORY_MODEL}'."
    )
GROQ_MODEL = MANDATORY_MODEL

# Phoenix Tracing Configuration
PHOENIX_COLLECTOR_ENDPOINT = os.getenv(
    "PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"
).strip()
PHOENIX_PROJECT_NAME = os.getenv(
    "PHOENIX_PROJECT_NAME", "agentic-workflow-optimizer"
).strip()
PHOENIX_API_KEY = (os.getenv("PHOENIX_API_KEY") or "").strip()

# Explicit per-agent key assignments across the 7 available keys (8..14)
# Each agent role receives a dedicated key from the pool.
AGENT_KEY_ASSIGNMENTS: Dict[str, str] = {
    # Workflow 1: IT Incident Triage (Exactly 7 agents -> 1-to-1 mapping with keys 8..14)
    "intake_agent": "GROQ_API_KEY_8",
    "classification_agent": "GROQ_API_KEY_9",
    "runbook_agent": "GROQ_API_KEY_10",
    "symptom_agent": "GROQ_API_KEY_11",
    "severity_agent": "GROQ_API_KEY_12",
    "remediation_agent": "GROQ_API_KEY_13",
    "incident_review_agent": "GROQ_API_KEY_14",

    # Workflow 2: Expense Reimbursement (8 agents distributed across keys 8..14)
    "receipt_agent": "GROQ_API_KEY_8",
    "normalize_agent": "GROQ_API_KEY_9",
    "category_agent": "GROQ_API_KEY_10",
    "amount_agent": "GROQ_API_KEY_11",
    "policy_agent": "GROQ_API_KEY_12",
    "duplicate_agent": "GROQ_API_KEY_13",
    "exception_agent": "GROQ_API_KEY_14",
    "expense_review_agent": "GROQ_API_KEY_8",

    # Workflow 3: Market Research (9 agents distributed across keys 8..14)
    "planning_agent": "GROQ_API_KEY_8",
    "profile_agent": "GROQ_API_KEY_9",
    "product_agent": "GROQ_API_KEY_10",
    "pricing_agent": "GROQ_API_KEY_11",
    "feedback_agent": "GROQ_API_KEY_12",
    "evidence_agent": "GROQ_API_KEY_13",
    "comparison_agent": "GROQ_API_KEY_14",
    "synthesis_agent": "GROQ_API_KEY_8",
    "fact_check_agent": "GROQ_API_KEY_9",
}


def get_groq_key_for_agent(agent_name: str) -> str:
    """Return the designated Groq API key (from 8 to 14) for a given agent name."""
    key_name = AGENT_KEY_ASSIGNMENTS.get(agent_name)
    if not key_name:
        # Fallback to key 8 if unrecognized
        key_name = "GROQ_API_KEY_8"
    
    key_val = GROQ_KEYS_POOL.get(key_name)
    if not key_val:
        # If specific key not set in env, use default or placeholder
        key_val = DEFAULT_GROQ_KEY
    return key_val


def create_agent_llm(agent_name: str, temperature: float = 0.1):
    """Factory creating a CrewAI LLM instance strictly bound to openai/gpt-oss-120b
    and the agent's dedicated Groq API key."""
    import litellm
    from crewai import LLM

    # Enable drop_params in LiteLLM
    litellm.drop_params = True

    # Ensure unsupported parameters like 'cache_breakpoint' from CrewAI are stripped for Groq
    if not getattr(litellm, "_groq_sanitizer_applied", False):
        orig_completion = litellm.completion

        def _sanitized_completion(*args, **kwargs):
            if "messages" in kwargs and isinstance(kwargs["messages"], list):
                for msg in kwargs["messages"]:
                    if isinstance(msg, dict):
                        msg.pop("cache_breakpoint", None)
            resp = orig_completion(*args, **kwargs)
            try:
                if hasattr(resp, "usage") and resp.usage:
                    from common.agent_runner import ACTIVE_TRACKER
                    prompt = getattr(resp.usage, "prompt_tokens", 0) or 0
                    completion = getattr(resp.usage, "completion_tokens", 0) or 0
                    total = getattr(resp.usage, "total_tokens", 0) or (prompt + completion)
                    ACTIVE_TRACKER.record_usage(prompt, completion, total)
            except Exception:
                pass
            return resp

        litellm.completion = _sanitized_completion
        litellm._groq_sanitizer_applied = True

    api_key = get_groq_key_for_agent(agent_name)
    if not api_key:
        api_key = "dummy_mock_key_for_offline_testing"

    # In CrewAI with litellm, Groq models are prefixed as 'groq/<model>'
    model_str = f"groq/{GROQ_MODEL}"
    return LLM(
        model=model_str,
        api_key=api_key,
        temperature=temperature,
    )

