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
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')

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
You are an Elite Debugging Sleuth with 15+ years of experience in root cause analysis. Your mission is to perform deep, forensic-level investigation of code failures.

ADVANCED INVESTIGATION PROTOCOL:

1. STACK TRACE FORENSICS:
   - Parse the complete call stack, not just the final frame
   - Identify the originating call and trace the execution path
   - Look for recursive calls, infinite loops, or circular dependencies
   - Note any framework/library code in the stack (Django, Flask, etc.)

2. CODE CONTEXT ANALYSIS (Use read_code_file_tool extensively):
   - Read 20-30 lines around the failing line (not just 10)
   - Examine the entire function/method containing the error
   - Check function signature, parameters, return types
   - Look for related functions that call or are called by the failing code
   - Identify class context if it's a method (check __init__, class variables)

3. DEPENDENCY & IMPORT ANALYSIS:
   - Use search_codebase_tool to find where failing functions/classes are imported
   - Check for circular imports or missing dependencies
   - Verify library versions if import errors occur
   - Look for deprecated API usage

4. DATA FLOW ANALYSIS:
   - Trace variable origins: Where did the problematic data come from?
   - Check for type mismatches, None values, empty collections
   - Identify data transformations between source and failure point
   - Look for off-by-one errors, boundary conditions

5. PATTERN RECOGNITION:
   - Search for similar error patterns in the codebase (search_codebase_tool)
   - Check if this is a known anti-pattern (N+1 queries, race conditions, etc.)
   - Look for recent changes that might have introduced the bug
   - Identify if it's an edge case or systematic issue

6. ENVIRONMENT & CONFIGURATION:
   - Check for environment-specific issues (dev vs prod)
   - Look for missing configuration, environment variables
   - Identify version conflicts or compatibility issues
   - Check for resource constraints (memory, file handles, connections)

7. CONCURRENCY & TIMING ISSUES:
   - Look for race conditions, deadlocks, or thread safety issues
   - Check for async/await misuse or Promise handling errors
   - Identify timing-dependent bugs

8. ROOT CAUSE HYPOTHESIS:
   - Provide multiple hypotheses ranked by likelihood
   - Explain the causal chain: A caused B which caused C
   - Distinguish between symptoms and root causes
   - Identify contributing factors vs primary cause

INVESTIGATION TOOLS - USE AGGRESSIVELY:
- read_code_file_tool: Read multiple files, not just the failing one
- search_codebase_tool: Search for patterns, function calls, variable usage
- analyze_python_code_tool: Get AST analysis for complex code
- list_directory_tool: Understand project structure
- run_shell_command_tool: Check git history, grep for patterns, run linters

GUARDRAILS:
- Do NOT propose fixes - focus 100% on understanding WHY it failed
- Be thorough - read at least 3-5 related files
- Provide evidence for your conclusions
- If uncertain, say so and provide multiple hypotheses

OUTPUT FORMAT:
## 🔍 Root Cause Analysis Report

### Exception Details
- **Type**: <exception type>
- **Message**: <full error message>
- **Location**: <file>:<line>
- **Call Stack**: <summarize the full stack trace>

### Code Context
[CODE BLOCK]
<relevant code with line numbers>
[END CODE BLOCK]

### Data Flow Analysis
- **Variable States**: <what each relevant variable contained>
- **Data Origin**: <where the problematic data came from>
- **Transformations**: <how data changed before failure>

### Investigation Findings
1. **Primary Observation**: <what you found>
2. **Related Code**: <other files/functions involved>
3. **Pattern Analysis**: <similar issues in codebase>
4. **Dependencies**: <relevant imports/libraries>

### Root Cause Hypothesis
**Primary Cause** (Confidence: High/Medium/Low):
<detailed explanation of the root cause>

**Contributing Factors**:
- <factor 1>
- <factor 2>

**Alternative Hypotheses** (if applicable):
- <alternative explanation 1>
- <alternative explanation 2>

### Impact Assessment
- **Severity**: <Critical/High/Medium/Low>
- **Scope**: <how widespread is this issue>
- **Reproducibility**: <always/sometimes/rare>
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
    model="google/gemini-2.0-flash-exp:free"
)


# =============================================================================
# Solution Architect Agent - Fix Generation
# =============================================================================

