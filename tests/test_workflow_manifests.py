"""Test workflow JSON manifests against implementation requirements."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def test_manifest_structure_and_model():
    manifests = [
        BASE_DIR / "Agents" / "incident_triage" / "workflow.json",
        BASE_DIR / "Agents" / "expense_reimbursement" / "workflow.json",
        BASE_DIR / "Agents" / "market_research" / "workflow.json",
    ]

    for m_path in manifests:
        assert m_path.exists(), f"Manifest missing at {m_path}"
        with open(m_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Mandatory model verification
        model_cfg = manifest.get("model_configuration", {})
        assert model_cfg.get("provider") == "groq"
        assert model_cfg.get("model") == "openai/gpt-oss-120b", "All manifests must declare openai/gpt-oss-120b"
        assert model_cfg.get("enforce_fixed_model") is True

        # Required manifest keys
        for key in ["workflow_name", "version", "execution_order", "agents", "optimization_opportunities"]:
            assert key in manifest, f"Missing key '{key}' in {m_path.name}"

        # Check each agent in manifest maps to an actual file
        agent_dir = m_path.parent
        for agent in manifest["agents"]:
            agent_file = agent_dir / agent["file"]
            assert agent_file.exists(), f"Agent file {agent['file']} not found in {agent_dir}"
            assert agent["assigned_key"].startswith("GROQ_API_KEY_")
            # Keys strictly 8 to 14
            key_num = int(agent["assigned_key"].split("_")[-1])
            assert 8 <= key_num <= 14, f"Key {agent['assigned_key']} out of allowed range 8..14"
