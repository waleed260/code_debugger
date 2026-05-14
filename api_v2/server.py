"""
FastAPI Server — Async-native API with websocket streaming

Vercel-ready: mounts all routes under /v2 prefix for proper URL routing.
"""

import os
import sys
import json
import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_debugger import DebuggingOrchestratorV2, DebugSessionConfig
from code_debugger.observability import ObservabilityTracker
from code_debugger.sandbox import ExecutionSandbox, Language


app = FastAPI(
    title="Code Debugger API",
    description="Autonomous multi-language AI debugging platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrator = None
_observability = ObservabilityTracker()

router = APIRouter(prefix="/v2")


def get_orchestrator() -> DebuggingOrchestratorV2:
    global _orchestrator
    if _orchestrator is None:
        config = DebugSessionConfig(
            enable_sandbox=True,
            enable_rag=True,
            enable_observability=True,
            enable_autonomous_repair=True,
        )
        _orchestrator = DebuggingOrchestratorV2(
            config=config,
            db_path="/tmp/debug_sessions_v2.db",
        )
    return _orchestrator


class DebugRequest(BaseModel):
    error_trace: str = Field(..., description="Error trace or stack trace")
    failing_file: str = Field("unknown", description="Path to the failing file")
    failing_line: Optional[int] = Field(None, description="Line number of the error")
    codebase_path: str = Field(".", description="Project root path")
    language: Optional[str] = Field(None, description="Programming language (auto-detected if omitted)")
    enable_sandbox: bool = Field(True, description="Execute code in sandbox for validation")
    enable_repair_loop: bool = Field(True, description="Enable autonomous repair iterations")


class DebugResponse(BaseModel):
    success: bool
    session_id: str
    validation_passed: bool
    confidence_score: float
    repair_iterations: int
    agent_timeline: List[Dict[str, Any]]
    final_report: str
    diff: Optional[str] = None
    root_cause: Optional[str] = None
    fix_proposal: Optional[str] = None


class IncidentRequest(BaseModel):
    description: str = Field(..., description="Incident description")


@router.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=INDEX_HTML)


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "code-debugger-v2",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/debug", response_model=DebugResponse)
async def debug(req: DebugRequest):
    orchestrator = get_orchestrator()
    error_context = {
        "error_trace": req.error_trace,
        "failing_file": req.failing_file,
        "failing_line": req.failing_line,
        "codebase_path": req.codebase_path,
        "language": req.language,
    }
    result = await orchestrator.run_full_debugging_cycle(error_context)
    return DebugResponse(
        success=result.get("success", False),
        session_id=result.get("session_id", ""),
        validation_passed=result.get("validation_passed", False),
        confidence_score=result.get("confidence_score", 0.0),
        repair_iterations=result.get("repair_iterations", 0),
        agent_timeline=result.get("agent_timeline", []),
        final_report=result.get("final_report", ""),
        diff=result.get("diff"),
        root_cause=result.get("root_cause"),
        fix_proposal=result.get("fix_proposal"),
    )


@router.get("/metrics")
async def get_metrics():
    report = _observability.get_report()
    return {
        "total_sessions": report.total_sessions,
        "success_rate": report.success_rate,
        "avg_duration_ms": report.avg_duration_ms,
        "total_tokens": report.total_tokens,
        "agent_stats": report.agent_stats,
        "error_distribution": report.error_distribution,
        "top_errors": report.top_errors,
    }


@router.get("/agents")
async def list_agents():
    return {
        "debug_agents": [
            {"name": "StackTraceAgent", "role": "Traceback parsing"},
            {"name": "DependencyAgent", "role": "Dependency analysis"},
            {"name": "RuntimeAgent", "role": "Runtime state analysis"},
            {"name": "DataFlowAgent", "role": "Data flow tracing"},
            {"name": "FixGenerationAgent", "role": "Fix generation"},
            {"name": "ValidationAgent", "role": "Fix validation"},
            {"name": "RegressionAgent", "role": "Regression detection"},
            {"name": "SecurityImpactAgent", "role": "Security analysis"},
            {"name": "PerformanceImpactAgent", "role": "Performance analysis"},
            {"name": "RefactorAgent", "role": "Code quality improvement"},
        ],
        "infra_agents": [
            {"name": "Infrastructure Analyzer", "role": "System health"},
            {"name": "Security Auditor", "role": "Security scanning"},
            {"name": "Performance Optimizer", "role": "Performance tuning"},
            {"name": "Cost Manager", "role": "Cost optimization"},
            {"name": "Incident Responder", "role": "Incident response"},
        ],
        "db_agents": [
            {"name": "SQLQueryOptimizer", "role": "SQL optimization"},
            {"name": "MigrationValidator", "role": "Migration safety"},
            {"name": "SchemaAnalyzer", "role": "Schema analysis"},
            {"name": "TransactionAgent", "role": "Transaction analysis"},
            {"name": "ORMMapperAgent", "role": "ORM optimization"},
        ],
    }


