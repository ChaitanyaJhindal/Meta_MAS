# 🚀 Meta_MAS

**A Production-Grade Multi-Agent System (MAS) Benchmark & Optimization Suite**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/Framework-CrewAI%20v1.15-orange.svg)](https://github.com/crewAIInc/crewAI)
[![Groq](https://img.shields.io/badge/Inference-Groq%20Cloud-red.svg)](https://groq.com/)
[![Observability](https://img.shields.io/badge/Tracing-Arize%20Phoenix-purple.svg)](https://phoenix.arize.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)](tests/)

---

## 📌 Overview

**Meta_MAS** is a production-ready benchmark suite containing **24 specialized AI agents** organized across **3 real-world enterprise workflows**. 

It is designed to test, benchmark, and optimize multi-agent interactions, token consumption, and execution graphs.

- **🤖 24 Autonomous Agents**: Divided across IT Incident Triage, Expense Reimbursement, and Market Research.
- **⚡ High-Speed Inference**: Powered exclusively by Groq running `openai/gpt-oss-120b`.
- **📊 Full Observability**: Built-in OpenTelemetry distributed tracing with **Arize Phoenix** to monitor latencies, tokens, and agent decision chains.
- **🧪 100% Offline Testing**: Comprehensive test suite that verifies workflow manifests, schemas, and deterministic math without using paid API tokens.
- **📁 Authentic Synthetic Data**: Ready-to-use local datasets for zero-setup execution.

---

## 🏗️ The 3 Workflows

| # | Workflow | Agents | Description | Execution Flow |
|---|---|:---:|---|---|
| **1** | **IT Incident Triage** | 7 | Classifies outages, retrieves runbooks, correlates symptoms, assigns severity, and drafts remediation steps. | Intake ➔ Classification ➔ Runbook ➔ Symptoms ➔ Severity ➔ Remediation ➔ Review |
| **2** | **Expense Reimbursement** | 8 | Extracts receipts, validates arithmetic, enforces corporate policy, catches duplicates, and flags audit exceptions. | Receipt ➔ Normalize ➔ Categorize ➔ Amount ➔ Policy ➔ Duplicates ➔ Audit ➔ Review |
| **3** | **Market Research** | 9 | Evaluates competitors, analyzes pricing and capabilities, reconciles contradictory claims, and drafts comparison matrices. | Plan ➔ Profile ➔ Product ➔ Pricing ➔ Feedback ➔ Evidence ➔ Matrix ➔ Synthesis ➔ Fact-Check |

---

## ⚡ Quick Start (Under 3 Minutes)

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/ChaitanyaJhindal/Meta_MAS.git
cd Meta_MAS
```

### 2. Set Up Virtual Environment

Using standard Python:
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Activate on Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

*(Optional: If you use `uv`, run `uv venv .venv --python 3.11 && .venv\Scripts\activate && uv pip install -r requirements.txt`)*

### 3. Configure API Keys
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and add your Groq API keys:
- The system distributes requests across dedicated keys (`GROQ_API_KEY_8` through `GROQ_API_KEY_14`) to prevent rate limits during multi-agent execution.
- If you only have one key for testing, you can paste the same key into `GROQ_API_KEY_8` through `GROQ_API_KEY_14`.

---

## 💻 How to Run

All workflows are controlled through a single command-line interface in `main.py`:

```bash
# 1. View all workflows and specifications
python main.py list

# 2. Run Workflow 1 (IT Incident Triage)
python main.py run-incident

# 3. Run Workflow 2 (Employee Expense Reimbursement)
python main.py run-expense

# 4. Run Workflow 3 (Market & Competitor Research)
python main.py run-market

# 5. Run live end-to-end smoke test on all workflows
python main.py live-smoke

# 6. Launch the local Arize Phoenix Tracing Dashboard
python main.py launch-phoenix
```

---

## 🔍 Observability with Arize Phoenix

Every run records end-to-end execution metrics (tokens, latency, agent inputs, and outputs).

1. In a separate terminal, launch the dashboard:
   ```bash
   python main.py launch-phoenix
   ```
2. Open your browser and go to:
   ```
   http://localhost:6006
   ```
3. You can inspect:
   - **Root Spans**: Workflow latency and execution status.
   - **Agent Spans**: Individual execution times and reasoning steps.
   - **LLM Spans**: Token counts, prompt text, and Groq response times.

---

## 🧪 Automated Testing

Run the full automated test suite without consuming any live API tokens:

```bash
pytest tests -v
```

**Test Coverage (16 Tests):**
- ✅ Agent count validation (7 + 8 + 9 = 24 agents)
- ✅ Synthetic dataset schema & presence checks
- ✅ Deterministic logic checks (severity calculations, expense arithmetic, duplicate detection)
- ✅ Workflow JSON manifest integrity
- ✅ End-to-end mocked execution contracts for all 3 workflows

---

## 📂 Project Structure

```
Meta_MAS/
├── Agents/                      # The 24 Functional Agents
│   ├── incident_triage/         # Workflow 1 (7 Agents + workflow.py)
│   ├── expense_reimbursement/   # Workflow 2 (8 Agents + workflow.py)
│   └── market_research/         # Workflow 3 (9 Agents + workflow.py)
│
├── common/                      # Shared Infrastructure
│   ├── settings.py              # Groq key routing & mandatory model check
│   ├── agent_runner.py          # Metrics collector & run summaries
│   └── tracing.py               # Arize Phoenix / OpenTelemetry tracing setup
│
├── data/                        # Authentic Local Datasets
│   ├── incident_triage/         # 200 incidents, 30 runbooks, log snippets
│   ├── expense_reimbursement/   # 150 receipts, policy documents, employee directory
│   └── market_research/         # 4 competitor profiles, 19 source documents
│
├── runs/                        # Run outputs and benchmark execution logs (.gitkeep)
├── tests/                       # 16 automated tests (Zero-token cost)
├── generate_dummy_data.py       # Seeded deterministic dataset generator
├── main.py                      # Unified CLI entrypoint
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment template
└── README.md                    # Project documentation
```

---

## 🔄 Regenerating Datasets

To regenerate all local datasets deterministically with fixed random seeds:

```bash
python generate_dummy_data.py
```

---

## 🛠️ Configuration Details

| Setting | Value | Description |
|---|---|---|
| **Primary Model** | `openai/gpt-oss-120b` | Enforced at startup across all agents. |
| **Provider** | Groq Cloud | Ultra-low latency agent execution. |
| **API Keys** | `GROQ_API_KEY_8` - `14` | Distributed key allocation across agent roles. |
| **Tracing URL** | `http://localhost:6006` | Arize Phoenix OpenTelemetry Collector. |

---

## 📄 License

This project is licensed under the MIT License.