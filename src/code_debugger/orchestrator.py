"""
Legacy orchestrator module - kept for backwards compatibility.
New implementation uses OpenAI Agents SDK in agents.py
"""

from .agents import SyncDebuggingOrchestrator as DebuggingOrchestrator, run_sample_debugging_session

__all__ = ['DebuggingOrchestrator', 'run_sample_debugging_session']