@router.websocket("/ws/debug")
async def websocket_debug(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        error_trace = data.get("error_trace", "")
        failing_file = data.get("failing_file", "unknown")

        await websocket.send_json({"type": "status", "stage": "starting", "message": "Starting multi-agent debugging pipeline..."})

        orchestrator = get_orchestrator()

        await websocket.send_json({"type": "status", "stage": "enrichment", "message": "Stage 1/4: Fast pattern detection & RAG enrichment..."})
        await asyncio.sleep(0.5)

        await websocket.send_json({"type": "status", "stage": "analysis", "message": "Stage 2/4: Running 10 specialized agents for root cause analysis..."})
        await asyncio.sleep(0.5)

        await websocket.send_json({"type": "status", "stage": "agents", "agents": [
            "StackTraceAgent", "DependencyAgent", "RuntimeAgent", "DataFlowAgent",
            "FixGenerationAgent", "ValidationAgent", "RegressionAgent",
            "SecurityImpactAgent", "PerformanceImpactAgent", "RefactorAgent",
        ]})
        await asyncio.sleep(0.5)

        result = await orchestrator.run_full_debugging_cycle({
            "error_trace": error_trace,
            "failing_file": failing_file,
            "codebase_path": data.get("codebase_path", "."),
        })

        await websocket.send_json({
            "type": "result",
            "success": result.get("success", False),
            "validation_passed": result.get("validation_passed", False),
            "confidence_score": result.get("confidence_score", 0.0),
            "repair_iterations": result.get("repair_iterations", 0),
            "final_report": result.get("final_report", ""),
            "diff": result.get("diff", ""),
        })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


app.include_router(router)


INDEX_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<meta name="theme-color" content="#06080f">
<title>Code Debugger v2 — Autonomous AI Debugging Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg-deep:#06080f;--surface:#0F172A;--elevated:#1E293B;--hoverbg:#273549;--border:#334155;--border-glow:rgba(34,197,94,0.35);--text:#F8FAFC;--secondary:#94A3B8;--muted:#64748B;--accent:#22C55E;--accent-dim:rgba(34,197,94,0.12);--accent-b:#06B6D4;--accent-b-dim:rgba(6,182,212,0.12);--accent-c:#F59E0B;--accent-c-dim:rgba(245,158,11,0.12);--danger:#EF4444;--danger-dim:rgba(239,68,68,0.12);--font:'JetBrains Mono',monospace;--radius-sm:4px;--radius-md:8px;--radius-lg:16px;--ease:0.2s cubic-bezier(0.16,1,0.3,1)}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg-deep);color:var(--text);min-height:100vh;line-height:1.7;overflow-x:hidden;-webkit-font-smoothing:antialiased;font-size:14px;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
::selection{background:var(--accent);color:var(--bg-deep)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:var(--radius-sm)}
.bg-grid{position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0}
.bg-glow{position:fixed;width:600px;height:600px;border-radius:50%;filter:blur(140px);pointer-events:none;z-index:0;opacity:0.06}
.bg-glow-1{top:-250px;left:-150px;background:var(--accent)}
.bg-glow-2{bottom:-250px;right:-150px;background:var(--accent-b)}
.container{max-width:1040px;margin:0 auto;padding:40px 20px 64px;position:relative;z-index:1}

/* Header */
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:36px;padding-bottom:16px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:12px}
.header-left h1{font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:500;text-transform:uppercase;letter-spacing:-0.01em;line-height:1.3}
.header-left h1 em{font-style:normal;color:var(--accent)}
.header-left .tagline{font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.12em;margin-top:2px}
.header-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:var(--accent-dim);border:1px solid rgba(34,197,94,0.25);border-radius:20px;font-size:0.6rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.08em;font-weight:500}

