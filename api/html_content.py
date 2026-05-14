INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0c0a1a">
<title>Code Debugger — Multi-Agent AI Debugging System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0c0a1a;--surface:#151230;--elevated:#1e1a45;--border:#2d2860;--text:#e8e5f8;--secondary:#a8a0d0;--muted:#7068a0;--cyan:#00f0ff;--pink:#ff4d9e;--purple:#a855f7;--green:#22d65e;--amber:#f59e0b;--red:#ef4444;--blue:#3b82f6;--orange:#f97316;--teal:#14b8a6;--violet:#8b5cf6;--grad-1:linear-gradient(135deg,#00f0ff,#a855f7);--grad-2:linear-gradient(135deg,#ff4d9e,#f97316);--grad-3:linear-gradient(135deg,#22d65e,#14b8a6);--grad-4:linear-gradient(135deg,#8b5cf6,#3b82f6);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:14px;--ease:0.25s cubic-bezier(0.34,1.56,0.64,1)}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;background-image:radial-gradient(ellipse 80% 60% at 50% -20%,rgba(168,85,247,0.12),transparent),radial-gradient(ellipse 60% 40% at 80% 100%,rgba(0,240,255,0.08),transparent)}
::selection{background:var(--cyan);color:#0c0a1a}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;border-radius:6px}
.container{max-width:960px;margin:0 auto;padding:36px 20px 56px;position:relative}
/* Header */
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;flex-wrap:wrap;gap:12px}
.logo{display:flex;align-items:center;gap:10px}
.logo-icon{width:36px;height:36px;border-radius:10px;background:var(--grad-1);display:flex;align-items:center;justify-content:center;font-size:18px;color:#fff;font-weight:700;font-family:var(--mono)}
.logo-text{font-size:1.2rem;font-weight:700;letter-spacing:-0.02em}
.logo-text span{background:var(--grad-1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.badge-group{display:flex;gap:6px;flex-wrap:wrap}
.badge{padding:4px 12px;border-radius:20px;font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em}
.badge.cyan{background:rgba(0,240,255,0.12);color:var(--cyan);border:1px solid rgba(0,240,255,0.2)}
.badge.pink{background:rgba(255,77,158,0.12);color:var(--pink);border:1px solid rgba(255,77,158,0.2)}
.badge.green{background:rgba(34,214,94,0.12);color:var(--green);border:1px solid rgba(34,214,94,0.2)}
.badge.purple{background:rgba(168,85,247,0.12);color:var(--purple);border:1px solid rgba(168,85,247,0.2)}
/* Card */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:18px;backdrop-filter:blur(20px);position:relative}
.card::before{content:'';position:absolute;inset:-1px;border-radius:calc(var(--radius)+1px);background:linear-gradient(135deg,rgba(0,240,255,0.1),rgba(168,85,247,0.1),rgba(255,77,158,0.1));z-index:-1;opacity:0;transition:opacity var(--ease)}
.card:hover::before{opacity:1}
.card-body{padding:20px 24px 24px}
.card-label{font-size:0.55rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);padding:12px 24px 0;font-weight:600}
/* Form */
.form-group{margin-bottom:16px}
label{display:block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:5px;font-weight:600;cursor:pointer}
textarea,input{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:10px;padding:11px 14px;font-family:var(--mono);font-size:0.75rem;color:var(--text);transition:all var(--ease)}
textarea:focus,input:focus{outline:none;border-color:var(--cyan);box-shadow:0 0 0 3px rgba(0,240,255,0.08)}
textarea::placeholder{color:var(--muted)}
textarea{min-height:120px;resize:vertical;line-height:1.7;font-size:0.7rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:12px 24px;margin-top:14px;border:none;border-radius:10px;font-family:var(--font);font-size:0.78rem;font-weight:600;cursor:pointer;transition:all var(--ease);letter-spacing:0.01em}
.btn-primary{background:var(--grad-1);color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,240,255,0.25)}
.btn-primary:disabled{opacity:0.35;cursor:not-allowed;transform:none;box-shadow:none}
.btn svg{width:14px;height:14px}
/* Result */
.result-card{display:none}
.result-card.active{display:block}
.result-head{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:8px}
.result-head span{font-size:0.65rem;color:var(--muted);font-family:var(--mono)}
.status-pill{display:inline-flex;align-items:center;gap:5px;padding:3px 12px;border-radius:20px;font-size:0.6rem;font-weight:600;text-transform:uppercase}
.status-pill.pass{background:rgba(34,214,94,0.12);color:var(--green);border:1px solid rgba(34,214,94,0.25)}
.status-pill.fail{background:rgba(239,68,68,0.12);color:var(--red);border:1px solid rgba(239,68,68,0.25)}
.result-body{padding:18px 24px 22px}
.result-pre{background:var(--elevated);border:1px solid var(--border);border-radius:10px;padding:16px;font-family:var(--mono);font-size:0.68rem;line-height:1.6;white-space:pre-wrap;max-height:380px;overflow-y:auto;color:var(--secondary)}
.result-pre::-webkit-scrollbar{width:3px}
.result-pre::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
/* Agent showcase */
.agent-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px;margin-top:6px}
.agent-chip{display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--elevated);border:1px solid var(--border);border-radius:10px;font-size:0.62rem;transition:all var(--ease);text-decoration:none;color:var(--secondary)}
.agent-chip:hover{transform:translateY(-2px);border-color:var(--cyan)}
.agent-chip .dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.dot.c1{background:var(--cyan);box-shadow:0 0 8px rgba(0,240,255,0.5)}
.dot.c2{background:var(--pink);box-shadow:0 0 8px rgba(255,77,158,0.5)}
.dot.c3{background:var(--green);box-shadow:0 0 8px rgba(34,214,94,0.5)}
.dot.c4{background:var(--amber);box-shadow:0 0 8px rgba(245,158,11,0.5)}
.dot.c5{background:var(--purple);box-shadow:0 0 8px rgba(168,85,247,0.5)}
.dot.c6{background:var(--blue);box-shadow:0 0 8px rgba(59,130,246,0.5)}
.dot.c7{background:var(--teal);box-shadow:0 0 8px rgba(20,184,166,0.5)}
.dot.c8{background:var(--orange);box-shadow:0 0 8px rgba(249,115,22,0.5)}
.dot.c9{background:var(--violet);box-shadow:0 0 8px rgba(139,92,246,0.5)}
.dot.c10{background:var(--red);box-shadow:0 0 8px rgba(239,68,68,0.5)}
/* Section headers */
.section-title{display:flex;align-items:center;gap:8px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;margin-top:24px;color:var(--secondary)}
.section-title svg{width:14px;height:14px}
/* Error */
.err{display:none;margin-top:12px;padding:10px 14px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);border-radius:10px;color:var(--red);font-size:0.7rem;align-items:flex-start;gap:8px}
.err.active{display:flex}
/* Nav link */
.nav-link{display:inline-flex;align-items:center;gap:6px;margin-top:14px;padding:8px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:0.65rem;color:var(--secondary);transition:all var(--ease);text-decoration:none}
.nav-link:hover{color:var(--cyan);border-color:var(--cyan);transform:translateY(-1px)}
/* Loading */
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(12,10,26,0.94);backdrop-filter:blur(16px);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:24px}
.loading-overlay.active{display:flex}
.loading-spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--cyan);border-radius:50%;animation:spin 0.8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-size:0.8rem;color:var(--secondary);text-align:center;line-height:1.8}
.loading-text span{color:var(--cyan);font-weight:600}
.loading-steps{display:flex;gap:20px;margin-top:6px;flex-wrap:wrap;justify-content:center}
.loading-step{font-size:0.6rem;color:var(--muted);opacity:0.3;transition:opacity 0.3s;display:flex;align-items:center;gap:4px}
.loading-step.active{color:var(--cyan);opacity:1}
/* Lang chips */
.lang-strip{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.lang-chip{padding:2px 10px;background:var(--elevated);border:1px solid var(--border);border-radius:6px;font-size:0.55rem;color:var(--muted);font-family:var(--mono)}
/* Footer */
footer{margin-top:40px;padding-top:14px;border-top:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
footer p{font-size:0.55rem;color:var(--muted)}
/* Anim */
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.af{animation:fadeUp 0.6s cubic-bezier(0.34,1.56,0.64,1) backwards}
.ad1{animation-delay:0.06s}.ad2{animation-delay:0.12s}.ad3{animation-delay:0.18s}.ad4{animation-delay:0.24s}.ad5{animation-delay:0.3s}
@media(prefers-reduced-motion:reduce){*, .af{animation:none!important}html{scroll-behavior:auto}}
@media(max-width:768px){
.container{padding:24px 14px 40px}
.form-row{grid-template-columns:1fr}
.agent-grid{grid-template-columns:repeat(2,1fr)}
.card-body{padding:16px 18px}
}
</style>
</head>
<body>
<div class="container">
<header class="af">
<div class="logo">
<div class="logo-icon">{ }</div>
<div class="logo-text">code <span>debugger</span></div>
</div>
<div class="badge-group">
<span class="badge cyan">10 agents</span>
<span class="badge pink">11 languages</span>
<span class="badge green">auto-repair</span>
</div>
</header>

<div class="card af ad1">
<div class="card-label">$ ./debug</div>
<div class="card-body">
<form id="debugForm" novalidate>
<div class="form-group">
<label for="errorTrace">Error Trace <span style="color:var(--pink)">*</span></label>
<textarea id="errorTrace" autocomplete="off" spellcheck="false" placeholder="Paste your stack trace here..."></textarea>
</div>
<div class="form-row">
<div class="form-group"><label for="failingFile">File</label><input type="text" id="failingFile" placeholder="app.py"></div>
<div class="form-group"><label for="failingLine">Line</label><input type="number" id="failingLine" placeholder="42"></div>
</div>
</form>
<div class="err" id="errorMsg" role="alert"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><span id="errorText"></span></div>
<button type="button" class="btn btn-primary" id="submitBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Analyze Error</button>
</div>
</div>

<div class="card result-card" id="resultCard">
<div class="result-head"><span>// report.md</span><span class="status-pill" id="statusPill"></span></div>
<div class="result-body"><pre class="result-pre" id="reportContent"></pre></div>
</div>

<div class="section-title af ad2">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
10 Specialized Debug Agents
</div>
<div class="agent-grid af ad2">
<a class="agent-chip" href="/v2/"><span class="dot c1"></span>StackTraceAgent <span style="color:var(--muted);font-size:0.55rem">traceback</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c2"></span>DependencyAgent <span style="color:var(--muted);font-size:0.55rem">versions</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c3"></span>RuntimeAgent <span style="color:var(--muted);font-size:0.55rem">runtime</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c4"></span>DataFlowAgent <span style="color:var(--muted);font-size:0.55rem">data flow</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c5"></span>FixGenAgent <span style="color:var(--muted);font-size:0.55rem">fixes</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c6"></span>ValidationAgent <span style="color:var(--muted);font-size:0.55rem">tests</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c7"></span>RegressionAgent <span style="color:var(--muted);font-size:0.55rem">side effects</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c8"></span>SecurityAgent <span style="color:var(--muted);font-size:0.55rem">vulnerabilities</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c9"></span>PerfAgent <span style="color:var(--muted);font-size:0.55rem">bottlenecks</span></a>
<a class="agent-chip" href="/v2/"><span class="dot c10"></span>RefactorAgent <span style="color:var(--muted);font-size:0.55rem">quality</span></a>
</div>

<div class="section-title af ad3">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
Execution Sandbox
</div>
<div class="lang-strip af ad3">
<span class="lang-chip">Python</span><span class="lang-chip">JS</span><span class="lang-chip">TS</span><span class="lang-chip">Go</span><span class="lang-chip">Rust</span>
<span class="lang-chip">Java</span><span class="lang-chip">C++</span><span class="lang-chip">Ruby</span><span class="lang-chip">PHP</span><span class="lang-chip">C#</span><span class="lang-chip">SQL</span>
</div>

<div style="display:flex;gap:8px;margin-top:20px;flex-wrap:wrap" class="af ad4">
<a href="/infrastructure" class="nav-link">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
Infrastructure
</a>
<a href="/v2/" class="nav-link">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
V2 Pipeline
</a>
</div>

<footer><p>// code debugger v2 // 20 agents total // open-source</p></footer>
</div>

<div class="loading-overlay" id="loadingOverlay">
<div class="loading-spinner"></div>
<div class="loading-text"><span>$</span> Running Analysis<div class="loading-steps"><span class="loading-step" id="s1">Parse</span><span class="loading-step" id="s2">Analyze</span><span class="loading-step" id="s3">Fix</span><span class="loading-step" id="s4">Validate</span></div></div>
</div>

<script>
const sts=['s1','s2','s3','s4'];let ci=0,iv;
function sl(){ci=0;sts.forEach((id,i)=>document.getElementById(id).classList.toggle('active',i===0));iv=setInterval(()=>{document.getElementById(sts[ci]).classList.remove('active');ci=(ci+1)%4;document.getElementById(sts[ci]).classList.add('active')},1800)}
function stl(){clearInterval(iv);sts.forEach(id=>document.getElementById(id).classList.remove('active'))}
document.getElementById('submitBtn').addEventListener('click',async()=>{
const e=document.getElementById('errorTrace'),ff=document.getElementById('failingFile'),fl=document.getElementById('failingLine');
const em=document.getElementById('errorMsg'),rc=document.getElementById('resultCard'),btn=document.getElementById('submitBtn');
if(!e.value.trim()){em.classList.add('active');return}
em.classList.remove('active');rc.classList.remove('active');btn.disabled=true;document.getElementById('loadingOverlay').classList.add('active');sl();
try{const r=await fetch('/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:e.value,failing_file:ff.value||'unknown',failing_line:fl.value?parseInt(fl.value):null})});const d=await r.json();
if(d.success){const p=document.getElementById('statusPill'),rp=document.getElementById('reportContent');p.className='status-pill '+(d.validation_passed?'pass':'fail');p.textContent=d.validation_passed?'PASS':'FAIL';rp.textContent=d.final_report;rc.classList.add('active');rc.scrollIntoView({behavior:'smooth'})}
else{document.getElementById('errorText').textContent=d.error||'Analysis failed';em.classList.add('active')}}
catch(e2){document.getElementById('errorText').textContent='Connection error';em.classList.add('active')}
finally{document.getElementById('loadingOverlay').classList.remove('active');stl();btn.disabled=false}});
document.getElementById('errorTrace').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))document.getElementById('submitBtn').click()});
</script>
</body>
</html>"""

INFRASTRUCTURE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0c0a1a">
<title>Infrastructure — Multi-Agent Infrastructure Management</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0c0a1a;--surface:#151230;--elevated:#1e1a45;--border:#2d2860;--text:#e8e5f8;--secondary:#a8a0d0;--muted:#7068a0;--cyan:#00f0ff;--pink:#ff4d9e;--purple:#a855f7;--green:#22d65e;--amber:#f59e0b;--red:#ef4444;--grad-1:linear-gradient(135deg,#00f0ff,#a855f7);--grad-2:linear-gradient(135deg,#ff4d9e,#f97316);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:14px;--ease:0.25s cubic-bezier(0.34,1.56,0.64,1)}
body{font-family:var(--font);background:var(--bg);color:var(--text);padding:24px;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;background-image:radial-gradient(ellipse 70% 50% at 30% -10%,rgba(168,85,247,0.1),transparent),radial-gradient(ellipse 50% 40% at 70% 110%,rgba(0,240,255,0.06),transparent)}
::selection{background:var(--cyan);color:#0c0a1a}
.container{max-width:960px;margin:0 auto}
h1{font-size:1.2rem;font-weight:700;letter-spacing:-0.02em}
h1 span{background:var(--grad-1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:20px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;margin-bottom:16px}
select,textarea{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-family:var(--mono);font-size:0.72rem;color:var(--text)}
select:focus,textarea:focus{outline:none;border-color:var(--cyan)}
.btn{display:flex;align-items:center;justify-content:center;padding:10px 18px;background:var(--grad-1);color:#fff;font-family:var(--font);font-size:0.7rem;font-weight:600;border:none;border-radius:10px;cursor:pointer;width:100%;margin-top:12px;transition:all var(--ease)}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,240,255,0.2)}
.btn:disabled{opacity:0.3;transform:none}
.result-pre{background:var(--elevated);border:1px solid var(--border);border-radius:10px;padding:14px;font-family:var(--mono);font-size:0.65rem;line-height:1.5;white-space:pre-wrap;max-height:320px;overflow-y:auto;color:var(--secondary);margin-top:10px}
a{color:var(--cyan);text-decoration:none}
a:hover{text-decoration:underline}
footer{margin-top:32px;padding-top:12px;border-top:1px solid var(--border);font-size:0.52rem;color:var(--muted)}
</style>
</head>
<body>
<div class="container">
<h1>infrastructure <span>manager</span></h1>
<p class="subtitle">5 Specialized Infrastructure Agents</p>
<div class="card">
<p class="card-label">agent selector</p>
<select id="agentSelect">
<option value="infrastructure">Infrastructure Analyzer</option>
<option value="security">Security Auditor</option>
<option value="performance">Performance Optimizer</option>
<option value="cost">Cost Manager</option>
<option value="incident">Incident Responder</option>
</select>
<button class="btn" id="runBtn">Run Agent</button>
<pre class="result-pre" id="output">Select an agent and click Run.</pre>
</div>
<a href="/">&larr; Back to Debugger</a>
<footer><p>// infrastructure ctl // 5 agents</p></footer>
</div>
<script>
document.getElementById('runBtn').addEventListener('click',async function(){
const btn=this,out=document.getElementById('output'),agent=document.getElementById('agentSelect').value;
btn.disabled=true;out.textContent='Running '+agent+'...';
try{const r=await fetch('/api/infrastructure/'+agent,{method:'POST'});const d=await r.json();
if(d.success)out.textContent=JSON.stringify(d.result?.output||d.result||d,null,2);else out.textContent='Error: '+(d.error||'Unknown')}
catch(e){out.textContent='Error: '+e.message}finally{btn.disabled=false}});
</script>
</body>
</html>"""
