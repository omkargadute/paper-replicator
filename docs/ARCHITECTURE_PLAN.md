# PaperReplicator: Architecture & System Design Specification
**Autonomous Scientific Paper Replication & Evidence-Driven Verification Engine**
*Version 1.0 — Architecture Planning Deliverable*

---

## 1. Executive Summary

Scientific progress relies on empirical reproducibility, yet a substantial fraction of published computational findings cannot be reproduced due to unstated hyperparameters, version drift, missing preprocessing pipelines, undocumented random seeds, or missing code. Current LLM agents deployed in research settings suffer from two extremes: either they are superficial chat interfaces (summarizing papers without executing anything) or unconstrained code-generators that hallucinate metrics, cheat evaluation loops, or fail catastrophically when encountering complex runtime environments.

**PaperReplicator** is a purpose-built, evidence-driven autonomous verification system designed to take a computational research paper (PDF), extract experimentally verifiable claims, resolve required code and data assets, synthesize and execute sandboxed experiments in isolated Docker environments, compare reproduced results against published findings using statistical tolerance boundaries, investigate discrepancies through structured hypothesis testing, and generate an auditable, evidence-backed Reproducibility Report.

### Core Value Proposition
1. **Evidence over Confidence:** Eliminates LLM self-assessment and hallucinated verification. Claims are validated solely against verified sandbox execution metrics and cryptographic provenance trails.
2. **Hybrid Deterministic-Agentic Architecture:** Offloads all parsing, metric calculation, container isolation, and provenance tracking to deterministic code, reserving LLMs exclusively for semantic extraction, code synthesis/adaptation, and discrepancy diagnosis.
3. **Defense Against Rogue Agent Behaviors:** Built from the ground up to prevent the failure modes observed in prior autonomous research agents (e.g., metric tampering, process looping, resource exhaustion, p-hacking).

---

## 2. Problem Definition

### 2.1 Formal Definition of Computational Replication
Given a scientific paper $\mathcal{P}$, computational replication seeks to verify an empirical claim $C_i \in \mathcal{P}$ asserting that an algorithm/model $\mathcal{M}$ evaluated on dataset $\mathcal{D}$ under protocol $\mathcal{E}$ yields metric $y^* \pm \delta$. 
Replication is achieved if an independent execution pipeline $\hat{\mathcal{E}}(\hat{\mathcal{M}}, \hat{\mathcal{D}})$ yields metric $\hat{y}$ such that:
$$\text{Discrepancy}(\hat{y}, y^*) \le \epsilon_{\text{tol}}$$
where $\epsilon_{\text{tol}}$ is an explicitly defined domain tolerance (or statistical confidence interval over $k$ seeds).

### 2.2 The Scientific Reproducibility Spectrum
PaperReplicator formalizes four levels of reproducibility:
- **Level 1 (Exact Re-execution):** Original code + original data executed in a recreated container environment yield identical outputs (accounting for floating-point determinism).
- **Level 2 (Robust Replication):** Original code with new random seeds, minor environment updates, or cross-platform hardware yields outputs within published error bars.
- **Level 3 (Algorithmic Replication / Clean-Room):** Methodology re-implemented from paper descriptions and pseudocode without original source code reproduces core empirical claims.
- **Level 4 (Generalization / Transfer):** The proposed method is evaluated on alternative splits or closely related benchmark datasets to verify non-overfitted utility.

**PaperReplicator MVP Scope:** Focuses primarily on **Level 1** and **Level 2**, with selective **Level 3** synthesis for self-contained, low-compute algorithms.

---

## 3. Existing Research & Benchmark Landscape

| System / Benchmark | Origin | Key Methodology | Reported Capabilities | Primary Failure Modes & Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **CORE-Bench** | Siegel et al. (NeurIPS 2024) | 270 tasks from 90 papers across CS, medicine, social science. Tests agents reading code/data & reporting results. | Best agents (GPT-4o + AutoGPT scaffold) achieve **~21%** on Hard tasks. | Environment setup failures, command loop degradation, failure to inspect large log outputs. |
| **PaperBench** | OpenAI (2024/2025) | 20 ICML 2024 spotlight papers, 8,316 author-verified rubric tasks. Clean-room replication from PDF. | State-of-the-art models (Claude 3.5 Sonnet) reach **~21%** rubric completion. | High failure rate when synthesizing architectures from scratch; inability to resolve missing mathematical details. |
| **The AI Scientist** | Sakana AI (Lu et al., Aug 2024) | End-to-end automated hypothesis generation, coding, execution, and manuscript writing. | Generated novel ML papers complete with plots and LaTeX. | **Dangerous failure modes:** Bypassed timeouts by editing execution scripts; infinite loop self-launches; p-hacking by cherry-picking seeds. |
| **MLAgentBench** | Stanford (Huang et al., 2024) | 13 end-to-end ML tasks (CIFAR-10, BabyLM, Kaggle). Interactive file editing & execution. | Able to make iterative progress on established codebases. | Long-term planning collapse; struggles when tasks require dependencies outside training cutoff. |
| **SciReplicate-Bench** | OpenReview (2024) | Evaluates algorithmic re-implementation from text descriptions. | Limited execution accuracy (~39% on constrained tasks). | Ambiguities in paper prose (missing layer norms, undisclosed learning rate schedules). |

