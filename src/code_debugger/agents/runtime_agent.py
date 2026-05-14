"""
RuntimeAgent — Analyzes runtime state including variable values,
memory usage, execution flow, and system resources at failure point.
"""

from agents import Agent, function_tool, ModelSettings
import os
import sys
import json
from typing import Dict, Any, Optional


RUNTIME_INSTRUCTIONS = """
You are a runtime analysis expert. Analyze the runtime state at failure point.

Capabilities:
1. Reconstruct variable state from traceback context
2. Identify None propagation and null reference chains
3. Detect memory/resource exhaustion patterns
4. Analyze execution flow to determine how the failing state was reached
5. Identify threading/concurrency issues from trace patterns

Output format:
- Analyzed State: <key variables and their inferred values>
- Runtime Pattern: NullPropagation / MemoryPressure / Concurrency / TypeMismatch / LogicError
- Root Cause Hypothesis: <1-2 sentences>
- Confidence: High/Medium/Low
"""


@function_tool
def analyze_error_pattern(error_trace: str) -> Dict[str, Any]:
    """Analyze the error trace for common runtime patterns."""
    patterns = {
        "none_propagation": [
            "NoneType", "'NoneType' object has no attribute",
            "NoneType object is not subscriptable",
            "NoneType object is not callable",
        ],
        "type_mismatch": [
            "TypeError", "must be", "cannot be interpreted",
            "unsupported operand type(s)",
        ],
        "index_error": [
            "index out of range", "IndexError",
            "list index out of range",
        ],
        "memory_pressure": [
            "MemoryError", "cannot allocate memory",
            "OutOfMemory",
        ],
        "recursion": [
            "RecursionError", "maximum recursion depth exceeded",
        ],
        "concurrency": [
            "RuntimeError: cannot join current thread",
            "deadlock", "race condition",
            "RuntimeError: threads can only be started once",
        ],
        "io_error": [
            "FileNotFoundError", "PermissionError",
            "ConnectionError", "TimeoutError",
            "BrokenPipeError",
        ],
    }

    detected = []
    for pattern_name, signatures in patterns.items():
        for sig in signatures:
            if sig.lower() in error_trace.lower():
                detected.append(pattern_name)
                break

    return {
        "detected_patterns": detected,
        "primary_pattern": detected[0] if detected else "unknown",
    }


@function_tool
def check_runtime_environment() -> Dict[str, Any]:
    """Check current runtime environment details."""
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
        "path": sys.path[:5],
        "recursion_limit": sys.getrecursionlimit(),
    }


RuntimeAgent = Agent(
    name="RuntimeAgent",
    instructions=RUNTIME_INSTRUCTIONS,
    tools=[analyze_error_pattern, check_runtime_environment],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