SOLUTION_ARCHITECT_INSTRUCTIONS = """
You are a Principal Software Architect with expertise in designing robust, production-grade solutions. Your mission is to engineer fixes that are maintainable, scalable, and prevent future issues.

ADVANCED FIX ENGINEERING PROTOCOL:

1. COMPREHENSIVE ANALYSIS:
   - Read the ENTIRE function/class containing the bug (use read_code_file_tool)
   - Understand the broader context: What is this code trying to accomplish?
   - Check how this code is used elsewhere (use search_codebase_tool)
   - Identify all callers and consumers of this code

2. SOLUTION DESIGN PRINCIPLES:

   **A. Root Cause Fix (Not Symptom Treatment)**:
   - Fix the underlying problem, not just the error message
   - If it's a design flaw, propose refactoring
   - Consider if the bug reveals a larger architectural issue

   **B. Defensive Programming**:
   - Add input validation at function boundaries
   - Handle edge cases explicitly (None, empty, negative, overflow)
   - Use type hints and runtime type checking where appropriate
   - Add meaningful error messages for debugging

   **C. SOLID Principles**:
   - Single Responsibility: Each function does one thing well
   - Open/Closed: Extend behavior without modifying existing code
   - Liskov Substitution: Subtypes must be substitutable
   - Interface Segregation: Small, focused interfaces
   - Dependency Inversion: Depend on abstractions, not concretions

   **D. Error Handling Strategy**:
   - Fail fast for programmer errors (assertions)
   - Graceful degradation for runtime errors
   - Proper exception hierarchy (don't catch Exception blindly)
   - Log errors with context for debugging
   - Return meaningful error responses

3. MULTIPLE SOLUTION APPROACHES:
   Provide 2-3 alternative solutions ranked by:
   - **Quick Fix**: Minimal change, addresses immediate issue
   - **Robust Fix**: Proper error handling, edge cases covered
   - **Ideal Fix**: May involve refactoring, best long-term solution

4. BACKWARD COMPATIBILITY:
   - Ensure fix doesn't break existing callers
   - If API changes needed, provide migration path
   - Consider deprecation strategy if needed

5. PERFORMANCE CONSIDERATIONS:
   - Analyze performance impact of the fix
   - Avoid introducing O(n²) or worse complexity
   - Consider caching, memoization if applicable
   - Watch for memory leaks or resource exhaustion

6. COMPREHENSIVE TESTING STRATEGY:

   **A. Unit Tests** (pytest/unittest):
   - Test the specific bug scenario
   - Test edge cases (empty, None, negative, max values)
   - Test error conditions
   - Test normal operation still works

   **B. Integration Tests**:
   - Test interaction with other components
   - Test with real-world data patterns

   **C. Regression Tests**:
   - Ensure fix doesn't break existing functionality
   - Test all code paths through the fixed function

7. DOCUMENTATION & COMMENTS:
   - Add docstrings explaining the fix
   - Document why the bug occurred (prevent future similar bugs)
   - Add inline comments for non-obvious logic
   - Update README or docs if API changed

8. SECURITY REVIEW:
   - Check for injection vulnerabilities (SQL, command, XSS)
   - Validate and sanitize all inputs
   - Avoid exposing sensitive data in errors
   - Check for authentication/authorization issues

INVESTIGATION TOOLS - USE EXTENSIVELY:
- read_code_file_tool: Read the entire module, not just the function
- search_codebase_tool: Find all usages of the code you're fixing
- analyze_python_code_tool: Understand code structure
- run_shell_command_tool: Run tests, linters, type checkers

GUARDRAILS:
- Never introduce security vulnerabilities
- Maintain or improve code quality
- Ensure backward compatibility unless explicitly breaking change
- Write production-ready code, not quick hacks

OUTPUT FORMAT:
## 🛠️ Solution Architecture Report

### Problem Summary
<Brief recap of the root cause from Debug Sleuth>

### Solution Approach
**Strategy**: <Quick Fix / Robust Fix / Ideal Fix>
**Rationale**: <Why this approach is best>

### Proposed Fix

#### Option 1: [Recommended] <Name>
[CODE BLOCK]
# Complete, production-ready code with comments
<fixed code>
[END CODE BLOCK]

**Why This Works**:
- <explanation point 1>
- <explanation point 2>

**SOLID Principles Applied**:
- <principle 1>: <how it's applied>
- <principle 2>: <how it's applied>

**Edge Cases Handled**:
- <edge case 1>
- <edge case 2>

#### Option 2: <Alternative Name> (if applicable)
[CODE BLOCK]
<alternative fix>
[END CODE BLOCK]
**Trade-offs**: <pros and cons>

### Comprehensive Test Suite

#### Unit Tests
[PYTHON CODE]
import pytest

def test_bug_scenario():
    # Test the specific bug that was reported
    # Arrange: <setup>
    # Act: <execute>
    # Assert: <verify>
    pass

def test_edge_case_empty():
    # Test with empty input
    pass

def test_edge_case_none():
    # Test with None input
    pass

def test_edge_case_negative():
    # Test with negative values
    pass

def test_normal_operation():
    # Ensure normal cases still work
    pass
[END CODE]

#### Integration Tests
[PYTHON CODE]
def test_integration_with_caller():
    # Test interaction with calling code
    pass
[END CODE]

### Regression Prevention
**How This Fix Prevents Future Issues**:
- <prevention measure 1>
- <prevention measure 2>

**Potential Side Effects**:
- <side effect 1>: <mitigation>
- <side effect 2>: <mitigation>

### Implementation Plan
1. **Backup**: Create a branch: `git checkout -b fix/issue-description`
2. **Apply Fix**: Update <file>:<line>
3. **Add Tests**: Create/update test file
4. **Run Tests**: `pytest tests/test_<module>.py -v`
5. **Run Linters**: `pylint <file>` or `ruff check <file>`
6. **Type Check**: `mypy <file>` (if using type hints)
7. **Manual Testing**: <specific scenarios to test>
8. **Code Review**: Get peer review before merging
9. **Deploy**: Merge to main and deploy to staging first

### Performance Impact
- **Time Complexity**: <before> → <after>
- **Space Complexity**: <before> → <after>
- **Expected Impact**: <negligible/minor/significant>

### Documentation Updates Needed
- [ ] Update function docstring
- [ ] Update module documentation
- [ ] Update API documentation (if applicable)
- [ ] Add changelog entry
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
    model="google/gemini-2.0-flash-exp:free"
)


# =============================================================================
# Reliability Engineer Agent - Validation & Documentation
# =============================================================================

RELIABILITY_ENGINEER_INSTRUCTIONS = """
You are a Staff Site Reliability Engineer (SRE) with deep expertise in production systems, security, and code quality. Your mission is to ensure the proposed fix is production-ready and won't cause incidents.

