"""
Example usage of the V2 debugging pipeline with autonomous repair loop.
"""

import asyncio
from src.code_debugger import DebuggingOrchestratorV2, DebugSessionConfig


async def main():
    config = DebugSessionConfig(
        enable_sandbox=True,
        enable_rag=True,
        enable_observability=True,
        enable_autonomous_repair=True,
        max_repair_iterations=3,
    )

    orchestrator = DebuggingOrchestratorV2(
        config=config,
        db_path="/tmp/debug_sessions_v2.db",
    )

    result = await orchestrator.run_full_debugging_cycle({
        "error_trace": """Traceback (most recent call last):
  File "example.py", line 15, in calculate_sum
    result = numbers[index] + numbers[index + 1]
IndexError: list index out of range""",
        "failing_file": "example.py",
        "failing_line": 15,
        "codebase_path": ".",
    })

    print("=== DEBUG RESULT ===")
    print(f"Success: {result['success']}")
    print(f"Validation: {'PASS' if result['validation_passed'] else 'FAIL'}")
    print(f"Confidence: {result['confidence_score']:.2%}")
    print(f"Repair Iterations: {result['repair_iterations']}")
    print(f"Agents Used: {len(result['agent_timeline'])}")
    print()
    print(result["final_report"])


if __name__ == "__main__":
    asyncio.run(main())