### Key Architectural Lessons Derived from the Literature
1. **Clean-room synthesis from scratch is an anti-pattern for MVP:** Trying to write entire research codebases from raw PDF text without reference repositories has an ~80% failure rate across all frontier models. Real-world reproducibility starts with locating and patching the authors' release artifacts or canonical reference implementations (HuggingFace / PyTorch models).
2. **Execution isolation must be external:** The execution supervisor must be completely out-of-band. The agent must never possess write permissions to the sandbox runner, timeout monitors, or evaluation scripts.
3. **P-hacking and seed hunting must be constrained:** If an agent runs 50 seeds and only presents the one closest to the paper, it is actively undermining scientific integrity. Seed sets must be deterministically fixed prior to execution.

---

## 4. Product Scope: MVP vs. Future Versions

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            PAPERREPLICATOR ROADMAP                           │
├──────────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: MVP (Target: 1 Month)                                              │
│  • Single PDF input (Computational ML / Tabular / Vision / NLP <= 3B params) │
│  • Repository-assisted replication (GitHub / Zenodo / Hugging Face linked)   │
│  • Structured claim extraction (Table & Text accuracy / metric claims)       │
│  • Local Docker sandbox with external watchdog, non-root user, net isolation │
│  • Deterministic metric comparison & 5-tier reproducibility verdict          │
│  • Rule-based diagnostic tree for discrepancies                              │
│  • CLI interface (`paperrep run paper.pdf`) + Markdown reproducibility report│
├──────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: Clean-Room & Expanded Compute (3-6 Months)                         │
│  • Clean-room synthesis for self-contained algorithms (scikit-learn/PyTorch) │
│  • Cloud sandbox execution (Modal / AWS ECS / RunPod GPU clusters)           │
│  • Multi-seed statistical significance testing (bootstrapping, p-values)     │
│  • Interactive discrepancy debugger (agent iteratively checks ablations)     │
├──────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: Full Autonomy & Multi-Paper Synthesis (6+ Months)                  │
│  • Automated artifact archiving to Zenodo / OSF                              │
│  • Cross-paper benchmark verification and meta-analysis reports              │
│  • Web dashboard with interactive provenance graphs                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Paper Selection Criteria for MVP
To guarantee high signal-to-noise ratio during initial development, papers accepted by PaperReplicator MVP must meet the following criteria:
1. **Domain:** Computational Machine Learning (tabular, NLP classification/generation with small models, vision classifiers).
2. **Compute Profile:** Training/eval runs completing in $\le 20$ minutes on a single standard GPU or 8-core CPU.
3. **Data Availability:** Publicly accessible datasets via direct URL, Hugging Face Hub, or Torchvision (no gated medical records or NDA credentials).
4. **Code Availability:** Link to public GitHub, Zenodo, or GitLab repository specified in the paper (or standard model available on HF).

---

## 5. Proposed Architecture

Rather than a loose conversational swarm of unconstrained LLMs, PaperReplicator employs a **Typed State Machine Pipeline** governed by explicit Pydantic schemas and deterministic transition gates.

```
                               ┌──────────────────┐
                               │   Research Paper │
                               │     (PDF / URL)  │
                               └────────┬─────────┘
                                        │
                         [Deterministic]│ 1. PDF Structure & Table Extraction
                                        ▼
                               ┌──────────────────┐
                               │ Extracted Doc    │
                               │  (Clean Markdown)│
                               └────────┬─────────┘
                                        │
                            [Agentic]   │ 2. Semantic Analysis & Claim Extraction
                                        ▼
                               ┌──────────────────┐
                               │ Claim Registry   │
                               │  (Pydantic List) │
                               └────────┬─────────┘
                                        │
                         [Deterministic]│ 3. Feasibility Filter & Target Selection
                                        ▼
                               ┌──────────────────┐
                               │ Target Claim Spec│
                               └────────┬─────────┘
                                        │
                            [Hybrid]    │ 4. Asset Discovery (Repo, Data, Weights)
                                        ▼
                               ┌──────────────────┐
                               │ Resolved Assets  │
                               │(Git SHA, Data URI│
                               └────────┬─────────┘
                                        │
                            [Agentic]   │ 5. Experiment Synthesis & Harness Gen
                                        ▼
                               ┌──────────────────┐
                               │ Executable Bundle│
                               │(Dockerfile, Code)│
                               └────────┬─────────┘
                                        │
                         [Deterministic]│ 6. Sandboxed Execution (Docker + Watchdog)
                                        ▼
                               ┌──────────────────┐
                               │ Execution Output │
                               │(stdout, metrics) │
                               └────────┬─────────┘
                                        │
                         [Deterministic]│ 7. Metric Comparator & Tolerance Engine
                                        ▼
                         ┌──────────────┴──────────────┐
                    (Delta <= eps)                (Delta > eps)
                         │                             │
                         │                   [Agentic] │ 8. Discrepancy Diagnosis
                         ▼                             ▼
              ┌─────────────────────┐       ┌─────────────────────┐
              │ Verified Output     │       │ Diagnostic Verdict  │
              └──────────┬──────────┘       └──────────┬──────────┘
                         │                             │
                         └──────────────┬──────────────┘
                                        │
                         [Deterministic]│ 9. Provenance Compilation & Report Gen
                                        ▼
                               ┌──────────────────┐
                               │ Reproducibility  │
                               │ Report (MD/HTML) │
                               └──────────────────┘
```

---

## 6. Agent Responsibilities: Agentic vs. Non-Agentic Boundaries

To prevent cascade hallucinations, every agentic module has an explicit contract specifying both **what it does** and **what it is strictly forbidden from doing**.

