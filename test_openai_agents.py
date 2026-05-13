"""
Comprehensive Test Suite for OpenAI Agents SDK Integration

This script tests:
1. Tool functionality
2. Individual agent responses
3. Full multi-agent workflow
4. Error handling
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import (
    DebugSleuth,
    SolutionArchitect, 
    ReliabilityEngineer,
    SyncDebuggingOrchestrator,
    list_directory_structure,
    read_code_file,
    search_codebase,
    run_shell_command
)
from agents import Runner


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_tools():
    """Test that all tools work correctly."""
    print_section("TEST 1: Tool Functionality")
    
    results = {
        'list_directory': None,
        'read_code_file': None,
        'search_codebase': None,
        'run_shell_command': None
    }
    
    # Test 1: List directory
    print("\n📁 Testing list_directory_structure...")
    try:
        dir_struct = list_directory_structure(".", max_depth=2)
        results['list_directory'] = dir_struct
        print(f"   ✓ Found {len(dir_struct.get('children', {}))} top-level items")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2: Read code file
    print("\n📄 Testing read_code_file...")
    try:
        code = read_code_file("src/code_debugger/agents.py", start_line=1, end_line=20)
        results['read_code_file'] = code
        print(f"   ✓ Read {len(code)} characters from agents.py")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 3: Search codebase
    print("\n🔍 Testing search_codebase...")
    try:
        search_results = search_codebase("def run_", file_extensions=['.py'])
        results['search_codebase'] = search_results
        print(f"   ✓ Found {len(search_results)} files with 'def run_'")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 4: Run shell command
    print("\n⚡ Testing run_shell_command...")
    try:
        cmd_result = run_shell_command("python --version", timeout=5)
        results['run_shell_command'] = cmd_result
        print(f"   ✓ Python version: {cmd_result['stdout'].strip()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return results


async def test_debug_sleuth_agent():
    """Test the Debug Sleuth agent with a real error."""
    print_section("TEST 2: Debug Sleuth Agent")
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "data_processor.py", line 42, in process_batch
    item = items[current_index]
IndexError: list index out of range''',
        'failing_file': 'src/code_debugger/agents.py',
        'failing_line': 100,
        'inputs': {
            'items': [1, 2, 3],
            'current_index': 5
        }
    }
    
    print("\n🔍 Running Debug Sleuth agent...")
    print("   This may take 10-20 seconds...")
    
    try:
        prompt = f"""
Analyze the following error and perform root cause analysis:

ERROR TRACE:
{error_context['error_trace']}

FAILING FILE: {error_context['failing_file']}
FAILING LINE: {error_context['failing_line']}

ADDITIONAL CONTEXT:
{json.dumps(error_context['inputs'], indent=2)}

Please provide your analysis in this structure:
- Exception Type
- Exception Message
- Failing Location
- Code Context (use read_code_file_tool to examine)
- State Analysis
- Root Cause
- Confidence Level
"""
        
        result = await Runner.run(DebugSleuth, prompt)
        
        print("\n✅ Debug Sleuth Response Received!")
        print(f"\n📊 Response Length: {len(result.final_output)} characters")
        print("\n📝 Analysis Preview (first 500 chars):")
        print("-" * 70)
        print(result.final_output[:500])
        print("-" * 70)
        
        return {
            'success': True,
            'output': result.final_output,
            'length': len(result.final_output)
        }
    except Exception as e:
        print(f"\n❌ Debug Sleuth Failed: {e}")
        return {'success': False, 'error': str(e)}


async def test_solution_architect_agent(bug_report: str):
    """Test the Solution Architect agent."""
    print_section("TEST 3: Solution Architect Agent")
    
    print("\n🔧 Running Solution Architect agent...")
    print("   This may take 15-30 seconds...")
    
    try:
        prompt = f"""
Based on the following bug analysis, create a comprehensive fix:

BUG REPORT:
{bug_report[:2000]}  # Truncate if too long

Please provide:
1. Proposed Fix (complete code block)
2. Fix Explanation
3. SOLID Principles Applied
4. Test Snippet (pytest)
5. Implementation Plan
"""
        
        result = await Runner.run(SolutionArchitect, prompt)
        
        print("\n✅ Solution Architect Response Received!")
        print(f"\n📊 Response Length: {len(result.final_output)} characters")
        print("\n📝 Fix Preview (first 500 chars):")
        print("-" * 70)
        print(result.final_output[:500])
        print("-" * 70)
        
        return {
            'success': True,
            'output': result.final_output,
            'length': len(result.final_output)
        }
    except Exception as e:
        print(f"\n❌ Solution Architect Failed: {e}")
        return {'success': False, 'error': str(e)}


async def test_reliability_engineer_agent(bug_report: str, fix_proposal: str):
    """Test the Reliability Engineer agent."""
    print_section("TEST 4: Reliability Engineer Agent")
    
    print("\n✅ Running Reliability Engineer agent...")
    print("   This may take 15-30 seconds...")
    
    try:
        prompt = f"""
Validate the following fix proposal:

ORIGINAL BUG REPORT:
{bug_report[:1000]}

PROPOSED FIX:
{fix_proposal[:2000]}

