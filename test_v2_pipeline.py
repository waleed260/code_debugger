"""
Tests for V2 Debugging Pipeline — specialized agents, sandbox, autonomous repair loop.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import (
    DebuggingOrchestratorV2,
    DebugSessionConfig,
    DebugRAG,
    PatchEngine,
    FilePatch,
    TestGenerator,
    ExecutionSandbox,
)


SAMPLE_ERROR = """Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range"""


class TestDebugRAG:
    def test_extract_error_type(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        error_type = rag._extract_error_type(SAMPLE_ERROR)
        assert error_type == "IndexError", f"Expected IndexError, got {error_type}"

    def test_retrieve_common_patterns(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag.retrieve(SAMPLE_ERROR, "python")
        assert len(results) > 0
        assert any("IndexError" in r.title or "IndexError" in r.content for r in results)

    def test_enrich_prompt(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        enriched = rag.enrich_prompt(SAMPLE_ERROR, "python")
        assert "sources" in enriched
        assert "formatted_context" in enriched

    def test_known_patterns(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        rag.add_known_pattern("IndexError", "Use safe_get with bounds checking", "test")
        solutions = rag._get_known_solutions("IndexError")
        assert len(solutions) > 0

    def test_retrieve_github_issues(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag.retrieve_github_issues("IndexError", "python")
        assert len(results) > 0

    def test_retrieve_docs(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag.retrieve_docs("json", "JSONDecodeError")
        assert len(results) > 0

    def test_retrieve_cve(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag.retrieve_cve("openssl", "1.1.1")
        assert len(results) > 0

    def test_retrieve_changelog(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag.retrieve_changelog("flask", "2.0", "3.0")
        assert len(results) > 0

    def test_search_common_patterns(self):
        rag = DebugRAG(cache_path=tempfile.mktemp(suffix=".db"))
        results = rag._search_common_patterns("KeyError", "python")
        assert len(results) > 0
        assert results[0].relevance_score == 0.8


class TestPatchEngine:
    def test_create_patch(self):
        engine = PatchEngine()
        original = "print('hello')"
        fixed = "print('hello world')"
        patch = engine.create_patch("test.py", original, fixed)
        assert patch.file_path == "test.py"
        assert patch.diff != ""

    def test_create_diff_preview(self):
        engine = PatchEngine()
        patches = [
            engine.create_patch("a.py", "old", "new"),
        ]
        preview = engine.create_diff_preview(patches)
        assert preview != ""

    def test_diff_text_static(self):
        diff = PatchEngine.diff_text("a\nb\n", "a\nc\n", "test.txt")
        assert diff != ""

    def test_rollback(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("original")
            fname = f.name

        engine = PatchEngine(repo_path=os.path.dirname(fname))
        patch = engine.create_patch(fname, "original", "modified")
        ok, _ = engine.apply_patch(patch)
        assert ok

        with open(fname) as f:
            assert f.read() == "modified"

        ok = engine.rollback(patch)
        assert ok

        with open(fname) as f:
            assert f.read() == "original"

        os.unlink(fname)

    def test_apply_patch_set(self):
        engine = PatchEngine()
        patch = engine.create_patch("test.py", "old", "new")
        from code_debugger.patch_engine import PatchSet
        pset = PatchSet(patches=[patch])
        result = engine.apply_patch_set(pset, dry_run=True)
        assert result.success

    def test_git_commit_no_repo(self):
        engine = PatchEngine(repo_path="/tmp/nonexistent")
        sha = engine.git_commit([])
        assert sha is None


class TestTestGenerator:
    def test_generate_basic(self):
        gen = TestGenerator()
        code = """
def add(a, b):
    return a + b