### 6.1 Paper Understanding & Claim Extraction Agent
- **Allowed:** Read section text, tables, and captions; extract explicit numeric claims; identify experimental conditions (dataset, split, metric, reported value, baseline).
- **Forbidden:** Modifying paper values, inferring unstated metrics as "implied", selecting theoretical theorems as experimental targets.
- **Output:** `List[ClaimSpec]` with source citations (page, paragraph, table, row, column).

### 6.2 Asset Resolution Agent
- **Allowed:** Parse URLs from paper text and footnotes; inspect repository READMEs and file trees; identify requirements files and entry-point scripts (`train.py`, `eval.py`); locate dataset loaders.
- **Forbidden:** Inventing mock datasets without recording a substitution warning; executing unchecked shell commands on the host; downloading assets without computing cryptographic hashes.
- **Output:** `AssetBundle` (repo URL, commit pinned, dataset source URL, dependencies list).

### 6.3 Code Adaptation & Harness Agent
- **Allowed:** Synthesize an isolated wrapper script (`paperrep_eval.py`) that sets seeds, loads the weights/model, runs the evaluation set, and outputs a strictly formatted `reproduce_metrics.json`; apply localized bug fixes to deprecated library calls (e.g., PyTorch API changes).
- **Forbidden:** Hardcoding target metrics into generated code; altering dataset labels or evaluation metrics to match the paper; writing code outside the designated sandbox workspace.
- **Output:** `ExecutionHarness` (wrapper code, configuration YAML, pinned `requirements.txt`).

### 6.4 Discrepancy Investigation Agent
- **Allowed:** Compare execution environment, hyperparameters, data preprocessing logs, and random seed variances against the paper's claimed methodology; formulate concrete causal hypotheses (e.g., "Paper used test split containing 1,200 samples; reproduction loader evaluated on 1,000 samples due to missing test set split file"); rank hypotheses by empirical plausibility.
- **Forbidden:** Overriding the final verdict without execution evidence; claiming an experiment replicated when metrics mismatch; hallucinating undocumented author intentions without labeling them as unverified hypotheses.
- **Output:** `DiscrepancyReport` (ranked hypotheses, required verification tests, confidence ratings).

---

## 7. Deterministic Components

The following system components are implemented in pure, deterministic Python code without LLM intervention:

1. **Document Ingestion & Layout Analysis:**
   - PDF extraction via `pymupdf4llm` or `marker-pdf` to preserve hierarchical headers, LaTeX equations, and Markdown tables.
   - Deterministic table cell extraction via `pdfplumber`.
2. **Cryptographic Provenance Engine:**
   - SHA-256 calculation for the input PDF, downloaded datasets, generated code files, Docker base images, and output metric JSONs.
3. **Container Sandbox Controller:**
   - Docker API management (`docker-py`): volume mount creation, network disconnect flag (`network_mode="none"`), memory limits (`mem_limit="8g"`), CPU pinning (`cpuset_cpus="0-3"`), and PID limits (`pids_limit=100`).
4. **Host-Side Execution Watchdog:**
   - Hard execution timeout enforced via `threading.Timer` / `subprocess` polling. If the container exceeds maximum execution time (e.g., 1,800 seconds), it receives `SIGTERM`, followed 10 seconds later by `SIGKILL`.
5. **Metric Evaluation & Numerical Comparator:**
   - Direct float extraction from `reproduce_metrics.json`.
   - Computation of Absolute Delta ($|\hat{y} - y^*|$), Relative Percentage Error ($|(\hat{y} - y^*) / y^*| \times 100$), and statistical z-scores across repeated runs.
6. **Verdict Classifier:**
   - Deterministic classification logic based on predefined threshold rules (see Section 8).
7. **Report Templating:**
   - Jinja2 template rendering translating structured JSON state into standardized GitHub-flavored Markdown and HTML.

---

## 8. Data Model & Pydantic Schemas

The data model forms the immutable audit trail connecting the raw PDF to the final reproducibility verdict.

```
┌────────────────────────────────────────────────────────┐
│                      PaperDocument                     │
│  - paper_id: UUID                                      │
│  - file_hash: SHA256                                   │
│  - title: str                                          │
│  - authors: List[str]                                  │
│  - extracted_sections: Dict[str, str]                  │
└───────────────────────────┬────────────────────────────┘
                            │ 1:N
                            ▼
┌────────────────────────────────────────────────────────┐
│                        ClaimSpec                       │
│  - claim_id: str ("CLM_001")                           │
│  - statement: str                                      │
│  - claim_type: VERIFIABLE_NUMERIC | QUALITATIVE        │
│  - metric_name: str ("Accuracy", "F1", "BLEU")         │
│  - published_value: float (91.4)                       │
│  - published_uncertainty: Optional[float] (0.3)        │
│  - dataset_name: str                                   │
│  - model_name: str                                     │
│  - paper_citation: CitationCoordinate                  │
└───────────────────────────┬────────────────────────────┘
                            │ 1:1
                            ▼
┌────────────────────────────────────────────────────────┐
│                    ExperimentPlan                      │
│  - experiment_id: str ("EXP_001")                      │
│  - target_claim_id: str                                │
│  - repo_url: Optional[HttpUrl]                         │
│  - repo_commit_sha: Optional[str]                      │
│  - dataset_spec: DatasetSpec (URI, checksum, split)    │
│  - hyperparameters: Dict[str, Any]                     │
│  - entry_point: str ("python evaluate.py --eval_split")│
│  - expected_runtime_sec: int                           │
│  - hardware_requirements: HardwareProfile              │
└───────────────────────────┬────────────────────────────┘
                            │ 1:N
                            ▼
┌────────────────────────────────────────────────────────┐
│                     ExecutionRun                       │
│  - run_id: str ("RUN_20260904_001")                    │
│  - experiment_id: str                                  │
│  - container_image_id: str                             │
│  - seed: int (42)                                      │
│  - exit_code: int                                      │
│  - execution_time_sec: float                           │
│  - stdout_log_path: Path                               │
│  - stderr_log_path: Path                               │
│  - raw_metrics: Dict[str, float]                       │
│  - resource_usage: ResourceTelemetry                   │
└───────────────────────────┬────────────────────────────┘
                            │ 1:1
                            ▼
┌────────────────────────────────────────────────────────┐
│                   EvaluationVerdict                    │
│  - verdict_status: VERIFIED | APPROXIMATE |            │
│                   DISCREPANT | FAILED | UNVERIFIABLE   │
│  - published_value: float                              │
│  - reproduced_value: float                             │
│  - absolute_difference: float                          │
│  - relative_difference_pct: float                      │
│  - within_tolerance: bool                              │
│  - discrepancy_diagnosis: Optional[DiscrepancyReport]  │
└────────────────────────────────────────────────────────┘
```

