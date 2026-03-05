"""
Simple usage example for the Code Debugger.

This shows the basic usage pattern for debugging errors.
"""

import os

# Make sure to set your API key first
# export OPENAI_API_KEY='your-key-here'

from code_debugger import SyncDebuggingOrchestrator


def main():
    # Create the orchestrator
    orchestrator = SyncDebuggingOrchestrator()
    
    # Define your error context
    error_context = {
        'error_trace': '''Traceback (most recent call last):
  File "my_app.py", line 23, in process_user
    user_name = users[user_id]["name"]
KeyError: 'name' ''',
        'failing_file': 'my_app.py',
        'failing_line': 23,
        'inputs': {
            'user_id': 123,
            'users': {123: {'email': 'user@example.com'}}
        }
    }
    
    # Run the full debugging cycle
    print("🔍 Starting debugging session...")
    result = orchestrator.run_full_debugging_cycle(error_context)
    
    # Print the final report
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result['final_report'])
    
    # Check validation status
    print("\n" + "=" * 60)
    print("VALIDATION STATUS")
    print("=" * 60)
    print(f"Passed: {result['validation_passed']}")
    print(f"Agents used: {[item['agent'] for item in result['session_history']]}")


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  Please set your OPENAI_API_KEY environment variable:")
        print("   export OPENAI_API_KEY='sk-...'")
        exit(1)
    
    main()
