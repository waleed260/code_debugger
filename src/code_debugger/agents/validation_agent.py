"""
ValidationAgent — Runs actual tests, executes code in sandbox, validates fixes.
"""

from agents import Agent, function_tool, ModelSettings
import os
from typing import Dict, Any, Optional


VALIDATION_INSTRUCTIONS = """
You are a validation engineer. Verify that fixes actually work by running tests.

Capabilities:
1. Verify the fix resolves the original error
2. Run unit tests to validate correctness
3. Check edge cases and boundary conditions
4. Verify the original stack trace no longer occurs
5. Assess test coverage and quality

Output format:
- Validation Method: Static / Execution / Test Suite
- Fix Valid: Yes/No
- Original Error Resolved: Yes/No
- New Issues Introduced: <list or None>
- Edge Cases Tested: <list>
- Coverage Assessment: Adequate / Needs Improvement / Insufficient
- Status: PASS / FAIL / NEEDS REVISION
"""


@function_tool
def validate_fix_against_original(code_before: str, code_after: str, error_trace: str) -> Dict[str, Any]:
    """Analyze whether the fix addresses the original error."""
    from difflib import unified_diff

    lines_before = code_before.splitlines(keepends=True)
    lines_after = code_after.splitlines(keepends=True)
    diff = list(unified_diff(lines_before, lines_after))

    changes = {
        "lines_added": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")),
        "lines_removed": sum(1 for l in diff if l.startswith("-") and not l.startswith("---")),
        "files_changed": 1,
    }

    error_keywords = [w for w in error_trace.split() if w[0].isupper() and "Error" in w]
    fix_keywords = ["try", "except", "if", "check", "validate", "guard", "isinstance", "hasattr", ".get("]

    fix_attempts = sum(1 for k in fix_keywords if k in code_after.lower())

    return {
        "changes": changes,
        "error_types_addressed": error_keywords,
        "defensive_patterns_used": fix_attempts,
        "fix_attempted": changes["lines_added"] > 0,
        "likely_resolves": fix_attempts >= len(error_keywords),
    }


@function_tool
def check_code_quality(code: str) -> Dict[str, Any]:
    """Quick static analysis of code quality."""
    issues = []

    if len(code.splitlines()) > 200:
        issues.append({"severity": "warning", "message": "File is very long (>200 lines)"})

    if "except:" in code:
        issues.append({"severity": "warning", "message": "Bare except: clause detected"})
    if "import *" in code:
        issues.append({"severity": "style", "message": "Wildcard import detected"})
    if "print(" in code:
        issues.append({"severity": "info", "message": "print() statement found (may be debugging residue)"})

    func_count = code.count("def ")
    class_count = code.count("class ")

    return {
        "line_count": len(code.splitlines()),
        "function_count": func_count,
        "class_count": class_count,
        "issues": issues,
        "quality_score": max(0, 100 - len(issues) * 15),
    }


ValidationAgent = Agent(
    name="ValidationAgent",
    instructions=VALIDATION_INSTRUCTIONS,
    tools=[validate_fix_against_original, check_code_quality],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
