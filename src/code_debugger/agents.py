"""
Multi-Agent Debugging System using OpenAI Agents SDK

Three specialized agents:
1. Debug Sleuth - Root Cause Analysis
2. Solution Architect - Fix Generation
3. Reliability Engineer - Validation & Documentation

Features:
- Session persistence with SQLite
- OpenAI Agents SDK integration
- Tool execution tracking
- Conversation history storage
- Gemini model support
"""

from typing import Dict, Any, Optional, List
from agents import Agent, Runner, function_tool, handoff
from .tools import (
    list_directory_structure,
    read_code_file,
    search_codebase,
    run_shell_command,
    analyze_python_code
)
from .session_manager import SessionManager
import os
import json
import time
import uuid
import google.genai as genai

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBgSpaU-oICNVMOtHmexiBNX4OVh_d3tG8')
GEMINI_BASE_URL = os.environ.get('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/openai/')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

def get_gemini_client():
    """Get configured Gemini client."""
    return genai.Client(api_key=GEMINI_API_KEY)


# =============================================================================
# Tool Definitions for OpenAI Agents SDK
# =============================================================================

@function_tool
def list_directory_tool(path: str = ".", max_depth: int = 3) -> Dict:
    """List the directory structure of the project."""
    return list_directory_structure(path, max_depth)


@function_tool
def read_code_file_tool(file_path: str, start_line: int = None, end_line: int = None) -> str:
    """Read the content of a code file with optional line range."""
    return read_code_file(file_path, start_line, end_line)


@function_tool
def search_codebase_tool(pattern: str, file_extensions: List[str] = None) -> List[Dict]:
    """Search for files containing a specific pattern."""
    if file_extensions is None:
        file_extensions = ['.py']
    return search_codebase(pattern, file_extensions, search_content=True)


@function_tool
def run_shell_command_tool(command: str, timeout: int = 30) -> Dict[str, str]:
    """Safely run a shell command (use with caution)."""
    return run_shell_command(command, timeout)


@function_tool
def analyze_python_code_tool(file_path: str) -> Dict:
    """Analyze Python code structure using AST."""
    return analyze_python_code(file_path)


# =============================================================================
# Debug Sleuth Agent - Root Cause Analysis
# =============================================================================

DEBUG_SLEUTH_INSTRUCTIONS = """
You are the Senior Debugging Sleuth. Your objective is to perform a Root Cause Analysis (RCA) on the provided error and codebase.

YOUR RESPONSIBILITIES:
1. Trace Analysis: Ingest the stack trace and identify the specific file, line number, and exception type.
2. Environment Check: Identify potential version conflicts or missing environment variables.
3. Heuristic Investigation: Use the read_code_file_tool to examine the failing line and the 10 lines of context around it.
4. Logical Deduction: Explain the 'State of the World' at the time of failure—what were the variables likely holding?
5. Handoff: Once you have a hypothesis, call handoff_to_fixer with a detailed summary of the bug.

GUARDRAILS:
- Do not propose code changes. Your output must focus entirely on the 'Why' of the failure.
- Be thorough in your analysis before handing off.
- Always examine the actual code context around the failing line.

OUTPUT FORMAT:
Provide your analysis in this structure:
- Exception Type: <type>
- Exception Message: <message>
- Failing Location: <file>:<line>
- Code Context: <surrounding code>
- State Analysis: <what variables likely contained>
- Root Cause: <your hypothesis>
- Confidence: <High/Medium/Low>
"""

DebugSleuth = Agent(
    name="DebugSleuth",
    instructions=DEBUG_SLEUTH_INSTRUCTIONS,
    tools=[
        list_directory_tool,
        read_code_file_tool,
        search_codebase_tool,
        run_shell_command_tool,
        analyze_python_code_tool
    ],
    model="gemini-2.0-flash"
)


# =============================================================================
# Solution Architect Agent - Fix Generation
# =============================================================================

SOLUTION_ARCHITECT_INSTRUCTIONS = """
You are the Lead Solution Architect. You receive a bug report from the Debug Sleuth and must engineer a permanent fix.

YOUR RESPONSIBILITIES:
1. Propose Fix: Write the corrected code block using industry best practices (DRY, SOLID principles).
2. Regression Prevention: Explain why this fix won't break other parts of the system.
3. Draft Tests: Provide a Python pytest or unittest snippet that would have caught this bug.
4. Handoff: Call handoff_to_validator to verify the fix.

GUARDRAILS:
- Always prefer robust error handling (try/except) over simple 'band-aid' fixes.
- Redact any sensitive credentials discovered in the code.
- Follow defensive programming practices.
- Ensure your fix handles edge cases.

OUTPUT FORMAT:
Provide your solution in this structure:
- Proposed Fix: <complete code block with the fix>
- Fix Explanation: <why this fix works>
- SOLID Principles Applied: <which principles you applied>
- Regression Analysis: <potential side effects and why they're mitigated>
- Test Snippet: <pytest code that would catch this bug>
- Implementation Plan: <step-by-step instructions>
"""

