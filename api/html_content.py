INDEX_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#09090b">
<title>Code Debugger — AI Debug Agent</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#09090b;--surface:#111113;--elevated:#1a1a1e;--border:#27272a;--text:#fafafa;--secondary:#a1a1aa;--muted:#52525b;--accent:#10b981;--accent-dim:rgba(16,185,129,0.1);--accent-glow:rgba(16,185,129,0.2);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:12px;--sm:8px;--ease:0.2s ease}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent);color:#09090b}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}
.container{max-width:680px;margin:0 auto;padding:40px 20px 64px}
/* Header */
header{margin-bottom:36px}
.logo{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.logo-icon{width:32px;height:32px;border-radius:8px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:15px;color:#09090b;font-weight:700;font-family:var(--mono)}
.logo-text{font-size:1.1rem;font-weight:600;color:var(--text);letter-spacing:-0.01em}
.tagline{font-size:0.72rem;color:var(--muted)}
/* Card */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:16px;transition:border-color 0.2s}
.card:hover{border-color:var(--accent)}
.card-body{padding:20px 22px}
.card-label{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--muted);padding:10px 22px 0;font-weight:500}
/* Form */
.form-group{margin-bottom:14px}
label{display:block;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);margin-bottom:5px;font-weight:500}
textarea,input{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:10px 13px;font-family:var(--mono);font-size:0.75rem;color:var(--text);transition:border-color 0.2s}
textarea:focus,input:focus{outline:none;border-color:var(--accent)}
textarea::placeholder{color:var(--muted)}
textarea{min-height:110px;resize:vertical;line-height:1.6;font-size:0.7rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
/* Button */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:11px 20px;margin-top:12px;border:none;border-radius:var(--sm);font-family:var(--font);font-size:0.78rem;font-weight:600;cursor:pointer;background:var(--accent);color:#09090b;transition:all 0.2s;letter-spacing:0.01em}
.btn:hover{box-shadow:0 0 24px var(--accent-glow)}
.btn:disabled{opacity:0.3;cursor:not-allowed}
.btn svg{width:14px;height:14px}
/* Result */
.result-card{display:none}
.result-card.active{display:block}
.result-head{display:flex;align-items:center;justify-content:space-between;padding:12px 22px;border-bottom:1px solid var(--border)}
.result-head span{font-size:0.65rem;color:var(--muted);font-family:var(--mono)}
.pill{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:10px;font-size:0.6rem;font-weight:600;text-transform:uppercase}
.pill.pass{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(16,185,129,0.25)}
.pill.fail{background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.25)}
.result-body{padding:16px 22px 20px}
.result-pre{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:14px;font-family:var(--mono);font-size:0.68rem;line-height:1.5;white-space:pre-wrap;max-height:360px;overflow-y:auto;color:var(--secondary)}
/* Agent */
.agent-bar{display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);margin-top:6px}
.agent-bar .pulse{width:8px;height:8px;border-radius:50%;background:var(--accent);flex-shrink:0}
.agent-bar .name{font-size:0.72rem;font-weight:500;color:var(--secondary)}
.agent-bar .desc{font-size:0.62rem;color:var(--muted);margin-left:auto}
/* Meta row */
.meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.meta span{font-size:0.58rem;padding:3px 9px;background:var(--elevated);border:1px solid var(--border);border-radius:5px;color:var(--muted);font-family:var(--mono)}
/* Nav link */
.nav-link{display:inline-flex;align-items:center;gap:6px;margin-top:14px;padding:7px 13px;border:1px solid var(--border);border-radius:var(--sm);font-size:0.65rem;color:var(--secondary);transition:all 0.2s;text-decoration:none;background:var(--surface)}
.nav-link:hover{border-color:var(--accent);color:var(--accent)}
/* Error */
.err{display:none;margin-top:10px;padding:9px 13px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);border-radius:var(--sm);color:#ef4444;font-size:0.68rem;align-items:flex-start;gap:7px}
.err.active{display:flex}
/* Loading */
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(9,9,11,0.94);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:20px}
.loading-overlay.active{display:flex}
.loading-ring{width:32px;height:32px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-size:0.78rem;color:var(--secondary);text-align:center}
.loading-text span{color:var(--accent)}
/* Footer */
footer{margin-top:40px;padding-top:12px;border-top:1px solid var(--border);font-size:0.55rem;color:var(--muted);text-align:center}
/* Anim */
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.fade{animation:fadeIn 0.35s ease backwards}
.d1{animation-delay:0.05s}.d2{animation-delay:0.1s}.d3{animation-delay:0.15s}
@media(prefers-reduced-motion:reduce){*,*::before{animation:none!important}html{scroll-behavior:auto}}
@media(max-width:600px){.container{padding:24px 14px 40px}.form-row{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<header class="fade">
<div class="logo"><div class="logo-icon">{/}</div><div class="logo-text">Code Debugger</div></div>
<p class="tagline">AI Debug Agent — root cause analysis, fix generation, validation</p>
</header>

<div class="card fade d1">
<div class="card-label">$ debug</div>
<div class="card-body">
<form id="debugForm" novalidate>
<div class="form-group">
<label for="errorTrace">Error trace <span style="color:var(--muted)">*</span></label>
<textarea id="errorTrace" autocomplete="off" spellcheck="false" placeholder="Paste stack trace..."></textarea>
</div>
<div class="form-row">
<div class="form-group"><label for="failingFile">File</label><input type="text" id="failingFile" placeholder="app.py"></div>
<div class="form-group"><label for="failingLine">Line</label><input type="number" id="failingLine" placeholder="42"></div>
</div>
</form>
<div class="err" id="errorMsg" role="alert"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><span id="errorText"></span></div>
<button type="button" class="btn" id="submitBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Debug</button>
</div>
</div>

<div class="card result-card" id="resultCard">
<div class="result-head"><span>// report</span><span class="pill" id="statusPill"></span></div>
<div class="result-body"><pre class="result-pre" id="reportContent"></pre></div>
</div>

<div class="fade d2">
<div class="agent-bar"><div class="pulse"></div><span class="name">Debug Agent</span><span class="desc">RCA &middot; Fix &middot; Validate</span></div>
<div class="meta">
<span>stack trace</span><span>dependency check</span><span>runtime analysis</span><span>data flow</span>
<span>fix generation</span><span>validation</span><span>regression</span><span>security</span><span>performance</span><span>refactor</span>
</div>
</div>

<div style="margin-top:20px" class="fade d3">
<a href="/infrastructure" class="nav-link">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
Infrastructure
</a>
<a href="/v2/" class="nav-link" style="margin-left:6px">
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
Advanced
</a>
</div>

<footer>code debugger &middot; single debug agent</footer>
</div>

<div class="loading-overlay" id="loadingOverlay">
<div class="loading-ring"></div>
<div class="loading-text"><span>$</span> Debugging...</div>
</div>

<script>
document.getElementById('submitBtn').addEventListener('click',async()=>{
const e=document.getElementById('errorTrace'),ff=document.getElementById('failingFile'),fl=document.getElementById('failingLine');
const em=document.getElementById('errorMsg'),rc=document.getElementById('resultCard'),btn=document.getElementById('submitBtn');
if(!e.value.trim()){em.classList.add('active');return}
em.classList.remove('active');rc.classList.remove('active');btn.disabled=true;document.getElementById('loadingOverlay').classList.add('active');
try{const r=await fetch('/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:e.value,failing_file:ff.value||'unknown',failing_line:fl.value?parseInt(fl.value):null})});const d=await r.json();
if(d.success){const p=document.getElementById('statusPill'),rp=document.getElementById('reportContent');p.className='pill '+(d.validation_passed?'pass':'fail');p.textContent=d.validation_passed?'PASS':'FAIL';rp.textContent=d.final_report;rc.classList.add('active');rc.scrollIntoView({behavior:'smooth'})}
else{document.getElementById('errorText').textContent=d.error||'Failed';em.classList.add('active')}}
catch(e2){document.getElementById('errorText').textContent='Connection error';em.classList.add('active')}
finally{document.getElementById('loadingOverlay').classList.remove('active');btn.disabled=false}});
document.getElementById('errorTrace').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))document.getElementById('submitBtn').click()});
</script>
</body>
</html>"""

INFRASTRUCTURE_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#09090b">
<title>Infrastructure — Infrastructure Manager</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#09090b;--surface:#111113;--elevated:#1a1a1e;--border:#27272a;--text:#fafafa;--secondary:#a1a1aa;--muted:#52525b;--accent:#10b981;--accent-dim:rgba(16,185,129,0.1);--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:12px;--sm:8px;--ease:0.2s ease}
body{font-family:var(--font);background:var(--bg);color:var(--text);padding:24px;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent);color:#09090b}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.container{max-width:680px;margin:0 auto}
h1{font-size:1.1rem;font-weight:600;letter-spacing:-0.01em;margin-bottom:2px}
.subtitle{font-size:0.72rem;color:var(--muted);margin-bottom:24px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-bottom:14px}
.card:hover{border-color:var(--accent)}
select,textarea{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:9px 12px;font-family:var(--mono);font-size:0.72rem;color:var(--text)}
select:focus,textarea:focus{outline:none;border-color:var(--accent)}
.btn{display:flex;align-items:center;justify-content:center;padding:10px 16px;background:var(--accent);color:#09090b;font-family:var(--font);font-size:0.72rem;font-weight:600;border:none;border-radius:var(--sm);cursor:pointer;width:100%;margin-top:10px;transition:all 0.2s}
.btn:hover{box-shadow:0 0 20px rgba(16,185,129,0.2)}
.btn:disabled{opacity:0.3}
.result-pre{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:12px;font-family:var(--mono);font-size:0.65rem;line-height:1.5;white-space:pre-wrap;max-height:300px;overflow-y:auto;color:var(--secondary);margin-top:10px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
footer{margin-top:32px;padding-top:12px;border-top:1px solid var(--border);font-size:0.55rem;color:var(--muted);text-align:center}
</style>
</head>
<body>
<div class="container">
<h1>Infrastructure</h1>
<p class="subtitle">System analysis, security, performance, cost, incident</p>
<div class="card">
<select id="agentSelect">
<option value="infrastructure">Infrastructure Analyzer</option>
<option value="security">Security Auditor</option>
<option value="performance">Performance Optimizer</option>
<option value="cost">Cost Manager</option>
<option value="incident">Incident Responder</option>
</select>
<button class="btn" id="runBtn">Run</button>
<pre class="result-pre" id="output">Select an agent and run.</pre>
</div>
<a href="/">&larr; Back</a>
<footer>code debugger &middot; infrastructure</footer>
</div>
<script>
document.getElementById('runBtn').addEventListener('click',async function(){
const btn=this,out=document.getElementById('output'),agent=document.getElementById('agentSelect').value;
btn.disabled=true;out.textContent='Running...';
try{const r=await fetch('/api/infrastructure/'+agent,{method:'POST'});const d=await r.json();
if(d.success)out.textContent=JSON.stringify(d.result?.output||d.result||d,null,2);else out.textContent='Error: '+(d.error||'')}
catch(e){out.textContent='Error: '+e.message}finally{btn.disabled=false}});
</script>
</body>
</html>"""