/* Pipeline visualization */
.pipeline{display:flex;gap:8px;margin-bottom:32px;overflow-x:auto;padding-bottom:4px}
.pipe-step{display:flex;align-items:center;gap:8px;flex-shrink:0}
.pipe-node{display:flex;align-items:center;gap:6px;padding:8px 14px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-md);font-size:0.65rem;color:var(--muted);transition:all var(--ease);white-space:nowrap}
.pipe-node.active{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.pipe-node.done{border-color:var(--accent);color:var(--accent);opacity:0.6}
.pipe-arrow{color:var(--border);font-size:0.7rem;flex-shrink:0}

/* Card */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);margin-bottom:20px;position:relative}
.card-header{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:8px}
.card-header-label{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);font-weight:500}
.card-body{padding:24px}
.card-tabs{display:flex;gap:0;border-bottom:1px solid var(--border);padding:0 24px}
.tab-btn{background:none;border:none;border-bottom:2px solid transparent;padding:12px 18px;font-family:var(--font);font-size:0.68rem;font-weight:500;color:var(--muted);cursor:pointer;transition:color var(--ease),border-color var(--ease);letter-spacing:0.04em}
.tab-btn:hover{color:var(--secondary)}
.tab-btn.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab-content{display:none}
.tab-content.active{display:block}

/* Form */
.form-group{margin-bottom:18px}
label{display:block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:6px;cursor:pointer;font-weight:500}
label .req{color:var(--accent-b)}
textarea,input[type=text],input[type=number]{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 14px;font-family:var(--font);font-size:0.78rem;color:var(--text);transition:border-color var(--ease),box-shadow var(--ease)}
textarea:focus,input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-dim)}
textarea::placeholder,input::placeholder{color:var(--muted)}
textarea{min-height:140px;resize:vertical;line-height:1.7;font-size:0.72rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}

/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:13px 24px;background:var(--accent);color:var(--bg-deep);font-family:var(--font);font-size:0.75rem;font-weight:500;border:none;border-radius:var(--radius-sm);cursor:pointer;transition:box-shadow var(--ease),transform var(--ease),opacity var(--ease);letter-spacing:0.02em}
.btn:hover{box-shadow:0 0 24px var(--border-glow);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:0.3;cursor:not-allowed;transform:none;box-shadow:none}
.btn svg{width:15px;height:15px;flex-shrink:0}

/* Agent grid */
.agent-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.agent-chip{display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--elevated);border:1px solid var(--border);border-radius:var(--radius-md);transition:border-color var(--ease);font-size:0.68rem}
.agent-chip .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;background:var(--muted)}
.agent-chip .dot.idle{background:var(--muted)}
.agent-chip .dot.active{background:var(--accent);box-shadow:0 0 8px var(--accent);animation:pulse 1.2s ease-in-out infinite}
.agent-chip .dot.done{background:var(--accent)}
.agent-chip .dot.error{background:var(--danger)}
.agent-chip .name{color:var(--secondary);font-weight:500}
.agent-chip .role{color:var(--muted);font-size:0.6rem;margin-left:auto}
.agent-chip.done{border-color:rgba(34,197,94,0.2)}
.agent-chip.active{border-color:var(--accent);background:var(--accent-dim)}
.agent-chip.error{border-color:var(--danger);background:var(--danger-dim)}

/* Results */
.result-timeline{position:relative;padding:0;margin:16px 0}
.tl-item{display:flex;gap:14px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)}
.tl-item:last-child{border:none}
.tl-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:5px}
.tl-dot.green{background:var(--accent)}
.tl-dot.cyan{background:var(--accent-b)}
.tl-dot.amber{background:var(--accent-c)}
.tl-dot.red{background:var(--danger)}
.tl-content{flex:1}
.tl-name{font-size:0.72rem;font-weight:500;color:var(--secondary)}
.tl-dur{font-size:0.6rem;color:var(--muted);margin-top:1px}
.tl-msg{font-size:0.68rem;color:var(--muted);margin-top:2px}

/* Metrics row */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:16px 0}
.metric{background:var(--elevated);border:1px solid var(--border);border-radius:var(--radius-md);padding:14px;text-align:center}
.metric .val{font-size:1.4rem;font-weight:600;color:var(--accent);line-height:1.2}
.metric .lbl{font-size:0.58rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-top:4px}