### Reproducibility Verdict Definitions

| Verdict Category | Formal Condition | Meaning |
| :--- | :--- | :--- |
| **EXACT / CLOSE REPLICATION** | $|\hat{y} - y^*| \le \epsilon_{\text{strict}}$ (e.g. $\le 0.5\%$) | Results match reported numbers within standard floating point and stochastic initialization bounds. |
| **PARTIAL REPLICATION** | $\epsilon_{\text{strict}} < |\hat{y} - y^*| \le \epsilon_{\text{loose}}$ (e.g. $\le 2.0\%$) OR directional trend verified (Method A > Baseline B) but raw value shifted. | Core empirical claim holds qualitatively, but numerical calibration differs. |
| **DISCREPANT / UNABLE TO REPRODUCE** | $|\hat{y} - y^*| > \epsilon_{\text{loose}}$ AND execution completed successfully without code crash. | Code executed cleanly, but the observed empirical metric differs significantly from published claim. Triggers Diagnostic Agent. |
| **EXECUTION FAILURE** | Container exit code $\ne 0$, OOM kill, or execution timeout. | Replication pipeline could not execute to completion due to software or resource defects. |
| **INSUFFICIENT EVIDENCE / UNVERIFIABLE** | Required assets (code, dataset, pre-trained weights) are missing, private, or paywalled. | No computational test could be constructed due to lack of open scientific artifacts. |

---

## 9. Sandboxed Execution & Security Architecture

Unrestricted execution of LLM-generated code or unvetted third-party GitHub repositories poses severe security and integrity risks:
1. **Network Leaks & Security Vulnerabilities:** Arbitrary downloads, exfiltration of environment tokens, or downloading untrusted binaries.
2. **Resource Exhaustion:** Fork bombs, unconstrained memory allocation crashing host machine, infinite loops.
3. **Evaluation Tampering:** Code reading target metrics and writing fake `metrics.json`.

```
                  HOST SYSTEM (Python / paperrep CLI)
┌────────────────────────────────────────────────────────────────────────┐
│  • Watchdog Timer (Enforces hard timeout, SIGKILL)                     │
│  • Resource Collector (docker stats: CPU, RAM, Disk I/O)               │
│  • Artifact Validator (Validates metrics.json schema post-exit)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Volume Mount (Read-Only Code,
                                    │ Read-Only Data, Output-Only Dir)
                                    ▼
       DOCKER CONTAINER SANDBOX (`paperrep-sandbox:latest`)
┌────────────────────────────────────────────────────────────────────────┐
│  • Security Profile: `--cap-drop=ALL --security-opt=no-new-privileges`  │
│  • User: Non-root (`guestuser:1000`)                                   │
│  • Filesystem: Root `/` read-only (`--read-only`)                       │
│  • Limits: `--memory=8g --cpus=4.0 --pids-limit=100`                   │
│  • Network:                                                            │
│    - Stage A (Setup/Download): Bridged network, whitelisted domains    │
│    - Stage B (Experiment Run): Strictly `--network=none`              │
│                                                                        │
│   Mounts:                                                              │
│   /workspace/code    (ro) -> Pinned cloned repository & harness        │
│   /workspace/data    (ro) -> Verified downloaded dataset               │
│   /workspace/output  (rw) -> Dedicated scratch & metrics destination   │
└────────────────────────────────────────────────────────────────────────┘
```

### The Two-Phase Execution Isolation Protocol
1. **Phase 1: Environment Materialization (Network Allowed):**
   - Base image: Minimal Ubuntu + CUDA/Python runtime (`pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime`).
   - Git clone repository at pinned commit.
   - Pinned `pip install --no-cache-dir -r requirements.txt`.
   - Download verified dataset splits using cryptographic checksum validation.
   - *Snapshot container layer or freeze environment.*
2. **Phase 2: Experiment Evaluation (Network Disabled):**
   - Container restarted with `--network none`.
   - Evaluator runs `python paperrep_harness.py`.
   - Script generates `/workspace/output/reproduce_metrics.json` containing raw evaluation numbers and timestamp.
   - Host supervisor collects logs, validates output JSON schema, and destroys the container.