Please perform:
1. Sanity Check (code smells)
2. Complexity Analysis (Big O)
3. Security Review
4. Validation Status (PASS/FAIL)
5. Final Markdown Report
"""
        
        result = await Runner.run(ReliabilityEngineer, prompt)
        
        print("\n✅ Reliability Engineer Response Received!")
        print(f"\n📊 Response Length: {len(result.final_output)} characters")
        
        # Check for validation status
        validation_passed = 'PASS' in result.final_output.upper()
        print(f"\n✅ Validation Status: {'PASS' if validation_passed else 'FAIL'}")
        
        print("\n📝 Report Preview (first 500 chars):")
        print("-" * 70)
        print(result.final_output[:500])
        print("-" * 70)
        
        return {
            'success': True,
            'output': result.final_output,
            'validation_passed': validation_passed
        }
    except Exception as e:
        print(f"\n❌ Reliability Engineer Failed: {e}")
        return {'success': False, 'error': str(e)}


def test_full_workflow():
    """Test the complete three-agent workflow."""
    print_section("TEST 5: Full Multi-Agent Workflow")
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
        'failing_file': 'src/code_debugger/agents.py',
        'failing_line': 100,
        'inputs': {'numbers': [1, 2, 3], 'index': 2}
    }
    
    print("\n🚀 Running complete workflow...")
    print("   This may take 30-60 seconds...")
    
    try:
        orchestrator = SyncDebuggingOrchestrator()
        result = orchestrator.run_full_debugging_cycle(error_context)
        
        print("\n✅ Workflow Completed Successfully!")
        print(f"\n📊 Results:")
        print(f"   - Agents Run: {len(result['session_history'])}")
        print(f"   - Validation Passed: {result['validation_passed']}")
        print(f"   - Final Report Length: {len(result['final_report'])} chars")
        
        return result
    except Exception as e:
        print(f"\n❌ Workflow Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_agent_imports():
    """Test that all agents and tools can be imported."""
    print_section("TEST 0: Import Verification")
    
    tests = {
        'DebugSleuth': DebugSleuth is not None,
        'SolutionArchitect': SolutionArchitect is not None,
        'ReliabilityEngineer': ReliabilityEngineer is not None,
        'SyncDebuggingOrchestrator': SyncDebuggingOrchestrator is not None,
        'list_directory_structure': callable(list_directory_structure),
        'read_code_file': callable(read_code_file),
        'search_codebase': callable(search_codebase),
        'run_shell_command': callable(run_shell_command)
    }
    
    all_passed = True
    for name, passed in tests.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {name}")
        if not passed:
            all_passed = False
    
    return all_passed


def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("\n" + "!" * 70)
        print("  WARNING: OPENAI_API_KEY not set!")
        print("!" * 70)
        print("\nPlease set your API key:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=sk-...")
        return False
    
    print(f"\n✅ API Key found: {api_key[:8]}...")
    return True


def run_all_tests():
    """Run all tests and generate a report."""
    import asyncio
    
    print("\n" + "=" * 70)
    print("  CODE DEBUGGER - OPENAI AGENTS SDK TEST SUITE")
    print("=" * 70)
    
    # Check API key
    if not check_api_key():
        print("\n⚠️  Skipping agent tests (no API key)")
        print("\nRunning tool tests only...")
        tool_results = test_tools()
        return {
            'tool_tests': tool_results,
            'agent_tests': 'SKIPPED'
        }
    
    results = {}
    
    # Test 0: Import verification
    results['imports'] = test_agent_imports()
    
    # Test 1: Tools
    results['tools'] = test_tools()
    
    # Test 2: Debug Sleuth
    sleuth_result = asyncio.run(test_debug_sleuth_agent())
    results['debug_sleuth'] = sleuth_result
    
    # Test 3: Solution Architect (depends on Sleuth)
    if sleuth_result.get('success'):
        architect_result = asyncio.run(
            test_solution_architect_agent(sleuth_result['output'])
        )
        results['solution_architect'] = architect_result
    else:
        results['solution_architect'] = 'SKIPPED (Sleuth failed)'
    
    # Test 4: Reliability Engineer (depends on Architect)
    if results['solution_architect'] != 'SKIPPED' and \
       isinstance(results['solution_architect'], dict) and \
       results['solution_architect'].get('success'):
        validator_result = asyncio.run(
            test_reliability_engineer_agent(
                sleuth_result['output'],
                results['solution_architect']['output']
            )
        )
        results['reliability_engineer'] = validator_result
    else:
        results['reliability_engineer'] = 'SKIPPED (Architect failed)'
    
    # Test 5: Full workflow
    print("\n" + "=" * 70)
    print("  Running integration test...")
    print("=" * 70)
    workflow_result = test_full_workflow()
    results['full_workflow'] = workflow_result
    
    # Generate summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for r in results.values() 
                 if r and (r is True or (isinstance(r, dict) and r.get('success'))))
    total = len([r for r in results.values() if r != 'SKIPPED'])
    
    print(f"\nTests Passed: {passed}/{total}")
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        if result is True:
            print(f"   ✅ {test_name}")
        elif result == 'SKIPPED':
            print(f"   ⏭️  {test_name} (skipped)")
        elif isinstance(result, dict):
            status = "✅" if result.get('success') else "❌"
            print(f"   {status} {test_name}")
        else:
            print(f"   ❌ {test_name}")
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
    
    # Save results to file
    results_file = Path(__file__).parent / "test_results.json"
    
    # Convert non-serializable objects
    serializable_results = {}
    for key, value in results.items():
        if isinstance(value, dict):
            serializable_results[key] = {
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                for k, v in value.items()
            }
        else:
            serializable_results[key] = str(value)
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