/* Diff output */
.diff-view{background:var(--bg-deep);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;font-size:0.68rem;line-height:1.6;overflow-x:auto;max-height:400px;overflow-y:auto;color:var(--secondary);white-space:pre-wrap;font-family:var(--font)}
.diff-view .add{color:var(--accent)}
.diff-view .del{color:var(--danger)}
.diff-view .info{color:var(--accent-b)}

/* Result section */
.result-section{margin-bottom:20px}
.result-section:last-child{margin-bottom:0}
.rhead{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.rhead svg{width:14px;height:14px;flex-shrink:0}
.rhead .rn{font-size:0.7rem;font-weight:500;color:var(--secondary);text-transform:uppercase;letter-spacing:0.06em}
.rbody{background:var(--elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px 16px;font-size:0.7rem;line-height:1.7;white-space:pre-wrap;max-height:360px;overflow-y:auto;color:var(--secondary)}

/* Badge */
.badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:12px;font-size:0.6rem;font-weight:500;text-transform:uppercase;letter-spacing:0.04em}
.badge.pass{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(34,197,94,0.25)}
.badge.fail{background:var(--danger-dim);color:var(--danger);border:1px solid rgba(239,68,68,0.25)}
.badge svg{width:9px;height:9px}

/* Loading overlay */
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(6,8,15,0.94);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:28px;overscroll-behavior:contain}
.loading-overlay.active{display:flex}
.loading-cursor{width:12px;height:18px;background:var(--accent);animation:cursorBlink 0.9s step-end infinite}
@keyframes cursorBlink{0%,100%{opacity:1}50%{opacity:0}}
.loading-text{font-size:0.8rem;color:var(--secondary);text-align:center;line-height:2}
.loading-text span{color:var(--accent)}
.loading-steps{display:flex;gap:28px;margin-top:6px;flex-wrap:wrap;justify-content:center}
.loading-step{font-size:0.65rem;color:var(--muted);opacity:0.3;transition:opacity 0.3s;display:flex;align-items:center;gap:5px}
.loading-step.active{color:var(--accent);opacity:1}

/* Agents showcase */
.agents-showcase{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:6px}
.agent-card{border:1px solid var(--border);border-radius:var(--radius-md);padding:16px;transition:border-color var(--ease),transform var(--ease);display:flex;flex-direction:column}
.agent-card:hover{border-color:var(--accent);transform:translateY(-2px)}
.agent-card .ac{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;font-weight:500}
.agent-card .ad{font-size:0.62rem;color:var(--muted);line-height:1.5;flex:1}
.agent-card:nth-child(1) .ac{color:var(--accent)}
.agent-card:nth-child(2) .ac{color:var(--accent-b)}
.agent-card:nth-child(3) .ac{color:var(--accent-c)}
.agent-card:nth-child(4) .ac{color:var(--accent)}
.agent-card:nth-child(5) .ac{color:var(--accent-b)}
.agent-card:nth-child(6) .ac{color:var(--accent-c)}
.agent-card:nth-child(7) .ac{color:var(--danger)}
.agent-card:nth-child(8) .ac{color:var(--accent)}
.agent-card:nth-child(9) .ac{color:var(--accent-b)}
.agent-card:nth-child(10) .ac{color:var(--accent-c)}

/* Sandbox languages */
.lang-chips{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}
.lang-chip{padding:3px 10px;background:var(--elevated);border:1px solid var(--border);border-radius:10px;font-size:0.6rem;color:var(--muted)}

/* Error */
.err{display:none;margin-top:14px;background:var(--danger-dim);border:1px solid rgba(239,68,68,0.2);border-radius:var(--radius-sm);padding:12px 16px;color:var(--danger);font-size:0.72rem;line-height:1.5;align-items:flex-start;gap:8px}
.err.active{display:flex}

/* Nav link */
.nav-link{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:0.65rem;color:var(--secondary);transition:color var(--ease),border-color var(--ease);text-decoration:none;margin-top:8px}
.nav-link:hover{color:var(--accent);border-color:var(--accent);text-decoration:none}

/* Footer */
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
footer p{font-size:0.55rem;color:var(--muted);letter-spacing:0.08em}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.7;transform:scale(0.85)}}
.af{animation:fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) backwards}
.ad1{animation-delay:0.05s}.ad2{animation-delay:0.1s}.ad3{animation-delay:0.15s}.ad4{animation-delay:0.2s}.ad5{animation-delay:0.25s}.ad6{animation-delay:0.3s}
@media(prefers-reduced-motion:reduce){*, .af{animation:none!important;transition-duration:0.01ms!important}html{scroll-behavior:auto}}

