"""
Code Intelligence Layer — AST parsing, Control Flow Graphs, Data Flow Graphs

Provides deep semantic understanding of code beyond regex/LLM reasoning.
Uses Python's built-in AST module and tree-sitter for multi-language support.
"""

import ast
import os
import sys
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionInfo:
    name: str
    line_start: int
    line_end: int
    args: List[str]
    decorators: List[str]
    docstring: Optional[str]
    calls: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    returns: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    line_start: int
    line_end: int
    bases: List[str]
    methods: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ImportInfo:
    module: str
    names: List[str]
    line: int


@dataclass
class VariableDef:
    name: str
    line: int
    type_hint: Optional[str]
    value_preview: Optional[str]


@dataclass
class CodeEntity:
    type: str
    name: str
    line: int
    content: str


@dataclass
class CallGraph:
    caller: str
    callee: str
    line: int


@dataclass
class DataFlowEdge:
    var_name: str
    defined_at: int
    used_at: int
    defined_in: str
    used_in: str


@dataclass
class DependencyRelation:
    importer: str
    imported: str
    import_type: str
    line: int


class ASTAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        abs_path = self._resolve(file_path)
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}"}

        try:
            with open(abs_path, "r") as f:
                content = f.read()
            tree = ast.parse(content)
            return self._analyze_tree(tree, content, file_path)
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}", "file": file_path}
        except Exception as e:
            return {"error": str(e), "file": file_path}

    def analyze_code(self, code: str, filename: str = "<code>") -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
            return self._analyze_tree(tree, code, filename)
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_tree(self, tree: ast.AST, source: str, filename: str) -> Dict[str, Any]:
        functions = []
        classes = []
        imports = []
        variables = []
        call_graph = []
        data_flow = []
        issues = []
        complexity_score = 0

        defined_vars: Dict[str, List[int]] = {}
        all_calls: List[Tuple[str, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node)
                functions.append(func_info.__dict__)
                calls_in_func = self._extract_calls(node)
                for callee in calls_in_func:
                    call_graph.append(CallGraph(
                        caller=func_info.name, callee=callee[0], line=callee[1]
                    ).__dict__)
                all_calls.extend((name, node.lineno) for name in calls_in_func)
                complexity_score += self._compute_complexity(node)

            elif isinstance(node, ast.ClassDef):
                classes.append(self._analyze_class(node))

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(self._analyze_import(node, source))

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_info = VariableDef(
                            name=target.id,
                            line=node.lineno,
                            type_hint=None,
                            value_preview=self._truncate(ast.get_source_segment(source, node.value) if source else "", 50),
                        )
                        variables.append(var_info.__dict__)
                        if target.id not in defined_vars:
                            defined_vars[target.id] = []
                        defined_vars[target.id].append(node.lineno)

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in defined_vars and node.id not in (v["name"] for v in variables):
                    pass

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                pass

        for var_name, def_lines in defined_vars.items():
            for def_line in def_lines:
                uses = self._find_variable_uses(tree, var_name, def_line)
                for use_line in uses:
                    data_flow.append(DataFlowEdge(
                        var_name=var_name, defined_at=def_line,
                        used_at=use_line, defined_in=filename, used_in=filename,
                    ).__dict__)

        complexity_score = min(complexity_score, 100)
        loc = len(source.splitlines()) if source else 0
        class_count = len(classes)
        issues = self._detect_issues(functions, classes, source)

        return {
            "file": filename,
            "loc": loc,
            "complexity_score": complexity_score,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "variables": variables,
            "call_graph": call_graph,
            "data_flow": data_flow,
            "issues": issues,
            "has_errors": len([i for i in issues if i["severity"] == "error"]) > 0,
        }

    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        calls = set()
        variables = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.add(f"{self._get_attribute_chain(child.func)}")
            elif isinstance(child, ast.Assign):
                for t in child.targets:
                    if isinstance(t, ast.Name):
                        variables.append(t.id)

        returns = None
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                returns = ast.dump(child.value)[:50]

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
            args=[arg.arg for arg in node.args.args],
            decorators=[d.id if isinstance(d, ast.Name) else ast.dump(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
            calls=list(calls),
            variables=variables,
            returns=returns,
        )

    def _analyze_class(self, node: ast.ClassDef) -> Dict:
        return {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": getattr(node, "end_lineno", node.lineno),
            "bases": [b.id if isinstance(b, ast.Name) else ast.dump(b) for b in node.bases],
            "methods": [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
            "docstring": ast.get_docstring(node),
        }

    def _analyze_import(self, node: ast.AST, source: str) -> Dict:
        if isinstance(node, ast.Import):
            return {
                "module": node.names[0].name,
                "names": [n.name for n in node.names],
                "alias": [n.asname for n in node.names],
                "line": node.lineno,
                "type": "import",
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "module": node.module or "",
                "names": [n.name for n in node.names],
                "alias": [n.asname for n in node.names],
                "line": node.lineno,
                "type": "from_import",
            }
        return {}

    def _extract_calls(self, node: ast.AST) -> List[Tuple[str, int]]:
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append((child.func.id, child.lineno))
                elif isinstance(child.func, ast.Attribute):
                    calls.append((self._get_attribute_chain(child.func), child.lineno))
        return calls

    def _get_attribute_chain(self, node: ast.Attribute) -> str:
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _compute_complexity(self, node: ast.FunctionDef) -> int:
        score = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                  ast.ExceptHandler, ast.With, ast.AsyncWith,
                                  ast.Try, ast.Assert)):
                score += 1
            elif isinstance(child, ast.BoolOp):
                score += len(child.values) - 1
            elif isinstance(child, ast.Compare):
                score += 1
        return score

    def _find_variable_uses(self, tree: ast.AST, var_name: str, after_line: int) -> List[int]:
        uses = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Name) and node.id == var_name
                    and isinstance(node.ctx, ast.Load)
                    and hasattr(node, 'lineno') and node.lineno > after_line):
                uses.append(node.lineno)
        return uses

    def _detect_issues(self, functions: List[Dict], classes: List[Dict], source: str) -> List[Dict]:
        issues = []
        seen_names = set()

        for func in functions:
            if func["name"] in seen_names:
                issues.append({
                    "type": "duplicate_function",
                    "severity": "warning",
                    "message": f"Duplicate function name: {func['name']}",
                    "line": func["line_start"],
                })
            seen_names.add(func["name"])

            complexity = self._compute_complexity_for_dict(func)
            if complexity > 10:
                issues.append({
                    "type": "high_complexity",
                    "severity": "warning",
                    "message": f"Function {func['name']} has high cyclomatic complexity ({complexity})",
                    "line": func["line_start"],
                })

            if len(func.get("args", [])) > 6:
                issues.append({
                    "type": "too_many_args",
                    "severity": "warning",
                    "message": f"Function {func['name']} has {len(func['args'])} arguments (max 6 recommended)",
                    "line": func["line_start"],
                })

            if not func.get("docstring"):
                issues.append({
                    "type": "missing_docstring",
                    "severity": "style",
                    "message": f"Function {func['name']} is missing a docstring",
                    "line": func["line_start"],
                })

        for cls in classes:
            if not cls.get("docstring"):
                issues.append({
                    "type": "missing_docstring",
                    "severity": "style",
                    "message": f"Class {cls['name']} is missing a docstring",
                    "line": cls["line_start"],
                })

        if source and "try:" not in source and "except" not in source:
            issues.append({
                "type": "no_error_handling",
                "severity": "info",
                "message": "File has no try/except blocks — consider adding error handling",
                "line": 1,
            })

        return issues

    def _compute_complexity_for_dict(self, func: Dict) -> int:
        return min(func.get("line_end", 0) - func.get("line_start", 0) // 5 + 1, 30)

    def _truncate(self, text: str, max_len: int) -> str:
        if not text:
            return None
        text = text.strip()
        return text[:max_len] + "..." if len(text) > max_len else text

    def _resolve(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.repo_path, path)

    def build_call_graph(self, files: List[str] = None) -> Dict[str, Any]:
        if files is None:
            files = []
            for root, _, filenames in os.walk(self.repo_path):
                if ".git" in root or "__pycache__" in root:
                    continue
                for f in filenames:
                    if f.endswith(".py"):
                        files.append(os.path.join(root, f))

        nodes = set()
        edges = []
        for file_path in files:
            result = self.analyze_file(file_path)
            if "error" in result:
                continue
            for func in result.get("functions", []):
                nodes.add(func["name"])
                for call in func.get("calls", []):
                    edges.append({"from": func["name"], "to": call})
            for cls in result.get("classes", []):
                nodes.add(cls["name"])
            for imp in result.get("imports", []):
                nodes.add(imp.get("module", ""))

        return {
            "nodes": list(nodes),
            "edges": edges,
            "file_count": len(files),
        }

    def find_data_flow_path(self, file_path: str, var_name: str, line: int) -> Dict[str, Any]:
        result = self.analyze_file(file_path)
        if "error" in result:
            return result
        path = []
        for edge in result.get("data_flow", []):
            if edge["var_name"] == var_name or edge["used_at"] == line:
                path.append(edge)
        return {
            "variable": var_name,
            "target_line": line,
            "flow_path": path,
        }

    def get_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        result = self.analyze_file(file_path)
        if "error" in result:
            return result
        return {
            "file": file_path,
            "imports": result.get("imports", []),
        }

    def get_project_dependencies(self) -> Dict[str, Any]:
        deps = {}
        for root, _, files in os.walk(self.repo_path):
            if ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    file_path = os.path.join(root, f)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    dep_info = self.get_file_dependencies(file_path)
                    if "error" not in dep_info:
                        deps[rel_path] = dep_info["imports"]
        return deps