"""
        suite = gen.generate_tests(code)
        assert len(suite.tests) > 0
        assert any("test_add_basic" in t.test_code for t in suite.tests)

    def test_generate_edge_cases(self):
        gen = TestGenerator()
        tests = gen.generate_edge_case_tests("process", ["data", "key"])
        assert len(tests) >= 2

    def test_generate_fuzz(self):
        gen = TestGenerator()
        test = gen.generate_fuzz_tests("func", ["x"])
        assert "fuzz" in test.test_type

    def test_generate_security_tests(self):
        gen = TestGenerator()
        tests = gen.generate_security_tests("run", ["command"])
        assert len(tests) > 0
        assert "injection" in tests[0].test_code

    def test_render_suite(self):
        gen = TestGenerator()
        code = "def foo(): pass"
        suite = gen.generate_tests(code)
        rendered = gen.render_suite(suite)
        assert "Auto-generated tests" in rendered

    def test_generate_regression_tests(self):
        gen = TestGenerator()
        suite = gen.generate_regression_tests("IndexError", "fixed_code", "original_code")
        assert len(suite.tests) >= 2


class TestExecutionSandbox:
    def test_detect_language(self):
        sandbox = ExecutionSandbox(use_docker=False)
        assert sandbox._detect_language("import os\nprint('hi')").value == "python"
        assert sandbox._detect_language("console.log('hello')").value == "javascript"
        assert sandbox._detect_language("SELECT * FROM users").value == "sql"
        assert sandbox._detect_language("fn main() { println! }").value == "rust"

    def test_detect_language_from_filename(self):
        sandbox = ExecutionSandbox(use_docker=False)
        lang = sandbox._detect_language("print(1)", "test.js")
        assert lang.value == "javascript"
        lang = sandbox._detect_language("print(1)", "test.rs")
        assert lang.value == "rust"
        lang = sandbox._detect_language("print(1)", "test.go")
        assert lang.value == "go"

    def test_local_execution(self):
        sandbox = ExecutionSandbox(use_docker=False)
        result = sandbox.execute("print('hello from sandbox')")
        assert result.stdout.strip() == "hello from sandbox"
        assert result.success

    def test_local_execution_error(self):
        sandbox = ExecutionSandbox(use_docker=False)
        result = sandbox.execute("x = 1/0")
        assert not result.success
        assert "division by zero" in (result.stderr + result.stdout)

    def test_local_execution_with_imports(self):
        sandbox = ExecutionSandbox(use_docker=False)
        result = sandbox.execute("import json\nprint(json.dumps({'a': 1}))")
        assert result.success
        assert '{"a": 1}' in result.stdout


class TestAgentModules:
    def test_stack_trace_agent_import(self):
        from code_debugger.agents import StackTraceAgent
        assert StackTraceAgent.name == "StackTraceAgent"

    def test_all_agents_importable(self):
        from code_debugger.agents import (
            StackTraceAgent, DependencyAgent, RuntimeAgent, DataFlowAgent,
            FixGenerationAgent, ValidationAgent, RegressionAgent,
            SecurityImpactAgent, PerformanceImpactAgent, RefactorAgent,
        )
        assert all([
            StackTraceAgent, DependencyAgent, RuntimeAgent, DataFlowAgent,
            FixGenerationAgent, ValidationAgent, RegressionAgent,
            SecurityImpactAgent, PerformanceImpactAgent, RefactorAgent,
        ])

    def test_agent_tools_have_schemas(self):
        from code_debugger.agents.stack_trace_agent import extract_traceback_info
        assert hasattr(extract_traceback_info, "name")
        assert hasattr(extract_traceback_info, "params_json_schema")
        assert "error_trace" in extract_traceback_info.params_json_schema["properties"]

    def test_runtime_agent_tools(self):
        from code_debugger.agents.runtime_agent import analyze_error_pattern
        assert hasattr(analyze_error_pattern, "name")
        assert analyze_error_pattern.name == "analyze_error_pattern"

    def test_security_scan_tool(self):
        from code_debugger.agents.security_impact_agent import scan_security_issues
        assert hasattr(scan_security_issues, "name")
        assert scan_security_issues.name == "scan_security_issues"

    def test_code_smell_tool(self):
        from code_debugger.agents.refactor_agent import detect_code_smells
        assert hasattr(detect_code_smells, "name")
        assert detect_code_smells.name == "detect_code_smells"

    def test_performance_analysis_tool(self):
        from code_debugger.agents.performance_impact_agent import (
            analyze_performance_patterns, estimate_fix_performance_impact
        )
        assert analyze_performance_patterns.name == "analyze_performance_patterns"
        assert estimate_fix_performance_impact.name == "estimate_fix_performance_impact"

    def test_v1_agents_still_importable(self):
        from code_debugger import DebugSleuth, SolutionArchitect, ReliabilityEngineer
        assert DebugSleuth.name == "DebugSleuth"
        assert SolutionArchitect.name == "SolutionArchitect"

    def test_data_flow_agent_tools(self):
        from code_debugger.agents.data_flow_agent import trace_variable_origin
        assert hasattr(trace_variable_origin, "params_json_schema")
        schema = trace_variable_origin.params_json_schema
        assert "file_path" in schema["properties"]
        assert "var_name" in schema["properties"]

    def test_fix_generation_agent_tools(self):
        from code_debugger.agents.fix_generation_agent import generate_safe_wrapper
        assert hasattr(generate_safe_wrapper, "name")
        assert generate_safe_wrapper.name == "generate_safe_wrapper"
        assert hasattr(generate_safe_wrapper, "params_json_schema")


class TestASTAnalyzer:
    def test_analyze_code(self):
        from code_debugger.code_intelligence import ASTAnalyzer
        analyzer = ASTAnalyzer()
        code = """
