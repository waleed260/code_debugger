"""
DataFlowAgent — Traces variable corruption and data flow paths
to identify where problematic values originate.
"""

from agents import Agent, function_tool, ModelSettings
import os
import ast
from typing import Dict, Any, List, Optional


DATA_FLOW_INSTRUCTIONS = """
You are a data flow analysis specialist. Trace where problematic values originate.

Capabilities:
1. Trace variable values through function calls
2. Identify where None/null values enter the data flow
3. Detect type mutations across assignment chains
4. Find uninitialized variables or stale values
5. Trace input validation failures

Output format:
- Target Variable: <name>
- Value at Failure: <inferred value or type>
- Origin Path: <where the value was created/modified>
- Intermediate Steps: <each mutation along the path>
- Root Cause: <what caused the bad value>
"""


@function_tool
def trace_variable_origin(file_path: str, var_name: str, line_number: int) -> Dict[str, Any]:
    """Trace where a variable's value originates by analyzing the AST."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        tree = ast.parse(content)

        assignments = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        assignments.append({
                            "line": node.lineno,
                            "value_type": type(node.value).__name__,
                            "value_preview": ast.dump(node.value)[:80],
                        })
            elif isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    if arg.arg == var_name:
                        assignments.insert(0, {
                            "line": node.lineno,
                            "value_type": "parameter",
                            "value_preview": f"parameter of {node.name}()",
                        })

        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if keyword.arg == var_name:
                        calls.append({
                            "line": node.lineno,
                            "call": ast.dump(node.func)[:60],
                        })
                for i, arg in enumerate(node.args):
                    if isinstance(arg, ast.Name) and arg.id == var_name:
                        calls.append({
                            "line": node.lineno,
                            "call": ast.dump(node.func)[:60],
                            "position": i,
                        })

        return {
            "variable": var_name,
            "assignments_found": assignments,
            "calls_found": calls,
            "defined": len(assignments) > 0,
            "used_in_calls": len(calls),
        }
    except Exception as e:
        return {"error": str(e)}


@function_tool
def analyze_function_returns(file_path: str, function_name: str) -> List[Dict[str, Any]]:
    """Analyze all return paths in a function to find potential None returns."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                returns = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Return):
                        returns.append({
                            "line": child.lineno,
                            "value": ast.dump(child.value)[:60] if child.value else "None (implicit)",
                            "returns_none": child.value is None,
                        })

                if not returns:
                    returns.append({
                        "line": node.lineno + (node.end_lineno or node.lineno),
                        "value": "None (no return statement = implicit None)",
                        "returns_none": True,
                    })

                return returns
        return [{"error": f"Function {function_name} not found"}]
    except Exception as e:
        return [{"error": str(e)}]


DataFlowAgent = Agent(
    name="DataFlowAgent",
    instructions=DATA_FLOW_INSTRUCTIONS,
    tools=[trace_variable_origin, analyze_function_returns],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=500),
)