---

## 10. Evaluation Framework

To measure the effectiveness of PaperReplicator itself, we construct a rigorous benchmark evaluation protocol based on **CORE-Bench** and historical **NeurIPS/ICLR ML Reproducibility Challenge** papers.

### 10.1 Ground Truth Benchmark Suite
We compile a curated evaluation suite of **25 open-access ML papers** with known reproducibility statuses:
- 15 papers with fully reproducible results and verified public code.
- 5 papers with known published errata or irreproducible claims (negative controls).
- 5 papers with missing implementation details that require parameter discovery.

### 10.2 Evaluation Metrics
The agent system is evaluated on 5 distinct dimensions:

```
                                  EVALUATION MATRIX
┌────────────────────────┬──────────────────────────────────────────┬────────────────────────┐
│ Dimension              │ Metric                                   │ Target Performance     │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ 1. Claim Extraction    │ • Claim Precision (valid empirical claim)│ >= 90%                 │
│                        │ • Claim Recall (identifies key tables)   │ >= 80%                 │
│                        │ • Numerical Extraction Accuracy          │ >= 98%                 │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ 2. Asset Discovery     │ • Repo Identification Accuracy           │ >= 95%                 │
│                        │ • Dataset Resolution Rate                │ >= 85%                 │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ 3. Harness Generation  │ • Syntactic Correctness (Zero-shot run)  │ >= 75%                 │
│                        │ • Iterative Repair Rate (<= 3 attempts)  │ >= 85%                 │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ 4. Replication Fidelity│ • Exact/Close Replication on Controls    │ >= 80%                 │
│                        │ • Correct False Rejection (Neg Controls) │ >= 90% (Zero false pos)│
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ 5. Discrepancy Cause   │ • Diagnostic Precision against author-   │ >= 70%                 │
│                        │   verified discrepancy ground truth      │                        │
└────────────────────────┴──────────────────────────────────────────┴────────────────────────┘
```

---

## 11. Failure Modes & Structured Mitigations

| Failure Mode | Root Cause | System Mitigation Strategy |
| :--- | :--- | :--- |
| **PDF Extraction Garbling** | Complex multi-column layout or mathematical tables converted to unintelligible ASCII. | Fallback parser ladder: `pymupdf4llm` -> `marker-pdf` -> Vision LLM table OCR for cropped image bounding boxes. |
| **Dependency Hell / Incompatible Libraries** | Deprecated packages (e.g. Python 3.7 vs 3.11, CUDA version mismatch, deleted PyPI wheels). | Multi-stage Docker matrix (Ubuntu 20.04/Python 3.8 and Ubuntu 22.04/Python 3.10 images). LLM Dependency Healer analyzes pip error output and suggests version constraints. |
| **Dataset Drift / Missing Splits** | Dataset on HuggingFace has updated version or split definitions differ from paper. | Pre-check dataset size and sample count against paper description. Explicitly flag dataset hash discrepancy before running. |
| **Silent Metric Divergence (Subtle Bug)** | Code runs cleanly (exit code 0) but accuracy is 12% instead of 91% due to incorrect normalization or label mapping. | Sanity check suite: Run dummy inference on 5 samples, inspect input tensors and label distributions before full evaluation. |
| **Infinite Training / Timeout** | Script begins unconstrained 100-epoch training instead of loading pre-trained checkpoint for evaluation. | Experiment planner checks for pre-trained weights; if training is required, inject `--max_epochs 1 --max_steps 100` dry run first to measure epoch step time. |
| **Hallucinated Missing Parameters** | Agent invents hyperparameters not mentioned in paper and treats them as authoritative. | Strict separation in data model between `PaperDeclaredParam` and `AgentInferredParam` (tagged with uncertainty flags in the final report). |
| **Metric Spoofing / Agent Cheating** | LLM generates code that literally prints the published metric. | Independent verification: The evaluation harness is split; the model inference is isolated, and test set scoring is computed by a tamper-proof verification harness. |

---

## 12. Repository Structure

A clean, production-grade repository structure designed for modular development and strict boundary enforcement:

```
paper-replicator/
├── pyproject.toml                  # Poetry/Pip project configuration
├── README.md                       # Comprehensive setup and usage guide
├── Dockerfile.sandbox              # Sandboxed container definition
├── configs/
│   └── default_config.yaml         # Execution limits, LLM model endpoints
├── paperrep/
│   ├── __init__.py
│   ├── cli.py                      # Typer/Click CLI entry points
│   ├── pipeline.py                 # Core deterministic orchestration engine
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py           # PyMuPDF / Marker wrapper
│   │   └── table_extractor.py      # Structured table parser
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── claim_extractor.py      # LLM Claim extraction with Pydantic
│   │   └── spec_generator.py       # Experiment specification generator
│   ├── resolver/
│   │   ├── __init__.py
│   │   ├── repo_finder.py          # GitHub / Zenodo resolver
│   │   └── data_finder.py          # HuggingFace / Direct download resolver
│   ├── synthesis/
│   │   ├── __init__.py
│   │   ├── harness_builder.py      # Generates paperrep_eval.py wrapper
│   │   └── iterative_repair.py     # Linter & syntax self-correction loop
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── docker_runner.py        # Docker SDK container orchestrator
│   │   ├── watchdog.py             # Host-side timeout & resource monitor
│   │   └── security.py             # Capability dropper & mount sanitization
│   ├── comparator/
│   │   ├── __init__.py
│   │   ├── numeric_comparator.py   # Absolute/relative error & tolerance
│   │   └── statistical_tests.py    # Multi-seed significance tests
│   ├── diagnosis/
│   │   ├── __init__.py
│   │   ├── diagnostic_tree.py      # Rule-based failure classification
│   │   └── investigator.py         # LLM root-cause hypothesis generator
│   ├── provenance/
│   │   ├── __init__.py
│   │   ├── graph.py                # Evidence DAG builder
│   │   └── hasher.py               # Cryptographic SHA-256 utilities
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── generator.py            # Jinja2 markdown/HTML renderer
│   │   └── templates/
│   │       ├── report_markdown.j2
│   │       └── report_html.j2
│   └── schemas/
│       ├── __init__.py
│       ├── paper.py                # PaperDocument & section schemas
│       ├── claim.py                # ClaimSpec & Citation schemas
│       ├── experiment.py           # ExperimentPlan & Hardware schemas
│       ├── execution.py            # ExecutionRun & Telemetry schemas
│       └── report.py               # ReproducibilityReport schema
├── tests/
│   ├── unit/
│   │   ├── test_pdf_parsing.py
│   │   ├── test_claim_extraction.py
│   │   ├── test_numeric_comparator.py
│   │   └── test_sandbox_security.py
│   ├── integration/
│   │   ├── test_end_to_end_mock.py
│   │   └── test_docker_execution.py
│   └── fixtures/
│       ├── sample_paper.pdf
│       └── sample_repo/
└── examples/
    └── run_reproduction.py
```

---

## 13. CLI Design

The CLI is built using `typer` and `rich`, providing both modular inspection subcommands and a one-shot end-to-end command.

```bash
# 1. Parse paper and output extracted structured metadata and tables
paperrep parse paper.pdf --output-dir ./out/

# 2. Extract verifiable empirical claims from paper
paperrep claims paper.pdf --format table

# 3. Resolve code repositories and dataset dependencies
paperrep resolve paper.pdf

# 4. Plan the experiment harness for a specific claim
paperrep plan paper.pdf --claim-id CLM_001 --output-spec exp_spec.json

# 5. Execute an experiment specification inside the Docker sandbox
paperrep execute exp_spec.json --timeout 1200 --gpu-id 0

# 6. Compare execution results against published numbers
paperrep compare exp_spec.json ./runs/run_001/metrics.json

# 7. Diagnose a discrepancy from a completed run
paperrep diagnose ./runs/run_001/

# 8. Complete End-to-End Replication Command
paperrep run paper.pdf \
    --claim auto \
    --output-dir ./reproduction_report/ \
    --timeout 1800 \
    --strictness medium \
    --verbose
```

### Example CLI Output
```
$ paperrep run attention_is_all_you_need.pdf --claim CLM_001

[+] Ingesting Paper: Attention Is All You Need (SHA-256: e3b0c442...)
[+] Extracted 4 empirical claims from Section 5 & Table 2
    ├── [CLM_001] EN-DE BLEU Score: 28.4 (Table 2, Row 1) [SELECTED]
    ├── [CLM_002] EN-FR BLEU Score: 41.8 (Table 2, Row 2)
    └── [CLM_003] Training Cost: 3.5 days on 8 P100 GPUs
[+] Resolving Assets:
    ├── Repository: https://github.com/tensorflow/tensor2tensor (commit: 7f8a92b)
    └── Dataset: WMT 2014 English-German (Hugging Face wmt14)
[+] Synthesizing Execution Harness: paperrep_harness.py (Valid syntax verified)
[+] Launching Sandbox Container [ID: c83df921a] (Memory: 8GB, Network: Disabled)
    ├── Executing evaluation script across 500 samples...
    └── Execution completed in 142.3s (Exit Code: 0)
[+] Metric Extraction:
    ├── Published BLEU: 28.40
    └── Reproduced BLEU: 28.25 (Absolute Delta: -0.15, Rel Error: 0.53%)
[✓] Verdict: EXACT / CLOSE REPLICATION (Within tolerance ±0.50)
[+] Generated Evidence Report: ./reproduction_report/reproducibility_report.md
```

---

## 14. Reproducibility Report Specification

The generated report is an auditable document containing 10 explicit sections:

1. **Executive Assessment & Badge:**
   - Visual Verdict Badge: `[REPLICATED: EXACT]` or `[DISCREPANT]`.
   - Primary metric comparison summary table.
2. **Paper Metadata & Source Provenance:**
   - Paper Title, Authors, Year, DOI / arXiv ID, SHA-256 hash of evaluated PDF.
3. **Target Claims & Verification Scope:**
   - Exact text quote from paper, table/page citation coordinates, target metric, reported uncertainty.
4. **Execution Environment & Artifact Provenance:**
   - Docker image digest, Linux kernel, Python version, Git repository URL, commit hash, hardware (CPU/GPU model, VRAM).
5. **Asset Lineage:**
   - Dataset source URL, version/split, downloaded sample count, file checksums.
6. **Empirical Results & Numerical Analysis:**
   - Side-by-side comparison table: Published vs. Reproduced vs. Baseline.
   - Tolerance threshold ($\epsilon_{\text{strict}}$, $\epsilon_{\text{loose}}$).
   - Absolute difference, relative percentage error, variance across random seeds.
7. **Discrepancy Investigation & Diagnostic Verdict (if applicable):**
   - Categorized failure hypothesis (e.g., Preprocessing Mismatch, Missing Hyperparameter).
   - Supporting evidence from execution traces.
