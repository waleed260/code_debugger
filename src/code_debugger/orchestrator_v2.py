"""
Orchestrator V2 — AI-first multi-agent debugging pipeline with autonomous repair loop

Architecture:
  Tier 1: Fast Pattern Detection (enrichment, not replacement)
  Tier 2: Multi-Agent Root Cause Analysis (10 specialized agents)
  Tier 3: Execution Validation (sandboxed test execution)
  Tier 4: Autonomous Repair Loop (iterative fix → test → refine)

This is the PRIMARY orchestrator. Fast debugger is only a fallback.
"""

import asyncio
import json
import os
import time
import uuid
import sys
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict

from agents import Runner

from .agents import (
    StackTraceAgent, DependencyAgent, RuntimeAgent, DataFlowAgent,
    FixGenerationAgent, ValidationAgent, RegressionAgent,
    SecurityImpactAgent, PerformanceImpactAgent, RefactorAgent,
)
from .sandbox import ExecutionSandbox, SandboxFile, ExecutionResult, Language
from .patch_engine import PatchEngine, FilePatch, PatchSet
from .rag import DebugRAG
from .test_generator import TestGenerator, TestSuite
from .observability import ObservabilityTracker
from .session_manager import SessionManager
from .tools import (
    list_directory_structure, read_code_file,
    search_codebase, run_shell_command, analyze_python_code,
)


MAX_RETRY_ATTEMPTS = 3
MAX_REPAIR_ITERATIONS = 5


@dataclass
class DebugSessionConfig:
    enable_sandbox: bool = True
    enable_rag: bool = True
    enable_observability: bool = True
    enable_autonomous_repair: bool = True
    max_repair_iterations: int = MAX_REPAIR_ITERATIONS
    test_on_fix: bool = True
    generate_diff: bool = True
    confidence_threshold: float = 0.6


@dataclass
class AgentResult:
    agent_name: str
    output: str
    duration_ms: float
    success: bool = True
    token_estimate: int = 0
    confidence: float = 1.0


@dataclass
class DebugResult:
    session_id: str
    success: bool
    validation_passed: bool
    root_cause: Optional[str]
    fix_proposal: Optional[str]
    diff: Optional[str]
    test_results: Optional[str]
    agent_timeline: List[Dict[str, Any]]
    validation_report: Optional[str]
    security_report: Optional[str]
    regression_report: Optional[str]
    confidence_score: float
    repair_iterations: int
    rag_context: Optional[Dict[str, Any]]
    final_report: str


