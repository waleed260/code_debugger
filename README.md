# Code Debugger — Multi-Agent AI Debugging & Infrastructure Management System

**Version:** 0.2.0  
**Author:** waleed260  
**Python:** 3.12+  
**License:** MIT  
**Roadmap:** [PRD.md](PRD.md) — full product requirements and future architecture

A multi-agent AI system built on the OpenAI Agents SDK that combines three debug agents (root cause analysis, fix generation, validation) with five infrastructure management agents (health monitoring, security auditing, performance optimization, cost management, incident response). Deployable as a Flask web app on Vercel or used via CLI.

---

## Table of Contents

- [Architecture](#architecture)
- [Debug Agents (3)](#debug-agents-3)
- [Infrastructure Agents (5)](#infrastructure-agents-5)
- [Fast Local Debugger](#fast-local-debugger)
- [Function Tools](#function-tools)
- [CLI Interface](#cli-interface)
- [Web API (Flask)](#web-api-flask)
- [Web UI](#web-ui)
- [Session Persistence](#session-persistence)
- [Configuration](#configuration)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment (Vercel)](#deployment-vercel)
- [MCP Integration](#mcp-integration)
- [Project Structure](#project-structure)
- [Known Limitations & Weaknesses](#known-limitations--weaknesses)

---

## Architecture

```
User Input (CLI / Web UI / API)
        │
        ▼
┌──────────────────────────────────────┐
│  Flask API (api/index.py)            │
│  OR CLI (code_debugger_cli.py)       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  SyncDebuggingOrchestrator /          │
│  DebuggingOrchestrator (async)        │
│  OR InfrastructureOrchestrator        │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  run_full_debugging_cycle()           │
│  ┌─────────────────────────────┐     │
│  │ Fast Local Debugger (sync)  │     │ ← No API calls, instant
│  │ 20+ Python errors covered   │     │
│  └─────────────────────────────┘     │
│  OR                                  │
│  ┌─────────────────────────────┐     │
│  │ 1. DebugSleuth (RCA)        │     │
│  │ 2. SolutionArchitect (Fix)  │     │ ← OpenAI Agents SDK + OpenRouter
│  │ 3. ReliabilityEngineer (QA) │     │   (async pipeline)
│  └─────────────────────────────┘     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  SessionManager (SQLite)             │
│  Tables: sessions, agent_interactions │
│  conversation_turns, agent_traces,   │
│  bug_reports                         │
└──────────────────────────────────────┘
```

### Key Architecture Decisions

- **Two orchestrator paths**: `SyncDebuggingOrchestrator` uses the fast local debugger (no API calls). `DebuggingOrchestrator` (async) runs the full 3-agent pipeline via OpenRouter.
- **OpenAI Agents SDK** handles agent definitions, tool registration, and conversation loops.
- **OpenRouter** serves as the LLM backend (supports Llama 3.3 70B, Gemini Flash, Qwen, GPT-3.5, and any OpenAI-compatible model).
- **Flask API** is the web entry point, deployed serverless on Vercel.
- **SQLite** persists all sessions, interactions, traces, and bug reports.

---

## Debug Agents (3)

### 1. Debug Sleuth — Root Cause Analysis

| Property | Detail |
|---|---|
| **Role** | Forensic stack trace analysis |
| **Model** | OpenRouter configurable (default: Llama 3.3 70B) |
| **Max Tokens** | 500 |
| **Tools** | `list_directory_tool`, `read_code_file_tool`, `search_codebase_tool`, `run_shell_command_tool`, `analyze_python_code_tool` |

**Capabilities:**
- Parses error type, message, and location from tracebacks
- Reads code context around failing lines with `>>>` marker
- Traces data flow to identify where problematic values originate
- Supports multiple hypotheses with confidence levels (High/Medium/Low)
- Outputs structured analysis with error type, location, root cause, and confidence

### 2. Solution Architect — Fix Generation

| Property | Detail |
|---|---|
| **Role** | Software architect creating fixes |
| **Model** | OpenRouter configurable |
| **Max Tokens** | 600 |
| **Tools** | Same 5 tools as Debug Sleuth |

**Capabilities:**
- Understands root cause and generates a single recommended fix
- Applies SOLID principles and defensive programming
- Includes a pytest snippet for verification
- Considers backward compatibility and security-first design
- Output includes corrected code, explanation, and test

### 3. Reliability Engineer — Validation & Documentation

| Property | Detail |
|---|---|
| **Role** | QA engineer validating fixes |
| **Model** | OpenRouter configurable |
| **Max Tokens** | 300 |
| **Tools** | Same 5 tools as Debug Sleuth |

**Capabilities:**
- Checks if the fix actually solves the root cause
- Identifies security issues and edge cases
- Assesses test adequacy
- Code smell detection (10+ patterns)
- 8+ security checks
- Quality scoring (0-100)
- Outputs PASS/FAIL status with reasoning

### Handoff Functions

Three handoff functions exist (defined but not wired into the Agents SDK handoff mechanism):
- `handoff_to_fixer(bug_analysis)` — Debug Sleuth → Solution Architect
- `handoff_to_validator(fix_proposal)` — Solution Architect → Reliability Engineer
- `handoff_back_to_architect(critique)` — Reliability Engineer → Solution Architect (for revision)

---

## Fast Local Debugger

A built-in offline fallback that requires **no API calls**. It contains a hardcoded dictionary of 20+ common Python error types. When an error trace is submitted, it extracts the error type using regex and returns a pre-written explanation, safe wrapper function, and test snippet.

**Covered Error Types (20+):**

| Error | Safe Function |
|---|---|
| `IndexError` | `get_item_safe(items, index)` |
| `KeyError` | `get_value_safe(data, key, default)` |
| `TypeError` | `add_safe(a, b)` |
| `ValueError` | `convert_safe(value, to_type)` |
| `AttributeError` | `safe_getattr(obj, attr, default)` |
| `ZeroDivisionError` | `divide_safe(a, b)` |
| `FileNotFoundError` | `read_file_safe(path)` |
| `ImportError` / `ModuleNotFoundError` | `safe_import(module_name, fallback)` |
| `NameError` | `safe_get_variable(name, default)` |
| `UnboundLocalError` | `safe_increment(counter)` |
| `RuntimeError` | `run_safe(operation, *args)` |
| `RecursionError` | `safe_recursive(func, max_depth)` |
| `StopIteration` | `next_safe(iterator, default)` |
| `AssertionError` | `assert_safe(condition, message)` |
| `PermissionError` | `read_file_permission_safe(path)` |
| `ConnectionError` / `TimeoutError` | `connect_safe(host, port, timeout)` |
| `OSError` | `os_operation_safe(operation, *args)` |
| `MemoryError` | `process_in_chunks(data, chunk_size)` |
| `OverflowError` | `power_safe(base, exp)` |
| `LookupError` | `lookup_safe(collection, key, default)` |
| `SystemError` / `FloatingPointError` | `safe_float_calc(operation, *args)` |

For unknown error types, a generic handler is generated with a try/except wrapper.

---

## Infrastructure Agents (5)

### 1. Infrastructure Analyzer — System Health & Architecture

| Tool | Purpose |
|---|---|
| `check_system_resources` | CPU, memory, disk, network stats via psutil |
| `check_running_processes` | Top resource-consuming processes |
| `check_docker_containers` | Docker container status (via subprocess) |
| `check_network_connections` | ESTABLISHED network connections |

**Output:** Health status, resource utilization, critical issues, capacity planning recommendations.

### 2. Security Auditor — Security & Compliance

| Tool | Purpose |
|---|---|
| `scan_open_ports` | Port scan on 15 common ports (21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 5432, 6379, 8080, 8443, 27017) |
| `check_ssl_certificate` | SSL certificate details (issuer, subject, validity) |
| `analyze_logs` | Regex-based log pattern matching |
| `check_network_connections` | Detect suspicious connections |

**Output:** Security score (0-100), critical vulnerabilities, warnings, compliance status (PCI DSS, GDPR, HIPAA), risk assessment.

### 3. Performance Optimizer — Performance Tuning

| Tool | Purpose |
|---|---|
| `check_system_resources` | Monitor resource usage |
| `check_running_processes` | Identify resource hogs |
| `check_docker_containers` | Optimize containers |
| `check_network_connections` | Analyze network performance |

**Output:** Bottlenecks (CPU, Memory, Disk I/O, Network), quick wins with expected gain percentages, medium-term improvements, long-term architecture changes.

### 4. Cost Manager — Cost Optimization

| Tool | Purpose |
|---|---|
| `check_system_resources` | Analyze resource usage |
| `check_running_processes` | Find resource waste |
| `check_docker_containers` | Optimize container costs |

**Output:** Cost breakdown (Compute, Storage, Network, Other), waste identification with dollar amounts, savings recommendations with ROI analysis, payback period.

### 5. Incident Responder — Incident Management

| Tool | Purpose |
|---|---|
| `check_system_resources` | Monitor system health |
| `check_running_processes` | Identify problematic processes |
| `check_docker_containers` | Check container health |
| `analyze_logs` | Review incident logs |
| `check_network_connections` | Detect network issues |

**Output:** Severity assessment (P0-P4), incident timeline, root cause analysis, immediate mitigation steps, prevention measures, postmortem items.

---

## Function Tools

All tools are registered as `@function_tool` decorated functions for the OpenAI Agents SDK.

### Debug Tools (shared by all 3 debug agents)

| Tool | Description |
|---|---|
| `list_directory_tool(path, max_depth)` | List directory structure recursively (configurable depth, default 3) |
| `read_code_file_tool(file_path, start_line, end_line)` | Read file content with optional line range; shows `>>>` marker on failing line |
| `search_codebase_tool(pattern, file_extensions)` | Search files by content or filename pattern (default: `.py`) |
| `run_shell_command_tool(command, timeout)` | Execute shell commands safely (default timeout: 30s) |
| `analyze_python_code_tool(file_path)` | AST-based Python analysis — extracts functions, classes, imports, variables |

### Infrastructure Tools (shared by infrastructure agents)

| Tool | Description |
|---|---|
| `check_system_resources(resource_type)` | CPU, memory, disk, network (uses psutil) |
| `check_running_processes(limit)` | Top resource-consuming processes (sorted by CPU) |
| `check_docker_containers()` | Docker container status and health |
| `check_network_connections(limit)` | ESTABLISHED TCP connections |
| `scan_open_ports(host)` | TCP connect scan on 15 common ports |
| `check_ssl_certificate(domain)` | SSL certificate details |
| `analyze_logs(log_file, pattern, limit)` | Regex-based log pattern matching |

---

## CLI Interface

File: `code_debugger_cli.py`

| Flag | Description |
|---|---|
| `--error-file PATH` | Read error trace from file |
| `--failing-file PATH` | Specify failing file path |
| `--failing-line N` | Specify failing line number |
| `--error-message STR` | Direct error trace string |
| `--run-sample` | Run a sample IndexError session |
| `--list-sessions` | List all stored sessions |
| `--session-report ID` | Get report for a specific session ID |
| `--db-path PATH` | Custom database path (default: `debug_sessions.db`) |

---

## Web API (Flask)

Base URL: `http://localhost:5000` (local) or `https://your-app.vercel.app`

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Debugger web UI |
| `/infrastructure` | GET | Infrastructure management web UI |
| `/api` | GET | API documentation (JSON) |
| `/health` | GET | Health check (`{"status": "healthy"}`) |
| `/debug` | POST | Debug an error trace |
| `/api/debug` | POST | Debug an error trace (alias) |
| `/api/agents` | GET | Get agent metadata and capabilities |
| `/api/infrastructure/<agent>` | POST | Run a specific infra agent |
| `/api/infrastructure/full-audit` | POST | Run all 5 infrastructure agents |
| `/api/infrastructure/incident` | POST | Respond to an incident description |

### Debug Endpoint (`POST /debug`)

**Request:**
```json
{
  "error_trace": "Traceback (most recent call last):\n  File \"example.py\", line 15, in calculate_sum\n    result = numbers[index] + numbers[index + 1]\nIndexError: list index out of range",
  "failing_file": "example.py",
  "failing_line": 15,
  "codebase_path": "."
}
```

**Response:**
```json
{
  "success": true,
  "validation_passed": true,
  "final_report": "## Error Explanation\n...",
  "agents_used": ["FastDebugAgent"],
  "root_cause_analysis": "...",
  "solution_architecture": "...",
  "reliability_validation": "..."
}
```

### Infrastructure Endpoints

- `POST /api/infrastructure/<agent>` — agent can be: `infrastructure`, `security`, `performance`, `cost`, `incident`
- `POST /api/infrastructure/full-audit` — runs all 5 agents sequentially
- `POST /api/infrastructure/incident` — requires `{"description": "..."}`

---

## Web UI

Two dark-themed terminal-style HTML pages:

### Debugger UI (`/`)
- Error trace textarea with Ctrl+Enter to submit
- Optional failing file/line inputs
- Animated loading overlay showing agent progression (Debug Sleuth → Solution Architect → Reliability Engineer)
- Results display with PASS/FAIL badge
- Agent info cards with feature lists
- Escape to cancel loading

### Infrastructure UI (`/infrastructure`)
- Tab-based layout (Dashboard, Full Audit, Incident)
- Dashboard: 5 agent cards with individual run buttons
- Full Audit: runs all 5 agents sequentially
- Incident: textarea for incident description with response button
- Scrollable results with agent-labeled sections

Both UIs use a shared design system: JetBrains Mono font, dark background (`#06080f`), green accent (`#22C55E`), responsive layout, accessible focus states, and reduced-motion support.

---

## Session Persistence

SQLite database managed by `SessionManager` in `session_manager.py`.

### Tables

| Table | Purpose |
|---|---|
| `sessions` | Session metadata, status, error context, final report, validation pass/fail |
| `agent_interactions` | Per-agent run records with input/output/tool_calls/duration |
| `conversation_turns` | Full conversation history (role, content, tool calls/responses) |
| `agent_traces` | OpenAI Agents SDK trace spans (parent/child hierarchy) |
| `bug_reports` | Bug descriptions, root causes, fix proposals, status tracking |

### Key Methods

| Method | Description |
|---|---|
| `create_session(session_id, error_context, metadata)` | Create new session |
| `get_session(session_id)` | Retrieve session by ID |
| `update_session(session_id, **kwargs)` | Update status, metadata, report |
| `add_interaction(session_id, agent_name, ...)` | Log an agent interaction |
| `add_conversation_turn(session_id, ...)` | Log a conversation turn |
| `add_agent_trace(session_id, ...)` | Log an SDK trace span |
| `add_bug_report(session_id, ...)` | Create a bug report |
| `get_session_interactions(session_id)` | Get all interactions for a session |
| `get_statistics()` | Get aggregate stats (total sessions, pass rate, agent usage) |
| `export_session(session_id)` | Export full session as JSON |
| `import_session(session_data)` | Import session from JSON |
| `delete_session(session_id)` | Hard delete session + all related data |
| `list_sessions(status, limit)` | List sessions with optional status filter |

A legacy module `database.py` exists with similar but simpler functionality (3 tables: sessions, agent_interactions, bugs) — currently unused.

---

## Configuration

### Environment Variables (`.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | — | Yes | OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | No | OpenRouter API base URL |
| `OPENROUTER_MODEL` | `meta-llama/llama-3.3-70b-instruct:free` | No | LLM model identifier |
| `DEBUG` | — | No | Enable debug logging |

The OpenRouter API key is injected into `OPENAI_API_KEY` and `OPENAI_BASE_URL` environment variables to make the OpenAI Agents SDK use OpenRouter as the backend.

### Model Settings

| Agent | max_tokens |
|---|---|
| DebugSleuth | 500 |
| SolutionArchitect | 600 |
| ReliabilityEngineer | 300 |
| Infra agents | Default (no explicit limit) |

---

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/waleed260/code_debugger.git
cd code_debugger

# Copy and configure environment
cp .env.example .env
# Edit .env with your OpenRouter API key

# Install dependencies using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

---

## Usage

### CLI — Debug an Error Trace

```bash
# Run sample IndexError session
python code_debugger_cli.py --run-sample

# Debug a specific error trace
python code_debugger_cli.py --error-message "IndexError: list index out of range" --failing-file example.py --failing-line 15

# Debug from a file
python code_debugger_cli.py --error-file error_trace.txt --failing-file app.py

# List all sessions
python code_debugger_cli.py --list-sessions

# Get session report
python code_debugger_cli.py --session-report <session-id>
```

### CLI — Package Entry Point

```bash
python -m code_debugger
# or
code-debugger
```

### Web Server (Local)

```bash
python api/index.py
# Serves on http://0.0.0.0:5000
```

### Web API — Debug via curl

```bash
curl -X POST http://localhost:5000/debug \
  -H "Content-Type: application/json" \
  -d '{
    "error_trace": "Traceback (most recent call last):\n  File \"app.py\", line 10, in <module>\n    print(x[10])\nIndexError: list index out of range",
    "failing_file": "app.py",
    "failing_line": 10
  }'
```

### Web API — Infrastructure

```bash
# Run infrastructure analyzer
curl -X POST http://localhost:5000/api/infrastructure/infrastructure

# Full infrastructure audit
curl -X POST http://localhost:5000/api/infrastructure/full-audit

# Incident response
curl -X POST http://localhost:5000/api/infrastructure/incident \
  -H "Content-Type: application/json" \
  -d '{"description": "High CPU usage on production server"}'
```

---

## Testing

```bash
# Test debug agents
python test_agents.py

# Test infrastructure agents
python test_infrastructure.py

# Test OpenAI Agents SDK integration
python test_openai_agents.py

# Test OpenRouter connection
python test_openrouter.py

# Basic initialization test
python test_fix.py
```

---

## Deployment (Vercel)

The project is configured for serverless deployment on Vercel:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy
```

Configuration (`vercel.json`):
- Runtime: Python 3.12 via `@vercel/python`
- Entry point: `api/index.py`
- All routes (`/(.*)`) map to `api/index.py`
- Database path: `/tmp/debug_sessions.db` (ephemeral on Vercel)

---

## MCP Integration

Two MCP config files exist for Claude Desktop integration:

- **`.mcp.json`** — Claude desktop MCP config (GitHub API via `@fre4x/github` + Playwright)
- **`mcp.json`** — Root-level MCP config for GitHub integration

These enable Claude to interact with the project's GitHub repository and perform browser automation during development.

---

## Project Structure

```
code_debugger/
├── api/
│   ├── index.py                  # Flask API server (main HTTP entry)
│   └── html_content.py           # Inline HTML/CSS/JS for web UIs
├── public/
│   ├── index.html                # Static debugger web UI
│   └── infrastructure.html       # Static infrastructure management UI
├── src/
│   └── code_debugger/
│       ├── __init__.py           # Package init, public API exports
│       ├── __main__.py           # `python -m code_debugger` entry
│       ├── agents.py             # 3 debug agents + fast local debugger + orchestrators
│       ├── tools.py              # All function tools (debug + infra shared)
│       ├── infra_agents.py       # 5 infrastructure agents + their tools
│       ├── infra_orchestrator.py # Orchestrator for infrastructure agents
│       ├── main.py               # CLI entry points and sample sessions
│       ├── session_manager.py    # SQLite session management
│       ├── database.py           # Simpler SQLite module (legacy/unused)
│       └── orchestrator.py       # Legacy re-export for backward compat
├── code_debugger_cli.py          # CLI interface script
├── pyproject.toml                # Project metadata and dependencies
├── requirements.txt              # Pip dependencies (mirrors pyproject.toml)
├── vercel.json                   # Vercel serverless deployment config
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── .mcp.json                     # MCP server config (Claude Desktop)
├── mcp.json                      # Root MCP config
├── .python-version               # Python 3.12
├── uv.lock                       # uv package lock file
├── .claude/
│   └── settings.local.json       # Claude permissions config
├── .vercel/                      # Vercel project metadata (auto-generated)
├── debug_sessions.db             # SQLite database (runtime, gitignored)
├── test_agents.py                # Debug agent tests
├── test_fix.py                   # Basic init test
├── test_infrastructure.py        # Infrastructure agent tests
├── test_openai_agents.py         # SDK integration tests
├── test_openrouter.py            # OpenRouter API test
└── .playwright-mcp/              # Auto-generated browser test artifacts
```

---

---

## Roadmap

For the complete vision, future architecture, and phased development plan, see **[PRD.md](PRD.md)**. Key priorities:

1. **Immediate**: Wire AI pipeline as primary path, add execution sandbox, add autonomous retry loop
2. **Mid-term**: Multi-language support, AST/CFG analysis, debugging RAG, repository graph
3. **Advanced**: Self-learning memory, distributed orchestration, auto PR generation, IDE integrations

---

## Known Limitations & Weaknesses

### Critical Issues

1. **Sync orchestrator bypasses AI pipeline** — `SyncDebuggingOrchestrator.run_full_debugging_cycle()` calls the fast local debugger instead of running the actual 3-agent AI workflow via OpenRouter. The CLI and Web API always use the sync path, so they never actually leverage the multi-agent AI pipeline.

2. **API key in .env is NOT gitignored** — The `.env` file containing `OPENROUTER_API_KEY` is not listed in `.gitignore`, creating a security risk of committing secrets.

3. **No authentication/authorization** — The Flask API has no auth middleware, making it publicly accessible if deployed.

4. **README was empty** — This file was originally empty; now populated with this comprehensive documentation.

### Pipeline & Agent Issues

5. **Handoff functions defined but unused** — `handoff_to_fixer`, `handoff_to_validator`, and `handoff_back_to_architect` exist as simple string-returning functions but are never wired into the Agents SDK's handoff mechanism.

6. **No error recovery in agent pipeline** — If an agent call fails (e.g., OpenRouter rate limit), there is no retry logic or graceful degradation.

7. **Model string disconnect** — `DebuggingOrchestrator.__init__` defaults model to `"gpt-4o"` as a string, but the actual agents use `OPENROUTER_MODEL` from environment variables.

8. **No caching** — Every agent run makes fresh API calls; no response caching for repeated error patterns.

### Database Issues

9. **Two database modules** — `database.py` (simpler, 3 tables) and `session_manager.py` (full-featured, 5+ tables) coexist. Only `session_manager.py` is used; `database.py` is dead code.

10. **Ephemeral storage on Vercel** — The `/tmp/debug_sessions.db` path is serverless-ephemeral; data is lost between cold starts.

### Testing & Coverage

11. **No end-to-end test for the AI pipeline** — Tests import agents but the sync orchestrator uses the local fallback, so the OpenRouter-based pipeline is never actually tested end-to-end.

12. **Fast debugger dictionary incomplete** — While it covers 20+ error types, many edge cases and compound errors are not handled (e.g., `json.JSONDecodeError`, custom exceptions).

### Infrastructure Agents

13. **Same model for all 5 infra agents** — No differentiation in model sizing for different complexity tasks.

14. **Security tools are limited** — Port scanner checks only 15 ports; SSL checker has no certificate chain validation; log analysis is simple regex matching.

15. **Cost Manager doesn't connect to cloud billing APIs** — It analyzes local resource usage but has no integration with AWS/Azure/GCP billing APIs.

### Code Quality

16. **`run_async()` helper is fragile** — The helper in `agents.py` has complex event loop handling logic that could fail in edge cases, especially in threaded environments.

17. **Commented-out imports** — Several files contain commented-out imports (e.g., `# from datetime import datetime` in `session_manager.py` and `main.py`).

18. **No type hints for complex dict returns** — Most tool return types use `Dict`/`Any` without specific type definitions.
