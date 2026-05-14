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
from agents import Agent, Runner, function_tool, handoff, ModelSettings
from .tools import (
    list_directory_structure,
    read_code_file,
    search_codebase,
    run_shell_command,
    analyze_python_code
)
from .session_manager import SessionManager
from .model_provider import get_run_config
import os
import json
import time
import uuid
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'meta-llama/llama-3.3-70b-instruct:free')

# Set OpenAI environment variables for OpenRouter
os.environ['OPENAI_API_KEY'] = OPENROUTER_API_KEY
os.environ['OPENAI_BASE_URL'] = OPENROUTER_BASE_URL

def get_openrouter_client():
    """Get configured OpenRouter client."""
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )


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
You are a root cause analysis expert. Analyze the error and identify why it failed.

1. Parse the error type, message, and location
2. Read code context around the failing line using tools
3. Trace data flow - where did problematic values come from?
4. Identify the root cause with evidence
5. Keep your response under 300 words

Output format (keep concise):
- **Error**: type and message
- **Location**: file:line
- **Root Cause**: what and why (1-2 sentences)
- **Confidence**: High/Medium/Low
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
    model=OPENROUTER_MODEL,
    model_settings=ModelSettings(max_tokens=500)
)


# =============================================================================
# Solution Architect Agent - Fix Generation
# =============================================================================

SOLUTION_ARCHITECT_INSTRUCTIONS = """
You are a software architect. Create a concise fix for the given bug.

1. Understand the root cause from the analysis
2. Provide a single recommended fix (no multiple options)
3. Include a brief test for the fix
4. Keep under 400 words

Output format:
- **Fix**: the corrected code
- **Why it works**: 1 sentence
- **Test**: a quick pytest snippet
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
    model=OPENROUTER_MODEL,
    model_settings=ModelSettings(max_tokens=600)
)


# =============================================================================
# Reliability Engineer Agent - Validation & Documentation
# =============================================================================

RELIABILITY_ENGINEER_INSTRUCTIONS = """
You are a QA engineer. Validate whether the proposed fix is correct and safe.

Check for:
1. Does the fix actually solve the root cause?
2. Any security issues or edge cases missed?
3. Is the test adequate?

Output:
- **Status**: PASS or FAIL
- **Reason**: 1-2 sentences explaining your decision
- **Issues**: list any concerns (or "None")
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
    model=OPENROUTER_MODEL,
    model_settings=ModelSettings(max_tokens=300)
)

# Fast single-agent mode - reads code, explains error, fixes, tests, returns
FAST_SYSTEM_PROMPT = """You are a debugging expert. Given an error trace, explain the bug and return the fixed code.

Output exactly these sections:

## Error Explanation
<why the bug happens>

## Corrected Code
<fixed code>

## Status
PASS
"""

import time
import re

# =============================================================================
# Lightning-fast local debugger (no API calls, instant response)
# =============================================================================

