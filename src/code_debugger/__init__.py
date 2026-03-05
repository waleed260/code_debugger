"""
Code Debugger Package

Multi-agent debugging system using OpenAI Agents SDK for:
- Root Cause Analysis (Debug Sleuth)
- Fix Generation (Solution Architect)
- Validation & Documentation (Reliability Engineer)
"""

from .agents import (
    DebugSleuth,
    SolutionArchitect,
    ReliabilityEngineer,
    DebuggingOrchestrator,
    SyncDebuggingOrchestrator,
    handoff_to_fixer,
    handoff_to_validator,
    handoff_back_to_architect
)
from .main import main, run_sample_debugging_session
from .tools import (
    list_directory_structure,
    read_code_file,
    search_codebase,
    run_shell_command,
    analyze_python_code
)

__all__ = [
    # Agents
    'DebugSleuth',
    'SolutionArchitect',
    'ReliabilityEngineer',
    
    # Orchestrator
    'DebuggingOrchestrator',
    'SyncDebuggingOrchestrator',
    
    # Handoffs
    'handoff_to_fixer',
    'handoff_to_validator',
    'handoff_back_to_architect',
    
    # Main entry
    'main',
    'run_sample_debugging_session',
    
    # Tools
    'list_directory_structure',
    'read_code_file',
    'search_codebase',
    'run_shell_command',
    'analyze_python_code'
]

__version__ = '0.2.0'