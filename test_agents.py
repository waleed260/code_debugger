"""
Test script for the Code Debugger multi-agent system.

This script demonstrates how to use the debugging system with various error scenarios.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import SyncDebuggingOrchestrator, DebuggingOrchestrator
import asyncio


def test_index_error():
    """Test with an IndexError scenario."""
    print("\n" + "=" * 70)
    print("TEST 1: IndexError - Array Index Out of Bounds")
    print("=" * 70)
    
    orchestrator = SyncDebuggingOrchestrator()
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "data_processor.py", line 42, in process_batch
    item = items[current_index]
IndexError: list index out of range''',
        'failing_file': 'data_processor.py',
        'failing_line': 42,
        'inputs': {
            'items': [1, 2, 3],
            'current_index': 5
        },
        'codebase_path': '.'
    }
    
    result = orchestrator.run_full_debugging_cycle(error_context)
    
    print("\n✅ Validation Passed:", result['validation_passed'])
    print("📄 Final Report Preview (first 1000 chars):")
    print(result['final_report'][:1000])
    
    return result


def test_key_error():
    """Test with a KeyError scenario."""
    print("\n" + "=" * 70)
    print("TEST 2: KeyError - Missing Dictionary Key")
    print("=" * 70)
    
    orchestrator = SyncDebuggingOrchestrator()
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "config_loader.py", line 18, in get_setting
    return config["database"]["host"]
KeyError: 'host' ''',
        'failing_file': 'config_loader.py',
        'failing_line': 18,
        'inputs': {
            'config': {'database': {'port': 5432}}
        }
    }
    
    result = orchestrator.run_full_debugging_cycle(error_context)
    
    print("\n✅ Validation Passed:", result['validation_passed'])
    return result


def test_type_error():
    """Test with a TypeError scenario."""
    print("\n" + "=" * 70)
    print("TEST 3: TypeError - Wrong Type Operation")
    print("=" * 70)
    
    orchestrator = SyncDebuggingOrchestrator()
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "calculator.py", line 25, in add_numbers
    return a + b
TypeError: can only concatenate str (not "int") to str''',
        'failing_file': 'calculator.py',
        'failing_line': 25,
        'inputs': {
            'a': '10',
            'b': 5
        }
    }
    
    result = orchestrator.run_full_debugging_cycle(error_context)
    
    print("\n✅ Validation Passed:", result['validation_passed'])
    return result


def test_individual_agents():
    """Test running individual agents separately."""
    print("\n" + "=" * 70)
    print("TEST 4: Running Individual Agents")
    print("=" * 70)
    
    orchestrator = SyncDebuggingOrchestrator()
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "utils.py", line 10, in divide
    return numerator / denominator
ZeroDivisionError: division by zero''',
        'failing_file': 'utils.py',
        'failing_line': 10
    }
    
    # Run Debug Sleuth only
    print("\n🔍 Running Debug Sleuth...")
    sleuth_result = orchestrator.run_debug_sleuth(error_context)
    print("Sleuth Analysis Complete")
    print(f"Session History: {orchestrator.get_session_summary()}")
    
    # Run Solution Architect only
    print("\n🔧 Running Solution Architect...")
    architect_result = orchestrator.run_solution_architect(sleuth_result['final_output'])
    print("Architect Fix Complete")
    
    # Run Reliability Engineer only
    print("\n✅ Running Reliability Engineer...")
    validator_result = orchestrator.run_reliability_engineer(
        architect_result['final_output'],
        sleuth_result['final_output']
    )
    print("Validator Complete")
    print(f"Validation Passed: {validator_result['validation_passed']}")
    
    return {
        'sleuth': sleuth_result,
        'architect': architect_result,
        'validator': validator_result
    }


async def test_async():
    """Test async usage of the orchestrator."""
    print("\n" + "=" * 70)
    print("TEST 5: Async Execution")
    print("=" * 70)
    
    orchestrator = DebuggingOrchestrator()
    
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "api_client.py", line 55, in fetch_data
    response = requests.get(url, timeout=timeout)
requests.exceptions.Timeout: HTTPConnectionPool(host='api.example.com', port=80): Read timed out.''',
        'failing_file': 'api_client.py',
        'failing_line': 55
    }
    
    result = await orchestrator.run_full_debugging_cycle(error_context)
    
    print("\n✅ Validation Passed:", result['validation_passed'])
    return result


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("  CODE DEBUGGER - TEST SUITE")
    print("  OpenAI Agents SDK Multi-Agent System")
    print("=" * 70)
    
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nSkipping tests...")
        return
    
    print(f"\n✓ API Key found: {api_key[:8]}...")
    
    results = {
        'test_index_error': None,
        'test_key_error': None,
        'test_type_error': None,
        'test_individual_agents': None,
        'test_async': None
    }
    
    try:
        results['test_index_error'] = test_index_error()
    except Exception as e:
        print(f"\n❌ Test 1 failed: {e}")
    
    try:
        results['test_key_error'] = test_key_error()
    except Exception as e:
        print(f"\n❌ Test 2 failed: {e}")
    
    try:
        results['test_type_error'] = test_type_error()
    except Exception as e:
        print(f"\n❌ Test 3 failed: {e}")
    
    try:
        results['test_individual_agents'] = test_individual_agents()
    except Exception as e:
        print(f"\n❌ Test 4 failed: {e}")
    
    try:
        results['test_async'] = asyncio.run(test_async())
    except Exception as e:
        print(f"\n❌ Test 5 failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r is not None)
    total = len(results)
    
    print(f"\nTests Completed: {passed}/{total}")
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    return results


if __name__ == "__main__":
    run_all_tests()