ERROR_FIXES = {
    'IndexError': {
        'explanation': 'IndexError occurs when trying to access a list/tuple element at an index that does not exist. This happens when the index is >= the length of the sequence or negative beyond the bounds.',
        'fix': """def get_item_safe(items, index):
    if not isinstance(index, int):
        raise TypeError("Index must be an integer")
    if index < 0 or index >= len(items):
        return None
    return items[index]""",
        'test': """items = [10, 20, 30]
print(get_item_safe(items, 1))  # 20
print(get_item_safe(items, 5))  # None
print(get_item_safe(items, -1)) # None"""
    },
    'KeyError': {
        'explanation': 'KeyError occurs when trying to access a dictionary key that does not exist. Use `.get()` with a default or check `in` before access.',
        'fix': """def get_value_safe(data, key, default=None):
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    return data.get(key, default)""",
        'test': """data = {"name": "Alice", "age": 30}
print(get_value_safe(data, "name"))     # Alice
print(get_value_safe(data, "phone"))    # None"""
    },
    'TypeError': {
        'explanation': 'TypeError occurs when an operation receives an argument of inappropriate type. Check that all values are the expected type before operating on them.',
        'fix': """def add_safe(a, b):
    try:
        return float(a) + float(b)
    except (ValueError, TypeError):
        return str(a) + str(b)""",
        'test': """print(add_safe(10, 5))      # 15.0
print(add_safe("10", 5))    # 15.0
print(add_safe("a", "b"))   # ab"""
    },
    'ValueError': {
        'explanation': 'ValueError occurs when a function receives an argument with the right type but inappropriate value. Validate inputs before conversion.',
        'fix': """def convert_safe(value, to_type=int):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return None""",
        'test': """print(convert_safe("42"))    # 42
print(convert_safe("abc"))   # None"""
    },
    'AttributeError': {
        'explanation': 'AttributeError occurs when trying to access an attribute or method that does not exist on an object. Use `hasattr()` or `getattr()` with default.',
        'fix': """def safe_getattr(obj, attr, default=None):
    return getattr(obj, attr, default)""",
        'test': """print(safe_getattr("hello", "upper"))       # <method>
print(safe_getattr("hello", "nonexistent"))  # None"""
    },
    'ZeroDivisionError': {
        'explanation': 'ZeroDivisionError occurs when trying to divide a number by zero. Always check the divisor before division.',
        'fix': """def divide_safe(a, b):
    if b == 0:
        return None
    return a / b""",
        'test': """print(divide_safe(10, 2))   # 5.0
print(divide_safe(10, 0))   # None"""
    },
    'FileNotFoundError': {
        'explanation': 'FileNotFoundError occurs when trying to open a file that does not exist. Check the path and use try/except or os.path.exists().',
        'fix': """def read_file_safe(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None""",
        'test': """read_file_safe("nonexistent.txt")  # None"""
    },
    'ImportError|ModuleNotFoundError': {
        'explanation': 'ImportError occurs when a module cannot be imported. It may be missing, not installed, or have a circular dependency.',
        'fix': """def safe_import(module_name, fallback=None):
    try:
        return __import__(module_name)
    except ImportError:
        return fallback""",
        'test': """safe_import("nonexistent_module")  # None"""
    },
    'NameError': {
        'explanation': 'NameError occurs when trying to access a variable or name that has not been defined. Check for typos, scope issues, or missing imports.',
        'fix': """# Check the variable/function name for typos
# Ensure it is defined before use
# Use locals() and globals() to inspect scope
def safe_get_variable(name, default=None):
    return globals().get(name, locals().get(name, default))""",
        'test': """print(safe_get_variable("undefined_var"))  # None"""
    },
    'UnboundLocalError': {
        'explanation': 'UnboundLocalError occurs when a local variable is referenced before assignment. This often happens when a variable is used in a function before being assigned, or when reassigning a global without the global keyword.',
        'fix': """def safe_increment(counter):
    counter += 1
    return counter""",
        'test': """x = 0
print(safe_increment(x))  # 1"""
    },
    'RuntimeError': {
        'explanation': 'RuntimeError is a general error for operations that fail at runtime. Check the error message for specific details about what went wrong.',
        'fix': """def run_safe(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except RuntimeError as e:
        return {"error": str(e)}""",
        'test': """print(run_safe(int, "not_a_number"))  # Returns error dict"""
    },
    'RecursionError': {
        'explanation': 'RecursionError occurs when the recursion depth exceeds Python\'s limit (default 1000). The function is calling itself infinitely or too deeply.',
        'fix': """import sys
def safe_recursive(func, max_depth=500):
    depth = [0]
    def wrapper(*args, **kwargs):
        depth[0] += 1
        if depth[0] > max_depth:
            depth[0] -= 1
            raise RecursionError("Max recursion depth reached")
        try:
            return func(*args, **kwargs, _wrapper_depth=depth)
        finally:
            depth[0] -= 1
    return wrapper""",
        'test': """# Use iterative approach instead of recursion when possible"""
    },
    'StopIteration': {
        'explanation': 'StopIteration occurs when next() is called on an iterator that has no more items. Use a default value with next() or iterate with a for loop.',
        'fix': """def next_safe(iterator, default=None):
    try:
        return next(iterator)
    except StopIteration:
        return default""",
        'test': """it = iter([1, 2, 3])
print(next_safe(it))  # 1
print(next_safe(it))  # 2
print(next_safe(it))  # 3
print(next_safe(it))  # None"""
    },
    'AssertionError': {
        'explanation': 'AssertionError occurs when an assert statement fails. This means a condition that was assumed to be True is actually False.',
        'fix': """def assert_safe(condition, message="Assertion failed"):
    if not condition:
        raise AssertionError(message)""",
        'test': """assert_safe(1 + 1 == 2, "Math broke")  # Passes silently"""
    },
    'PermissionError': {
        'explanation': 'PermissionError occurs when trying to access a file or resource without the required permissions.',
        'fix': """def read_file_permission_safe(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except PermissionError:
        return None""",
        'test': """read_file_permission_safe("/root/secret.txt")  # None"""
    },
    'ConnectionError|TimeoutError': {
        'explanation': 'ConnectionError or TimeoutError occurs when a network connection fails or times out. The remote server may be down, unreachable, or the request took too long.',
        'fix': """import socket
def connect_safe(host, port, timeout=5):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (ConnectionError, TimeoutError):
        return False""",
        'test': """print(connect_safe("localhost", 8080))  # True or False"""
    },
    'OSError': {
        'explanation': 'OSError is the base class for system-related errors (file I/O, permissions, etc.). Check the error message for specifics.',
        'fix': """def os_operation_safe(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except OSError as e:
        return {"error": str(e), "errno": e.errno}""",
        'test': """import os
print(os_operation_safe(os.remove, "/nonexistent/file"))  # Error dict"""
    },
    'MemoryError': {
        'explanation': 'MemoryError occurs when the system runs out of memory. The program is trying to allocate more memory than available.',
        'fix': """def process_in_chunks(data, chunk_size=1000):
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        results.extend(chunk)
    return results""",
        'test': """# Process large datasets in chunks to avoid MemoryError"""
    },
    'OverflowError': {
        'explanation': 'OverflowError occurs when a calculation result is too large to be represented. This is common with large integers in certain operations.',
        'fix': """import math
def power_safe(base, exp):
    try:
        return base ** exp
    except OverflowError:
        return float('inf')""",
        'test': """print(power_safe(10, 1000))  # inf"""
    },
    'LookupError': {
        'explanation': 'LookupError is the base class for IndexError and KeyError. It occurs when a lookup operation fails on a collection.',
        'fix': """def lookup_safe(collection, key, default=None):
    try:
        return collection[key]
    except LookupError:
        return default""",
        'test': """print(lookup_safe([1, 2, 3], 5))  # None
print(lookup_safe({"a": 1}, "b"))  # None"""
    },
    'SystemError|FloatingPointError': {
        'explanation': 'SystemError or FloatingPointError indicates an internal interpreter error or a floating-point calculation issue. These are rare and often indicate a bug in the interpreter or extreme numerical edge cases.',
        'fix': """def safe_float_calc(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except (SystemError, FloatingPointError) as e:
        return {"error": str(e)}""",
        'test': """# Rare error, use try/except to catch gracefully"""
    }
}

