# Code Debugger - Multi-Agent Debugging System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)


A sophisticated AI-powered debugging assistant that uses **three specialized agents** to analyze errors, generate fixes, and validate solutions.

---

## 🎯 Overview

Code Debugger automates the debugging process through a pipeline of three specialized AI agents:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Debug Sleuth   │ ──→ │  Solution       │ ──→ │  Reliability    │
│  (Analysis)     │     │  Architect      │     │  Engineer       │
│                 │     │  (Fix)          │     │  (Validation)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

Each agent has specific responsibilities and access to powerful tools for code analysis, file operations, and shell command execution.

---

## ✨ Features

### Three Specialized Agents

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Debug Sleuth** | Root Cause Analysis | Stack trace analysis, code context examination, variable state deduction, confidence-rated hypotheses |
| **Solution Architect** | Fix Generation | Clean idiomatic fixes (DRY/SOLID), defensive programming, pytest test snippets, implementation plans |
| **Reliability Engineer** | Validation | Code smell detection, complexity analysis, security review, comprehensive markdown reports |

### Built-in Tools

Agents have access to these powerful tools:

- `list_directory_tool` - Explore project structure
- `read_code_file_tool` - Read code files with line ranges
- `search_codebase_tool` - Search for patterns across files
- `run_shell_command_tool` - Execute shell commands (with safeguards)
- `analyze_python_code_tool` - AST-based Python code analysis

### Session Management

- SQLite database for debugging session persistence
- Session history tracking and retrieval
- Conversation history storage for each agent interaction

---

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- OpenAI API key

### Quick Install

```bash
# Clone the repository
git clone <your-repo-url>
cd code_debugger

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

---

## 🔑 Configuration

Set your OpenAI API key:

```bash
# Option 1: Environment variable (recommended)
export OPENAI_API_KEY="sk-your-api-key-here"

# Option 2: Create a .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

---

## 🚀 Usage

### CLI Interface

```bash
# Run the CLI
python code_debugger_cli.py --help

# Run a sample debugging session
python code_debugger_cli.py --run-sample

# Debug from an error file
python code_debugger_cli.py --error-file error.txt --failing-file app.py --failing-line 42

# List all debugging sessions
python code_debugger_cli.py --list-sessions

# Get report for a specific session
python code_debugger_cli.py --session-report <session-id>
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--error-file` | Path to file containing error trace |
| `--failing-file` | Path to the file that's failing |
| `--failing-line` | Line number where the error occurred |
| `--error-message` | Direct error message/stack trace |
| `--run-sample` | Run a sample debugging session |
| `--list-sessions` | List all debugging sessions in the database |
| `--session-report` | Get report for a specific session ID |
| `--db-path` | Path to SQLite database (default: `debug_sessions.db`) |

### Python API - Basic Usage

```python
from code_debugger import SyncDebuggingOrchestrator

# Create orchestrator
orchestrator = SyncDebuggingOrchestrator()

# Define error context
error_context = {
    'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
    'failing_file': 'example.py',
    'failing_line': 15,
    'inputs': {'numbers': [1, 2, 3], 'index': 2}
}

# Run full debugging cycle
result = orchestrator.run_full_debugging_cycle(error_context)

# Access results
print(result['final_report'])
print(f"Validation Passed: {result['validation_passed']}")
```

### Python API - Async Usage

```python
import asyncio
from code_debugger import DebuggingOrchestrator

async def debug_code():
    orchestrator = DebuggingOrchestrator()
    
    error_context = {...}  # Your error context
    
    result = await orchestrator.run_full_debugging_cycle(error_context)
    return result

# Run
asyncio.run(debug_code())
```

### Individual Agent Usage

```python
from code_debugger import SyncDebuggingOrchestrator

orchestrator = SyncDebuggingOrchestrator()

# Run only Debug Sleuth
sleuth_result = orchestrator.run_debug_sleuth(error_context)
print(sleuth_result['final_output'])

# Run only Solution Architect (needs bug report)
architect_result = orchestrator.run_solution_architect(
    sleuth_result['final_output']
)

# Run only Reliability Engineer
validator_result = orchestrator.run_reliability_engineer(
    architect_result['final_output'],
    sleuth_result['final_output']
)
```

---

## 📊 Example Output

The system generates comprehensive markdown reports:

```markdown
# 🔍 Debug Analysis Report

## 📋 Root Cause Summary
Root Cause: IndexError - list index out of range
Underlying Issue: Array/list index out of bounds
Confidence: High

## 🛠️ The Fix
```python
def safe_array_access(array: list, index: int, default=None):
    """Safely access array elements with bounds checking."""
    if not array:
        return default
    if 0 <= index < len(array):
        return array[index]
    return default
```

## ✅ Verification Steps
```bash
pip install pytest
pytest -v test_fix.py
```

## 📊 Quality Analysis
| Metric | Status |
|--------|--------|
| Code Quality | 85/100 |
| Security | Secure |
| Complexity | O(1) |

## 📝 Implementation Plan
1. Replace direct array access with safe_array_access()
2. Add unit tests for edge cases
3. Run existing test suite to ensure no regressions

## 🚨 Recommendations
- Consider adding type hints throughout the codebase
- Add input validation at function boundaries
```

---

## 🏗️ Architecture

### Package Structure

```
src/code_debugger/
├── __init__.py          # Package exports
├── __main__.py          # Module entry point
├── agents.py            # Agent definitions & orchestrator
├── tools.py             # Tool implementations
├── orchestrator.py      # Workflow orchestration
├── session_manager.py   # SQLite session management
├── database.py          # Database utilities
└── main.py              # Main entry point
```

### Agent Workflow

1. **Debug Sleuth** receives error context
   - Analyzes stack trace
   - Examines code context using tools
   - Produces root cause analysis
   - Hands off to Solution Architect

2. **Solution Architect** receives bug report
   - Designs fix following best practices
   - Creates test snippets
   - Documents implementation plan
   - Hands off to Reliability Engineer

3. **Reliability Engineer** receives fix proposal
   - Performs code smell detection
   - Analyzes complexity
   - Reviews security
   - Generates final report or sends back for revision

---

## 🧪 Testing

```bash
# Run basic tests
python test_agents.py

# Run OpenAI-specific tests
python test_openai_agents.py

# Run the example usage
python example_usage.py
```

---

## 🔒 Security Notes

- The `run_shell_command_tool` should be used with caution
- The Reliability Engineer automatically scans for:
  - Hardcoded credentials
  - SQL injection risks
  - Command injection vulnerabilities
  - Path traversal issues
- Never commit API keys or credentials in your code

---

## 📝 Configuration Options

### Custom Model

```python
# Use a different OpenAI model
orchestrator = SyncDebuggingOrchestrator(model="gpt-4o")
```

### Custom Database Path

```python
# Use a custom SQLite database path
orchestrator = SyncDebuggingOrchestrator(db_path="/path/to/debug.db")
```

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install in development mode
pip install -e .

# Run tests before committing
python test_agents.py
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `OPENAI_API_KEY not found`
```bash
# Solution: Set your API key
export OPENAI_API_KEY="sk-your-key-here"
```

**Issue:** `Module not found: agents`
```bash
# Solution: Ensure dependencies are installed
uv sync  # or: pip install -e .
```

**Issue:** `Database locked`
```bash
# Solution: Close other connections or remove the database
rm debug_sessions.db
```

---

## 📚 Additional Resources

- [Example Usage](example_usage.py)

---


