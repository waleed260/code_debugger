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
<title>Code Debugger v2 — Advanced</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#09090b;--surface:#111113;--elevated:#1a1a1e;--border:#27272a;--text:#fafafa;--secondary:#a1a1aa;--muted:#52525b;--accent:#10b981;--accent-dim:rgba(16,185,129,0.08);--accent-glow:rgba(16,185,129,0.15);--danger:#ef4444;--danger-dim:rgba(239,68,68,0.08);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:12px;--sm:8px;--ease:0.2s ease}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;padding:24px}
::selection{background:var(--accent);color:#09090b}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}
.container{max-width:720px;margin:0 auto}
header{margin-bottom:28px}
.logo{display:flex;align-items:center;gap:8px;margin-bottom:2px}
.logo-icon{width:28px;height:28px;border-radius:7px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:13px;color:#09090b;font-weight:700;font-family:var(--mono)}
.logo-text{font-size:1rem;font-weight:600;letter-spacing:-0.01em}
.tagline{font-size:0.68rem;color:var(--muted)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:14px}
.card:hover{border-color:var(--accent)}
.card-header{display:flex;align-items:center;justify-content:space-between;padding:10px 18px;border-bottom:1px solid var(--border)}
.card-header-label{font-size:0.58rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--muted);font-weight:500}
.card-body{padding:18px}
.card-tabs{display:flex;gap:2px;border-bottom:1px solid var(--border);padding:0 18px}
.tab-btn{background:none;border:none;border-bottom:2px solid transparent;padding:8px 14px;font-family:var(--font);font-size:0.65rem;font-weight:500;color:var(--muted);cursor:pointer;transition:color 0.2s,border-color 0.2s}
.tab-btn:hover{color:var(--secondary)}
.tab-btn.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab-content{display:none}
.tab-content.active{display:block}
.form-group{margin-bottom:12px}
label{display:block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);margin-bottom:4px;font-weight:500}
textarea,input{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:9px 12px;font-family:var(--mono);font-size:0.72rem;color:var(--text);transition:border-color 0.2s}
textarea:focus,input:focus{outline:none;border-color:var(--accent)}
textarea::placeholder{color:var(--muted)}
textarea{min-height:100px;resize:vertical;line-height:1.5;font-size:0.68rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;width:100%;padding:10px 18px;margin-top:10px;border:none;border-radius:var(--sm);font-family:var(--font);font-size:0.72rem;font-weight:600;cursor:pointer;background:var(--accent);color:#09090b;transition:all 0.2s}
.btn:hover{box-shadow:0 0 20px var(--accent-glow)}
.btn:disabled{opacity:0.3;cursor:not-allowed}
.btn svg{width:13px;height:13px}
.pill{display:inline-flex;align-items:center;gap:3px;padding:2px 9px;border-radius:8px;font-size:0.58rem;font-weight:600;text-transform:uppercase}
.pill.pass{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(16,185,129,0.2)}
.pill.fail{background:var(--danger-dim);color:var(--danger);border:1px solid rgba(239,68,68,0.2)}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}
.metric{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:10px;text-align:center}
.metric .val{font-size:1.1rem;font-weight:600;color:var(--accent)}
.metric .lbl{font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em;margin-top:2px}
.section{margin-bottom:16px}
.shead{display:flex;align-items:center;gap:6px;margin-bottom:6px}
.shead svg{width:12px;height:12px;color:var(--accent)}
.shead .sn{font-size:0.65rem;font-weight:500;color:var(--secondary);text-transform:uppercase;letter-spacing:0.06em}
.sbody{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:12px 14px;font-family:var(--mono);font-size:0.65rem;line-height:1.5;white-space:pre-wrap;max-height:320px;overflow-y:auto;color:var(--secondary)}
.timeline{padding:0}
.tl-item{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.tl-item:last-child{border:none}
.tl-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:4px}
.tl-dot.g{background:var(--accent)}
.tl-name{font-size:0.68rem;font-weight:500;color:var(--secondary)}
.tl-dur{font-size:0.55rem;color:var(--muted)}
.diff-view{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:12px;font-family:var(--mono);font-size:0.65rem;line-height:1.5;overflow-x:auto;max-height:320px;overflow-y:auto;color:var(--secondary);white-space:pre-wrap}
.diff-view .a{color:var(--accent)}
.diff-view .d{color:var(--danger)}
.diff-view .i{color:var(--muted)}
.err{display:none;margin-top:10px;padding:9px 13px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);border-radius:var(--sm);color:var(--danger);font-size:0.65rem;align-items:flex-start;gap:6px}
.err.active{display:flex}
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(9,9,11,0.94);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:18px}
.loading-overlay.active{display:flex}
.loading-ring{width:28px;height:28px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-size:0.72rem;color:var(--secondary);text-align:center}
.loading-text span{color:var(--accent)}
.loading-steps{display:flex;gap:16px;margin-top:4px;justify-content:center}
.loading-step{font-size:0.58rem;color:var(--muted);opacity:0.3;transition:opacity 0.3s}
.loading-step.active{color:var(--accent);opacity:1}
footer{margin-top:36px;padding-top:12px;border-top:1px solid var(--border);font-size:0.55rem;color:var(--muted);text-align:center}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.af{animation:fadeIn 0.35s ease backwards}
.ad1{animation-delay:0.05s}.ad2{animation-delay:0.1s}.ad3{animation-delay:0.15s}.ad4{animation-delay:0.2s}
@media(prefers-reduced-motion:reduce){.af{animation:none!important}html{scroll-behavior:auto}}
@media(max-width:600px){
.form-row{grid-template-columns:1fr}
.metrics{grid-template-columns:repeat(2,1fr)}
.container{padding:12px}
}
</style>
</head>
<body>
<div class="container">
<header class="af">
<div class="logo"><div class="logo-icon">v2</div><div class="logo-text">Code Debugger</div></div>
<p class="tagline">Advanced pipeline &mdash; multi-agent analysis, sandbox execution, autonomous repair</p>
</header>

