"""
StackTraceAgent — Precisely parses tracebacks and identifies the error type,
location, call chain, and relevant context.
"""

from agents import Agent, function_tool, ModelSettings
import os
import re
from typing import Dict, Any, Optional


STACK_TRACE_INSTRUCTIONS = """
You are a traceback parsing specialist. Your job is to precisely analyze error traces.

Capabilities:
1. Parse error type, message, and exact location from any traceback format
2. Identify the full call chain leading to the failure
3. Extract relevant code context around the failing line
4. Determine if the error is a runtime error, logic error, or system error
5. Identify patterns like None propagation, type mismatches, off-by-one errors

Output format:
- Error Type: <exact exception class>
- Error Message: <the error message>
- Location: <file:line>
- Call Chain: <caller → ... → failing frame>
- Line Context: <surrounding code with >>> on failing line>
- Error Category: Runtime / Logic / System / Resource
- First Occurrence: Yes/No (is this likely the first time this error occurs)
"""


@function_tool
def extract_traceback_info(error_trace: str) -> Dict[str, Any]:
    """Extract structured information from a traceback string."""
    lines = error_trace.strip().split("\n")
    frames = []
    error_type = "UnknownError"
    error_message = ""
    failing_file = ""
    failing_line = 0

    for line in lines:
        file_match = re.match(r'\s*File "([^"]+)", line (\d+), in (.+)', line)
        if file_match:
            frames.append({
                "file": file_match.group(1),
                "line": int(file_match.group(2)),
                "function": file_match.group(3),
            })
            failing_file = file_match.group(1)
            failing_line = int(file_match.group(2))

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        colon_idx = line.find(":")
        if colon_idx != -1:
            candidate = line[:colon_idx].strip()
            if candidate and (
                candidate[0].isupper() and ("Error" in candidate or "Exception" in candidate)
            ):
                error_type = candidate
                error_message = line[colon_idx + 1:].strip()
                break

    if not error_message and frames:
        last_line = lines[-1].strip() if lines else ""
        error_message = last_line

    return {
        "error_type": error_type,
        "error_message": error_message,
        "failing_file": failing_file,
        "failing_line": failing_line,
        "call_chain": frames,
        "frame_count": len(frames),
    }


StackTraceAgent = Agent(
    name="StackTraceAgent",
    instructions=STACK_TRACE_INSTRUCTIONS,
    tools=[extract_traceback_info],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
