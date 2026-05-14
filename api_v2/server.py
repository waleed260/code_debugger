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
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#09090b">
<title>Code Debugger — Advanced</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#09090b;--surface:#111113;--elevated:#1a1a1e;--border:#27272a;--text:#fafafa;--secondary:#a1a1aa;--muted:#52525b;--accent:#10b981;--accent-dim:rgba(16,185,129,0.08);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:12px;--sm:8px}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;display:flex;flex-direction:column}
::selection{background:var(--accent);color:#09090b}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}
.container{max-width:680px;margin:0 auto;padding:48px 20px 32px;width:100%;flex:1}
.logo{display:flex;align-items:center;gap:8px;margin-bottom:32px}
.logo-icon{width:28px;height:28px;border-radius:7px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:13px;color:#09090b;font-weight:700;font-family:var(--mono);margin-right:2px}
.logo-text{font-size:1rem;font-weight:600;letter-spacing:-0.01em}
.logo .sub{font-size:0.6rem;color:var(--muted);margin-left:auto}
.input-area{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:6px;transition:border-color 0.15s}
.input-area:focus-within{border-color:var(--accent)}
textarea{width:100%;background:transparent;border:none;padding:10px 12px;font-family:var(--mono);font-size:0.82rem;color:var(--text);resize:none;min-height:60px;max-height:300px;line-height:1.5}
textarea:focus{outline:none}
textarea::placeholder{color:var(--muted)}
.input-footer{display:flex;align-items:center;justify-content:space-between;padding:4px 12px 6px}
.input-footer span{font-size:0.6rem;color:var(--muted)}
.send-btn{width:28px;height:28px;border-radius:6px;border:none;background:var(--accent);color:#09090b;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:opacity 0.15s}
.send-btn:hover{opacity:0.85}
.send-btn:disabled{opacity:0.2;cursor:default}
.send-btn svg{width:14px;height:14px}
.output{display:none;margin-top:16px;padding:14px 18px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);font-family:var(--mono);font-size:0.72rem;line-height:1.5;white-space:pre-wrap;color:var(--secondary);max-height:480px;overflow-y:auto}
.output.show{display:block}
.output .pass{color:var(--accent);font-weight:600}
.output .fail{color:#ef4444;font-weight:600}
.meta{display:none;margin-top:8px;font-size:0.6rem;color:var(--muted);font-family:var(--mono);gap:12px;flex-wrap:wrap}
.meta.show{display:flex}
.meta span{background:var(--elevated);padding:2px 8px;border-radius:4px;border:1px solid var(--border)}
.loading{display:none;align-items:center;gap:8px;margin-top:16px;padding:10px 14px}
.loading.show{display:flex}
.loading .ring{width:16px;height:16px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:s 0.7s linear infinite;flex-shrink:0}
@keyframes s{to{transform:rotate(360deg)}}
.loading span{font-size:0.72rem;color:var(--muted)}
.loading .dots::after{content:'';animation:d 1.5s steps(4,end) infinite}
@keyframes d{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}100%{content:''}}
.nav{display:flex;gap:6px;margin-top:16px}
.nav a{padding:6px 10px;border:1px solid var(--border);border-radius:var(--sm);font-size:0.6rem;color:var(--muted);text-decoration:none;transition:color 0.15s,border-color 0.15s}
.nav a:hover{color:var(--accent);border-color:var(--accent)}
footer{padding:16px 20px;text-align:center;font-size:0.55rem;color:var(--muted)}
@media(max-width:600px){.container{padding:24px 14px 16px}textarea{font-size:0.78rem}}
</style>
</head>
<body>
<div class="container">
<div class="logo"><div class="logo-icon">v2</div><div class="logo-text">Code Debugger</div><span class="sub">advanced</span></div>
<div class="input-area">
<textarea id="input" rows="2" placeholder="Paste an error trace..." autocomplete="off" spellcheck="false">Traceback (most recent call last):
  File "app.py", line 5, in process_data
    return items[index] + items[index + 1]
IndexError: list index out of range</textarea>
<div class="input-footer">
<span>Ctrl+Enter</span>
<button class="send-btn" id="sendBtn" aria-label="Debug">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polyline points="22 2 15 22 11 13 2 9 22 2"/></svg>
</button>
</div>
</div>
<div class="loading" id="loading" role="status"><div class="ring"></div><span>Analyzing<span class="dots"></span></span></div>
<div class="meta" id="meta"></div>
<div class="output" id="output" role="region" aria-live="polite"></div>
<div class="nav"><a href="/">&larr; Main</a><a href="/infrastructure">Infrastructure</a></div>
</div>
<footer>Code Debugger</footer>
<script>
const input=document.getElementById('input'),send=document.getElementById('sendBtn'),output=document.getElementById('output'),loading=document.getElementById('loading'),meta=document.getElementById('meta');
function autoResize(){input.style.height='auto';input.style.height=Math.min(input.scrollHeight,300)+'px'}
input.addEventListener('input',autoResize);
send.addEventListener('click',debug);
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();debug()}});
async function debug(){
const text=input.value.trim();if(!text)return;
send.disabled=true;output.classList.remove('show');output.textContent='';meta.classList.remove('show');meta.textContent='';loading.classList.add('show');
try{
const r=await fetch('/v2/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:text,failing_file:'',failing_line:null})});
const d=await r.json();
loading.classList.remove('show');
if(d.success){const passed=d.validation_passed;output.innerHTML=(passed?'<span class="pass">PASS</span>\n\n':'<span class="fail">FAIL</span>\n\n')+d.final_report;output.classList.add('show');
if(d.confidence_score!==undefined){meta.innerHTML='<span>confidence '+Math.round(d.confidence_score*100)+'%</span><span>'+d.agent_timeline.length+' agents</span><span>'+d.repair_iterations+' iterations</span>';meta.classList.add('show')}}
else{output.innerHTML='<span class="fail">Error:</span> '+(d.detail||'Request failed');output.classList.add('show')}
}catch(e){loading.classList.remove('show');output.innerHTML='<span class="fail">Connection error</span>';output.classList.add('show')}
finally{send.disabled=false;input.focus()}}
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