<div class="card af ad1">
<div class="card-header"><span class="card-header-label">debug</span><span style="font-size:0.58rem;color:var(--muted)">Ctrl+Enter</span></div>
<div class="card-body">
<form id="debugForm" novalidate>
<div class="form-group"><label for="errorTrace">Error trace</label><textarea id="errorTrace" autocomplete="off" spellcheck="false" placeholder="Paste stack trace...">Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = process_data(data)
  File "app.py", line 5, in process_data
    return items[index] + items[index + 1]
IndexError: list index out of range</textarea></div>
<div class="form-row">
<div class="form-group"><label for="failingFile">File</label><input type="text" id="failingFile" value="app.py"></div>
<div class="form-group"><label for="failingLine">Line</label><input type="number" id="failingLine" value="5"></div>
</div>
</form>
<div class="err" id="errorMsg" role="alert"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><span id="errorText"></span></div>
<button type="button" class="btn" id="debugBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Debug</button>
</div>
</div>

<div class="card af ad2" style="display:none" id="resultsCard">
<div class="card-header"><span class="card-header-label">report</span><span class="pill" id="statusPill"></span></div>
<div class="card-tabs">
<button class="tab-btn active" data-tab="tab-r">Report</button>
<button class="tab-btn" data-tab="tab-a">Trace</button>
<button class="tab-btn" data-tab="tab-d">Diff</button>
<button class="tab-btn" data-tab="tab-s">Security</button>
</div>
<div class="card-body">
<div class="tab-content active" id="tab-r"><div class="metrics" id="metrics"></div><div class="section"><div class="shead"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><span class="sn">Analysis</span></div><div class="sbody" id="reportContent"></div></div></div>
<div class="tab-content" id="tab-a"><div class="timeline" id="agentTimeline"></div></div>
<div class="tab-content" id="tab-d"><pre class="diff-view" id="diffContent"><span class="i">// no diff</span></pre></div>
<div class="tab-content" id="tab-s"><div class="sbody" id="securityContent"><span class="i">// no security analysis</span></div></div>
</div>
</div>