@media(max-width:768px){
.container{padding:24px 14px 48px}
.agents-showcase{grid-template-columns:repeat(2,1fr)}
.form-row{grid-template-columns:1fr}
.agent-grid{grid-template-columns:1fr}
.loading-steps{flex-direction:column;gap:6px}
.metrics{grid-template-columns:repeat(2,1fr)}
header{flex-direction:column;align-items:flex-start}
.card-body{padding:18px}
}
</style>
</head>
<body>
<div class="bg-grid" aria-hidden="true"></div>
<div class="bg-glow bg-glow-1" aria-hidden="true"></div>
<div class="bg-glow bg-glow-2" aria-hidden="true"></div>

<div class="container">
<header class="af">
<div class="header-left">
<h1>code <em>debugger</em> v2</h1>
<p class="tagline">Autonomous Multi-Language AI Debugging Platform</p>
</div>
<div class="header-badge">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
10 Specialized Agents
</div>
</header>

<div class="pipeline af ad1" role="tablist" aria-label="Pipeline stages">
<div class="pipe-step"><div class="pipe-node" data-stage="enrichment"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Parse & Enrich</div><span class="pipe-arrow">→</span></div>
<div class="pipe-step"><div class="pipe-node" data-stage="agents"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>10-Agent RCA</div><span class="pipe-arrow">→</span></div>
<div class="pipe-step"><div class="pipe-node" data-stage="sandbox"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>Sandbox Execute</div><span class="pipe-arrow">→</span></div>
<div class="pipe-step"><div class="pipe-node" data-stage="repair"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>Repair Loop</div></div>
</div>

<div class="card af ad2">
<div class="card-header"><span class="card-header-label">// error_input</span><span style="font-size:0.6rem;color:var(--muted)">Ctrl+Enter to submit</span></div>
<div class="card-body">
<form id="debugForm" novalidate>
<div class="form-group">
<label for="errorTrace">Error Trace / Stack Trace <span class="req">*</span></label>
<textarea id="errorTrace" autocomplete="off" spellcheck="false" placeholder="Paste error trace here...">Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = process_data(data)
  File "app.py", line 5, in process_data
    return items[index] + items[index + 1]
IndexError: list index out of range</textarea>
</div>
<div class="form-row">
<div class="form-group">
<label for="failingFile">Failing File</label>
<input type="text" id="failingFile" autocomplete="off" spellcheck="false" placeholder="path/to/file.py" value="app.py">
</div>
<div class="form-group">
<label for="failingLine">Failing Line</label>
<input type="number" id="failingLine" autocomplete="off" placeholder="42" value="5">
</div>
</div>
</form>
<div class="err" id="errorMsg" role="alert">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
<span id="errorText"></span>
</div>
<button type="button" class="btn" id="debugBtn">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
Run V2 Debugging Pipeline
</button>
</div>
</div>

<div class="card af ad3" style="display:none" id="resultsCard">
<div class="card-header">
<span class="card-header-label">// analysis_report</span>
<span class="badge" id="statusBadge" role="status"></span>
</div>
<div class="card-tabs" role="tablist">
<button class="tab-btn active" role="tab" aria-selected="true" data-tab="tab-report">Report</button>
<button class="tab-btn" role="tab" aria-selected="false" data-tab="tab-agents">Agents</button>
<button class="tab-btn" role="tab" aria-selected="false" data-tab="tab-diff">Diff</button>
<button class="tab-btn" role="tab" aria-selected="false" data-tab="tab-security">Security</button>
<button class="tab-btn" role="tab" aria-selected="false" data-tab="tab-regression">Regression</button>
</div>
<div class="card-body">
<div class="tab-content active" id="tab-report">
<div class="metrics" id="metrics"></div>
<div class="result-section">
<div class="rhead"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg><span class="rn">Full Report</span></div>
<pre class="rbody" id="reportContent"></pre>
</div>
</div>
<div class="tab-content" id="tab-agents">
<div class="result-section">
<div class="rhead"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg><span class="rn">Agent Timeline</span></div>
<div class="result-timeline" id="agentTimeline"></div>
</div>
</div>
<div class="tab-content" id="tab-diff">
<div class="result-section">
<div class="rhead"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg><span class="rn">Code Diff</span></div>
<pre class="diff-view" id="diffContent"><span class="info">// No diff generated (run debug first)</span></pre>
</div>
</div>
<div class="tab-content" id="tab-security">
<div class="result-section">
<div class="rhead"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><span class="rn">Security Assessment</span></div>
<pre class="rbody" id="securityContent"><span class="info">// Security analysis will appear here</span></pre>
</div>
</div>
<div class="tab-content" id="tab-regression">
<div class="result-section">
<div class="rhead"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><span class="rn">Regression Check</span></div>
<pre class="rbody" id="regressionContent"><span class="info">// Regression analysis will appear here</span></pre>
</div>
</div>
</div>
</div>

