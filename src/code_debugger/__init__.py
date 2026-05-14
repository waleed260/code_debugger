"""
Code Debugger Package — Multi-Agent AI Debugging & Infrastructure Management System

V2 Architecture:
- 10 specialized debug agents + 5 DB agents
- Execution sandbox (multi-language)
- AI-first pipeline with autonomous repair loop
- AST/CFG intelligence layer
- Debugging RAG system
- Patch engine with diff generation
- Observability stack
"""

from .v1_agents import (
    DebugSleuth,
    SolutionArchitect,
    ReliabilityEngineer,
    DebuggingOrchestrator,
    SyncDebuggingOrchestrator,
    handoff_to_fixer,
    handoff_to_validator,
    handoff_back_to_architect,
)
from .main import main, run_sample_debugging_session
from .tools import (
    list_directory_structure,
    read_code_file,
    search_codebase,
    run_shell_command,
    analyze_python_code,
)

# V2 imports
from .orchestrator_v2 import DebuggingOrchestratorV2, DebugSessionConfig, DebugResult
from .sandbox import ExecutionSandbox, Language, ExecutionResult, SandboxFile
from .patch_engine import PatchEngine, FilePatch, PatchSet, PatchResult
from .code_intelligence import ASTAnalyzer
from .rag import DebugRAG
from .test_generator import TestGenerator, TestSuite, GeneratedTest
from .observability import ObservabilityTracker, ObservabilityReport

# V2 agent package
from .agents import (
    StackTraceAgent,
    DependencyAgent,
    RuntimeAgent,
    DataFlowAgent,
    FixGenerationAgent,
    ValidationAgent,
    RegressionAgent,
    SecurityImpactAgent,
    PerformanceImpactAgent,
    RefactorAgent,
)

__all__ = [
    # V1 Agents
    'DebugSleuth',
    'SolutionArchitect',
    'ReliabilityEngineer',
    
    # V2 Agents
    'StackTraceAgent',
    'DependencyAgent',
    'RuntimeAgent',
    'DataFlowAgent',
    'FixGenerationAgent',
    'ValidationAgent',
    'RegressionAgent',
    'SecurityImpactAgent',
    'PerformanceImpactAgent',
    'RefactorAgent',
    
    # Orchestrators
    'DebuggingOrchestrator',
    'SyncDebuggingOrchestrator',
    'DebuggingOrchestratorV2',
    'DebugSessionConfig',
    'DebugResult',
    
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
    'analyze_python_code',
    
    # V2 Modules
    'ExecutionSandbox',
    'Language',
    'ExecutionResult',
    'SandboxFile',
    'PatchEngine',
    'FilePatch',
    'PatchSet',
    'PatchResult',
    'ASTAnalyzer',
    'DebugRAG',
    'TestGenerator',
    'TestSuite',
    'GeneratedTest',
    'ObservabilityTracker',
    'ObservabilityReport',
]

__version__ = '2.0.0'