def greet(name: str) -> str:
    return f"Hello {name}"

class Person:
    def __init__(self, name):
        self.name = name
"""
        result = analyzer.analyze_code(code)
        assert "functions" in result
        assert "classes" in result
        assert len(result["functions"]) >= 1
        assert len(result["classes"]) == 1
        assert any(f["name"] == "greet" for f in result["functions"])

    def test_analyze_imports(self):
        from code_debugger.code_intelligence import ASTAnalyzer
        analyzer = ASTAnalyzer()
        code = "import os\nimport json\nfrom typing import List, Optional\n"
        result = analyzer.analyze_code(code)
        assert len(result["imports"]) >= 2

    def test_analyze_variables(self):
        from code_debugger.code_intelligence import ASTAnalyzer
        analyzer = ASTAnalyzer()
        code = "x = 10\nname = 'hello'\n"
        result = analyzer.analyze_code(code)
        assert len(result["variables"]) >= 2

    def test_analyze_issues(self):
        from code_debugger.code_intelligence import ASTAnalyzer
        analyzer = ASTAnalyzer()
        code = """
def a(): pass
def a(): pass  # duplicate
"""
        result = analyzer.analyze_code(code)
        assert len(result["issues"]) > 0


class TestOrchestratorV2:
    @pytest.mark.asyncio
    async def test_full_debugging_cycle(self):
        config = DebugSessionConfig(
            enable_sandbox=False,
            enable_rag=True,
            enable_observability=False,
            enable_autonomous_repair=False,
        )
        orch = DebuggingOrchestratorV2(
            config=config,
            db_path=tempfile.mktemp(suffix=".db"),
        )
        result = await orch.run_full_debugging_cycle({
            "error_trace": SAMPLE_ERROR,
            "failing_file": "example.py",
            "failing_line": 15,
            "codebase_path": ".",
        })
        assert result["success"] is True
        assert result["final_report"] != ""

    @pytest.mark.asyncio
    async def test_fast_enrichment(self):
        config = DebugSessionConfig(enable_rag=True)
        orch = DebuggingOrchestratorV2(config=config)
        enrichment = await orch._stage_1_fast_enrichment({
            "error_trace": SAMPLE_ERROR,
        })
        assert enrichment["error_type"] == "IndexError"
        assert "trace_info" in enrichment
        assert "pattern_hints" in enrichment

    def test_confidence_estimation(self):
        config = DebugSessionConfig()
        orch = DebuggingOrchestratorV2(config=config)
        score = orch._estimate_confidence(
            "try:\n    result = safe_get(items, index)\nexcept IndexError:\n    return None",
            "IndexError: list index out of range"
        )
        assert score > 0.5

    def test_detect_language_from_context(self):
        config = DebugSessionConfig()
        orch = DebuggingOrchestratorV2(config=config)
        lang = orch._detect_language_from_context({"failing_file": "test.py"})
        assert lang == "python"
        lang = orch._detect_language_from_context({"failing_file": "test.js"})
        assert lang == "javascript"
        lang = orch._detect_language_from_context({"failing_file": "test.rs"})
        assert lang == "rust"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