<section class="af ad4" style="margin-top:32px">
<h2 style="font-size:0.8rem;font-weight:500;margin-bottom:14px;color:var(--secondary);text-transform:uppercase;letter-spacing:0.08em">10 Specialized Agents</h2>
<div class="agents-showcase">
<div class="agent-card"><span class="ac">01 StackTrace</span><span class="ad">Parse traceback, extract error type, location, and call chain</span></div>
<div class="agent-card"><span class="ac">02 Dependency</span><span class="ad">Detect package conflicts, version issues, import chains</span></div>
<div class="agent-card"><span class="ac">03 Runtime</span><span class="ad">Analyze runtime state, identify None propagation patterns</span></div>
<div class="agent-card"><span class="ac">04 DataFlow</span><span class="ad">Trace variable corruption and data flow paths</span></div>
<div class="agent-card"><span class="ac">05 FixGen</span><span class="ad">Generate candidate fixes with multi-approach strategy</span></div>
<div class="agent-card"><span class="ac">06 Validation</span><span class="ad">Execute tests, run linting, verify fix correctness</span></div>
<div class="agent-card"><span class="ac">07 Regression</span><span class="ad">Detect side effects, signature changes, risk patterns</span></div>
<div class="agent-card"><span class="ac">08 Security</span><span class="ad">Scan for injections, secrets, insecure patterns</span></div>
<div class="agent-card"><span class="ac">09 Performance</span><span class="ad">Detect bottlenecks, estimate fix performance impact</span></div>
<div class="agent-card"><span class="ac">10 Refactor</span><span class="ad">Detect code smells, suggest type hints, improve quality</span></div>
</div>

<div style="margin-top:20px">
<h2 style="font-size:0.8rem;font-weight:500;margin-bottom:10px;color:var(--secondary);text-transform:uppercase;letter-spacing:0.08em">Execution Sandbox</h2>
<div class="lang-chips">
<span class="lang-chip">Python</span>
<span class="lang-chip">JavaScript</span>
<span class="lang-chip">TypeScript</span>
<span class="lang-chip">Go</span>
<span class="lang-chip">Rust</span>
<span class="lang-chip">Java</span>
<span class="lang-chip">C++</span>
<span class="lang-chip">Ruby</span>
<span class="lang-chip">PHP</span>
<span class="lang-chip">C#</span>
<span class="lang-chip">SQL</span>
</div>
</div>
</section>

<footer>
<p>// code debugger v2 // 10 agents // autonomous repair // execution sandbox</p>
<p>powered by openai agents sdk + openrouter</p>
</footer>
</div>

<div class="loading-overlay" id="loadingOverlay" role="dialog" aria-modal="true" aria-label="Running multi-agent debugging pipeline">
<div class="loading-cursor" aria-hidden="true"></div>
<div class="loading-text">
<span>$</span> Running Multi-Agent Pipeline
<div class="loading-steps">
<span class="loading-step" id="step1"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Enrichment</span>
<span class="loading-step" id="step2"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> Agent Analysis</span>
<span class="loading-step" id="step3"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> Sandbox</span>
<span class="loading-step" id="step4"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg> Repair Loop</span>
</div>
</div>
</div>

<script>
const steps=['step1','step2','step3','step4'];let cur=0,intv;
function startLoad(){cur=0;steps.forEach((id,i)=>{document.getElementById(id).classList.toggle('active',i===0)});intv=setInterval(()=>{document.getElementById(steps[cur]).classList.remove('active');cur=(cur+1)%steps.length;document.getElementById(steps[cur]).classList.add('active')},2000)}
function stopLoad(){clearInterval(intv);steps.forEach(id=>document.getElementById(id).classList.remove('active'))}

