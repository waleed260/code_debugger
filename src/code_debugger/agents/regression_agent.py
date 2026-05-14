"""
RegressionAgent — Detects side effects and regressions introduced by fixes.
"""

from agents import Agent, function_tool, ModelSettings
import os
import ast
from typing import Dict, Any, List


REGRESSION_INSTRUCTIONS = """
You are a regression prevention specialist. Detect side effects of fixes.

Capabilities:
1. Identify if a fix introduces new failure modes
2. Check if downstream callers are affected by signature changes
3. Detect performance regressions from fix patterns
4. Verify backward compatibility is maintained
5. Flag risky fix patterns that may cause cascading failures

Output format:
- Regression Risk: Low / Medium / High
- Affected Callers: <list>
- Backward Compatible: Yes/No
- Performance Impact: None / Minor / Significant
- Risk Patterns Detected: <list>
- Recommended: Safe to Deploy / Needs Review / Redesign Required
"""


@function_tool
def analyze_signature_changes(code_before: str, code_after: str) -> Dict[str, Any]:
    """Detect function signature changes between original and fixed code."""
    def extract_signatures(source: str) -> List[Dict]:
        sigs = []
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sigs.append({
                        "name": node.name,
                        "args": [(a.arg, None) for a in node.args.args],
                        "has_return": any(
                            isinstance(n, ast.Return) and n.value
                            for n in ast.walk(node)
                        ),
                    })
        except SyntaxError:
            pass
        return sigs

    before_sigs = {s["name"]: s for s in extract_signatures(code_before)}
    after_sigs = {s["name"]: s for s in extract_signatures(code_after)}

    changes = []
    for name, after_sig in after_sigs.items():
        before_sig = before_sigs.get(name)
        if not before_sig:
            changes.append({"type": "new_function", "name": name})
        else:
            before_args = [a for a, _ in before_sig["args"]]
            after_args = [a for a, _ in after_sig["args"]]
            if before_args != after_args:
                changes.append({
                    "type": "signature_change",
                    "name": name,
                    "before": before_args,
                    "after": after_args,
                })

    removed = [name for name in before_sigs if name not in after_sigs]
    for name in removed:
        changes.append({"type": "removed_function", "name": name})

    return {
        "changes": changes,
        "has_breaking_changes": any(
            c["type"] in ("signature_change", "removed_function")
            for c in changes
        ),
    }


@function_tool
def detect_risky_patterns(code: str) -> List[Dict[str, Any]]:
    """Detect risky code patterns that may cause regressions."""
    patterns = []
    lines = code.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "except:" and not stripped.startswith("#"):
            patterns.append({"line": i, "pattern": "Bare except", "risk": "high", "message": "Catches ALL exceptions, may hide bugs"})
        if "global " in stripped and not stripped.startswith("#"):
            patterns.append({"line": i, "pattern": "Global mutation", "risk": "medium", "message": "Modifying global state can cause side effects"})
        if "eval(" in stripped or "exec(" in stripped:
            patterns.append({"line": i, "pattern": "Dynamic execution", "risk": "high", "message": "eval/exec can execute arbitrary code"})
        if "threading" in stripped:
            patterns.append({"line": i, "pattern": "Threading", "risk": "medium", "message": "Threading can introduce race conditions"})
        if "del " in stripped:
            patterns.append({"line": i, "pattern": "Deletion", "risk": "medium", "message": "Deleting variables/attributes can break dependent code"})
        if "os.system" in stripped or "subprocess" in stripped:
            patterns.append({"line": i, "pattern": "Shell execution", "risk": "high", "message": "Shell commands must be properly sanitized"})

    return patterns


RegressionAgent = Agent(
    name="RegressionAgent",
    instructions=REGRESSION_INSTRUCTIONS,
    tools=[analyze_signature_changes, detect_risky_patterns],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
