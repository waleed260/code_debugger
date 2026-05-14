"""
Infrastructure Management Orchestrator

Coordinates all 5 infrastructure agents to provide comprehensive infrastructure management.
"""

from typing import Dict, Any, List
import asyncio
import concurrent.futures
import threading
from .infra_agents import (
    InfrastructureAnalyzer,
    SecurityAuditor,
    PerformanceOptimizer,
    CostManager,
    IncidentResponder
)
from agents import Runner


class InfrastructureOrchestrator:
    """Orchestrates infrastructure management agents."""

    def __init__(self):
        self.session_history: List[Dict[str, Any]] = []

    async def run_infrastructure_analysis(self) -> Dict[str, Any]:
        """Run infrastructure analysis."""
        print("🏗️ Infrastructure Analyzer: Analyzing system...")

        prompt = """
        Perform a comprehensive infrastructure analysis:
        1. Check system resources (CPU, memory, disk, network)
        2. Check running processes
        3. Check Docker containers if available
        4. Analyze network connections
        5. Provide health score and recommendations
        """

        result = await Runner.run(InfrastructureAnalyzer, prompt)

        analysis = {
            'agent': 'InfrastructureAnalyzer',
            'output': result.final_output
        }

        self.session_history.append(analysis)
        return analysis

    async def run_security_audit(self) -> Dict[str, Any]:
        """Run security audit."""
        print("🔒 Security Auditor: Performing security audit...")

        prompt = """
        Perform a comprehensive security audit:
        1. Scan for open ports on localhost
        2. Check network connections for suspicious activity
        3. Provide security score and recommendations
        4. Identify critical vulnerabilities
        """

        result = await Runner.run(SecurityAuditor, prompt)

        audit = {
            'agent': 'SecurityAuditor',
            'output': result.final_output
        }

        self.session_history.append(audit)
        return audit

    async def run_performance_optimization(self) -> Dict[str, Any]:
        """Run performance optimization analysis."""
        print("⚡ Performance Optimizer: Analyzing performance...")

        prompt = """
        Perform performance optimization analysis:
        1. Check system resources for bottlenecks
        2. Identify resource-hungry processes
        3. Analyze Docker container performance
        4. Provide optimization recommendations with expected gains
        """

        result = await Runner.run(PerformanceOptimizer, prompt)

        optimization = {
            'agent': 'PerformanceOptimizer',
            'output': result.final_output
        }

        self.session_history.append(optimization)
        return optimization

    async def run_cost_analysis(self) -> Dict[str, Any]:
        """Run cost analysis."""
        print("💰 Cost Manager: Analyzing costs...")

        prompt = """
        Perform cost analysis:
        1. Check resource utilization
        2. Identify underutilized resources
        3. Find idle processes
        4. Provide cost optimization recommendations
        """

        result = await Runner.run(CostManager, prompt)

        cost_analysis = {
            'agent': 'CostManager',
            'output': result.final_output
        }

        self.session_history.append(cost_analysis)
        return cost_analysis

    async def run_incident_response(self, incident_description: str = None) -> Dict[str, Any]:
        """Run incident response."""
        print("🚨 Incident Responder: Analyzing incident...")

        if incident_description:
            prompt = f"""
            Respond to the following incident:
            {incident_description}

            1. Assess severity
            2. Check system resources
            3. Analyze logs if available
            4. Provide immediate mitigation steps
            5. Recommend prevention measures
            """
        else:
            prompt = """
            Perform proactive incident detection:
            1. Check system health
            2. Monitor resource usage
            3. Check for anomalies
            4. Identify potential issues before they become incidents
            """

        result = await Runner.run(IncidentResponder, prompt)

        response = {
            'agent': 'IncidentResponder',
            'output': result.final_output
        }

        self.session_history.append(response)
        return response

    async def run_full_infrastructure_audit(self) -> Dict[str, Any]:
        """Run complete infrastructure audit with all agents."""
        print("\n" + "="*70)
        print("🚀 Starting Full Infrastructure Audit")
        print("="*70 + "\n")

        # Run all agents
        infra_analysis = await self.run_infrastructure_analysis()
        security_audit = await self.run_security_audit()
        performance_opt = await self.run_performance_optimization()
        cost_analysis = await self.run_cost_analysis()
        incident_check = await self.run_incident_response()

        print("\n" + "="*70)
        print("✅ Full Infrastructure Audit Complete")
        print("="*70 + "\n")

        return {
            'infrastructure_analysis': infra_analysis,
            'security_audit': security_audit,
            'performance_optimization': performance_opt,
            'cost_analysis': cost_analysis,
            'incident_response': incident_check,
            'session_history': self.session_history
        }


def _run_async(coro):
    """Run an async coroutine from a synchronous context, safely handling running event loops."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(lambda: asyncio.run(coro))
            return future.result()
    else:
        return asyncio.run(coro)


class SyncInfrastructureOrchestrator(InfrastructureOrchestrator):
    """Synchronous wrapper for InfrastructureOrchestrator."""

    def run_infrastructure_analysis(self) -> Dict[str, Any]:
        return _run_async(super().run_infrastructure_analysis())

    def run_security_audit(self) -> Dict[str, Any]:
        return _run_async(super().run_security_audit())

    def run_performance_optimization(self) -> Dict[str, Any]:
        return _run_async(super().run_performance_optimization())

    def run_cost_analysis(self) -> Dict[str, Any]:
        return _run_async(super().run_cost_analysis())

    def run_incident_response(self, incident_description: str = None) -> Dict[str, Any]:
        return _run_async(super().run_incident_response(incident_description))

    def run_full_infrastructure_audit(self) -> Dict[str, Any]:
        return _run_async(super().run_full_infrastructure_audit())
