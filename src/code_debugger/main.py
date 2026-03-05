"""
Code Debugger CLI - Multi-Agent Debugging System using OpenAI Agents SDK

This module provides the main entry point for the debugging system.
"""

from .agents import SyncDebuggingOrchestrator, DebuggingOrchestrator
import asyncio


def run_sample_debugging_session():
    """Run a sample debugging session to demonstrate the system."""
    print("🚀 Starting sample debugging session...")
    print("=" * 60)
    print("Using OpenAI Agents SDK for multi-agent debugging")
    print("=" * 60)

    orchestrator = SyncDebuggingOrchestrator()

    # Sample error context - this would normally come from an actual error
    sample_error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
        'failing_file': 'example.py',
        'failing_line': 15,
        'inputs': {'numbers': [1, 2, 3], 'index': 2},
        'codebase_path': '.'
    }

    # Run the full debugging cycle
    result = orchestrator.run_full_debugging_cycle(sample_error_context)

    # Print the final report
    print("\n" + "=" * 60)
    print("📋 Final Debugging Report:")
    print("=" * 60)
    print(result['final_report'])
    
    # Print validation status
    print("\n" + "=" * 60)
    print("✅ Validation Status:")
    print("=" * 60)
    print(f"Validation Passed: {result['validation_passed']}")
    print(f"Agents Used: {[item['agent'] for item in result['session_history']]}")

    return result


async def run_sample_debugging_session_async():
    """Run a sample debugging session asynchronously."""
    print("🚀 Starting sample debugging session (async)...")
    print("=" * 60)

    orchestrator = DebuggingOrchestrator()

    sample_error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
        'failing_file': 'example.py',
        'failing_line': 15,
        'inputs': {'numbers': [1, 2, 3], 'index': 2},
        'codebase_path': '.'
    }

    result = await orchestrator.run_full_debugging_cycle(sample_error_context)

    print("\n" + "=" * 60)
    print("📋 Final Debugging Report:")
    print("=" * 60)
    print(result['final_report'])
    
    print("\n" + "=" * 60)
    print("✅ Validation Status:")
    print("=" * 60)
    print(f"Validation Passed: {result['validation_passed']}")

    return result


def main():
    """Main entry point for the code-debugger CLI."""
    print("=" * 60)
    print("  Code Debugger - Multi-Agent Root Cause Analysis System")
    print("  Powered by OpenAI Agents SDK")
    print("=" * 60)
    print()
    
    run_sample_debugging_session()


if __name__ == "__main__":
    main()