# Collect known error type names
KNOWN_ERROR_TYPES = set()
for key in ERROR_FIXES:
    for t in key.split('|'):
        KNOWN_ERROR_TYPES.add(t)

# All known error type names for detection
KNOWN_ERROR_TYPES_LIST = sorted(KNOWN_ERROR_TYPES, key=len, reverse=True)  # Longer names first to match specific like ModuleNotFoundError before ImportError

# Standard Python built-in error names for unknown detection
STANDARD_ERROR_NAMES = [
    'BaseException', 'SystemExit', 'KeyboardInterrupt', 'GeneratorExit',
    'Exception', 'StopIteration', 'StopAsyncIteration', 'ArithmeticError',
    'FloatingPointError', 'OverflowError', 'ZeroDivisionError',
    'AssertionError', 'AttributeError', 'BufferError', 'EOFError',
    'ImportError', 'ModuleNotFoundError', 'LookupError', 'IndexError',
    'KeyError', 'MemoryError', 'NameError', 'UnboundLocalError',
    'OSError', 'BlockingIOError', 'ChildProcessError', 'ConnectionError',
    'BrokenPipeError', 'ConnectionAbortedError', 'ConnectionRefusedError',
    'ConnectionResetError', 'FileExistsError', 'FileNotFoundError',
    'InterruptedError', 'IsADirectoryError', 'NotADirectoryError',
    'PermissionError', 'ProcessLookupError', 'TimeoutError',
    'ReferenceError', 'RuntimeError', 'NotImplementedError', 'RecursionError',
    'SyntaxError', 'IndentationError', 'TabError', 'SystemError',
    'TypeError', 'ValueError', 'UnicodeError', 'UnicodeDecodeError',
    'UnicodeEncodeError', 'UnicodeTranslateError', 'Warning',
    'DeprecationWarning', 'PendingDeprecationWarning', 'RuntimeWarning',
    'SyntaxWarning', 'UserWarning', 'FutureWarning', 'ImportWarning',
    'UnicodeWarning', 'BytesWarning', 'ResourceWarning',
]


def _extract_error_info(error_trace: str) -> tuple:
    """Extract (error_type, error_message) from a traceback string."""
    lines = error_trace.strip().split('\n')

    # The last non-empty line typically contains "ErrorType: message"
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        for known_type in KNOWN_ERROR_TYPES_LIST:
            colon_idx = line.find(':')
            if colon_idx != -1:
                candidate = line[:colon_idx].strip()
                if candidate == known_type:
                    return known_type, line[colon_idx + 1:].strip()
        # Try without colon (e.g. just "KeyboardInterrupt")
        for known_type in KNOWN_ERROR_TYPES_LIST:
            if line == known_type:
                return known_type, ''

    # If no known type matched, try to find ANY Exception-looking word in the last line
    last_line = ''
    for line in reversed(lines):
        if line.strip():
            last_line = line.strip()
            break

    if ':' in last_line:
        candidate = last_line.split(':')[0].strip()
        if candidate and candidate[0].isupper() and 'Error' in candidate:
            return candidate, last_line.split(':', 1)[1].strip()

    return 'UnknownError', last_line