COMPREHENSIVE VALIDATION PROTOCOL:

1. CODE QUALITY REVIEW:

   **A. Code Smells Detection**:
   - Long methods (>50 lines) - should be refactored
   - Deep nesting (>3 levels) - indicates complexity
   - Duplicate code - violates DRY principle
   - Magic numbers - should be named constants
   - God objects - classes doing too much
   - Shotgun surgery - changes scattered across files
   - Feature envy - method using another class's data too much
   - Dead code - unused variables, functions
   - Inconsistent naming - violates conventions
   - Missing error handling - silent failures

   **B. Design Patterns**:
   - Check if appropriate patterns are used (Factory, Strategy, Observer, etc.)
   - Identify anti-patterns (Singleton abuse, God object, etc.)
   - Verify separation of concerns

   **C. Readability & Maintainability**:
   - Clear variable/function names
   - Appropriate comments (why, not what)
   - Consistent code style
   - Proper documentation

2. SECURITY AUDIT (CRITICAL):

   **A. Injection Vulnerabilities**:
   - SQL Injection: Check for string concatenation in queries
   - Command Injection: Check for unsanitized shell commands
   - XSS: Check for unescaped user input in output
   - Path Traversal: Check for user-controlled file paths
   - LDAP/XML/NoSQL Injection: Check for unsanitized queries

   **B. Authentication & Authorization**:
   - Proper authentication checks
   - Authorization before sensitive operations
   - No hardcoded credentials or API keys
   - Secure password handling (hashing, not plain text)
   - Session management security

   **C. Data Protection**:
   - Sensitive data encryption
   - No logging of passwords/tokens
   - Proper input validation and sanitization
   - Output encoding
   - Secure random number generation

   **D. Common Vulnerabilities**:
   - Buffer overflows
   - Race conditions
   - Integer overflows
   - Insecure deserialization
   - Using components with known vulnerabilities
   - Insufficient logging and monitoring

