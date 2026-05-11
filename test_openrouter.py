"""
Simple test script to verify OpenRouter API integration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import SyncDebuggingOrchestrator


def test_simple_error():
    """Test with a simple IndexError scenario."""
    print("\n" + "=" * 70)
    print("  OPENROUTER API TEST")
    print("  Testing Multi-Agent Debugging System")
    print("=" * 70)

    # Check for API key
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not set!")
        print("Please check your .env file")
        return False

    print(f"\n✓ API Key found: {api_key[:20]}...")
    print(f"✓ Base URL: {os.environ.get('OPENROUTER_BASE_URL')}")
    print(f"✓ Model: {os.environ.get('OPENROUTER_MODEL')}")

    print("\n" + "=" * 70)
    print("Running Debug Cycle...")
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

    try:
        result = orchestrator.run_full_debugging_cycle(error_context)

        print("\n" + "=" * 70)
        print("  RESULTS")
        print("=" * 70)
        print(f"\n✅ Validation Passed: {result['validation_passed']}")
        print(f"\n📊 Session Summary:")
        summary = orchestrator.get_session_summary()
        print(f"  - Total Agents Run: {summary['total_agents_run']}")
        print(f"  - Agents: {', '.join(summary['agents'])}")

        print(f"\n📄 Final Report:")
        print("-" * 70)
        print(result['final_report'])
        print("-" * 70)

        print("\n✅ TEST PASSED - OpenRouter API is working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_error()
    sys.exit(0 if success else 1)