SolutionArchitect = Agent(
    name="SolutionArchitect",
    instructions=SOLUTION_ARCHITECT_INSTRUCTIONS,
    tools=[
        list_directory_tool,
        read_code_file_tool,
        search_codebase_tool,
        run_shell_command_tool,
        analyze_python_code_tool
    ],
    model="gemini-2.0-flash"
)


# =============================================================================
# Reliability Engineer Agent - Validation & Documentation
# =============================================================================

RELIABILITY_ENGINEER_INSTRUCTIONS = """
You are the Site Reliability Engineer (SRE). Your task is the final validation of the proposed fix.

YOUR RESPONSIBILITIES:
1. Sanity Check: Review the Architect's fix for 'Code Smells' or performance bottlenecks.
2. Complexity Analysis: Briefly note the Big O complexity change (if any).
3. Security Review: Check for security issues (hardcoded credentials, injection risks, etc.).
4. Final Report: Present the user with a clean Markdown report.

GUARDRAILS:
- If the fix looks unsafe or incomplete, hand it back to the Architect with a critique.
- Be strict about code quality and security.
- Ensure tests are comprehensive.

OUTPUT FORMAT:
Provide your validation in this structure:
- Sanity Check Results: <code smells found or "Clean">
- Complexity Analysis: <time/space complexity>
- Security Review: <security issues or "Secure">
- Validation Status: <PASS/FAIL with reasons>
- Final Report: <complete markdown report below>

FINAL REPORT FORMAT:
```markdown
# 🔍 Debug Analysis Report

## 📋 Root Cause Summary
<Summary from Debug Sleuth>

## 🛠️ The Fix
<Code block from Solution Architect>

## ✅ Verification Steps
<How to run the suggested tests>

## 📊 Quality Analysis
| Metric | Status |
|--------|--------|
| Code Quality | <score>/100 |
| Security | <status> |
| Complexity | <O notation> |

## 📝 Implementation Plan
<Steps to apply the fix>

## 🚨 Recommendations
<Any recommendations>
```
"""

ReliabilityEngineer = Agent(
    name="ReliabilityEngineer",
    instructions=RELIABILITY_ENGINEER_INSTRUCTIONS,
    tools=[
        list_directory_tool,
        read_code_file_tool,
        search_codebase_tool,
        run_shell_command_tool,
        analyze_python_code_tool
    ],
    model="gemini-2.0-flash"
)


# =============================================================================
# Handoff Functions
# =============================================================================

def handoff_to_fixer(bug_analysis: str) -> str:
    """Handoff from Debug Sleuth to Solution Architect with bug analysis."""
    return f"HANDOFF_TO_FIXER: {bug_analysis}"


def handoff_to_validator(fix_proposal: str) -> str:
    """Handoff from Solution Architect to Reliability Engineer with fix proposal."""
    return f"HANDOFF_TO_VALIDATOR: {fix_proposal}"


def handoff_back_to_architect(critique: str) -> str:
    """Handoff from Reliability Engineer back to Solution Architect for revision."""
    return f"HANDOFF_BACK_TO_ARCHITECT: {critique}"


# =============================================================================
# Orchestrator Class for Multi-Agent Workflow
# =============================================================================

