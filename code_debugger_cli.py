#!/usr/bin/env python3
"""
CLI interface for the Multi-Agent Debugging System.

This script provides a command-line interface to the three-agent debugging system:
1. Debug Sleuth (Root Cause Analysis)
2. Solution Architect (The Fixer)
3. Reliability Engineer (The Validator)
"""

import argparse
import sys
import traceback
from pathlib import Path
from src.code_debugger.orchestrator import DebuggingOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Debugging System - Root Cause Analysis & Fix Generation"
    )
    parser.add_argument(
        "--error-file",
        type=str,
        help="Path to file containing error trace/output"
    )
    parser.add_argument(
        "--failing-file",
        type=str,
        help="Path to the file that's failing"
    )
    parser.add_argument(
        "--failing-line",
        type=int,
        help="Line number where the error occurred"
    )
    parser.add_argument(
        "--error-message",
        type=str,
        help="Direct error message/stack trace"
    )
    parser.add_argument(
        "--run-sample",
        action="store_true",
        help="Run a sample debugging session"
    )
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="List all debugging sessions in the database"
    )
    parser.add_argument(
        "--session-report",
        type=str,
        help="Get report for a specific session ID"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="debug_sessions.db",
        help="Path to the SQLite database (default: debug_sessions.db)"
    )

    args = parser.parse_args()

    try:
        orchestrator = DebuggingOrchestrator(db_path=args.db_path)

        if args.run_sample:
            # Run a sample debugging session
            print("🚀 Running sample debugging session...")
            result = orchestrator.run_full_debugging_cycle({
                'error_trace': '''Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range''',
                'failing_file': 'example.py',
                'failing_line': 15,
                'inputs': {'numbers': [1, 2, 3], 'index': 2}
            })
            print("\n📋 Sample Session Report:")
            print(result['complete_report'])

        elif args.list_sessions:
            # List all sessions
            sessions = orchestrator.list_all_sessions()
            print(f"📁 Found {len(sessions)} debugging sessions:")
            for session in sessions:
                print(f"  • {session['session_id']} - {session['created_at']} - {session['status']}")

        elif args.session_report:
            # Get report for specific session
            report = orchestrator.get_session_report(args.session_report)
            print(f"📋 Report for session {args.session_report}:")
            print(f"Interactions: {report['interactions_count']}")
            print(f"Bugs found: {report['bugs_found']}")

            for bug in report['bugs']:
                print(f"\nBug ID: {bug['id']}")
                print(f"Description: {bug['bug_description'][:100]}...")
                print(f"Status: {bug['status']}")

        elif args.error_file or args.error_message:
            # Run debugging on provided error
            error_trace = args.error_message
            if args.error_file:
                with open(args.error_file, 'r') as f:
                    error_trace = f.read()

            failing_file = args.failing_file or ""
            failing_line = args.failing_line

            error_context = {
                'error_trace': error_trace,
                'failing_file': failing_file,
                'failing_line': failing_line
            }

            print("🚀 Starting debugging session...")
            result = orchestrator.run_full_debugging_cycle(error_context)
            print("\n📋 Debugging Report:")
            print(result['complete_report'])

        else:
            print("❌ No command specified. Use --help for usage information.")
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running debugger: {str(e)}")
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()