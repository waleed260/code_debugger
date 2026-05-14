# Code Debugger — Autonomous Multi-Language AI Debugging Platform

**Version:** 2.0.0  
**Author:** waleed260  
**Python:** 3.12+  
**License:** MIT  
**Roadmap:** [PRD.md](PRD.md) — full product requirements and future architecture

A production-grade autonomous AI debugging platform built on the OpenAI Agents SDK. Features **10 specialized debug agents**, an **execution sandbox** (multi-language), **autonomous repair loop**, **AST/CFG code intelligence**, **debugging RAG system**, and **5 infrastructure management agents**. Deployable as a FastAPI web app with websocket streaming or used via CLI.

---

## Table of Contents

- [V2 Architecture](#v2-architecture)
- [10 Specialized Debug Agents](#10-specialized-debug-agents)
- [V1 Agents (Legacy)](#v1-agents-legacy)
- [Infrastructure Agents (5)](#infrastructure-agents-5)
- [Autonomous Repair Loop](#autonomous-repair-loop)
- [Execution Sandbox](#execution-sandbox)
- [Code Intelligence Layer](#code-intelligence-layer)
- [Debugging RAG System](#debugging-rag-system)
- [Patch Engine](#patch-engine)
- [Test Generator](#test-generator)
- [Observability Stack](#observability-stack)
- [FastAPI Web Server (V2)](#fastapi-web-server-v2)
- [Fast Local Debugger](#fast-local-debugger)
- [Function Tools](#function-tools)
- [CLI Interface](#cli-interface)
- [Web API (V1 Flask)](#web-api-v1-flask)
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

## V2 Architecture

```
                ┌──────────────────────┐
                │ FastAPI / CLI / WebUI │
                └──────────┬───────────┘
                           │
                ┌──────────▼───────────┐
                │ OrchestratorV2        │ ← AI-first primary pipeline
                │ DebuggingOrchestrator │
                └──────────┬───────────┘
                           │
        ┌──────────────────────────────────┐
        │  Stage 1: Fast Enrichment        │
        │  - Error type extraction         │
        │  - RAG context retrieval         │
        │  - Pattern detection             │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │  Stage 2: Multi-Agent RCA         │
        │  ┌───────────────────────────┐   │
        │  │ StackTraceAgent           │   │ ← Parse traceback
        │  │ DependencyAgent           │   │ ← Check imports/versions
        │  │ RuntimeAgent              │   │ ← Analyze runtime state
        │  │ DataFlowAgent             │   │ ← Trace variable corruption
        │  │ FixGenerationAgent        │   │ ← Generate candidate fix
        │  │ ValidationAgent           │   │ ← Run tests
        │  │ RegressionAgent           │   │ ← Detect side effects
        │  │ SecurityImpactAgent       │   │ ← Security audit
        │  │ PerformanceImpactAgent    │   │ ← Performance check
        │  │ RefactorAgent             │   │ ← Code quality
        │  └───────────────────────────┘   │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │  Stage 3: Execution Validation   │
        │  - Docker sandbox (if available) │
        │  - Multi-language runtime        │
        │  - stdout/stderr capture         │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │  Stage 4: Autonomous Repair Loop │
        │  ┌───────────────────────────┐   │
        │  │ Fix → Test → Refine × N  │   │ ← Iterative repair
        │  │ Confidence scoring       │   │
        │  │ Rollback support         │   │
        │  └───────────────────────────┘   │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │  Output                          │
        │  - Root cause analysis           │
        │  - Diff/patch                    │
        │  - Validation report             │
        │  - Security assessment           │
        │  - Regression check              │
        │  - Confidence score              │
        └──────────────────────────────────┘
```

### Key Architecture Decisions

- **AI-first pipeline**: `DebuggingOrchestratorV2` is the primary path. The fast local debugger is only a fallback when the API is unreachable.
- **Tiered execution**: Stage 1 (pattern detection) → Stage 2 (multi-agent RCA) → Stage 3 (sandbox validation) → Stage 4 (autonomous repair loop).
- **10 specialized agents**: Replaced 3 generic agents (DebugSleuth, SolutionArchitect, ReliabilityEngineer) with targeted agents for traceback parsing, dependency analysis, runtime state, data flow, fix generation, validation, regression, security, performance, and refactoring.
- **OpenAI Agents SDK** handles agent definitions, tool registration, and conversation loops.
- **OpenRouter** serves as the LLM backend (supports Llama 3.3 70B, Gemini Flash, Qwen, GPT-3.5, and any OpenAI-compatible model).
- **FastAPI** is the V2 web entry point with async-native endpoints and websocket streaming.
- **SQLite** persists all sessions, interactions, traces, and bug reports.

---

## 10 Specialized Debug Agents

### 1. StackTraceAgent — Traceback Parsing

| Property | Detail |
|---|---|
| **Role** | Precisely parse tracebacks and identify error type, location, call chain |
| **Max Tokens** | 400 |
| **Tool** | `extract_traceback_info(error_trace)` — extracts error type, message, failing file/line, full call chain |

**Capabilities:**
- Parse error type, message, and exact location from any traceback format
- Identify the full call chain leading to the failure
- Extract relevant code context around the failing line
- Classify errors as Runtime / Logic / System / Resource

### 2. DependencyAgent — Package & Version Conflict Detection

| Property | Detail |
|---|---|
| **Role** | Detect missing packages, version conflicts, circular imports |
| **Max Tokens** | 500 |
| **Tools** | `check_import(module_name)`, `check_package_version(package_name)`, `find_import_chains(file_path)` |

**Capabilities:**
- Detect missing or incompatible packages
- Identify version conflicts
- Analyze import chains for circular dependencies
- Check for deprecated or insecure packages

### 3. RuntimeAgent — Runtime State Analysis

| Property | Detail |
|---|---|
| **Role** | Analyze runtime state at failure point |
| **Max Tokens** | 400 |
| **Tools** | `analyze_error_pattern(error_trace)`, `check_runtime_environment()` |

**Capabilities:**
- Identify None propagation and null reference chains
- Detect memory/resource exhaustion patterns
- Identify threading/concurrency issues
- Classify as NullPropagation / MemoryPressure / Concurrency / TypeMismatch / LogicError

### 4. DataFlowAgent — Variable Corruption Tracing

| Property | Detail |
|---|---|
| **Role** | Trace where problematic values originate in data flow |
| **Max Tokens** | 500 |
| **Tools** | `trace_variable_origin(file_path, var_name, line_number)`, `analyze_function_returns(file_path, function_name)` |

**Capabilities:**
- Trace variable values through function calls using AST analysis
- Identify where None/null values enter the data flow
- Detect type mutations across assignment chains
- Find uninitialized variables or stale values

### 5. FixGenerationAgent — Candidate Fix Generation

| Property | Detail |
|---|---|
| **Role** | Generate targeted code fixes with multiple approaches |
| **Max Tokens** | 800 |
| **Tool** | `generate_safe_wrapper(error_type, code_context)` — returns safe wrapper for 10+ error types |

**Capabilities:**
- Generate minimal, correct fixes for identified bugs
- Provide multiple approaches (Quick / Robust / Ideal)
- Include test-driven validation for each fix
- Output structured diffs for automatic application

### 6. ValidationAgent — Real Test-Based Validation

| Property | Detail |
|---|---|
| **Role** | Verify fixes by running tests and static analysis |
| **Max Tokens** | 400 |
| **Tools** | `validate_fix_against_original(code_before, code_after, error_trace)`, `check_code_quality(code)` |

**Capabilities:**
- Verify the fix resolves the original error
- Run unit tests to validate correctness
- Check edge cases and boundary conditions
- Assess test coverage and quality

### 7. RegressionAgent — Side Effect Detection

| Property | Detail |
|---|---|
| **Role** | Detect side effects and regressions introduced by fixes |
| **Max Tokens** | 400 |
| **Tools** | `analyze_signature_changes(code_before, code_after)`, `detect_risky_patterns(code)` |

**Capabilities:**
- Identify if a fix introduces new failure modes
- Check if downstream callers are affected by signature changes
- Detect performance regressions from fix patterns
- Flag risky fix patterns (bare except, global mutation, dynamic execution)

### 8. SecurityImpactAgent — Vulnerability Assessment

| Property | Detail |
|---|---|
| **Role** | Check if the bug or fix introduces security vulnerabilities |
| **Max Tokens** | 400 |
| **Tools** | `scan_security_issues(code)`, `check_security_score(issues_json)` |

**Capabilities:**
- Scan for SQL injection, command injection, XSS, insecure deserialization
- Detect hardcoded secrets and credentials
- Identify path traversal and unsafe file operations
- Calculate security score (0-100) with CVSS-style risk assessment

### 9. PerformanceImpactAgent — Performance Analysis

| Property | Detail |
|---|---|
| **Role** | Analyze performance implications of bugs and fixes |
| **Max Tokens** | 400 |
| **Tools** | `analyze_performance_patterns(code)`, `estimate_fix_performance_impact(original_code, fixed_code)` |

**Capabilities:**
- Detect performance anti-patterns (nested loops, N+1 queries, string concatenation)
- Assess fix performance impact (improves / neutral / degrades)
- Estimate performance gain/loss percentages

### 10. RefactorAgent — Code Quality Improvement

| Property | Detail |
|---|---|
| **Role** | Improve code maintainability during and after fixes |
| **Max Tokens** | 400 |
| **Tools** | `detect_code_smells(code)`, `suggest_type_hints(code)` |

**Capabilities:**
- Detect code smells (long functions, excessive nesting, missing docstrings)
- Suggest type hints and documentation improvements
- Apply DRY, SOLID, and clean code principles
- Score code quality and recommend cleanup

### Database Debugging Agents

5 additional agents for database-related debugging:

| Agent | Purpose |
|---|---|
| `SQLQueryOptimizer` | Analyze slow queries, detect missing indexes, N+1 problems |
| `MigrationValidator` | Check schema migration safety, detect breaking changes |
| `SchemaAnalyzer` | Find missing PKs, FK constraints, data type issues |
| `TransactionAgent` | Detect deadlocks, race conditions, isolation level issues |
| `ORMMapperAgent` | Detect N+1 patterns, lazy loading issues, ORM/schema mismatches |

---

## Autonomous Repair Loop

The orchestrator runs an iterative fix → test → refine cycle for autonomous repair:

```
Iteration 1: Generate fix → Validate → Check confidence
Iteration 2: Refine based on previous results → Re-validate
...
Iteration N: Stop when confidence threshold met or max iterations reached
```

**Configuration:** `DebugSessionConfig.max_repair_iterations` (default: 5), `confidence_threshold` (default: 0.6)

**Confidence scoring** factors:
- Error keywords addressed in the fix
- Defensive patterns used (try/except, type checks, guards)
- Test generation and execution results
- Security and regression analysis results

---

## Execution Sandbox

Docker-based multi-language runtime execution for safe code validation.

**Supported languages:**

| Language | Docker Image | Timeout | Memory |
|---|---|---|---|
| Python | `python:3.12-slim` | 30s | 512MB |
| JavaScript | `node:20-slim` | 30s | 512MB |
| TypeScript | `node:20-slim` | 30s | 512MB |
| Go | `golang:1.22` | 45s | 512MB |
| Rust | `rust:1.78-slim` | 60s | 1GB |
| Java | `openjdk:21-slim` | 45s | 1GB |
| C++ | `gcc:14-bookworm` | 45s | 512MB |
| Ruby | `ruby:3.3-slim` | 30s | 512MB |
| PHP | `php:8.3-cli` | 30s | 512MB |
| C# | `dotnet/sdk:8.0` | 60s | 1GB |
| SQL | `postgres:16-alpine` | 30s | 512MB |

**Sandbox features:**
- Language auto-detection from code and filename
- Docker container isolation with resource limits
- Network disabled by default (opt-in)
- File write support for multi-file projects
- Test execution support (pytest, jest, go test, cargo test, etc.)
- Falls back to local subprocess when Docker is unavailable

**Key class:** `ExecutionSandbox(use_docker=True)`
- `execute(code, language, files, timeout, test_command)` → `ExecutionResult`
- `execute_test(code, test_code, language)` → `ExecutionResult`

---

## Code Intelligence Layer

AST-based static analysis for deep code understanding beyond regex/LLM reasoning.

**Class:** `ASTAnalyzer(repo_path)`

**Capabilities:**
- **Function analysis**: parameters, decorators, docstrings, return types, called functions
- **Class analysis**: bases, methods, inheritance hierarchy
- **Import analysis**: module names, aliases, import types
- **Variable tracking**: definitions, assignments, type hints
- **Call graph construction**: caller/callee relationships across files
- **Data flow edges**: variable definition → usage chains
- **Code quality scoring**: cyclomatic complexity, code smell detection
- **Project-wide dependency graph**: module-level import relationships

**Output structure:**
```python
{
  "file": "path/to/file.py",
  "loc": 150,
  "complexity_score": 42,
  "functions": [...],
  "classes": [...],
  "imports": [...],
  "variables": [...],
  "call_graph": [...],
  "data_flow": [...],
  "issues": [...],
}
```

---

## Debugging RAG System

Retrieval-Augmented Debugging — retrieves relevant solutions from external sources to enrich debugging prompts.

**Class:** `DebugRAG(cache_path)`

**Sources:**
- **Common patterns**: hardcoded fixes for IndexError, KeyError, TypeError, etc.
- **StackOverflow patterns**: error-specific solution templates
- **GitHub issues**: search queries for similar bugs
- **Documentation**: links to Python docs, MDN, etc.
- **CVE database**: known vulnerabilities in dependencies
- **Changelogs**: breaking changes between versions
- **Known patterns**: user-curated fix database (learns over time)

**Methods:**
- `retrieve(error_trace, language, code_context, top_k)` → `List[DebugSource]`
- `enrich_prompt(error_trace, language, code_context)` → formatted context
- `add_known_pattern(error_type, solution, source_type)` → persistent learning
- `retrieve_github_issues(query)` / `retrieve_docs(module, error)` / `retrieve_cve(package)` / `retrieve_changelog(package, from_v, to_v)`

---

## Patch Engine

Structured diff generation, application, and rollback with git integration.

**Class:** `PatchEngine(repo_path)`

**Key classes:**
- `FilePatch(file_path, original_content, patched_content)` — represents a single file diff
- `PatchSet(patches, summary, confidence_score)` — group of related patches
- `PatchResult(success, applied_patches, failed_patches)` — result of applying patches

**Methods:**
- `create_patch(file_path, original, fixed)` → `FilePatch` with unified diff
- `apply_patch(patch, dry_run)` → apply changes to filesystem
- `apply_patch_set(patch_set, dry_run)` → apply batch of patches
- `rollback(patch)` / `rollback_all(patches)` → revert changes
- `create_diff_preview(patches)` → human-readable diff output
- `git_commit(patches, message)` → commit to git
- `git_create_branch_and_push(branch, patches, message)` → push to remote
- `diff_text(original, fixed, filename)` → static unified diff utility

---

## Test Generator

Automatically generates unit tests, integration tests, edge cases, and fuzz tests.

**Class:** `TestGenerator()`

**Methods:**
- `generate_tests(source_code, file_path)` → `TestSuite` with unit tests for all functions and classes
- `generate_regression_tests(bug_description, fix_code, original_code)` → regression test suite
- `generate_edge_case_tests(func_name, args)` → edge case tests (None, empty, type mismatch)
- `generate_fuzz_tests(func_name, args)` → randomized fuzz testing
- `generate_security_tests(func_name, args)` → injection/malicious input tests
- `render_suite(suite)` → formatted pytest test file output

---

## Observability Stack

Tracks token usage, latency, success rates, agent metrics, and error distribution.

**Class:** `ObservabilityTracker(db_path)`

**Metrics collected:**
- Per-agent duration, token count, success/failure, confidence score, retry count
- Per-session total duration, total tokens, agents used, final status
- Error type distribution across sessions

**Reports:**
- `get_report()` → `ObservabilityReport` with:
  - Total sessions, success rate, average duration
  - Per-agent stats (runs, avg duration, success rate, avg confidence, avg tokens)
  - Error type distribution
  - Recent sessions
  - Top 10 most frequent errors
- `get_timeline(session_id)` → chronological agent execution timeline

---

## FastAPI Web Server (V2)

Migrated from Flask for native async, websocket streaming, auto OpenAPI docs, and Pydantic validation.

**Run:**
```bash
uv run uvicorn api_v2.server:app --host 0.0.0.0 --port 8000 --reload
```

**Endpoints:**

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | V2 Web UI |
| `/health` | GET | Health check with timestamp |
| `/debug` | POST | Run full V2 debugging pipeline |
| `/metrics` | GET | Observability report |
| `/agents` | GET | List all agents with roles |
| `/ws/debug` | WebSocket | Streaming debug with real-time agent progress |

**WebSocket streaming** sends events:
- `{"type": "status", "stage": "...", "message": "..."}` — progress updates
- `{"type": "agents", "agents": [...]}` — list of running agents
- `{"type": "result", ...}` — final debugging result
- `{"type": "error", "message": "..."}` — error messages

---

## Fast Local Debugger

A built-in offline fallback that requires **no API calls**. It is only used when the V2 AI pipeline is unavailable (API key missing, network error, etc.). It contains a hardcoded dictionary of 20+ common Python error types. When an error trace is submitted, it extracts the error type using regex and returns a pre-written explanation, safe wrapper function, and test snippet.

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
│   ├── index.py                  # Flask API server (V1, legacy)
│   └── html_content.py           # Inline HTML/CSS/JS for web UIs
├── api_v2/
│   └── server.py                 # FastAPI server (V2, async + websockets)
├── public/
│   ├── index.html                # Static debugger web UI
│   └── infrastructure.html       # Static infrastructure management UI
├── src/
│   └── code_debugger/
│       ├── __init__.py           # Package init, public API exports
│       ├── __main__.py           # `python -m code_debugger` entry
│       ├── v1_agents.py          # V1 agents (legacy, backward compat)
│       ├── tools.py              # All function tools
│       ├── infra_agents.py       # 5 infrastructure agents + their tools
│       ├── infra_orchestrator.py # Orchestrator for infrastructure agents
│       ├── main.py               # CLI entry points and sample sessions
│       ├── session_manager.py    # SQLite session management
│       ├── database.py           # Simpler SQLite module (legacy/unused)
│       ├── orchestrator.py       # Legacy re-export for backward compat
│       ├── orchestrator_v2.py    # V2 orchestrator (AI-first, repair loop)
│       ├── sandbox.py            # Execution sandbox (Docker, multi-language)
│       ├── code_intelligence.py  # AST/CFG analysis layer
│       ├── patch_engine.py       # Diff/patch generation and application
│       ├── rag.py                # Retrieval-Augmented Debugging system
│       ├── test_generator.py     # Automatic test generation
│       ├── observability.py      # Metrics and observability tracking
│       └── agents/               # 10 specialized debug agents
│           ├── __init__.py
│           ├── stack_trace_agent.py
│           ├── dependency_agent.py
│           ├── runtime_agent.py
│           ├── data_flow_agent.py
│           ├── fix_generation_agent.py
│           ├── validation_agent.py
│           ├── regression_agent.py
│           ├── security_impact_agent.py
│           ├── performance_impact_agent.py
│           ├── refactor_agent.py
│           └── db_debug_agents.py
├── code_debugger_cli.py          # CLI interface script
├── example_v2.py                 # V2 pipeline example
├── pyproject.toml                # Project metadata and dependencies
├── requirements.txt              # Pip dependencies
├── PRD.md                        # Product Requirements Document
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
├── debug_sessions_v2.db          # V2 SQLite database (runtime, gitignored)
├── rag_cache.db                  # RAG cache database (runtime, gitignored)
├── observability.db              # Observability database (runtime, gitignored)
├── test_v2_pipeline.py           # V2 pipeline tests (44 tests)
├── test_agents.py                # V1 debug agent tests
├── test_fix.py                   # Basic init test
├── test_infrastructure.py        # Infrastructure agent tests
├── test_openai_agents.py         # SDK integration tests
├── test_openrouter.py            # OpenRouter API test
└── .playwright-mcp/              # Auto-generated browser test artifacts
```

---

---

## Roadmap

All Phase 1 and Phase 2 items from **[PRD.md](PRD.md)** are now **implemented**:

- ✅ AI pipeline as primary path (V2 orchestrator)
- ✅ Execution sandbox (Docker-based, 11 languages)
- ✅ Autonomous retry loop (iterative fix → test → refine)
- ✅ Real test validation (test generation + execution)
- ✅ Diff/patch system (unified diff + git integration)
- ✅ 10 specialized agents (replaced 3 generic agents)
- ✅ AST/CFG analysis (code intelligence layer)
- ✅ Debugging RAG system (semantic retrieval)
- ✅ Observability stack (metrics, tracking, reporting)
- ✅ FastAPI + websocket streaming (migrated from Flask)

**Next priorities:**
- Repository knowledge graph (Neo4j + graph embeddings)
- IDE integrations (VSCode extension, JetBrains plugin)
- PR automation (auto-fix GitHub PRs)
- Self-learning memory system

---

## Known Limitations & Weaknesses

### Known Issues

1. **API key in .env is NOT gitignored** — The `.env` file containing `OPENROUTER_API_KEY` is not listed in `.gitignore`, creating a security risk of committing secrets.

2. **No authentication/authorization** — The Flask/FastAPI APIs have no auth middleware, making them publicly accessible if deployed.

3. **Ephemeral storage on Vercel** — The `/tmp/debug_sessions.db` path is serverless-ephemeral; data is lost between cold starts.

4. **Two database modules** — `database.py` (simpler, 3 tables) and `session_manager.py` (full-featured) coexist. Only `session_manager.py` is used; `database.py` is dead code.

5. **Security tools are limited** — Port scanner checks only 15 ports; SSL checker has no certificate chain validation; log analysis is simple regex matching.

6. **Cost Manager doesn't connect to cloud billing APIs** — It analyzes local resource usage but has no integration with AWS/Azure/GCP billing APIs.

7. **No type hints for complex dict returns** — Some tool return types use `Dict`/`Any` without specific type definitions.

8. **Commented-out imports** — Several files contain commented-out imports (e.g., `# from datetime import datetime` in `session_manager.py` and `main.py`).

9. **Model string disconnect** — `DebuggingOrchestrator.__init__` defaults model to `"gpt-4o"` as a string, but the actual agents use `OPENROUTER_MODEL` from environment variables.

10. **Fast debugger dictionary incomplete** — Covers 20+ error types but misses compound/custom exceptions like `json.JSONDecodeError`.

11. **`run_async()` helper is fragile** — The helper in `v1_agents.py` has complex event loop handling that could fail in threaded environments.

12. **No caching for LLM responses** — Every agent run makes fresh API calls; no caching for repeated error patterns.
