# Functional Multi-Agent Workflows for Agentic Workflow Optimizer (AWO)

This repository implements the target baseline multi-agent workflows designed for testing and benchmarking the **Agentic Workflow Optimizer (AWO)**.

Each workflow is built using **CrewAI**, powered exclusively by **Groq**'s `openai/gpt-oss-120b` model, observed with **Arize Phoenix** distributed tracing, and validated against rich, domain-authentic local synthetic datasets.

---

## 1. Workflows & Agent Architecture

The project consists of **three workflows** comprising **exactly 24 functional agents**:

```
project/
├── Agents/
│   ├── incident_triage/         # Workflow 1 (7 Agents)
│   ├── expense_reimbursement/   # Workflow 2 (8 Agents)
│   └── market_research/         # Workflow 3 (9 Agents)
├── common/
│   ├── settings.py              # Groq key distribution & mandatory model enforcement
│   ├── agent_runner.py          # Metrics collection & execution logger
│   └── tracing.py               # Arize Phoenix OpenTelemetry tracing
├── data/                        # Local synthetic datasets
├── runs/                        # Execution JSON artifacts and JSONL summaries
├── tests/                       # Automated test suite (16 test cases)
├── main.py                      # Unified CLI entry point
├── generate_dummy_data.py       # Seeded deterministic dataset generator
├── requirements.txt
├── .env.example
└── README.md
```

### Workflow 1: IT Incident Triage (7 Agents)
* **Execution Graph:** Intake $\rightarrow$ Classification $\rightarrow$ Runbook Retrieval $\rightarrow$ Symptom Correlation $\rightarrow$ Severity Assessment $\rightarrow$ Remediation $\rightarrow$ Final Review
* **Agents:**
  1. `intake_agent` (Intake Specialist) — *Key: `GROQ_API_KEY_8`*
  2. `classification_agent` (Classification Engineer) — *Key: `GROQ_API_KEY_9`*
  3. `runbook_agent` (Runbook Specialist) — *Key: `GROQ_API_KEY_10`*
  4. `symptom_agent` (Diagnostic & Symptom Specialist) — *Key: `GROQ_API_KEY_11`*
  5. `severity_agent` (Severity Assessment Specialist) — *Key: `GROQ_API_KEY_12`*
  6. `remediation_agent` (Remediation Engineer) — *Key: `GROQ_API_KEY_13`*
  7. `review_agent` (Incident Quality Reviewer) — *Key: `GROQ_API_KEY_14`*
* **AWO Optimization Opportunities:** Dynamic routing for Simple vs. Complex incidents, bypassing diagnostic stages on recurring issues, parallel execution of runbook and symptom retrieval.

### Workflow 2: Employee Expense Reimbursement (8 Agents)
* **Execution Graph:** Receipt Extraction $\rightarrow$ Normalization $\rightarrow$ Categorization $\rightarrow$ Amount Validation $\rightarrow$ Policy Validation $\rightarrow$ Duplicate Detection $\rightarrow$ Exception Audit $\rightarrow$ Final Review
* **Agents:**
  1. `receipt_agent` (Receipt Extraction) — *Key: `GROQ_API_KEY_8`*
  2. `normalize_agent` (Expense Normalization) — *Key: `GROQ_API_KEY_9`*
  3. `category_agent` (Category Classifier) — *Key: `GROQ_API_KEY_10`*
  4. `amount_agent` (Deterministic Arithmetic) — *Key: `GROQ_API_KEY_11`*
  5. `policy_agent` (Policy Compliance) — *Key: `GROQ_API_KEY_12`*
  6. `duplicate_agent` (Duplicate Detection) — *Key: `GROQ_API_KEY_13`*
  7. `exception_agent` (Independent Red-Team Audit) — *Key: `GROQ_API_KEY_14`*
  8. `review_agent` (Adjudication & Synthesis) — *Key: `GROQ_API_KEY_8`*
* **AWO Optimization Opportunities:** Pruning overlapping audit agents (`exception_agent` $\rightarrow$ `policy_agent` + `amount_agent`), parallel execution of compliance checks, fast-path approval routing.

