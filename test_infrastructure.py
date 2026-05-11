"""
Test script for Infrastructure Management Multi-Agent System
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger.infra_orchestrator import SyncInfrastructureOrchestrator


def test_infrastructure_analyzer():
    """Test Infrastructure Analyzer agent."""
    print("\n" + "=" * 70)
    print("TEST 1: Infrastructure Analyzer")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_infrastructure_analysis()

    print("\n✅ Infrastructure Analysis Complete")
    print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])


def test_security_auditor():
    """Test Security Auditor agent."""
    print("\n" + "=" * 70)
    print("TEST 2: Security Auditor")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_security_audit()

    print("\n✅ Security Audit Complete")
    print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])


def test_performance_optimizer():
    """Test Performance Optimizer agent."""
    print("\n" + "=" * 70)
    print("TEST 3: Performance Optimizer")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_performance_optimization()

    print("\n✅ Performance Optimization Complete")
    print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])


def test_cost_manager():
    """Test Cost Manager agent."""
    print("\n" + "=" * 70)
    print("TEST 4: Cost Manager")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_cost_analysis()

    print("\n✅ Cost Analysis Complete")
    print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])


def test_incident_responder():
    """Test Incident Responder agent."""
    print("\n" + "=" * 70)
    print("TEST 5: Incident Responder")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_incident_response()

    print("\n✅ Incident Response Complete")
    print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])


def test_full_audit():
    """Test full infrastructure audit with all agents."""
    print("\n" + "=" * 70)
    print("TEST 6: Full Infrastructure Audit (All 5 Agents)")
    print("=" * 70)

    orchestrator = SyncInfrastructureOrchestrator()
    result = orchestrator.run_full_infrastructure_audit()

    print("\n✅ Full Audit Complete")
    print(f"\nAgents Run: {len(result['session_history'])}")
    print(f"Agents: {[item['agent'] for item in result['session_history']]}")


def run_all_tests():
    """Run all infrastructure agent tests."""
    print("\n" + "=" * 70)
    print("  INFRASTRUCTURE MANAGEMENT - TEST SUITE")
    print("  Multi-Agent Infrastructure Monitoring System")
    print("=" * 70)

    # Check for API key
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("\n⚠️  WARNING: OPENROUTER_API_KEY not set!")
        print("Please set your OpenRouter API key in .env file")
        print("\nSkipping tests...")
        return

    print(f"\n✓ API Key found: {api_key[:20]}...")

    tests = [
        ("Infrastructure Analyzer", test_infrastructure_analyzer),
        ("Security Auditor", test_security_auditor),
        ("Performance Optimizer", test_performance_optimizer),
        ("Cost Manager", test_cost_manager),
        ("Incident Responder", test_incident_responder),
        ("Full Audit", test_full_audit)
    ]

    results = {}

    for name, test_func in tests:
        try:
            test_func()
            results[name] = True
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTests Completed: {passed}/{total}")

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    return results


if __name__ == "__main__":
    run_all_tests()