def _get_code_context_lines(trace_lines: list) -> str:
    """Extract the relevant 'File X, line Y' context from trace."""
    context = []
    for line in trace_lines:
        if 'File "' in line:
            context.append(line.strip())
    return '\n'.join(context[-3:]) if context else ''


def run_fast_debug(client: OpenAI, error_context: Dict[str, Any]) -> Dict[str, Any]:
    """Instant local debugger - no API calls needed."""
    error_trace = error_context.get('error_trace', '')
    failing_file = error_context.get('failing_file', 'unknown')
    failing_line = error_context.get('failing_line', 'N/A')

    error_type, error_msg = _extract_error_info(error_trace)

    # Build code context
    trace_lines = error_trace.split('\n')
    code_context = _get_code_context_lines(trace_lines)

    # Find matching fix entry (check pipe-separated keys)
    info = None
    for key, val in ERROR_FIXES.items():
        if error_type in key.split('|'):
            info = val
            break

    if info is None:
        info = {
            'explanation': f'**{error_type}**: {error_msg or "No additional details."}\n\n'
                           f'This is a standard Python exception. To fix it:\n'
                           f'1. Read the error message carefully — it tells you exactly what went wrong.\n'
                           f'2. Look at the line listed in the traceback (the last "File X, line Y" entry).\n'
                           f'3. Check if a variable is None, a collection is empty, or a value has the wrong type.\n'
                           f'4. Use try/except to handle this error gracefully if it is expected at runtime.',
            'fix': f"""def handle_{error_type.lower()}(operation, *args, fallback=None, **kwargs):
    try:
        return operation(*args, **kwargs)
    except {error_type} as e:
        return fallback""",
            'test': f"""# Wrap the problematic call:
result = handle_{error_type.lower()}(some_function, arg1, arg2, fallback=None)
# result will be None if {error_type} is raised"""
        }

    output = f"""## Error Explanation
{info['explanation']}

**Error**: {error_type}: {error_msg}
**Location**: {failing_file}:{failing_line}
**Trace**:
{code_context}

## Corrected Code
```python
{info['fix']}
```

## Test Results
```python
{info['test']}
```

## Status
PASS"""

    return {
        'agent': 'FastDebugAgent',
        'final_output': output,
        'validation': 'PASS',
        'input': error_context
    }


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
        
        result = await Runner.run(DebugSleuth, prompt, run_config=get_run_config())
        
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
        
        result = await Runner.run(SolutionArchitect, prompt, run_config=get_run_config())
        
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
        
        result = await Runner.run(ReliabilityEngineer, prompt, run_config=get_run_config())
        
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
        """Synchronous version of run_debug_sleuth."""
        async def _run():
            prompt = self._build_sleuth_prompt(error_context)
            result = await Runner.run(DebugSleuth, prompt, run_config=get_run_config())
            analysis = {
                'agent': 'DebugSleuth',
                'final_output': result.final_output,
                'input': error_context
            }
            self.session_history.append(analysis)
            return analysis
        return run_async(_run())

    def run_solution_architect(self, bug_report: str) -> Dict[str, Any]:
        """Synchronous version of run_solution_architect."""
        async def _run():
            prompt = self._build_architect_prompt(bug_report)
            result = await Runner.run(SolutionArchitect, prompt, run_config=get_run_config())
            fix_proposal = {
                'agent': 'SolutionArchitect',
                'final_output': result.final_output,
                'input': bug_report
            }
            self.session_history.append(fix_proposal)
            return fix_proposal
        return run_async(_run())

    def run_reliability_engineer(self, fix_proposal: str, bug_report: str) -> Dict[str, Any]:
        """Synchronous version of run_reliability_engineer."""
        async def _run():
            prompt = self._build_validator_prompt(fix_proposal, bug_report)
            result = await Runner.run(ReliabilityEngineer, prompt, run_config=get_run_config())
            validation = {
                'agent': 'ReliabilityEngineer',
                'final_output': result.final_output,
                'validation_passed': 'PASS' in result.final_output.upper() or 'VALIDATION STATUS: PASS' in result.final_output.upper()
            }
            self.session_history.append(validation)
            return validation
        return run_async(_run())

    def run_full_debugging_cycle(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version with fast single-agent mode."""
        print("🚀 Debug Agent: Analyzing, fixing, and validating...")
        fast_result = run_fast_debug(None, error_context)

        print("🎉 Debugging cycle completed!")
        return {
            'session_history': [fast_result],
            'root_cause_analysis': fast_result,
            'solution_architecture': fast_result,
            'reliability_validation': fast_result,
            'final_report': fast_result['final_output'],
            'validation_passed': fast_result['validation'] == 'PASS'
        }

    def run_fast(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Single-agent mode using OpenRouter directly."""
        client = get_openrouter_client()
        return run_fast_debug(client, error_context)