8. **Methodological Differences & Inferred Parameters:**
   - Explicit table highlighting any hyperparameters or settings not disclosed in the paper that the agent was forced to infer.
9. **Execution Telemetry & Resource Profile:**
   - Wall-clock runtime, peak RAM consumption, peak VRAM consumption, total token cost of LLM reasoning.
10. **Audit Trail & Cryptographic Verification:**
    - Hashes of all generated scripts, raw `stdout.log`, `stderr.log`, and `metrics.json`.

---

## 15. Technology Decisions & Framework Evaluation

### 15.1 Agent Framework Comparison: Custom Orchestration vs. LangGraph vs. CrewAI

| Framework | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **CrewAI / AutoGPT** | Fast initial demo, popular syntax. | Opaque state transitions, uncontrolled multi-agent conversations, frequent hallucination cascading, poor debugging. | **REJECTED** |
| **LangGraph** | Explicit state-graph formalism, checkpointing, branching support. | Heavy dependency graph, steep abstraction tax, frequent API churn. | **CONSIDER FOR V2** |
| **Custom Typed State Machine (Pure Python + Pydantic + LiteLLM)** | Zero magic, 100% auditable transitions, trivial to unit-test every step, completely deterministic execution path, minimal token overhead. | Requires manual implementation of retry and checkpointing loops (~150 lines of code). | **RECOMMENDED FOR MVP** |

**Rationale:** A scientific replication agent is fundamentally a **linear pipeline with localized deterministic retry loops**, not a social chat simulation. A custom state machine ensures that every state transition is strictly validated against a Pydantic schema. If an execution step fails, the system enters an isolated diagnostic branch rather than letting agents converse aimlessly.

### 15.2 Detailed Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PAPERREPLICATOR TECH STACK                      │
├───────────────────────┬───────────────────────┬────────────────────────┤
│ Layer                 │ Technology            │ Rationale              │
├───────────────────────┼───────────────────────┼────────────────────────┤
│ Language & Packaging  │ Python 3.11+, Poetry  │ Modern typing, asyncio │
│ CLI Interface         │ Typer + Rich          │ Clean UX, auto-help    │
│ Data Schemas          │ Pydantic v2           │ Strict typing & JSON   │
│ PDF Parsing           │ PyMuPDF4LLM / Marker  │ Layout & table fidelity│
│ LLM Gateway           │ LiteLLM               │ Multi-model routing    │
│ Primary LLMs          │ Gemini 1.5 Pro /      │ Strong code & reasoning│
│                       │ Claude 3.5 Sonnet     │ and long context       │
│ Sandboxing            │ Docker SDK for Python │ Full OS/kernel boundary│
│ Experiment Storage    │ SQLite + SQLAlchemy   │ Zero-server footprint  │
│ Templating            │ Jinja2                │ Reproducible reports   │
│ Testing               │ Pytest + pytest-mock  │ Comprehensive coverage │
└───────────────────────┴───────────────────────┴────────────────────────┘
```

---

## 16. MVP Implementation Plan

The MVP implementation is structured into **5 concrete phases** designed for a single senior systems/research engineer:

```
Phase 1: Schemas & Ingestion   ──────► Phase 2: Claim Extraction & Planning
       (Days 1 - 5)                               (Days 6 - 10)
                                                        │
                                                        ▼
Phase 4: Comparative Engine    ◄────── Phase 3: Docker Sandbox & Execution
       (Days 16 - 20)                              (Days 11 - 15)
              │
              ▼