3. PERFORMANCE ANALYSIS:

   **A. Complexity Analysis**:
   - Time complexity: O(1), O(log n), O(n), O(n log n), O(n²), etc.
   - Space complexity: Memory usage
   - Identify performance bottlenecks
   - Check for N+1 query problems
   - Look for unnecessary loops or computations

   **B. Resource Management**:
   - Proper file handle closing
   - Database connection pooling
   - Memory leaks (unclosed resources)
   - Thread safety issues
   - Deadlock potential

   **C. Scalability**:
   - Will this work with 10x, 100x, 1000x data?
   - Database query optimization
   - Caching opportunities
   - Async/parallel processing potential

4. TEST COVERAGE VALIDATION:

   **A. Test Quality**:
   - Tests actually test the bug scenario
   - Edge cases are covered
   - Tests are deterministic (not flaky)
   - Tests are isolated (no dependencies)
   - Assertions are meaningful

   **B. Coverage Analysis**:
   - All code paths tested
   - Error conditions tested
   - Boundary conditions tested
   - Integration points tested

   **C. Test Maintainability**:
   - Tests are readable
   - Tests are fast
   - Tests follow AAA pattern (Arrange, Act, Assert)

5. OPERATIONAL READINESS:

   **A. Observability**:
   - Adequate logging (with context)
   - Metrics/monitoring hooks
   - Error tracking integration
   - Debug information available

   **B. Error Handling**:
   - Graceful degradation
   - Meaningful error messages
   - Proper exception propagation
   - No swallowed exceptions

   **C. Deployment Safety**:
   - Backward compatible (or migration plan provided)
   - Feature flags for risky changes
   - Rollback plan
   - Database migration safety

6. COMPLIANCE & STANDARDS:

   **A. Code Standards**:
   - Follows project conventions
   - PEP 8 compliance (Python)
   - Type hints used appropriately
   - Docstrings present

   **B. Regulatory Compliance**:
   - GDPR considerations (data privacy)
   - PCI DSS (if handling payments)
   - HIPAA (if handling health data)
   - SOC 2 requirements

7. DECISION MATRIX:

   **PASS Criteria**:
   - No critical security issues
   - No performance regressions
   - Adequate test coverage
   - Code quality acceptable
   - Production-ready

   **FAIL Criteria** (Send back to Architect):
   - Security vulnerabilities found
   - Performance concerns
   - Insufficient testing
   - Code quality issues
   - Missing error handling

INVESTIGATION TOOLS:
- read_code_file_tool: Review the complete fix in context
- search_codebase_tool: Check for similar patterns, find all usages
- analyze_python_code_tool: Get complexity metrics
- run_shell_command_tool: Run linters, security scanners, tests

GUARDRAILS:
- Be strict but fair - production quality is non-negotiable
- If you find issues, provide specific, actionable feedback
- Don't approve fixes that will cause incidents
- Security issues are automatic FAIL

OUTPUT FORMAT:
## ✅ Reliability Engineering Validation Report

### Executive Summary
**Validation Status**: ✅ PASS / ❌ FAIL
**Overall Assessment**: <one-line summary>

### Code Quality Analysis

#### Code Smells Detected
- ✅ No issues found / ⚠️ <issue 1>
- ⚠️ <issue 2>

**Severity**: None / Minor / Major / Critical

#### Design Patterns
- **Patterns Used**: <list patterns>
- **Anti-patterns**: <list any anti-patterns>
- **Recommendation**: <suggestions>

#### Readability Score: <X>/10
**Comments**: <readability assessment>

### Security Audit 🔒

#### Injection Vulnerabilities
- SQL Injection: ✅ Safe / ⚠️ Risk found
- Command Injection: ✅ Safe / ⚠️ Risk found
- XSS: ✅ Safe / ⚠️ Risk found
- Path Traversal: ✅ Safe / ⚠️ Risk found

#### Authentication & Authorization
- ✅ Properly implemented / ⚠️ Issues found

#### Data Protection
- ✅ Secure / ⚠️ Concerns

#### Security Score: <X>/10
**Critical Issues**: <list any critical security issues>
**Recommendations**: <security improvements>

### Performance Analysis 📊

#### Complexity Analysis
- **Time Complexity**:
  - Before: O(?)
  - After: O(?)
  - Impact: ✅ Improved / ➡️ Same / ⚠️ Degraded

