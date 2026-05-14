"""
FixGenerationAgent — Generates candidate fixes with multi-approach strategy.
"""

from agents import Agent, function_tool, ModelSettings
import os
from typing import Dict, Any, List


FIX_GENERATION_INSTRUCTIONS = """
You are a fix generation engineer. Create targeted code fixes.

Capabilities:
1. Generate minimal, correct fixes for identified bugs
2. Provide multiple approaches when appropriate (Quick / Robust / Ideal)
3. Include test-driven validation for each fix
4. Consider edge cases, performance, and security
5. Output structured diffs that can be applied automatically

Output format:
- Root Cause Confirmed: <yes/no with evidence>
- Fix Approach: Quick / Robust / Ideal
- Changed File: <path>
- Diff:
  ```diff
  - old code
  + new code
  ```
- Why This Works: <1-2 sentences>
- Edge Cases Covered: <list>
- Test Snippet: <pytest code>
"""


@function_tool
def generate_safe_wrapper(error_type: str, code_context: str) -> str:
    """Generate a safe wrapper function for common error types."""
    wrappers = {
        "IndexError": """def safe_get(sequence, index, default=None):
    try:
        return sequence[index]
    except (IndexError, TypeError):
        return default""",
        "KeyError": """def safe_get(dictionary, key, default=None):
    return dictionary.get(key, default)""",
        "TypeError": """def safe_operation(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except TypeError as e:
        return {"error": str(e)}""",
        "ValueError": """def safe_convert(value, to_type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default""",
        "AttributeError": """def safe_access(obj, attr, default=None):
    return getattr(obj, attr, default)""",
        "ZeroDivisionError": """def safe_divide(a, b, default=None):
    try:
        return a / b
    except ZeroDivisionError:
        return default""",
        "FileNotFoundError": """def safe_read(path, default=None):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return default""",
        "ImportError": """def safe_import(module_name, fallback=None):
    try:
        return __import__(module_name)
    except ImportError:
        return fallback""",
        "ConnectionError": """import socket
def safe_connect(host, port, timeout=5):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (ConnectionError, TimeoutError, OSError):
        return False""",
    }

    for error_name, wrapper in wrappers.items():
        if error_name in error_type:
            return wrapper

    return f"""def safe_execute(operation, *args, fallback=None, **kwargs):
    try:
        return operation(*args, **kwargs)
    except Exception:
        return fallback"""


FixGenerationAgent = Agent(
    name="FixGenerationAgent",
    instructions=FIX_GENERATION_INSTRUCTIONS,
    tools=[generate_safe_wrapper],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=800),
)