// Tab system
document.querySelectorAll('.tab-btn').forEach(btn=>{
btn.addEventListener('click',()=>{
document.querySelectorAll('.tab-btn').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-selected','false')});
document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
btn.classList.add('active');btn.setAttribute('aria-selected','true');
document.getElementById(btn.dataset.tab).classList.add('active');
})});

async function debugCode(){
const err=document.getElementById('errorTrace'),ff=document.getElementById('failingFile'),fl=document.getElementById('failingLine');
const em=document.getElementById('errorMsg'),rc=document.getElementById('resultsCard'),btn=document.getElementById('debugBtn'),lo=document.getElementById('loadingOverlay'),et=document.getElementById('errorText');
if(!err.value.trim()){et.textContent='Provide an error trace to analyze';em.classList.add('active');err.focus();return}
em.classList.remove('active');rc.style.display='none';btn.disabled=true;lo.classList.add('active');startLoad();
try{
const r=await fetch('/v2/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:err.value,failing_file:ff.value||'unknown',failing_line:fl.value?parseInt(fl.value):null})});
const d=await r.json();
if(d.success)showResult(d);else{et.textContent=d.detail||'Analysis failed';em.classList.add('active')}
}catch(e){et.textContent='Connection failed: '+e.message;em.classList.add('active')}
finally{lo.classList.remove('active');stopLoad();btn.disabled=false}
}

function showResult(d){
const sb=document.getElementById('statusBadge'),rp=document.getElementById('reportContent'),rc=document.getElementById('resultsCard');
sb.className='badge '+(d.validation_passed?'pass':'fail');
sb.innerHTML=(d.validation_passed
?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>PASS'
:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>FAIL');
sb.innerHTML+=' | confidence '+Math.round(d.confidence_score*100)+'%';
document.getElementById('metrics').innerHTML=
'<div class="metric"><div class="val">'+d.agent_timeline.length+'</div><div class="lbl">Agents Run</div></div>'+
'<div class="metric"><div class="val">'+d.repair_iterations+'</div><div class="lbl">Repair Iterations</div></div>'+
'<div class="metric"><div class="val">'+Math.round(d.confidence_score*100)+'%</div><div class="lbl">Confidence</div></div>'+
'<div class="metric"><div class="val">'+(d.validation_passed?'PASS':'FAIL')+'</div><div class="lbl">Validation</div></div>';
rp.textContent=d.final_report||'No report generated';
document.getElementById('diffContent').innerHTML=d.diff?d.diff.replace(/^-/gm,'<span class="del">-</span>').replace(/^\\+/gm,'<span class="add">+</span>').replace(/^@/gm,'<span class="info">@</span>'):'<span class="info">// No diff generated</span>';
document.getElementById('securityContent').textContent=d.security_report||'// No security analysis performed';
document.getElementById('regressionContent').textContent=d.regression_report||'// No regression analysis performed';
if(d.agent_timeline&&d.agent_timeline.length){
document.getElementById('agentTimeline').innerHTML=d.agent_timeline.map(a=>
'<div class="tl-item"><div class="tl-dot green"></div><div class="tl-content"><div class="tl-name">'+
a.agent+'</div><div class="tl-dur">'+(a.duration_ms?Math.round(a.duration_ms)+'ms':'N/A')+'</div></div></div>'
).join('')}
rc.style.display='block';rc.scrollIntoView({behavior:'smooth',block:'start'})
}

document.getElementById('debugBtn').addEventListener('click',debugCode);
document.getElementById('errorTrace').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))debugCode()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.getElementById('loadingOverlay').classList.remove('active');stopLoad()}});
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_v2.server:app", host="0.0.0.0", port=port, reload=True)


# Vercel deployment notes:
# - Routes are prefixed with /v2/ to match vercel.json routing
# - WebSocket endpoints will NOT work on Vercel (Python runtime limitation)
#   Use local uvicorn for WebSocket streaming
# - On Vercel, access: https://<project>.vercel.app/v2/ (UI)
#                       https://<project>.vercel.app/v2/debug (API)
#                       https://<project>.vercel.app/v2/health (health check)
# - Local dev: uvicorn api_v2.server:app --host 0.0.0.0 --port 8000 --reload
# - The V1 Flask API remains at root (/debug, /infrastructure, etc.)
