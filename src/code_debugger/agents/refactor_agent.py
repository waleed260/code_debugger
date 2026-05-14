"""
RefactorAgent — Improves code quality during and after fixes.
"""

from agents import Agent, function_tool, ModelSettings
import os
from typing import Dict, Any, List


REFACTOR_INSTRUCTIONS = """
You are a code quality engineer. Improve code maintainability during fixes.

Capabilities:
1. Detect code smells in buggy code
2. Suggest refactoring improvements alongside fixes
3. Apply DRY, SOLID, and clean code principles
4. Suggest type hints and documentation improvements
5. Identify opportunities for better abstractions

Output format:
- Quality Score: 0-100
- Code Smells Found: <list>
- Refactoring Suggestions: <list>
- Type Hints Missing: <list>
- Documentation Issues: <list>
- Recommended Cleanup: <list>
"""


@function_tool
def detect_code_smells(code: str) -> List[Dict[str, Any]]:
    """Detect common code smells."""
    smells = []
    lines = code.splitlines()
    function_lengths = {}
    current_func = None
    func_start = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("def ") and stripped.endswith(":"):
            if current_func:
                func_len = i - func_start
                if func_len > 50:
                    smells.append({
                        "line": func_start,
                        "smell": "Long Function",
                        "detail": f"Function '{current_func}' is {func_len} lines",
                        "severity": "warning",
                    })
            current_func = stripped[4:stripped.index("(")]
            func_start = i

        if "==" and "None" in stripped:
            smells.append({
                "line": i,
                "smell": "Equality with None",
                "detail": "Use 'is None' instead of '== None'",
                "severity": "style",
            })
        if "not " in stripped and " in " in stripped and "if " in stripped:
            pass
        if stripped.count("(") > 4:
            smells.append({
                "line": i,
                "smell": "Complex Expression",
                "detail": "Consider breaking into multiple statements",
                "severity": "style",
            })

    if current_func:
        func_len = len(lines) - func_start
        if func_len > 50:
            smells.append({
                "line": func_start,
                "smell": "Long Function",
                "detail": f"Function '{current_func}' is {func_len} lines",
                "severity": "warning",
            })

    comment_ratio = sum(1 for l in lines if l.strip().startswith("#")) / max(len(lines), 1)
    if comment_ratio > 0.3:
        smells.append({
            "line": 1,
            "smell": "Excessive Comments",
            "detail": f"{comment_ratio:.0%} of lines are comments",
            "severity": "info",
        })

    nested_count = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if indent > 24:
            nested_count += 1
    if nested_count > 3:
        smells.append({
            "line": 1,
            "smell": "Deep Nesting",
            "detail": f"{nested_count} lines have >24 spaces indentation",
            "severity": "warning",
        })

    return smells


@function_tool
def suggest_type_hints(code: str) -> List[Dict[str, Any]]:
    """Suggest type hints for functions missing them."""
    import ast
    suggestions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return_hint = node.returns is not None
                has_arg_hints = all(
                    a.annotation is not None for a in node.args.args
                ) if node.args.args else True

                if not has_return_hint or not has_arg_hints:
                    missing = []
                    if not has_return_hint:
                        missing.append("return type")
                    if not has_arg_hints:
                        missing.append("parameter types")
                    suggestions.append({
                        "function": node.name,
                        "line": node.lineno,
                        "missing": missing,
                    })
    except SyntaxError:
        pass
    return suggestions


RefactorAgent = Agent(
    name="RefactorAgent",
    instructions=REFACTOR_INSTRUCTIONS,
    tools=[detect_code_smells, suggest_type_hints],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
