#!/usr/bin/env python3
"""Test script to verify the debugger works."""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import SyncDebuggingOrchestrator

def test_basic_functionality():
    """Test basic debugger functionality without API key."""
    print("Testing basic debugger functionality...")
    
    # Create orchestrator
    try:
        orchestrator = SyncDebuggingOrchestrator()
        print("✓ Orchestrator created successfully")
    except Exception as e:
        print(f"✗ Failed to create orchestrator: {e}")
        return False
    
    # Test error context
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
        'failing_file': 'example.py',
        'failing_line': 15,
        'inputs': {'numbers': [1, 2, 3], 'index': 2}
    }
    
    # Try to run debugger (will fail without API key, but we can see if it gets past initialization)
    try:
        result = orchestrator.run_full_debugging_cycle(error_context)
        print("✓ Debugger ran successfully")
        return True
    except Exception as e:
        # Expect this to fail due to missing API key, but not due to initialization issues
        if "API key" in str(e) or "OPENAI_API_KEY" in str(e):
            print("✓ Orchestrator initialization works (failed on API key as expected)")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)