### Workflow 3: Market and Competitor Research (9 Agents)
* **Execution Graph:** Planning $\rightarrow$ Profile Research $\rightarrow$ Product Capabilities $\rightarrow$ Pricing & Licensing $\rightarrow$ Customer Feedback $\rightarrow$ Evidence Correlation $\rightarrow$ Competitor Comparison $\rightarrow$ Executive Synthesis $\rightarrow$ Fact-Checking
* **Agents:**
  1. `planning_agent` (Research Planning) — *Key: `GROQ_API_KEY_8`*
  2. `profile_agent` (Corporate Profiling) — *Key: `GROQ_API_KEY_9`*
  3. `product_agent` (Technical Capabilities) — *Key: `GROQ_API_KEY_10`*
  4. `pricing_agent` (Pricing & Licensing) — *Key: `GROQ_API_KEY_11`*
  5. `feedback_agent` (Customer Sentiment) — *Key: `GROQ_API_KEY_12`*
  6. `evidence_agent` (Conflict Triangulation) — *Key: `GROQ_API_KEY_13`*
  7. `comparison_agent` (Comparison Matrix) — *Key: `GROQ_API_KEY_14`*
  8. `synthesis_agent` (Executive Narrative) — *Key: `GROQ_API_KEY_8`*
  9. `fact_check_agent` (Citation Verification) — *Key: `GROQ_API_KEY_9`*
* **AWO Optimization Opportunities:** Parallelization of the 4 independent data retrieval agents, consolidating serial summarization, direct citation linking.

---

## 2. Model & API Key Constraints

1. **Mandatory Model:** Every agent strictly uses `openai/gpt-oss-120b` via Groq. Startup validation aborts if any other model is configured.
2. **Key Distribution:** Strictly utilizes `GROQ_API_KEY_8` through `GROQ_API_KEY_14` (keys 1–7 are ignored). Each agent role is assigned a dedicated key to prevent cross-agent collisions.

---

## 3. Installation & Setup

### Prerequisites
* Python 3.10 or 3.11 installed.

### Setup Virtual Environment
```bash
# Using uv (recommended)
uv venv .venv --python 3.11
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Configure Environment Variables
Copy `.env.example` to `.env` and insert your keys:
```bash
cp .env.example .env
```
Ensure `GROQ_API_KEY_8` through `GROQ_API_KEY_14` are present in `.env`.

---

## 4. CLI Usage

The system provides a clean command-line interface in `main.py`:

```bash
# 1. List all available workflows and specifications
python main.py list

# 2. Run IT Incident Triage on a sample ticket
python main.py run-incident

# 3. Run Employee Expense Reimbursement on a sample claim
python main.py run-expense

# 4. Run Market & Competitor Research on a research query
python main.py run-market

# 5. Run live smoke test against Groq
python main.py live-smoke --workflow incident_triage

# 6. Launch local Arize Phoenix tracing UI
python main.py launch-phoenix --port 6006
```

---

## 5. Arize Phoenix Observability

Traces are automatically captured for all workflows:
- **Root Spans:** `workflow.<name>` tracking overall latency, status, input parameters, and duration.
- **Child Spans:** `agent.<name>` tracking individual agent execution times and intermediate outputs.
- **LLM Spans:** OpenInference instrumentor records all Groq LLM completions, model name (`openai/gpt-oss-120b`), token counts, and prompts.

### Starting Phoenix UI
In a separate terminal, run:
```bash
python main.py launch-phoenix
```
Open your browser to `http://localhost:6006` to inspect live traces, spans, and dependency trees.

---

## 6. Synthetic Datasets

All datasets are stored locally under `data/` and marked with `"synthetic": true`:
- `data/incident_triage/`: 200 historical incidents, 30 operational runbooks (`RB-101`..`RB-130`), 50 log snippets, and a service catalog.
- `data/expense_reimbursement/`: 150 claims with realistic ASCII receipts, 6 reimbursement policies (`POL-EXP-01`..`POL-EXP-06`), 40 historical submissions for duplicate detection, and employee directories.
- `data/market_research/`: 4 fictional B2B SaaS competitors (*CloudScale AI*, *DataPulse Systems*, *NexusOps Technologies*, *Veloce Security*) and 19 granular source documents with stable IDs (`DOC-CS-*`, `DOC-DP-*`, `DOC-NO-*`, `DOC-VS-*`) and deliberate real-world contradictions for conflict analysis.

To regenerate datasets deterministically:
```bash
python generate_dummy_data.py
```

---

## 7. Running Automated Tests

A comprehensive 16-test suite verifies agent counts, schemas, deterministic arithmetic, policy matrices, and manifests without consuming live API tokens:

```bash
pytest tests -v
```
All 16 tests pass:
- `test_workflow_agent_counts.py` (Validates 7, 8, 9 agents = 24 total)
- `test_datasets.py` (Validates presence, schema, and synthetic labels)
- `test_deterministic_logic.py` (Verifies severity rules, expense math, duplicate matching)
- `test_workflow_manifests.py` (Verifies `workflow.json` parity with code and key ranges 8..14)
- `test_agent_contracts_mocked.py` (Verifies end-to-end execution of all 3 workflows)
#   M e t a _ M A S  
 