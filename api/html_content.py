INDEX_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<meta name="theme-color" content="#06080f">
<title>Code Debugger — Multi-Agent AI Debugging & Infrastructure</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg-deep:#06080f;--bg-surface:#0F172A;--bg-elevated:#1E293B;--bg-hover:#273549;--border:#334155;--border-glow:rgba(34,197,94,0.35);--text:#F8FAFC;--secondary:#94A3B8;--muted:#64748B;--accent:#22C55E;--accent-dim:rgba(34,197,94,0.12);--accent-b:#06B6D4;--accent-b-dim:rgba(6,182,212,0.12);--accent-c:#F59E0B;--accent-c-dim:rgba(245,158,11,0.12);--danger:#EF4444;--danger-dim:rgba(239,68,68,0.12);--font:'JetBrains Mono',monospace;--radius-sm:4px;--radius-md:8px;--radius-lg:16px;--ease:0.2s cubic-bezier(0.16,1,0.3,1)}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg-deep);color:var(--text);min-height:100vh;line-height:1.7;overflow-x:hidden;-webkit-font-smoothing:antialiased;font-size:14px;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
::selection{background:var(--accent);color:var(--bg-deep)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:var(--radius-sm)}
p{color:var(--secondary)}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.bg-grid{position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0}
.bg-glow{position:fixed;width:500px;height:500px;border-radius:50%;filter:blur(120px);pointer-events:none;z-index:0;opacity:0.06}
.bg-glow-1{top:-200px;left:-100px;background:var(--accent)}
.bg-glow-2{bottom:-200px;right:-100px;background:var(--accent-b)}
.container{max-width:960px;margin:0 auto;padding:40px 20px 64px;position:relative;z-index:1}
h1{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:500;letter-spacing:-0.01em;text-transform:uppercase;margin-bottom:4px;line-height:1.3}
h1 em{font-style:normal;color:var(--accent)}
h2{font-size:0.85rem;font-weight:500;text-transform:uppercase;letter-spacing:0.08em;color:var(--secondary);margin-bottom:14px;display:flex;align-items:center;gap:8px}
h2 svg{width:14px;height:14px;color:var(--accent);flex-shrink:0}
h3{font-size:0.82rem;font-weight:500;margin-bottom:2px;color:var(--text)}
header{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:36px;padding-bottom:14px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:10px}
.header-tagline{font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.12em}
.header-badge{display:inline-flex;align-items:center;gap:5px;padding:5px 12px;background:var(--accent-dim);border:1px solid rgba(34,197,94,0.2);border-radius:16px;font-size:0.55rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.06em;font-weight:500}
.card{background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-lg);margin-bottom:20px}
.card-body{padding:24px 28px}
.card-label{font-size:0.55rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);padding:12px 28px 0;font-weight:500}
.form-group{margin-bottom:18px}
label{display:block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:5px;font-weight:500}
textarea,input{width:100%;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:11px 14px;font-family:var(--font);font-size:0.78rem;color:var(--text);transition:border-color var(--ease),box-shadow var(--ease)}
textarea:focus,input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-dim)}
textarea::placeholder,input::placeholder{color:var(--muted)}
textarea{min-height:140px;resize:vertical;line-height:1.7;font-size:0.72rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:12px 24px;margin-top:16px;background:var(--accent);color:var(--bg-deep);font-family:var(--font);font-size:0.75rem;font-weight:500;border:none;border-radius:var(--radius-sm);cursor:pointer;transition:box-shadow var(--ease),transform var(--ease);letter-spacing:0.02em}
.btn:hover{box-shadow:0 0 20px var(--border-glow);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:0.3;cursor:not-allowed;transform:none;box-shadow:none}
.btn svg{width:14px;height:14px;flex-shrink:0}
.result-card{display:none}
.result-card.active{display:block}
.result-head{display:flex;align-items:center;justify-content:space-between;padding:14px 28px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:8px}
.result-head span{font-size:0.65rem;color:var(--muted)}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;border-radius:12px;font-size:0.6rem;font-weight:500;text-transform:uppercase}
.badge.pass{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(34,197,94,0.25)}
.badge.fail{background:var(--danger-dim);color:var(--danger);border:1px solid rgba(239,68,68,0.25)}
.badge svg{width:9px;height:9px}
.result-body{padding:18px 28px 24px}
.result-pre{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;font-size:0.7rem;line-height:1.7;white-space:pre-wrap;max-height:400px;overflow-y:auto;color:var(--secondary)}
.result-pre::-webkit-scrollbar{width:3px}
.result-pre::-webkit-scrollbar-thumb{background:var(--bg-hover);border-radius:2px}
.err{display:none;margin-top:14px;background:var(--danger-dim);border:1px solid rgba(239,68,68,0.2);border-radius:var(--radius-sm);padding:12px 16px;color:var(--danger);font-size:0.7rem;line-height:1.5;align-items:flex-start;gap:8px}
.err.active{display:flex}
.err svg{width:12px;height:12px;flex-shrink:0;margin-top:2px}
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(6,8,15,0.93);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:22px;overscroll-behavior:contain}
.loading-overlay.active{display:flex}
.loading-cursor{width:12px;height:18px;background:var(--accent);animation:blink 0.8s step-end infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
.loading-text{font-size:0.78rem;color:var(--secondary);text-align:center;line-height:2}
.loading-text span{color:var(--accent)}
.loading-steps{display:flex;gap:22px;margin-top:4px;flex-wrap:wrap;justify-content:center}
.loading-step{font-size:0.6rem;color:var(--muted);opacity:0.3;transition:opacity 0.3s;display:flex;align-items:center;gap:4px}
.loading-step.active{color:var(--accent);opacity:1}

/* Agent showcase */
.agent-groups{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:4px}
.agent-group{border:1px solid var(--border);border-radius:var(--radius-md);overflow:hidden}
.agent-group h3{padding:10px 14px;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;background:var(--bg-elevated);border-bottom:1px solid var(--border)}
.agent-group.debug h3{color:var(--accent)}
.agent-group.infra h3{color:var(--accent-b)}
.agent-group.db h3{color:var(--accent-c)}
.agent-group .items{display:flex;flex-direction:column}
.agent-item{display:flex;align-items:center;gap:10px;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.65rem;transition:background var(--ease)}
.agent-item:last-child{border:none}
.agent-item:hover{background:var(--bg-elevated)}
.agent-item .dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.agent-item .dot.g{background:var(--accent)}
.agent-item .dot.c{background:var(--accent-b)}
.agent-item .dot.a{background:var(--accent-c)}
.agent-item .name{color:var(--secondary);font-weight:500}
.agent-item .role{color:var(--muted);font-size:0.6rem;margin-left:auto;text-align:right}

/* Lang chips */
.lang-chips{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.lang-chip{padding:2px 8px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:8px;font-size:0.55rem;color:var(--muted)}

.nav-link{display:inline-flex;align-items:center;gap:6px;margin-top:16px;padding:8px 14px;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:0.65rem;color:var(--secondary);transition:color var(--ease),border-color var(--ease)}
.nav-link:hover{color:var(--accent);border-color:var(--accent);text-decoration:none}
.nav-link svg{width:12px;height:12px;flex-shrink:0}
footer{margin-top:48px;padding-top:14px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
footer p{font-size:0.55rem;color:var(--muted);letter-spacing:0.08em}

@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.af{animation:fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) backwards}
.ad1{animation-delay:0.05s}.ad2{animation-delay:0.1s}.ad3{animation-delay:0.15s}.ad4{animation-delay:0.2s}.ad5{animation-delay:0.25s}.ad6{animation-delay:0.3s}
@media(prefers-reduced-motion:reduce){*, .af{animation:none!important;transition-duration:0.01ms!important}html{scroll-behavior:auto}}
@media(max-width:768px){
.container{padding:24px 14px 48px}
.agent-groups{grid-template-columns:1fr}
.form-row{grid-template-columns:1fr}
.card-body{padding:18px}
.loading-steps{flex-direction:column;gap:4px}
.result-head{flex-direction:column;align-items:flex-start}
}
</style>
</head>
<body>
<div class="bg-grid" aria-hidden="true"></div>
<div class="bg-glow bg-glow-1" aria-hidden="true"></div>
<div class="bg-glow bg-glow-2" aria-hidden="true"></div>

<div class="container">
<header class="af">
<div>
<h1>code&nbsp;<em>debugger</em></h1>
<p class="header-tagline">Multi-Agent AI Debugging &amp; Infrastructure Platform</p>
</div>
<div class="header-badge">
<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
20 Agents Total
</div>
</header>

<div class="card af ad1">
<p class="card-label">$ ./submit_error_trace</p>
<div class="card-body">
<form id="debugForm" novalidate>
<div class="form-group">
<label for="errorTrace">Error Trace / Stack Trace <span style="color:var(--accent-b)">*</span></label>
<textarea id="errorTrace" autocomplete="off" spellcheck="false" placeholder="$ paste error trace here..."></textarea>
</div>
<div class="form-row">
<div class="form-group">
<label for="failingFile">Failing File</label>
<input type="text" id="failingFile" autocomplete="off" spellcheck="false" placeholder="path/to/file.py">
</div>
<div class="form-group">
<label for="failingLine">Failing Line</label>
<input type="number" id="failingLine" autocomplete="off" placeholder="42">
</div>
</div>
</form>
<div class="err" id="errorMsg" role="alert">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
<span id="errorText"></span>
</div>
<button type="button" class="btn" id="submitBtn">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
Run Analysis
</button>
</div>
</div>

<div class="card result-card" id="resultCard" role="region" aria-live="polite">
<div class="result-head">
<span>// analysis_report.md</span>
<span class="badge" id="statusBadge" role="status"></span>
</div>
<div class="result-body">
<pre class="result-pre" id="reportContent" tabindex="0"></pre>
</div>
</div>

<section class="af ad3">
<h2>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
Agent Capabilities
</h2>
<div class="agent-groups">
<div class="agent-group debug">
<h3>10 Debug Agents</h3>
<div class="items">
<div class="agent-item"><span class="dot g"></span><span class="name">StackTraceAgent</span><span class="role">Traceback parsing</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">DependencyAgent</span><span class="role">Version conflict detection</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">RuntimeAgent</span><span class="role">Runtime state analysis</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">DataFlowAgent</span><span class="role">Variable corruption tracing</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">FixGenerationAgent</span><span class="role">Fix generation</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">ValidationAgent</span><span class="role">Test execution &amp; verification</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">RegressionAgent</span><span class="role">Side effect detection</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">SecurityImpactAgent</span><span class="role">Vulnerability scanning</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">PerformanceImpactAgent</span><span class="role">Bottleneck analysis</span></div>
<div class="agent-item"><span class="dot g"></span><span class="name">RefactorAgent</span><span class="role">Code quality improvement</span></div>
</div>
</div>
<div class="agent-group infra">
<h3>5 Infrastructure + 5 DB Agents</h3>
<div class="items">
<div class="agent-item"><span class="dot c"></span><span class="name">Infrastructure Analyzer</span><span class="role">System health &amp; capacity</span></div>
<div class="agent-item"><span class="dot c"></span><span class="name">Security Auditor</span><span class="role">Port scan &amp; compliance</span></div>
<div class="agent-item"><span class="dot c"></span><span class="name">Performance Optimizer</span><span class="role">Tuning &amp; bottleneck fix</span></div>
<div class="agent-item"><span class="dot c"></span><span class="name">Cost Manager</span><span class="role">Cost optimization &amp; waste</span></div>
<div class="agent-item"><span class="dot c"></span><span class="name">Incident Responder</span><span class="role">Incident detection &amp; RCA</span></div>
<div class="agent-item" style="border-top:1px solid rgba(255,255,255,0.04);margin-top:4px;padding-top:10px">
<span class="dot a"></span><span class="name">SQLQueryOptimizer</span><span class="role">Slow query analysis</span></div>
<div class="agent-item"><span class="dot a"></span><span class="name">MigrationValidator</span><span class="role">Migration safety</span></div>
<div class="agent-item"><span class="dot a"></span><span class="name">SchemaAnalyzer</span><span class="role">Schema constraint check</span></div>
<div class="agent-item"><span class="dot a"></span><span class="name">TransactionAgent</span><span class="role">Deadlock &amp; race detection</span></div>
<div class="agent-item"><span class="dot a"></span><span class="name">ORMMapperAgent</span><span class="role">ORM mismatch detection</span></div>
</div>
</div>
</div>
<div style="margin-top:14px">
<h2 style="margin-bottom:6px">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
Execution Sandbox Languages
</h2>
<div class="lang-chips">
<span class="lang-chip">Python</span><span class="lang-chip">JavaScript</span><span class="lang-chip">TypeScript</span><span class="lang-chip">Go</span><span class="lang-chip">Rust</span>
<span class="lang-chip">Java</span><span class="lang-chip">C++</span><span class="lang-chip">Ruby</span><span class="lang-chip">PHP</span><span class="lang-chip">C#</span><span class="lang-chip">SQL</span>
</div>
</div>
</section>

<a href="/infrastructure" class="nav-link">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
Infrastructure Management
</a>

<footer>
<p>// code debugger v2 // 20 agents // autonomous repair // sandbox execution</p>
<p>powered by openai agents sdk</p>
</footer>
</div>

<div class="loading-overlay" id="loadingOverlay" role="dialog" aria-modal="true" aria-label="Running analysis">
<div class="loading-cursor" aria-hidden="true"></div>
<div class="loading-text">
<span>$</span> Running Multi-Agent Analysis...
<div class="loading-steps">
<span class="loading-step" id="step1"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/></svg> Root Cause</span>
<span class="loading-step" id="step2"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg> Fix Generation</span>
<span class="loading-step" id="step3"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Validation</span>
</div>
</div>
</div>

<script>
const steps=['step1','step2','step3'];let cur=0,intv;
function startLoad(){cur=0;steps.forEach((id,i)=>{document.getElementById(id).classList.toggle('active',i===0)});intv=setInterval(()=>{document.getElementById(steps[cur]).classList.remove('active');cur=(cur+1)%steps.length;document.getElementById(steps[cur]).classList.add('active')},2200)}
function stopLoad(){clearInterval(intv);steps.forEach(id=>document.getElementById(id).classList.remove('active'))}
async function debugCode(){
const err=document.getElementById('errorTrace'),ff=document.getElementById('failingFile'),fl=document.getElementById('failingLine');
const em=document.getElementById('errorMsg'),rc=document.getElementById('resultCard'),btn=document.getElementById('submitBtn'),lo=document.getElementById('loadingOverlay');
if(!err.value.trim()){em.classList.add('active');document.getElementById('errorText').textContent='Provide an error trace';err.focus();return}
em.classList.remove('active');rc.classList.remove('active');btn.disabled=true;lo.classList.add('active');startLoad();
try{
const r=await fetch('/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:err.value,failing_file:ff.value||'unknown',failing_line:fl.value?parseInt(fl.value):null})});
const d=await r.json();
if(d.success){const sb=document.getElementById('statusBadge'),rp=document.getElementById('reportContent');
sb.className='badge '+(d.validation_passed?'pass':'fail');
sb.innerHTML=(d.validation_passed?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>PASS':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>FAIL');
rp.textContent=d.final_report;rc.classList.add('active');rc.scrollIntoView({behavior:'smooth',block:'start'})
}else{document.getElementById('errorText').textContent=d.error||'Analysis failed';em.classList.add('active')}
}catch(e){document.getElementById('errorText').textContent='Connection error';em.classList.add('active')}
finally{lo.classList.remove('active');stopLoad();btn.disabled=false}
}
document.getElementById('submitBtn').addEventListener('click',debugCode);
document.getElementById('errorTrace').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))debugCode()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.getElementById('loadingOverlay').classList.remove('active');stopLoad()}});
</script>
</body>
</html>"""

INFRASTRUCTURE_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<meta name="theme-color" content="#06080f">
<title>Infrastructure — Multi-Agent Infrastructure Management</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg-deep:#06080f;--bg-surface:#0F172A;--bg-elevated:#1E293B;--bg-hover:#273549;--border:#334155;--border-glow:rgba(34,197,94,0.35);--text:#F8FAFC;--secondary:#94A3B8;--muted:#64748B;--accent:#22C55E;--accent-dim:rgba(34,197,94,0.12);--accent-b:#06B6D4;--accent-b-dim:rgba(6,182,212,0.12);--accent-c:#F59E0B;--accent-c-dim:rgba(245,158,11,0.12);--danger:#EF4444;--danger-dim:rgba(239,68,68,0.12);--font:'JetBrains Mono',monospace;--radius-sm:4px;--radius-md:8px;--radius-lg:16px;--ease:0.2s cubic-bezier(0.16,1,0.3,1)}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg-deep);color:var(--text);min-height:100vh;line-height:1.7;overflow-x:hidden;-webkit-font-smoothing:antialiased;font-size:14px;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
::selection{background:var(--accent);color:var(--bg-deep)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:var(--radius-sm)}
p{color:var(--secondary);font-size:0.7rem;line-height:1.6}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
button{cursor:pointer;font-family:var(--font)}
.bg-grid{position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0}
.bg-glow{position:fixed;width:500px;height:500px;border-radius:50%;filter:blur(120px);pointer-events:none;z-index:0;opacity:0.06}
.bg-glow-1{top:-200px;left:-200px;background:var(--accent)}
.bg-glow-2{bottom:-200px;right:-200px;background:var(--accent-b)}
.container{max-width:960px;margin:0 auto;padding:36px 20px 64px;position:relative;z-index:1}
h1{font-size:clamp(1.2rem,2.5vw,1.6rem);font-weight:500;letter-spacing:-0.01em;text-transform:uppercase;line-height:1.3}
h1 em{font-style:normal;color:var(--accent)}
h2{font-size:0.82rem;font-weight:500;margin-bottom:14px;color:var(--secondary)}
h3{font-size:0.75rem;font-weight:500;margin-bottom:3px;color:var(--text)}
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:10px}
header p{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted)}
header .badge{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:var(--accent-dim);border:1px solid rgba(34,197,94,0.2);border-radius:14px;font-size:0.55rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.06em;font-weight:500}
.tab-bar{display:flex;gap:0;margin-bottom:24px;border-bottom:1px solid var(--border)}
.tab-btn{background:none;border:none;border-bottom:2px solid transparent;padding:9px 18px;font-size:0.68rem;font-weight:500;color:var(--muted);transition:color var(--ease),border-color var(--ease);letter-spacing:0.04em}
.tab-btn:hover{color:var(--secondary)}
.tab-btn[aria-selected="true"]{color:var(--accent);border-bottom-color:var(--accent)}
.tab-content{display:none}
.tab-content[aria-hidden="false"]{display:block}
.card{background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:22px 24px;margin-bottom:18px}
.card-label{font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:8px;font-weight:500}
.agent-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.agent-item{background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-md);padding:18px;display:flex;flex-direction:column;transition:border-color var(--ease),transform var(--ease)}
.agent-item:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.2)}
.agent-item:nth-child(2):hover,.agent-item:nth-child(3):hover{border-color:var(--accent-b)}
.agent-item:nth-child(4):hover{border-color:var(--accent-c)}
.agent-item:nth-child(5):hover,.agent-item:nth-child(6):hover{border-color:var(--danger)}
.agent-item .tag{font-size:0.5rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;font-weight:500}
.agent-item:nth-child(1) .tag{color:var(--accent)}
.agent-item:nth-child(2) .tag,
.agent-item:nth-child(3) .tag{color:var(--accent-b)}
.agent-item:nth-child(4) .tag{color:var(--accent-c)}
.agent-item:nth-child(5) .tag,
.agent-item:nth-child(6) .tag{color:var(--danger)}
.agent-item p{font-size:0.62rem;color:var(--muted);margin-bottom:10px;flex:1;line-height:1.5}
.agent-btn{margin-top:auto;padding:7px 0;width:100%;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:0.6rem;font-weight:500;color:var(--secondary);transition:color var(--ease),border-color var(--ease),background var(--ease);text-transform:uppercase;letter-spacing:0.06em}
.agent-item:hover .agent-btn{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.agent-item:nth-child(2):hover .agent-btn,
.agent-item:nth-child(3):hover .agent-btn{border-color:var(--accent-b);color:var(--accent-b);background:var(--accent-b-dim)}
.agent-item:nth-child(4):hover .agent-btn{border-color:var(--accent-c);color:var(--accent-c);background:var(--accent-c-dim)}
.agent-item:nth-child(5):hover .agent-btn,
.agent-item:nth-child(6):hover .agent-btn{border-color:var(--danger);color:var(--danger);background:var(--danger-dim)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:11px 18px;background:var(--accent);color:var(--bg-deep);font-family:var(--font);font-size:0.7rem;font-weight:500;border:none;border-radius:var(--radius-sm);cursor:pointer;transition:box-shadow var(--ease),transform var(--ease)}
.btn:hover{box-shadow:0 0 20px var(--border-glow);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:0.3;cursor:not-allowed;transform:none;box-shadow:none}
.btn svg{width:12px;height:12px;flex-shrink:0}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--secondary)}
.btn-outline:hover{color:var(--accent);border-color:var(--accent);box-shadow:none}
.form-group{margin-bottom:14px}
label{display:block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:5px;font-weight:500}
textarea{width:100%;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:11px 14px;font-family:var(--font);font-size:0.75rem;color:var(--text);transition:border-color var(--ease)}
textarea:focus{outline:none;border-color:var(--accent)}
textarea::placeholder{color:var(--muted)}
textarea{min-height:90px;resize:vertical;line-height:1.7}
.loading{display:none;text-align:center;padding:36px}
.loading.active{display:block}
.loading-cursor{width:10px;height:16px;background:var(--accent);animation:blink 0.8s step-end infinite;margin:0 auto 14px}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
.loading p{font-size:0.68rem;color:var(--muted)}
.results{display:none}
.results.active{display:block}
.result-section{margin-bottom:14px}
.result-section .rhead{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm) var(--radius-sm) 0 0;padding:9px 14px;font-size:0.65rem;font-weight:500;color:var(--accent);border-bottom:none}
.result-section:nth-child(4) .rhead{color:var(--accent-c)}
.result-section:last-child .rhead{color:var(--danger)}
.result-section .rbody{background:var(--bg-surface);border:1px solid var(--border);border-radius:0 0 var(--radius-sm) var(--radius-sm);padding:12px 14px;font-size:0.68rem;line-height:1.6;white-space:pre-wrap;max-height:360px;overflow-y:auto;color:var(--secondary)}
.err{display:none;margin-top:14px;background:var(--danger-dim);border:1px solid rgba(239,68,68,0.2);border-radius:var(--radius-sm);padding:10px 14px;color:var(--danger);font-size:0.68rem;align-items:flex-start;gap:8px}
.err.active{display:flex}
.nav-link{display:inline-flex;align-items:center;gap:6px;margin-top:10px;padding:7px 12px;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:0.62rem;color:var(--secondary);transition:color var(--ease),border-color var(--ease)}
.nav-link:hover{color:var(--accent);border-color:var(--accent);text-decoration:none}
footer{margin-top:40px;padding-top:14px;border-top:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
footer p{font-size:0.55rem;color:var(--muted);letter-spacing:0.08em}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.af{animation:fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) backwards}
.ad1{animation-delay:0.05s}.ad2{animation-delay:0.1s}.ad3{animation-delay:0.15s}.ad4{animation-delay:0.2s}
@media(prefers-reduced-motion:reduce){*, .af{animation:none!important;transition-duration:0.01ms!important}html{scroll-behavior:auto}}
@media(max-width:768px){
.container{padding:24px 14px 48px}
.agent-grid{grid-template-columns:1fr}
.card{padding:16px 18px}
.tab-btn{padding:9px 12px;font-size:0.6rem}
}
</style>
</head>
<body>
<div class="bg-grid" aria-hidden="true"></div>
<div class="bg-glow bg-glow-1" aria-hidden="true"></div>
<div class="bg-glow bg-glow-2" aria-hidden="true"></div>

<div class="container">
<header>
<div>
<h1>infrastructure&nbsp;<em>ctl</em></h1>
<p>Multi-Agent Infrastructure Management</p>
</div>
<div class="badge">5 Specialized Agents</div>
</header>

<div class="tab-bar" role="tablist" aria-label="Infrastructure views">
<button class="tab-btn" role="tab" aria-selected="true" aria-controls="panel-dashboard" id="tab-dashboard" tabindex="0">Dashboard</button>
<button class="tab-btn" role="tab" aria-selected="false" aria-controls="panel-audit" id="tab-audit" tabindex="-1">Full Audit</button>
<button class="tab-btn" role="tab" aria-selected="false" aria-controls="panel-incident" id="tab-incident" tabindex="-1">Incident</button>
</div>

<div class="tab-content" role="tabpanel" id="panel-dashboard" aria-hidden="false">
<div class="card af">
<p class="card-label">// agents</p>
<div class="agent-grid">
<div class="agent-item" tabindex="0">
<span class="tag">01 Infrastructure Analyzer</span>
<p>System health, resource monitoring, container checks, capacity planning, architecture review.</p>
<button class="agent-btn" data-agent="infrastructure">Run Analysis</button>
</div>
<div class="agent-item" tabindex="0">
<span class="tag">02 Security Auditor</span>
<p>Port scanning, SSL checks, vulnerability assessment, compliance (PCI DSS, GDPR, HIPAA).</p>
<button class="agent-btn" data-agent="security">Run Audit</button>
</div>
<div class="agent-item" tabindex="0">
<span class="tag">03 Performance Optimizer</span>
<p>Bottleneck detection, resource tuning, load balancing review, optimization recommendations.</p>
<button class="agent-btn" data-agent="performance">Optimize</button>
</div>
<div class="agent-item" tabindex="0">
<span class="tag">04 Cost Manager</span>
<p>Waste identification, underutilized resources, savings recommendations, ROI analysis.</p>
<button class="agent-btn" data-agent="cost">Analyze Costs</button>
</div>
<div class="agent-item" tabindex="0">
<span class="tag">05 Incident Responder</span>
<p>Proactive monitoring, anomaly detection, root cause analysis, mitigation steps, postmortems.</p>
<button class="agent-btn" data-agent="incident">Check Health</button>
</div>
</div>
</div>
</div>

<div class="tab-content" role="tabpanel" id="panel-audit" aria-hidden="true">
<div class="card af">
<p class="card-label">// full_audit</p>
<p style="margin-bottom:14px">Runs all 5 infrastructure agents sequentially — analysis, security, performance, cost, and incident response.</p>
<button class="btn" id="fullAuditBtn" style="width:100%">Run Full Audit</button>
</div>
</div>

<div class="tab-content" role="tabpanel" id="panel-incident" aria-hidden="true">
<div class="card af">
<p class="card-label">// incident_response</p>
<div class="form-group">
<label for="incidentDesc">Incident Description</label>
<textarea id="incidentDesc" autocomplete="off" placeholder="e.g. High CPU usage on production, response times degraded 300%..."></textarea>
</div>
<button class="btn" id="incidentBtn" style="width:100%;background:var(--danger)">Analyze & Respond</button>
</div>
</div>

<div class="loading" id="loading" role="status">
<div class="loading-cursor" aria-hidden="true"></div>
<p id="loadingText">Running analysis...</p>
</div>

<div class="err" id="error" role="alert">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
<span id="errorText"></span>
</div>

<div class="results" id="results" role="region">
<div class="card">
<p class="card-label">// output</p>
<div id="resultsContent"></div>
</div>
</div>

<a href="/" class="nav-link">&larr; Back to Debugger</a>

<footer>
<p>// infrastructure ctl // 5 specialized agents</p>
<p>powered by openai agents sdk</p>
</footer>
</div>

<script>
const tabs=document.querySelectorAll('[role="tab"]'),panels=document.querySelectorAll('[role="tabpanel"]');
tabs.forEach(tab=>{tab.addEventListener('click',()=>switchTab(tab.id))});
function switchTab(id){
tabs.forEach(t=>{const s=t.id===id;t.setAttribute('aria-selected',s);t.tabIndex=s?0:-1});
panels.forEach(p=>{p.setAttribute('aria-hidden',p.id!=='panel-'+id.replace('tab-',''))})}
document.addEventListener('keydown',e=>{
if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;
const cur=document.querySelector('[role="tab"][aria-selected="true"]'),arr=[...tabs],idx=arr.indexOf(cur);
const nxt=e.key==='ArrowRight'?(idx+1)%arr.length:(idx-1+arr.length)%arr.length;
arr[nxt].focus();switchTab(arr[nxt].id)});

const loading=document.getElementById('loading'),lt=document.getElementById('loadingText');
const errDiv=document.getElementById('error'),et=document.getElementById('errorText');
const results=document.getElementById('results'),rc=document.getElementById('resultsContent');
function showLoad(t){lt.textContent=t;loading.classList.add('active')}
function hideLoad(){loading.classList.remove('active')}
function showErr(m){et.textContent=m;errDiv.classList.add('active')}
function hideErr(){errDiv.classList.remove('active');results.classList.remove('active')}
function hideRes(){results.classList.remove('active')}

function renderResult(agent,output){
const names={'infrastructure':'Infrastructure Analyzer','security':'Security Auditor','performance':'Performance Optimizer','cost':'Cost Manager','incident':'Incident Responder'};
rc.innerHTML='<div class="result-section"><div class="rhead">$ '+names[agent]+'</div><div class="rbody">'+(output||'No output')+'</div></div>';
results.classList.add('active');results.scrollIntoView({behavior:'smooth',block:'start'})}

function renderFullAudit(r){
const items=[{k:'infrastructure_analysis',l:'Infrastructure Analyzer'},{k:'security_audit',l:'Security Auditor'},{k:'performance_optimization',l:'Performance Optimizer'},{k:'cost_analysis',l:'Cost Manager'},{k:'incident_response',l:'Incident Responder'}];
rc.innerHTML=items.map(i=>r[i.k]?'<div class="result-section"><div class="rhead">$ '+i.l+'</div><div class="rbody">'+(r[i.k].output||'No output')+'</div></div>':'').join('');
results.classList.add('active');results.scrollIntoView({behavior:'smooth',block:'start'})}

document.querySelectorAll('[data-agent]').forEach(btn=>{
btn.addEventListener('click',async function(){
const agent=this.dataset.agent;hideErr();hideRes();showLoad('Running '+agent+'...');
try{const r=await fetch('/api/infrastructure/'+agent,{method:'POST'});const d=await r.json();
if(d.success)renderResult(agent,d.result.output);else showErr(d.error||'Failed')}
catch(e){showErr('Connection failed')}finally{hideLoad()}});});

document.getElementById('fullAuditBtn').addEventListener('click',async function(){
hideErr();hideRes();this.disabled=true;showLoad('Full audit (5 agents)...');
try{const r=await fetch('/api/infrastructure/full-audit',{method:'POST'});const d=await r.json();
if(d.success)renderFullAudit(d.result);else showErr(d.error||'Audit failed')}
catch(e){showErr('Connection failed')}finally{hideLoad();this.disabled=false}});

document.getElementById('incidentBtn').addEventListener('click',async function(){
const desc=document.getElementById('incidentDesc').value;
if(!desc.trim()){showErr('Describe the incident');return}
hideErr();hideRes();this.disabled=true;showLoad('Analyzing incident...');
try{const r=await fetch('/api/infrastructure/incident',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({description:desc})});const d=await r.json();
if(d.success)renderResult('incident',d.result.output);else showErr(d.error||'Failed')}
catch(e){showErr('Connection failed')}finally{hideLoad();this.disabled=false}});
</script>
</body>
</html>"""
