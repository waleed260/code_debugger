# Code Debugger - Multi-Agent Debugging System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://github.com/openai/openai-agents-python)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Supported-orange.svg)](https://openrouter.ai/)

A sophisticated AI-powered debugging assistant that uses **three specialized agents** to analyze errors, generate fixes, and validate solutions. Built with the **OpenAI Agents SDK** and supports **OpenRouter** for flexible model selection.

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
- OpenRouter API key (recommended) or OpenAI API key

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

### Option 1: OpenRouter (Recommended)

OpenRouter provides access to multiple AI models including GPT-4, Claude, Gemini, and more through a single API.

```bash
# Get your API key from https://openrouter.ai/keys

# Create a .env file
cat > .env << EOF
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-3.5-turbo
EOF
```

**Available Models via OpenRouter:**
- `gpt-4o` - OpenAI GPT-4 Optimized
- `gpt-3.5-turbo` - OpenAI GPT-3.5 (cost-effective)
- `google/gemini-2.0-flash-exp:free` - Google Gemini (free tier)
- `anthropic/claude-3-opus` - Anthropic Claude 3 Opus
- And many more at [openrouter.ai/models](https://openrouter.ai/models)

### Option 2: OpenAI Direct

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

**Note:** The system automatically detects which configuration you're using based on the environment variables set.

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

The system generates comprehensive markdown reports. Here's a real example from testing:

### Input Error
```python
error_context = {
    'error_trace': '''Traceback (most recent call last):
  File "data_processor.py", line 42, in process_batch
    item = items[current_index]
IndexError: list index out of range''',
    'failing_file': 'data_processor.py',
    'failing_line': 42,
    'inputs': {
        'items': [1, 2, 3],
        'current_index': 5
    }
}
```

### Agent Output

```markdown
# 🔍 Debug Analysis Report

## 📋 Root Cause Summary
The root cause of the IndexError at line 42 in data_processor.py is accessing an index in the `items` list beyond its valid range, triggered by the `current_index` variable holding a value greater than the length of the list.

## 🛠️ The Fix
```python
items = [1, 2, 3]

try:
    item = items[current_index]
except IndexError:
    item = None  # Handle index out of range gracefully
```

## ✅ Verification Steps
1. Open the `data_processor.py` file.
2. Locate line 42 where the index access is performed.
3. Replace the index access line with the provided try-except block.
4. Test the fix using the test snippet to ensure that the IndexError is handled correctly.
5. Deploy the updated `data_processor.py` file to the relevant environment.
6. Monitor for any unexpected behavior and ensure the fix works as intended.

## 📊 Quality Analysis
| Metric       | Status   |
|--------------|----------|
| Code Quality | 95/100   |
| Security     | Secure   |
| Complexity   | O(1)     |

## 📝 Implementation Plan
The proposed fix effectively handles the index out of range exception at line 42 in data_processor.py and provides a graceful way to handle the error.

## 🚨 Recommendations
Ensure the fix does not hide underlying logic errors and monitor for any unexpected behavior after deployment.
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
# Run OpenRouter integration test
uv run python test_openrouter.py

# Run basic tests
python test_agents.py

# Run OpenAI-specific tests
python test_openai_agents.py

# Run the example usage
python example_usage.py
```

The `test_openrouter.py` script verifies that:
- OpenRouter API key is configured correctly
- All three agents can communicate with OpenRouter
- The full debugging cycle completes successfully

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

The agents use the model specified in your `.env` file. To change models:

```bash
# In your .env file
OPENROUTER_MODEL=gpt-4o  # For more powerful analysis
# or
OPENROUTER_MODEL=gpt-3.5-turbo  # For cost-effective debugging
```

You can also modify the model directly in `src/code_debugger/agents.py`:

```python
DebugSleuth = Agent(
    name="DebugSleuth",
    instructions=DEBUG_SLEUTH_INSTRUCTIONS,
    tools=[...],
    model="gpt-4o"  # Change this
)
```

### Custom Database Path

```python
# Use a custom SQLite database path
orchestrator = SyncDebuggingOrchestrator(db_path="/path/to/debug.db")
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `OPENROUTER_BASE_URL` | OpenRouter API endpoint | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | Model to use for agents | `gpt-3.5-turbo` |
| `DEBUG` | Enable debug logging | `false` |

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

**Issue:** `OPENROUTER_API_KEY not found`
```bash
# Solution: Create a .env file with your API key
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

**Issue:** `Error code: 402 - requires more credits`
```bash
# Solution: Either:
# 1. Add credits to your OpenRouter account at https://openrouter.ai/settings/credits
# 2. Use a free model like gpt-3.5-turbo or google/gemini-2.0-flash-exp:free
# 3. Switch to a different model in your .env file
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

**Issue:** `Unknown prefix: google` or model errors
```bash
# Solution: Use standard model names like gpt-4o or gpt-3.5-turbo
# OpenRouter will route them through their API automatically
```

---

## 📚 Additional Resources

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [Example Usage](example_usage.py)
- [Test Files](test_agents.py, test_openai_agents.py)

---

**Built with ❤️ using OpenAI Agents SDK**
