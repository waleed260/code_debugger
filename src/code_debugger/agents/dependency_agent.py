"""
DependencyAgent — Detects package version conflicts, import failures,
dependency graph issues, and missing modules.
"""

from agents import Agent, function_tool, ModelSettings
import os
import subprocess
import importlib
from importlib.metadata import distribution, PackageNotFoundError
from typing import Dict, Any, List, Optional


DEPENDENCY_INSTRUCTIONS = """
You are a dependency analysis expert. Investigate package/import issues.

Capabilities:
1. Detect missing or incompatible packages
2. Identify version conflicts
3. Analyze import chains for circular dependencies
4. Check for deprecated or insecure packages
5. Suggest specific version pins to resolve conflicts

Output format:
- Checked Dependencies: <list>
- Issues Found: <list with severity>
- Circular Dependencies: <list or None>
- Version Conflicts: <list>
- Recommended Fix: <specific instructions>
"""


@function_tool
def check_import(module_name: str) -> Dict[str, Any]:
    """Check if a module can be imported and get its version."""
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", "unknown")
        return {
            "importable": True,
            "version": version,
            "file": getattr(mod, "__file__", "unknown"),
        }
    except ImportError as e:
        return {
            "importable": False,
            "version": None,
            "error": str(e),
        }
    except Exception as e:
        return {
            "importable": False,
            "version": None,
            "error": f"Unexpected error: {e}",
        }


@function_tool
def check_package_version(package_name: str) -> Dict[str, Any]:
    """Check installed version and available versions of a package."""
    try:
        dist = distribution(package_name)
        return {
            "installed": True,
            "version": dist.version,
            "location": dist.locate_file(".") if hasattr(dist, "locate_file") else "",
        }
    except PackageNotFoundError:
        return {
            "installed": False,
            "version": None,
            "error": f"{package_name} is not installed",
        }


@function_tool
def find_import_chains(file_path: str) -> List[Dict[str, Any]]:
    """Find all imports in a file and build import chains."""
    import ast
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": f"{node.module}.{alias.name}" if node.module else alias.name,
                        "alias": alias.asname,
                    })
        return imports
    except Exception as e:
        return [{"error": str(e)}]


DependencyAgent = Agent(
    name="DependencyAgent",
    instructions=DEPENDENCY_INSTRUCTIONS,
    tools=[check_import, check_package_version, find_import_chains],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=500),
)