<div style="display:flex;gap:6px;margin-top:14px" class="af ad3">
<a href="/" class="tab-btn" style="display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border:1px solid var(--border);border-radius:var(--sm);font-size:0.6rem;color:var(--secondary);text-decoration:none;background:var(--surface)">&larr; Main</a>
<a href="/infrastructure" class="tab-btn" style="display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border:1px solid var(--border);border-radius:var(--sm);font-size:0.6rem;color:var(--secondary);text-decoration:none;background:var(--surface)">Infrastructure</a>
</div>

<footer>code debugger v2 &middot; advanced pipeline</footer>
</div>

<div class="loading-overlay" id="loadingOverlay">
<div class="loading-ring"></div>
<div class="loading-text"><span>$</span> Running<div class="loading-steps"><span class="loading-step" id="s1">Parse</span><span class="loading-step" id="s2">Analyze</span><span class="loading-step" id="s3">Sandbox</span><span class="loading-step" id="s4">Repair</span></div></div>
</div>

<script>
const sts=['s1','s2','s3','s4'];let ci=0,iv;
function sl(){ci=0;sts.forEach((id,i)=>document.getElementById(id).classList.toggle('active',i===0));iv=setInterval(()=>{document.getElementById(sts[ci]).classList.remove('active');ci=(ci+1)%4;document.getElementById(sts[ci]).classList.add('active')},1800)}
function stl(){clearInterval(iv);sts.forEach(id=>document.getElementById(id).classList.remove('active'))}
document.querySelectorAll('.tab-btn').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.tab-btn').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.tab).classList.add('active')}));
document.getElementById('debugBtn').addEventListener('click',async()=>{
const e=document.getElementById('errorTrace'),ff=document.getElementById('failingFile'),fl=document.getElementById('failingLine');
const em=document.getElementById('errorMsg'),rc=document.getElementById('resultsCard'),btn=document.getElementById('debugBtn');
if(!e.value.trim()){em.classList.add('active');return}
em.classList.remove('active');rc.style.display='none';btn.disabled=true;document.getElementById('loadingOverlay').classList.add('active');sl();
try{const r=await fetch('/v2/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:e.value,failing_file:ff.value||'unknown',failing_line:fl.value?parseInt(fl.value):null})});const d=await r.json();
if(d.success){const p=document.getElementById('statusPill'),rp=document.getElementById('reportContent');p.className='pill '+(d.validation_passed?'pass':'fail');p.textContent=d.validation_passed?'PASS':'FAIL';document.getElementById('metrics').innerHTML='<div class="metric"><div class="val">'+d.agent_timeline.length+'</div><div class="lbl">Agents</div></div><div class="metric"><div class="val">'+d.repair_iterations+'</div><div class="lbl">Iterations</div></div><div class="metric"><div class="val">'+Math.round(d.confidence_score*100)+'%</div><div class="lbl">Confidence</div></div><div class="metric"><div class="val">'+(d.validation_passed?'PASS':'FAIL')+'</div><div class="lbl">Status</div></div>';rp.textContent=d.final_report;document.getElementById('diffContent').innerHTML=d.diff?'<span class="a">+</span>'.repeat(3):'<span class="i">// no diff</span>';document.getElementById('securityContent').textContent=d.security_report||'// none';if(d.agent_timeline)document.getElementById('agentTimeline').innerHTML=d.agent_timeline.map(a=>'<div class="tl-item"><div class="tl-dot g"></div><div><div class="tl-name">'+a.agent+'</div><div class="tl-dur">'+(a.duration_ms?Math.round(a.duration_ms)+'ms':'')+'</div></div></div>').join('');rc.style.display='block';rc.scrollIntoView({behavior:'smooth'})}
else{document.getElementById('errorText').textContent=d.detail||'Failed';em.classList.add('active')}}
catch(e2){document.getElementById('errorText').textContent='Connection error';em.classList.add('active')}
finally{document.getElementById('loadingOverlay').classList.remove('active');stl();btn.disabled=false}});
document.getElementById('errorTrace').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctlKey))document.getElementById('debugBtn').click()});
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
