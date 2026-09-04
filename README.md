# PaperReplicator 🔬

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-Deterministic%20Sandbox%20%2B%20Typed%20LLM-success.svg)]()
[![Evaluations](https://img.shields.io/badge/Provenance-Cryptographic%20SHA--256-orange.svg)]()

> **Autonomous Scientific Paper Replication & Evidence-Driven Verification Engine**
> 
> *Given a scientific research paper, extract verifiable empirical claims, resolve required code and dataset assets, execute sandboxed experiments in isolated Docker environments, compare results against published findings using statistical tolerance boundaries, investigate discrepancies, and produce an evidence-backed reproducibility report.*

---

## 🎯 The Problem

A significant fraction of published computational machine learning findings cannot be reproduced due to:
* Undocumented hyperparameters or missing preprocessing pipelines.
* Silent environment and dependency decay ("code rot").
* Stochastic seed sensitivity and unreported variance.

Existing agentic approaches suffer from two extremes:
1. **Superficial Chatbots:** Summarize papers without executing or verifying any code.
2. **Unconstrained Agents (e.g., *The AI Scientist*):** Prone to dangerous failure modes including p-hacking (cherry-picking seeds), bypassing execution timeouts by altering internal scripts, and hallucinating evaluation metrics.

**PaperReplicator** solves this with an **adversarial, out-of-band execution architecture** that separates semantic reasoning from deterministic execution and cryptographic provenance.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    A[Research Paper PDF] -->|Deterministic Layout Parsing| B[Structured Markdown & Tables]
    B -->|Typed LLM Extraction| C[Verifiable Claims Registry]
    C -->|Asset Discovery Engine| D[Resolved Git Repo & Dataset Specs]
    D -->|Harness Builder| E[Isolated Execution Bundle]
    
    subgraph Sandbox["Docker Sandbox (Network: None, Memory: 8GB)"]
        E -->|Out-of-Band Watchdog Enforced| F[Execute Verification Pipeline]
        F --> G[stdout / stderr / reproduce_metrics.json]
    end
    
    G -->|Deterministic Tolerance Comparator| H{Within Tolerance?}
    H -->|Delta <= eps| I[Verdict: REPLICATED EXACT / APPROXIMATE]
    H -->|Delta > eps| J[Forensic Discrepancy Engine]
    J -->|Hypothesis Ranking| K[Diagnostic Investigation]
    
    I --> L[Cryptographic Provenance DAG]
    K --> L
    L --> M[Auditable Reproducibility Report]
```

---

## 🔑 Core Differentiators

| Feature | Generic LLM Agents | PaperReplicator |
| :--- | :--- | :--- |
| **Trust Model** | "Self-assessment" (hallucination prone) | **Cryptographic Chain of Custody** (SHA-256 for PDF, code, data, logs) |
| **Security Boundary** | LLM executes arbitrary host commands | **Isolated Docker Sandbox** (`--network none`, non-root, read-only root) |
| **Integrity Guardrails** | Susceptible to timeout tampering & p-hacking | **Host-Side Watchdog** (`SIGKILL` enforcer) + deterministic seed injection |
| **Failure Analysis** | Binary crash (`0.0` or `1.0`) | **Forensic Discrepancy Engine** (isolates data drift, seed variance, ablations) |
| **Evaluation** | Free-form chat text | **Deterministic 5-Tier Verdict** (`EXACT`, `PARTIAL`, `DISCREPANT`, `FAILED`, `UNVERIFIABLE`) |

---

## 📦 Repository Structure

```
paper-replicator/
├── Dockerfile.sandbox          # Hardened container definition
├── pyproject.toml              # Build & dependency specifications
├── configs/
│   └── default_config.yaml     # Execution limits & model endpoints
├── paperrep/
│   ├── cli.py                  # Typer/Rich command-line interface
│   ├── pipeline.py             # Orchestrator state machine
│   ├── schemas/                # Pydantic v2 data contracts
│   │   ├── paper.py            # PaperDocument & Section schemas
│   │   ├── claim.py            # ClaimSpec & Citation schemas
│   │   ├── experiment.py       # ExperimentPlan & Dataset schemas
│   │   ├── execution.py        # ExecutionRun & Telemetry schemas
│   │   └── verdict.py          # 5-Tier EvaluationVerdict & Diagnosis
│   ├── comparator/             # Deterministic numerical comparator
│   ├── provenance/             # Cryptographic SHA-256 hashing
│   └── sandbox/                # Security sanitization & watchdog supervisor
└── tests/                      # Unit & integration test suite
```

---

## 🚀 Quickstart

### 1. Installation
```bash
git clone https://github.com/omkargadute/paper-replicator.git
cd paper-replicator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Compare Published Claims vs. Reproduction Results
```bash
paperrep compare 91.4 91.1 --metric Accuracy --strict 0.5 --loose 2.0
```

### 3. Compute Cryptographic Artifact Hashes
```bash
paperrep hash path/to/paper.pdf
```

### 4. Run Test Suite
```bash
pytest
```

---

## 📄 License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.
