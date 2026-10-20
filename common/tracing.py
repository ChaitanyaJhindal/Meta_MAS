"""Arize Phoenix and OpenTelemetry distributed tracing integration.

Provides OpenTelemetry spans for:
- Root Workflow executions (e.g., incident_triage, expense_reimbursement, market_research)
- Child Agent executions (e.g., intake_agent, classification_agent, etc.)
- Automatic instrumentation of LLM calls via OpenInference LiteLLM instrumentor.
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

# Ensure UTF-8 console output for Windows compatibility with Phoenix emojis
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Tracer
from phoenix.otel import register
from openinference.instrumentation.litellm import LiteLLMInstrumentor

from common.settings import PHOENIX_COLLECTOR_ENDPOINT, PHOENIX_PROJECT_NAME

_TRACER: Optional[Tracer] = None
_LITELLM_INSTRUMENTED = False
_PHOENIX_SESSION = None


def setup_tracing(project_name: Optional[str] = None, endpoint: Optional[str] = None) -> Tracer:
    """Initialize Arize Phoenix OpenTelemetry tracing and LiteLLM instrumentation."""
    global _TRACER, _LITELLM_INSTRUMENTED

    proj = project_name or PHOENIX_PROJECT_NAME
    ep = endpoint or PHOENIX_COLLECTOR_ENDPOINT

    # Instrument LiteLLM if not already active
    if not _LITELLM_INSTRUMENTED:
        try:
            LiteLLMInstrumentor().instrument()
            _LITELLM_INSTRUMENTED = True
        except Exception:
            pass

    # Register Phoenix TracerProvider with BatchSpanProcessor
    try:
        register(
            project_name=proj,
            endpoint=ep,
            set_global_tracer_provider=True,
            use_batch_processor=True,
        )
        _TRACER = trace.get_tracer(proj)
    except Exception:
        _TRACER = trace.get_tracer("agentic-workflow-optimizer")

    return _TRACER



def get_tracer() -> Tracer:
    """Return the active OpenTelemetry tracer, initializing if necessary."""
    global _TRACER
    if _TRACER is None:
        _TRACER = setup_tracing()
    return _TRACER


def launch_phoenix_server(port: int = 6006):
    """Launch local Phoenix UI server for real-time visualization."""
    global _PHOENIX_SESSION
    import phoenix as px
    if _PHOENIX_SESSION is None:
        try:
            _PHOENIX_SESSION = px.launch_app(port=port)
            print(f"[Phoenix] Tracing UI started at: {_PHOENIX_SESSION.url}")
            return _PHOENIX_SESSION
        except Exception as e:
            print(f"[Phoenix] Note: Could not launch local UI ({e}). Continuing with collector endpoint.")
    return _PHOENIX_SESSION


@contextmanager
def workflow_span(
    workflow_name: str,
    run_id: str,
    inputs: Optional[Dict[str, Any]] = None
) -> Generator[trace.Span, None, None]:
    """Context manager for tracing top-level workflow executions."""
    tracer = get_tracer()
    span_name = f"workflow.{workflow_name}"
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("workflow.name", workflow_name)
        span.set_attribute("workflow.run_id", run_id)
        span.set_attribute("openinference.span.kind", "CHAIN")
        if inputs:
            for k, v in inputs.items():
                span.set_attribute(f"workflow.input.{k}", str(v)[:500])
        start_t = time.perf_counter()
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
        finally:
            elapsed = time.perf_counter() - start_t
            span.set_attribute("workflow.duration_seconds", elapsed)


@contextmanager
def agent_span(
    agent_name: str,
    run_id: str,
    agent_inputs: Optional[Dict[str, Any]] = None
) -> Generator[trace.Span, None, None]:
    """Context manager for tracing individual agent step executions under workflow."""
    tracer = get_tracer()
    span_name = f"agent.{agent_name}"
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.run_id", run_id)
        span.set_attribute("openinference.span.kind", "AGENT")
        if agent_inputs:
            for k, v in agent_inputs.items():
                span.set_attribute(f"agent.input.{k}", str(v)[:500])
        start_t = time.perf_counter()
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
        finally:
            elapsed = time.perf_counter() - start_t
            span.set_attribute("agent.duration_seconds", elapsed)
