# Code Debugger API

Live API for the multi-agent debugging system.

## Endpoints

### GET /
API documentation and information

### GET /health
Health check endpoint

### POST /debug
Debug an error using the multi-agent system

**Request Body:**
```json
{
  "error_trace": "Traceback (most recent call last)...",
  "failing_file": "app.py",
  "failing_line": 42,
  "inputs": {"items": [1, 2, 3], "index": 5},
  "codebase_path": "."
}
```

**Response:**
```json
{
  "success": true,
  "validation_passed": true,
  "final_report": "...",
  "agents_used": ["DebugSleuth", "SolutionArchitect", "ReliabilityEngineer"],
  "root_cause_analysis": "...",
  "solution_architecture": "...",
  "reliability_validation": "..."
}
```

### GET /api/agents
Get information about available agents

## Example Usage

```bash
curl -X POST https://your-app.vercel.app/debug \
  -H "Content-Type: application/json" \
  -d '{
    "error_trace": "Traceback (most recent call last):\n  File \"app.py\", line 42, in process\n    item = items[index]\nIndexError: list index out of range",
    "failing_file": "app.py",
    "failing_line": 42,
    "inputs": {"items": [1, 2, 3], "index": 5}
  }'
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python api/index.py

# Test
curl http://localhost:5000/health
```