class DebuggingOrchestrator:
    """
    Orchestrates the three-agent debugging workflow using OpenAI Agents SDK.
    
    Manages the handoff process between:
    1. Debug Sleuth → Solution Architect → Reliability Engineer
    """
    
    def __init__(self, model: str = "gpt-4o", db_path: str = "debug_sessions.db"):
        self.model = model
        self.db_path = db_path
        self.session_history: List[Dict[str, Any]] = []
        self.session_manager = SessionManager(db_path)
        
    async def run_debug_sleuth(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Debug Sleuth agent for root cause analysis.
        
        Args:
            error_context: Dictionary with error_trace, failing_file, failing_line, etc.
            
        Returns:
            Root cause analysis results
        """
        prompt = self._build_sleuth_prompt(error_context)
        
        result = await Runner.run(DebugSleuth, prompt)
        
        analysis = {
            'agent': 'DebugSleuth',
            'final_output': result.final_output,
            'input': error_context
        }
        
        self.session_history.append(analysis)
        return analysis
    
    async def run_solution_architect(self, bug_report: str) -> Dict[str, Any]:
        """
        Run the Solution Architect agent for fix generation.
        
        Args:
            bug_report: Bug analysis from Debug Sleuth
            
        Returns:
            Fix proposal with tests
        """
        prompt = self._build_architect_prompt(bug_report)
        
        result = await Runner.run(SolutionArchitect, prompt)
        
        fix_proposal = {
            'agent': 'SolutionArchitect',
            'final_output': result.final_output,
            'input': bug_report
        }
        
        self.session_history.append(fix_proposal)
        return fix_proposal
    
    async def run_reliability_engineer(self, fix_proposal: str, 
                                        bug_report: str) -> Dict[str, Any]:
        """
        Run the Reliability Engineer agent for validation.
        
        Args:
            fix_proposal: Fix from Solution Architect
            bug_report: Original bug report
            
        Returns:
            Validation results and final report
        """
        prompt = self._build_validator_prompt(fix_proposal, bug_report)
        
        result = await Runner.run(ReliabilityEngineer, prompt)
        
        validation = {
            'agent': 'ReliabilityEngineer',
            'final_output': result.final_output,
            'validation_passed': 'PASS' in result.final_output.upper() or 'VALIDATION STATUS: PASS' in result.final_output.upper()
        }
        
        self.session_history.append(validation)
        return validation
    
    async def run_full_debugging_cycle(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete three-agent debugging cycle.
        
        Args:
            error_context: Dictionary containing error information
            
        Returns:
            Complete debugging report
        """
        print("🔍 Debug Sleuth: Performing root cause analysis...")
        sleuth_result = await self.run_debug_sleuth(error_context)
        
        print("🔧 Solution Architect: Creating a fix...")
        architect_result = await self.run_solution_architect(sleuth_result['final_output'])
        
        print("✅ Reliability Engineer: Validating the fix...")
        validator_result = await self.run_reliability_engineer(
            architect_result['final_output'],
            sleuth_result['final_output']
        )
        
        print("🎉 Debugging cycle completed!")
        
        return {
            'session_history': self.session_history,
            'root_cause_analysis': sleuth_result,
            'solution_architecture': architect_result,
            'reliability_validation': validator_result,
            'final_report': validator_result['final_output'],
            'validation_passed': validator_result['validation_passed']
        }
    
    def _build_sleuth_prompt(self, error_context: Dict[str, Any]) -> str:
        """Build the prompt for Debug Sleuth."""
        error_trace = error_context.get('error_trace', 'No error trace provided')
        failing_file = error_context.get('failing_file', '')
        failing_line = error_context.get('failing_line', None)
        codebase_path = error_context.get('codebase_path', '.')
        
        prompt = f"""
Analyze the following error and perform root cause analysis:

ERROR TRACE:
{error_trace}

FAILING FILE: {failing_file}
FAILING LINE: {failing_line}
CODEBASE PATH: {codebase_path}

ADDITIONAL CONTEXT:
{json.dumps({k: v for k, v in error_context.items() 
              if k not in ['error_trace', 'failing_file', 'failing_line', 'codebase_path']}, 
             indent=2)}

Please perform a thorough root cause analysis following your instructions.
"""
        return prompt
    
    def _build_architect_prompt(self, bug_report: str) -> str:
        """Build the prompt for Solution Architect."""
        return f"""
Based on the following bug analysis from the Debug Sleuth, create a comprehensive fix:

BUG REPORT FROM DEBUG SLEUTH:
{bug_report}

Please engineer a permanent fix following best practices (DRY, SOLID, defensive programming).
Include tests and an implementation plan.
"""
    
    def _build_validator_prompt(self, fix_proposal: str, bug_report: str) -> str:
        """Build the prompt for Reliability Engineer."""
        return f"""
Validate the following fix proposal from the Solution Architect:

ORIGINAL BUG REPORT:
{bug_report}

PROPOSED FIX:
{fix_proposal}

Please perform a thorough validation including sanity checks, complexity analysis, and security review.
Provide a final markdown report.
"""
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current debugging session."""
        return {
            'total_agents_run': len(self.session_history),
            'agents': [item['agent'] for item in self.session_history],
            'history': self.session_history
        }
    
    def clear_session(self):
        """Clear the current session history."""
        self.session_history = []


# =============================================================================
# Synchronous Wrapper for Convenience
# =============================================================================

import asyncio


def run_async(coro):
    """Helper to run async functions in synchronous context."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, we need to create a new thread
            # or use asyncio.run_coroutine_threadsafe, but for simplicity,
            # we'll create a new event loop in a separate thread
            import concurrent.futures
            import threading
            
            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                return future.result()
        else:
            # Loop exists but is not running, safe to use run_until_complete
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


class SyncDebuggingOrchestrator(DebuggingOrchestrator):
    """Synchronous wrapper for the DebuggingOrchestrator."""
    
    def run_debug_sleuth(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        return run_async(super().run_debug_sleuth(error_context))
    
    def run_solution_architect(self, bug_report: str) -> Dict[str, Any]:
        return run_async(super().run_solution_architect(bug_report))
    
    def run_reliability_engineer(self, fix_proposal: str, bug_report: str) -> Dict[str, Any]:
        return run_async(super().run_reliability_engineer(fix_proposal, bug_report))
    
    def run_full_debugging_cycle(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        return run_async(super().run_full_debugging_cycle(error_context))
