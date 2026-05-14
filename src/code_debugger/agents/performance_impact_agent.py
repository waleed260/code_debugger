"""
PerformanceImpactAgent — Analyzes performance impact of bugs and fixes.
"""

from agents import Agent, function_tool, ModelSettings
import os
from typing import Dict, Any, List


PERFORMANCE_INSTRUCTIONS = """
You are a performance impact analyst. Assess the performance implications.

Capabilities:
1. Detect performance anti-patterns in buggy code
2. Assess fix performance impact (better/worse/neutral)
3. Identify N^2 algorithms, memory leaks, I/O bottlenecks
4. Suggest performance improvements alongside bug fixes

Output format:
- Performance Score: 0-100
- Bottlenecks Detected: <list>
- Fix Performance Impact: Improves / Neutral / Degrades
- Estimated Performance Gain/Loss: <percentage>
- Optimization Suggestions: <list>
"""


@function_tool
def analyze_performance_patterns(code: str) -> List[Dict[str, Any]]:
    """Detect performance anti-patterns in code."""
    issues = []
    lines = code.splitlines()
    nested_loops = 0
    in_loop = False
    loop_depth = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if any(kw in stripped for kw in ["for ", "while "]) and ":" in stripped:
            if in_loop:
                loop_depth += 1
            in_loop = True
            if loop_depth >= 2:
                issues.append({
                    "line": i,
                    "pattern": "Nested Loop",
                    "impact": "O(n²) or worse complexity",
                    "severity": "warning",
                    "code": stripped[:60],
                })

        if stripped.startswith(("def ", "class ")):
            in_loop = False
            loop_depth = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if ".append(" in stripped and i < len(lines) and "for " in lines[i] if i < len(lines) else False:
            pass

        if re_match := __import__("re").match(r".*for\s+\w+\s+in\s+.*\.keys\(\)", stripped):
            issues.append({
                "line": i,
                "pattern": "dict.keys() iteration",
                "impact": "Minor - use direct iteration",
                "severity": "info",
                "code": stripped[:60],
            })
        elif re_match := __import__("re").match(r".*\+\s*=\s*\w+\s*\+\s*", stripped):
            issues.append({
                "line": i,
                "pattern": "String concatenation in loop",
                "impact": "Use .join() for better performance",
                "severity": "info",
                "code": stripped[:60],
            })
        elif "pandas" in stripped and "apply" in stripped and "lambda" in stripped:
            issues.append({
                "line": i,
                "pattern": "Slow pandas apply with lambda",
                "impact": "Use vectorized operations instead",
                "severity": "warning",
                "code": stripped[:60],
            })

    return issues


@function_tool
def estimate_fix_performance_impact(original_code: str, fixed_code: str) -> Dict[str, Any]:
    """Estimate the performance impact of a fix."""
    original_lines = len(original_code.splitlines())
    fixed_lines = len(fixed_code.splitlines())

    original_try_except = original_code.count("try:") + original_code.count("except")
    fixed_try_except = fixed_code.count("try:") + fixed_code.count("except")

    original_loops = original_code.count("for ") + original_code.count("while ")
    fixed_loops = fixed_code.count("for ") + fixed_code.count("while ")

    impact = "neutral"
    if fixed_try_except > original_try_except + 2:
        impact = "slightly_degraded"
    elif fixed_loops < original_loops:
        impact = "improved"

    return {
        "line_count_change": fixed_lines - original_lines,
        "try_except_change": fixed_try_except - original_try_except,
        "loop_count_change": fixed_loops - original_loops,
        "estimated_performance_impact": impact,
        "notes": "Adding try/except has negligible performance cost unless in hot path",
    }


PerformanceImpactAgent = Agent(
    name="PerformanceImpactAgent",
    instructions=PERFORMANCE_INSTRUCTIONS,
    tools=[analyze_performance_patterns, estimate_fix_performance_impact],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
