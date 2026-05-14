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


# --- V2 Routes (prefixed with /v2) ---

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


# --- WebSocket (prefixed with /v2) ---

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
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Code Debugger V2 — Autonomous AI Debugging</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#06080f;--surface:#0F172A;--elevated:#1E293B;--border:#334155;--text:#F8FAFC;--muted:#94A3B8;--dim:#64748B;--accent:#22C55E;--accent-b:#06B6D4;--accent-c:#F59E0B;--danger:#EF4444;--font:'JetBrains Mono',monospace}
body{font-family:var(--font);background:var(--bg);color:var(--text);padding:24px;font-size:14px;line-height:1.7}
.container{max-width:960px;margin:0 auto}
h1{font-size:1.5rem;font-weight:500;text-transform:uppercase;margin-bottom:4px}
h1 em{font-style:normal;color:var(--accent)}
.subtitle{font-size:0.7rem;color:var(--dim);text-transform:uppercase;margin-bottom:32px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px;margin-bottom:24px}
label{display:block;font-size:0.65rem;text-transform:uppercase;color:var(--dim);margin-bottom:6px}
textarea,input{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:4px;padding:12px;font-family:var(--font);font-size:0.8rem;color:var(--text)}
textarea:focus,input:focus{outline:none;border-color:var(--accent)}
textarea{min-height:150px;resize:vertical}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 24px;background:var(--accent);color:var(--bg);font-family:var(--font);font-size:0.78rem;font-weight:500;border:none;border-radius:4px;cursor:pointer;width:100%;margin-top:16px}
.btn:hover{box-shadow:0 0 20px rgba(34,197,94,0.35)}
.btn:disabled{opacity:0.35;cursor:not-allowed}
.badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:12px;font-size:0.65rem;text-transform:uppercase}
.badge.pass{background:rgba(34,197,94,0.12);color:var(--accent);border:1px solid rgba(34,197,94,0.3)}
.badge.fail{background:rgba(239,68,68,0.12);color:var(--danger);border:1px solid rgba(239,68,68,0.3)}
.result-pre{background:var(--elevated);border:1px solid var(--border);border-radius:4px;padding:18px;font-size:0.75rem;white-space:pre-wrap;max-height:500px;overflow-y:auto;color:var(--muted);margin-top:16px}
.result-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:16px 0}
.metric{background:var(--elevated);border:1px solid var(--border);border-radius:4px;padding:12px;text-align:center}
.metric .val{font-size:1.2rem;font-weight:600;color:var(--accent)}
.metric .lbl{font-size:0.6rem;color:var(--dim);text-transform:uppercase}
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);font-size:0.6rem;color:var(--dim)}
</style>
</head>
<body>
<div class="container">
<h1>code <em>debugger</em> v2</h1>
<p class="subtitle">V2 API — Autonomous AI Debugging Platform</p>
<div class="card">
<label>Error Trace / Stack Trace</label>
<textarea id="errorTrace" placeholder="Paste error trace here...">Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = process_data(data)
  File "app.py", line 5, in process_data
    return items[index] + items[index + 1]
IndexError: list index out of range</textarea>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px">
<div><label>Failing File</label><input id="failingFile" value="app.py"></div>
<div><label>Failing Line</label><input id="failingLine" type="number" value="5"></div>
</div>
<button class="btn" id="debugBtn">Run V2 Debugging Pipeline</button>
</div>
<div id="results" style="display:none">
<div class="card">
<div class="result-head"><span>// analysis report</span><span class="badge" id="statusBadge"></span></div>
<div class="metrics" id="metrics"></div>
<pre class="result-pre" id="reportContent"></pre>
</div>
</div>
<footer><p>// 10 specialized agents // autonomous repair loop // execution sandbox</p></footer>
</div>
<script>
const btn=document.getElementById('debugBtn'),results=document.getElementById('results');
const sb=document.getElementById('statusBadge'),rp=document.getElementById('reportContent'),m=document.getElementById('metrics');
btn.addEventListener('click',async()=>{
btn.disabled=true;results.style.display='none';
const r=await fetch('/v2/debug',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({error_trace:document.getElementById('errorTrace').value,
failing_file:document.getElementById('failingFile').value||'unknown',
failing_line:document.getElementById('failingLine').value?parseInt(document.getElementById('failingLine').value):null})});
const d=await r.json();
if(d.success){sb.className='badge '+(d.validation_passed?'pass':'fail');
sb.innerHTML=(d.validation_passed?'PASS':'FAIL')+' | confidence: '+Math.round(d.confidence_score*100)+'%';
m.innerHTML='<div class="metric"><div class="val">'+d.agent_timeline.length+'</div><div class="lbl">Agents Used</div></div>'+
'<div class="metric"><div class="val">'+d.repair_iterations+'</div><div class="lbl">Repair Iterations</div></div>'+
'<div class="metric"><div class="val">'+Math.round(d.confidence_score*100)+'%</div><div class="lbl">Confidence</div></div>';
rp.textContent=d.final_report;results.style.display='block'}
else{rp.textContent='Error: '+(d.detail||'Unknown error');results.style.display='block'}
btn.disabled=false});
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