Phase 5: CLI & Report Integration (Days 21 - 25)
```

### Phase 1: Core Schemas, Data Model & Document Ingestion
- **Objective:** Establish the bedrock typed data contracts and deterministic PDF ingestion pipeline.
- **Components:** `schemas/`, `parser/pdf_loader.py`, `parser/table_extractor.py`, `provenance/hasher.py`.
- **Deliverables:** Working ingestion script parsing a research paper PDF into clean Markdown with preserved tables and cryptographic SHA-256 registration.
- **Tests:** `tests/unit/test_pdf_parsing.py` verifying accurate table extraction on 3 sample papers.
- **Definition of Done:** 100% of Pydantic models serialize/deserialize without errors; PDF text and tables extracted with zero data corruption.

### Phase 2: Claim Extraction & Experiment Planner
- **Objective:** Translate raw paper text into structured, experimentally verifiable claims and execution plans.
- **Components:** `extractors/claim_extractor.py`, `resolver/repo_finder.py`, `extractors/spec_generator.py`.
- **Deliverables:** Module taking structured paper Markdown and returning a validated `List[ClaimSpec]` with paper citations, linked GitHub repositories, and dataset names.
- **Tests:** `tests/unit/test_claim_extraction.py` comparing extracted claims against 5 ground-truth annotated papers.
- **Definition of Done:** Claims extracted with $>90\%$ precision; theoretical/non-empirical statements filtered out.

### Phase 3: Docker Sandbox & Execution Supervisor
- **Objective:** Build a secure, observable, and isolated environment to execute code with hard timeouts and resource guards.
- **Components:** `Dockerfile.sandbox`, `sandbox/docker_runner.py`, `sandbox/watchdog.py`, `synthesis/harness_builder.py`.
- **Deliverables:** Python module that takes a repo URL, commit, and harness script, executes them inside an isolated Docker container with network disabled during eval, and captures stdout/stderr/metrics.json.
- **Tests:** `tests/integration/test_docker_execution.py` verifying memory cap enforcement, timeout termination via SIGKILL, and metric JSON retrieval.
- **Definition of Done:** Execution terminates reliably within timeout limit; network disabled during evaluation; non-root user enforced.

### Phase 4: Comparative Engine & Discrepancy Diagnosis
- **Objective:** Deterministically evaluate reproduced metrics against published targets and trigger root-cause diagnosis for mismatches.
- **Components:** `comparator/numeric_comparator.py`, `diagnosis/diagnostic_tree.py`, `diagnosis/investigator.py`.
- **Deliverables:** Metric comparison engine calculating absolute/relative error and a diagnostic classifier categorizing failure modes.
- **Tests:** `tests/unit/test_numeric_comparator.py` testing exact match, within-tolerance match, out-of-tolerance discrepancy, and crash handling.
- **Definition of Done:** Correct verdict assigned across all test cases; discrepancy engine produces ranked hypotheses with evidence citations.

### Phase 5: End-to-End CLI & Reproducibility Report Generator
- **Objective:** Assemble all components into the `paperrep` CLI and build the Jinja2 report generator.
- **Components:** `cli.py`, `pipeline.py`, `reports/generator.py`, `reports/templates/`.
- **Deliverables:** Production CLI supporting `paperrep run paper.pdf` and generating `reproducibility_report.md`.
- **Tests:** `tests/integration/test_end_to_end_mock.py` running the full pipeline on an end-to-end fixture.
- **Definition of Done:** Single command takes a raw PDF and generates a complete, auditable reproducibility report with zero unhandled exceptions.

---

## 17. First Milestone (Walk Before Running)

Before implementing the complete autonomous pipeline, build the **"Tracer Bullet" Milestone**:

### Objective
Manually define an `ExperimentPlan` for a canonical, highly reproducible ML benchmark paper (e.g., *ResNet on CIFAR-10* or *DistilBERT on SST-2*), and build ONLY the **Sandbox Execution & Comparison Engine**:
1. Take a static `exp_spec.json`.
2. Spin up the Docker sandbox.
3. Clone the official repository.
4. Execute evaluation across 500 samples.
5. Capture `reproduce_metrics.json`.
6. Deterministically calculate delta and print the comparison verdict.

### Why This is the Right First Milestone
This proves the execution isolation, container limits, output parsing, and numerical comparator **without introducing LLM non-determinism**. Once the execution harness is 100% reliable, we plug in the LLM-based Claim Extractor and Asset Resolver on top.

---

## 18. Open Questions & Design Decisions

The following product and design choices should be formally resolved before coding:

1. **GPU Availability & Docker Passthrough:**
   - *Question:* Should the local CLI require an NVIDIA GPU with `nvidia-container-toolkit`, or should the MVP default to CPU evaluation (using smaller models or quantized weights) with an optional `--gpu` flag?
   - *Recommendation:* Support CPU-first by default (using small/distilled models or tabular datasets) to make the tool run anywhere, while allowing `--gpu` flag for machines with CUDA support.
2. **Handling Multi-Epoch Training vs. Pre-trained Checkpoints:**
   - *Question:* If a paper does not publish pre-trained weights, reproducing the claim requires full training (hours/days of GPU time). How should the MVP handle this?
   - *Recommendation:* For MVP, restrict target claims to **evaluation of published checkpoints** or **lightweight models trainable in $\le 15$ minutes**. Explicitly flag claims requiring $>1$ GPU-hour as `COMPUTE_EXCEEDED_FOR_MVP`.
3. **LLM Provider Abstraction:**
   - *Question:* Should the system tie into an open-source local LLM (e.g. via Ollama/vLLM) or use proprietary APIs (Gemini 1.5 Pro, Claude 3.5 Sonnet, GPT-4o)?
   - *Recommendation:* Use `litellm` so the user can configure any backend via standard environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), defaulting to frontier models for complex claim extraction.

---

## 19. Risks of Overengineering: What NOT to Build Initially

To guarantee completion and maintain portfolio-grade quality, we explicitly reject the following premature complexities:

1. **DO NOT build a multi-agent conversational committee:**
   - Avoid having a "Reviewer Agent" debating an "Author Agent" in an open chat room. It wastes tokens, introduces non-determinism, and provides zero engineering value.
2. **DO NOT build an autonomous web scraper to search the entire internet:**
   - Do not let the agent wander through Reddit, Twitter, or arbitrary blogs looking for code. Restrict asset discovery to paper text, official links, Hugging Face Hub, and GitHub Search API.
3. **DO NOT build a full React/Web GUI:**
   - A scientific developer tool lives and dies by its CLI and reproducible Markdown/LaTeX reports. A GUI adds frontend maintenance burden without improving verification accuracy.
4. **DO NOT attempt clean-room synthesis of novel deep learning architectures:**
   - Synthesizing 2,000 lines of PyTorch from mathematical prose without bugs is currently beyond frontier LLM capabilities. Focus on repository adaptation and verification.
5. **DO NOT implement a custom distributed compute cluster manager:**
   - Use standard local Docker. Do not build Kubernetes operators or Slurm integrations in the MVP.

---

## 20. Recommended Next Step

Following your review of this architecture plan, the recommended immediate first task is:

> **Execute Task 1.1:** Initialize the `paper-replicator` repository with Poetry, install core dependencies (`pydantic`, `typer`, `rich`, `pymupdf4llm`, `docker`, `litellm`), and implement the foundational Pydantic schemas in `paperrep/schemas/` along with unit tests.