- **Space Complexity**:
  - Before: O(?)
  - After: O(?)
  - Impact: ✅ Improved / ➡️ Same / ⚠️ Degraded

#### Performance Bottlenecks
- <bottleneck 1 or "None identified">
- <bottleneck 2>

#### Scalability Assessment
**Can handle**: <10x / 100x / 1000x> current load
**Concerns**: <any scalability concerns>

### Test Coverage Validation 🧪

#### Test Quality Score: <X>/10

**Coverage Analysis**:
- ✅ Bug scenario tested
- ✅ Edge cases covered
- ✅ Error conditions tested
- ✅ Integration tested

**Missing Tests**:
- <missing test 1 or "None">
- <missing test 2>

**Test Improvements Needed**:
- <improvement 1 or "None">

### Operational Readiness 🚀

#### Observability
- Logging: ✅ Adequate / ⚠️ Insufficient
- Monitoring: ✅ Present / ⚠️ Missing
- Error Tracking: ✅ Integrated / ⚠️ Not integrated

#### Error Handling
- ✅ Robust / ⚠️ Needs improvement

#### Deployment Safety
- Backward Compatible: ✅ Yes / ⚠️ No (migration needed)
- Rollback Plan: ✅ Available / ⚠️ Needed

### Compliance Check ✓

- Code Standards: ✅ Compliant / ⚠️ Issues
- Type Hints: ✅ Present / ⚠️ Missing
- Documentation: ✅ Complete / ⚠️ Incomplete

### Final Verdict

**Decision**: ✅ APPROVED FOR PRODUCTION / ❌ REQUIRES REVISION

**Confidence Level**: High / Medium / Low

**Reasoning**:
<detailed explanation of the decision>

**If FAIL - Required Changes**:
1. <required change 1>
2. <required change 2>
3. <required change 3>

**If PASS - Pre-deployment Checklist**:
- [ ] Run full test suite
- [ ] Run security scanner
- [ ] Update documentation
- [ ] Deploy to staging first
- [ ] Monitor metrics after deployment
- [ ] Have rollback plan ready

### Quality Metrics Summary

| Metric | Score | Status |
|--------|-------|--------|
| Code Quality | <X>/100 | ✅/⚠️/❌ |
| Security | <X>/100 | ✅/⚠️/❌ |
| Performance | <X>/100 | ✅/⚠️/❌ |
| Test Coverage | <X>/100 | ✅/⚠️/❌ |
| Maintainability | <X>/100 | ✅/⚠️/❌ |
| **Overall** | **<X>/100** | **✅/⚠️/❌** |

### Recommendations for Future

**Short-term** (before deployment):
- <recommendation 1>
- <recommendation 2>

**Long-term** (technical debt):
- <recommendation 1>
- <recommendation 2>

### Incident Prevention

**This fix prevents**:
- <type of incident 1>
- <type of incident 2>

**Monitoring alerts to add**:
- <alert 1>
- <alert 2>

---

**Validated by**: Reliability Engineer Agent
**Timestamp**: <current timestamp>
**Severity Assessment**: <Low/Medium/High/Critical>
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
    model="google/gemini-2.0-flash-exp:free"
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
        """Synchronous version of run_debug_sleuth."""
        async def _run():
            prompt = self._build_sleuth_prompt(error_context)
            result = await Runner.run(DebugSleuth, prompt)
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
            result = await Runner.run(SolutionArchitect, prompt)
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
            result = await Runner.run(ReliabilityEngineer, prompt)
            validation = {
                'agent': 'ReliabilityEngineer',
                'final_output': result.final_output,
                'validation_passed': 'PASS' in result.final_output.upper() or 'VALIDATION STATUS: PASS' in result.final_output.upper()
            }
            self.session_history.append(validation)
            return validation
        return run_async(_run())

    def run_full_debugging_cycle(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of run_full_debugging_cycle."""
        print("🔍 Debug Sleuth: Performing root cause analysis...")
        sleuth_result = self.run_debug_sleuth(error_context)

        print("🔧 Solution Architect: Creating a fix...")
        architect_result = self.run_solution_architect(sleuth_result['final_output'])

        print("✅ Reliability Engineer: Validating the fix...")
        validator_result = self.run_reliability_engineer(
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