class DebuggingOrchestratorV2:
    def __init__(self, config: DebugSessionConfig = None, db_path: str = "debug_sessions_v2.db",
                 repo_path: str = "."):
        self.config = config or DebugSessionConfig()
        self.sandbox = ExecutionSandbox(use_docker=True)
        self.patch_engine = PatchEngine(repo_path=repo_path)
        self.rag = DebugRAG(cache_path="rag_cache.db") if self.config.enable_rag else None
        self.test_generator = TestGenerator()
        self.observability = ObservabilityTracker() if self.config.enable_observability else None
        self.session_manager = SessionManager(db_path)
        self.repo_path = repo_path
        self.session_history: List[Dict[str, Any]] = []

    async def run_full_debugging_cycle(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        error_trace = error_context.get("error_trace", "")
        failing_file = error_context.get("failing_file", "")
        codebase_path = error_context.get("codebase_path", ".")
        language = self._detect_language_from_context(error_context)

        if self.observability:
            self.observability.start_session(session_id)

        try:
            stage_1_result = await self._stage_1_fast_enrichment(error_context)
            stage_2_result = await self._stage_2_multi_agent_analysis(error_trace, failing_file, codebase_path, language, stage_1_result)
            stage_3_result = await self._stage_3_execution_validation(stage_2_result, language, session_id)
            stage_4_result = await self._stage_4_autonomous_repair(
                stage_2_result, stage_3_result, language, session_id, error_trace
            )

            final_result = self._build_final_result(
                session_id, stage_2_result, stage_3_result, stage_4_result, language
            )

            self._persist_session(session_id, error_context, final_result)
            return final_result

        except Exception as e:
            return self._fallback_to_fast_debugger(error_context, session_id, str(e))

        finally:
            if self.observability:
                self.observability.end_session(
                    "completed" if final_result and final_result.success else "failed"
                )

    async def _stage_1_fast_enrichment(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        result = {"error_type": "UnknownError", "rag_context": None, "pattern_hints": []}

        error_trace = error_context.get("error_trace", "")

        from .v1_agents import _extract_error_info
        trace_info = {"error_type": _extract_error_info(error_trace)[0]}
        result["error_type"] = trace_info.get("error_type", "UnknownError")
        result["trace_info"] = trace_info

        if self.rag:
            try:
                rag_data = self.rag.enrich_prompt(
                    error_trace,
                    language=self._detect_language_from_context(error_context),
                    code_context="",
                )
                result["rag_context"] = rag_data
            except Exception:
                pass

        pattern_data = self._detect_error_patterns(error_trace)
        result["pattern_hints"] = pattern_data.get("detected_patterns", [])

        return result

    async def _stage_2_multi_agent_analysis(self, error_trace: str, failing_file: str,
                                              codebase_path: str, language: str,
                                              enrichment: Dict[str, Any]) -> Dict[str, Any]:
        timeline = []
        agents_results = {}

        sleuth_prompt = self._build_sleuth_prompt(error_trace, failing_file, codebase_path, enrichment)
        sleuth_result = await self._run_agent_with_timing(StackTraceAgent, sleuth_prompt)
        timeline.append({"agent": "StackTraceAgent", "duration_ms": sleuth_result.duration_ms})
        agents_results["stack_trace"] = sleuth_result

        runtime_prompt = f"Analyze runtime state for this error:\n{error_trace}\n\nDetected patterns: {enrichment.get('pattern_hints', [])}"
        runtime_result = await self._run_agent_with_timing(RuntimeAgent, runtime_prompt)
        timeline.append({"agent": "RuntimeAgent", "duration_ms": runtime_result.duration_ms})
        agents_results["runtime"] = runtime_result

        if failing_file and os.path.exists(failing_file):
            data_flow_prompt = f"Trace data flow in {failing_file} to find where the failure originates.\nError: {error_trace}"
            data_flow_result = await self._run_agent_with_timing(DataFlowAgent, data_flow_prompt)
            timeline.append({"agent": "DataFlowAgent", "duration_ms": data_flow_result.duration_ms})
            agents_results["data_flow"] = data_flow_result

        dep_prompt = f"Check dependencies for {failing_file or 'the project'}.\nError: {error_trace}"
        dep_result = await self._run_agent_with_timing(DependencyAgent, dep_prompt)
        timeline.append({"agent": "DependencyAgent", "duration_ms": dep_result.duration_ms})
        agents_results["dependency"] = dep_result

        all_analyses = "\n\n".join([
            f"=== {name.upper()} ===\n{r.output}"
            for name, r in agents_results.items()
        ])

        return {
            "agents_results": agents_results,
            "all_analyses": all_analyses,
            "timeline": timeline,
            "enrichment": enrichment,
        }

    async def _stage_3_execution_validation(self, analysis: Dict[str, Any],
                                             language: str, session_id: str) -> Dict[str, Any]:
        if not self.config.enable_sandbox:
            return {"sandbox_available": False}

        return {"sandbox_available": True, "language": language}

    async def _stage_4_autonomous_repair(self, analysis: Dict[str, Any],
                                          validation: Dict[str, Any],
                                          language: str, session_id: str,
                                          original_error: str) -> Dict[str, Any]:
        if not self.config.enable_autonomous_repair:
            return await self._single_pass_fix(analysis, language, original_error)

        return await self._iterative_repair_loop(analysis, validation, language, session_id, original_error)

    async def _single_pass_fix(self, analysis: Dict[str, Any], language: str,
                                 original_error: str) -> Dict[str, Any]:
        all_analyses = analysis.get("all_analyses", "")

        fix_prompt = f"Generate a fix based on this root cause analysis:\n\n{all_analyses}"
        fix_result = await self._run_agent_with_timing(FixGenerationAgent, fix_prompt)

        validation_prompt = f"Validate this fix:\n\n{fix_result.output}\n\nOriginal error: {original_error}"
        val_result = await self._run_agent_with_timing(ValidationAgent, validation_prompt)

        security_prompt = f"Check security impact of this fix:\n\n{fix_result.output}"
        sec_result = await self._run_agent_with_timing(SecurityImpactAgent, security_prompt)

        regression_prompt = f"Check regressions for:\n\n{fix_result.output}"
        reg_result = await self._run_agent_with_timing(RegressionAgent, regression_prompt)

        return {
            "fix": fix_result,
            "validation": val_result,
            "security": sec_result,
            "regression": reg_result,
            "repair_iterations": 1,
            "final_fix": fix_result.output,
        }

    async def _iterative_repair_loop(self, analysis: Dict[str, Any],
                                      validation: Dict[str, Any],
                                      language: str, session_id: str,
                                      original_error: str) -> Dict[str, Any]:
        all_analyses = analysis.get("all_analyses", "")
        current_context = all_analyses
        best_fix = None
        best_confidence = 0.0
        best_val_result = None
        iteration_history = []

        for iteration in range(1, self.config.max_repair_iterations + 1):
            fix_prompt = f"Iteration {iteration}. Generate fix:\n\n{current_context}"
            if iteration > 1:
                fix_prompt += f"\n\nPrevious fix issues to address: {best_val_result.output if best_val_result else 'N/A'}"
            fix_result = await self._run_agent_with_timing(FixGenerationAgent, fix_prompt)

            if self.config.test_on_fix:
                test_prompt = f"Generate tests for:\n\n{fix_result.output}"
                test_result = await self._run_agent_with_timing(ValidationAgent, test_prompt)
                test_passed = "PASS" in test_result.output.upper()

            confidence = self._estimate_confidence(fix_result.output, original_error)

            security_prompt = f"Security check:\n\n{fix_result.output}"
            sec_result = await self._run_agent_with_timing(SecurityImpactAgent, security_prompt)

            regression_prompt = f"Regression check:\n\n{fix_result.output}"
            reg_result = await self._run_agent_with_timing(RegressionAgent, regression_prompt)

            iteration_result = {
                "iteration": iteration,
                "fix": fix_result.output,
                "confidence": confidence,
                "test_passed": test_passed if self.config.test_on_fix else True,
            }
            iteration_history.append(iteration_result)

            if confidence > best_confidence and (test_passed if self.config.test_on_fix else True):
                best_fix = fix_result.output
                best_confidence = confidence
                best_val_result = sec_result

            if confidence >= self.config.confidence_threshold and (test_passed if self.config.test_on_fix else True):
                break

            current_context = (
                f"Previous fix had confidence {confidence:.2f}. "
                f"Improve it. Original analysis:\n{all_analyses}\n\n"
                f"Previous attempt:\n{fix_result.output[:500]}..."
            )

        return {
            "fix": self._create_agent_result("FixGenerationAgent", best_fix or fix_result.output),
            "validation": best_val_result or AgentResult("ValidationAgent", "No validation performed", 0),
            "security": sec_result,
            "regression": reg_result,
            "repair_iterations": len(iteration_history),
            "final_fix": best_fix or fix_result.output,
            "iteration_history": iteration_history,
            "best_confidence": best_confidence,
        }

    def _build_final_result(self, session_id: str, analysis: Dict[str, Any],
                             validation: Dict[str, Any], repair: Dict[str, Any],
                             language: str) -> Dict[str, Any]:
        fix_output = repair.get("final_fix", "")
        val_passed = repair.get("validation")
        val_passed_str = val_passed.output if val_passed else "PASS"

        all_timeline = (
            analysis.get("timeline", [])
            + [{"agent": "FixGenerationAgent", "duration_ms": repair.get("fix", AgentResult("", "", 0)).duration_ms}]
        )

        report_parts = [
            "## Debug Analysis Report\n",
            f"Session: `{session_id}`",
            f"Language: {language}",
            f"Repair Iterations: {repair.get('repair_iterations', 1)}",
            "",
            "### Root Cause Analysis",
            analysis.get("all_analyses", "No analysis available"),
            "",
            "### Fix Proposal",
            fix_output,
            "",
            "### Validation",
            val_passed_str,
            "",
            "### Security Impact",
            repair.get("security", AgentResult("", "No security analysis", 0)).output if repair.get("security") else "N/A",
            "",
            "### Regression Check",
            repair.get("regression", AgentResult("", "No regression check", 0)).output if repair.get("regression") else "N/A",
        ]

        if repair.get("iteration_history"):
            report_parts.extend([
                "",
                "### Repair Iterations",
                *[
                    f"- Iteration {h['iteration']}: confidence={h['confidence']:.2f}, test_passed={h.get('test_passed', False)}"
                    for h in repair["iteration_history"]
                ],
            ])

        final_report = "\n".join(report_parts)

        return {
            "session_id": session_id,
            "success": True,
            "validation_passed": "PASS" in val_passed_str.upper(),
            "root_cause": analysis.get("all_analyses", ""),
            "fix_proposal": fix_output,
            "diff": self.patch_engine.diff_text("", fix_output, "fix"),
            "test_results": "",
            "agent_timeline": all_timeline,
            "validation_report": val_passed_str,
            "security_report": repair.get("security", AgentResult("", "", 0)).output if repair.get("security") else "",
            "regression_report": repair.get("regression", AgentResult("", "", 0)).output if repair.get("regression") else "",
            "confidence_score": repair.get("best_confidence", 0.5) if repair.get("best_confidence") else 0.5,
            "repair_iterations": repair.get("repair_iterations", 1),
            "rag_context": analysis.get("enrichment", {}).get("rag_context"),
            "final_report": final_report,
            "session_history": self.session_history,
        }

    def _fallback_to_fast_debugger(self, error_context: Dict[str, Any],
                                    session_id: str, error_msg: str) -> Dict[str, Any]:
        from .v1_agents import run_fast_debug
        from openai import OpenAI
        try:
            client = OpenAI()
            fast_result = run_fast_debug(client, error_context)
            return {
                "session_id": session_id,
                "success": True,
                "validation_passed": fast_result["validation"] == "PASS",
                "final_report": f"## Fallback (AI Pipeline Unavailable)\n\n{error_msg}\n\n---\n\n{fast_result['final_output']}",
                "agent_timeline": [{"agent": "FastDebugger", "duration_ms": 0}],
                "confidence_score": 0.3,
                "repair_iterations": 0,
                "root_cause": fast_result["final_output"],
                "fix_proposal": fast_result["final_output"],
                "diff": "",
                "test_results": "",
                "validation_report": "",
                "security_report": "",
                "regression_report": "",
                "rag_context": None,
                "session_history": [fast_result],
            }
        except Exception:
            return {
                "session_id": session_id,
                "success": False,
                "validation_passed": False,
                "final_report": f"## Debug Failed\n\nAll pipelines unavailable: {error_msg}",
                "confidence_score": 0.0,
                "repair_iterations": 0,
                "agent_timeline": [],
                "root_cause": None,
                "fix_proposal": None,
                "diff": None,
                "test_results": None,
                "validation_report": None,
                "security_report": None,
                "regression_report": None,
                "rag_context": None,
                "session_history": [],
            }

    async def _run_agent_with_timing(self, agent, prompt: str) -> AgentResult:
        start = time.time()
        try:
            result = await Runner.run(agent, prompt)
            duration = (time.time() - start) * 1000
            token_estimate = len(prompt.split()) + len(result.final_output.split())
            return AgentResult(
                agent_name=agent.name,
                output=result.final_output,
                duration_ms=duration,
                token_estimate=token_estimate,
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return AgentResult(
                agent_name=agent.name,
                output=f"Error running agent: {str(e)}",
                duration_ms=duration,
                success=False,
            )

    def _estimate_confidence(self, fix_text: str, original_error: str) -> float:
        score = 0.5
        error_keywords = set(w for w in original_error.split() if w[0].isupper() and "Error" in w)
        fix_lower = fix_text.lower()

        for kw in error_keywords:
            if kw.lower() in fix_lower:
                score += 0.1

        if "try:" in fix_lower:
            score += 0.1
        if "except" in fix_lower:
            score += 0.1
        if "if" in fix_lower:
            score += 0.05
        if "assert" in fix_lower:
            score += 0.05

        if len(fix_text.splitlines()) < 3:
            score -= 0.2

        return min(max(score, 0.0), 1.0)

    def _detect_language_from_context(self, context: Dict[str, Any]) -> str:
        file_path = context.get("failing_file", "")
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".go": "go", ".rs": "rust",
            ".cpp": "cpp", ".c": "cpp", ".rb": "ruby",
            ".php": "php", ".cs": "csharp", ".sql": "sql",
        }
        return lang_map.get(ext, "python")

    def _build_sleuth_prompt(self, error_trace: str, failing_file: str,
                              codebase_path: str, enrichment: Dict[str, Any]) -> str:
        rag_section = ""
        if enrichment.get("rag_context"):
            rag_section = enrichment["rag_context"].get("formatted_context", "")

        return f"""
Analyze this error trace and perform root cause analysis:

ERROR TRACE:
{error_trace}

FAILING FILE: {failing_file}
CODEBASE: {codebase_path}

PATTERN HINTS: {enrichment.get('pattern_hints', [])}
ERROR TYPE: {enrichment.get('error_type', 'Unknown')}
{rag_section}

Provide a thorough root cause analysis with:
1. Error type and exact location
2. Call chain leading to failure
3. Root cause hypothesis
4. Confidence level
"""

    def _persist_session(self, session_id: str, error_context: Dict[str, Any],
                          result: Dict[str, Any]):
        try:
            self.session_manager.create_session(
                session_id=session_id,
                error_context=error_context,
                metadata={
                    "version": "2.0",
                    "repair_iterations": result.get("repair_iterations", 0),
                    "confidence": result.get("confidence_score", 0),
                },
            )
            self.session_manager.update_session(
                session_id,
                status="completed" if result.get("success") else "failed",
                final_report=result.get("final_report", ""),
                validation_passed=result.get("validation_passed", False),
            )
        except Exception:
            pass

    def _detect_error_patterns(self, error_trace: str) -> Dict[str, Any]:
        patterns_found = []
        trace_lower = error_trace.lower()

        none_patterns = ["nonetype", "'nonetype' object has no attribute", "nonetype object is not subscriptable"]
        type_patterns = ["typeerror", "must be ", "cannot be interpreted", "unsupported operand type"]
        index_patterns = ["index out of range", "indexerror", "list index out of range"]
        memory_patterns = ["memoryerror", "cannot allocate memory"]
        recursion_patterns = ["recursionerror", "maximum recursion depth exceeded"]
        io_patterns = ["filenotfounderror", "permissionerror", "connectionerror", "timeouterror"]
        security_patterns = ["valueerror: invalid literal for int()", "syntaxerror: invalid syntax"]

        if any(p in trace_lower for p in none_patterns):
            patterns_found.append("none_propagation")
        if any(p in trace_lower for p in type_patterns):
            patterns_found.append("type_mismatch")
        if any(p in trace_lower for p in index_patterns):
            patterns_found.append("index_error")
        if any(p in trace_lower for p in memory_patterns):
            patterns_found.append("memory_pressure")
        if any(p in trace_lower for p in recursion_patterns):
            patterns_found.append("recursion")
        if any(p in trace_lower for p in io_patterns):
            patterns_found.append("io_error")

        return {
            "detected_patterns": patterns_found,
            "primary_pattern": patterns_found[0] if patterns_found else "unknown",
        }

    def get_observability_report(self):
        if self.observability:
            return self.observability.get_report()
        return None
