INDEX_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#09090b">
<title>Code Debugger</title>
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
.logo-icon{width:28px;height:28px;border-radius:7px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:13px;color:#09090b;font-weight:700;font-family:var(--mono)}
.logo-text{font-size:1rem;font-weight:600;letter-spacing:-0.01em;color:var(--text)}
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
.output{display:none;margin-top:20px;padding:16px 20px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);font-family:var(--mono);font-size:0.74rem;line-height:1.6;white-space:pre-wrap;color:var(--secondary);max-height:500px;overflow-y:auto}
.output.show{display:block}
.output .pass{color:var(--accent);font-weight:600}
.output .fail{color:#ef4444;font-weight:600}
.loading{display:none;align-items:center;gap:8px;margin-top:16px;padding:10px 14px}
.loading.show{display:flex}
.loading .ring{width:16px;height:16px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:s 0.7s linear infinite;flex-shrink:0}
@keyframes s{to{transform:rotate(360deg)}}
.loading span{font-size:0.72rem;color:var(--muted)}
.loading .dots::after{content:'';animation:d 1.5s steps(4,end) infinite}
@keyframes d{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}100%{content:''}}
.status{display:none;margin-top:8px;font-size:0.65rem;font-family:var(--mono);color:var(--muted);padding:0 4px}
.status.show{display:block}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
footer{padding:16px 20px;text-align:center;font-size:0.55rem;color:var(--muted)}
@media(max-width:600px){.container{padding:24px 14px 16px}textarea{font-size:0.78rem}}
</style>
</head>
<body>
<div class="container">
<div class="logo"><div class="logo-icon">{/}</div><div class="logo-text">Code Debugger</div></div>
<div class="input-area">
<textarea id="input" rows="2" placeholder="Paste an error trace..." autocomplete="off" spellcheck="false"></textarea>
<div class="input-footer">
<span>Ctrl+Enter to send</span>
<button class="send-btn" id="sendBtn" aria-label="Debug">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polyline points="22 2 15 22 11 13 2 9 22 2"/></svg>
</button>
</div>
</div>
<div class="loading" id="loading" role="status"><div class="ring"></div><span>Debugging<span class="dots"></span></span></div>
<div class="status" id="status"></div>
<div class="output" id="output" role="region" aria-live="polite"></div>
</div>
<footer>Code Debugger</footer>
<script>
const input=document.getElementById('input'),send=document.getElementById('sendBtn'),output=document.getElementById('output'),loading=document.getElementById('loading'),status=document.getElementById('status');
function autoResize(){input.style.height='auto';input.style.height=Math.min(input.scrollHeight,300)+'px'}
input.addEventListener('input',autoResize);
send.addEventListener('click',debug);
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();debug()}});
async function debug(){
const text=input.value.trim();if(!text)return;
send.disabled=true;output.classList.remove('show');output.textContent='';loading.classList.add('show');status.classList.remove('show');
let dots=0;const dotInt=setInterval(()=>{dots=(dots+1)%4;status.textContent='analyzing'+'.'.repeat(dots)},400);
try{
const r=await fetch('/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({error_trace:text,failing_file:'',failing_line:null})});
const d=await r.json();
clearInterval(dotInt);loading.classList.remove('show');status.classList.remove('show');
if(d.success){const passed=d.validation_passed;output.innerHTML=(passed?'<span class="pass">PASS</span>\n\n':'<span class="fail">FAIL</span>\n\n')+d.final_report;output.classList.add('show')}
else{output.innerHTML='<span class="fail">Error:</span> '+(d.error||'Request failed');output.classList.add('show')}
}catch(e){clearInterval(dotInt);loading.classList.remove('show');status.classList.remove('show');output.innerHTML='<span class="fail">Connection error</span>';output.classList.add('show')}
finally{send.disabled=false;input.focus()}}
</script>
</body>
</html>"""

INFRASTRUCTURE_HTML = """<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#09090b">
<title>Infrastructure</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#09090b;--surface:#111113;--elevated:#1a1a1e;--border:#27272a;--text:#fafafa;--secondary:#a1a1aa;--muted:#52525b;--accent:#10b981;--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;--radius:12px;--sm:8px}
body{font-family:var(--font);background:var(--bg);color:var(--text);padding:32px 20px;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent);color:#09090b}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.container{max-width:600px;margin:0 auto}
.logo{display:flex;align-items:center;gap:8px;margin-bottom:24px}
.logo-icon{width:28px;height:28px;border-radius:7px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:13px;color:#09090b;font-weight:700;font-family:var(--mono)}
.logo-text{font-size:1rem;font-weight:600;letter-spacing:-0.01em}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:8px}
select,textarea{width:100%;background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:9px 12px;font-family:var(--mono);font-size:0.72rem;color:var(--text);margin-bottom:6px}
select:focus,textarea:focus{outline:none;border-color:var(--accent)}
.btn{display:flex;align-items:center;justify-content:center;gap:6px;padding:9px 16px;width:100%;border:none;border-radius:var(--sm);font-family:var(--font);font-size:0.72rem;font-weight:500;cursor:pointer;background:var(--elevated);border:1px solid var(--border);color:var(--secondary);transition:all 0.15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn:disabled{opacity:0.25}
.pre{background:var(--elevated);border:1px solid var(--border);border-radius:var(--sm);padding:12px;margin-top:8px;font-family:var(--mono);font-size:0.65rem;line-height:1.5;white-space:pre-wrap;max-height:300px;overflow-y:auto;color:var(--secondary);display:none}
.pre.show{display:block}
a{color:var(--accent);text-decoration:none;font-size:0.65rem;display:inline-block;margin-top:12px;padding:6px 10px;border:1px solid var(--border);border-radius:var(--sm);transition:border-color 0.15s}
a:hover{border-color:var(--accent)}
footer{margin-top:32px;text-align:center;font-size:0.55rem;color:var(--muted)}
</style>
</head>
<body>
<div class="container">
<div class="logo"><div class="logo-icon">{ }</div><div class="logo-text">Infrastructure</div></div>
<div class="panel">
<select id="agentSelect">
<option value="infrastructure">Analyzer</option>
<option value="security">Security</option>
<option value="performance">Performance</option>
<option value="cost">Cost</option>
<option value="incident">Incident</option>
</select>
<button class="btn" id="runBtn">Run</button>
<pre class="pre" id="output"></pre>
</div>
<a href="/">&larr; Back</a>
<footer>Code Debugger</footer>
</div>
<script>
document.getElementById('runBtn').addEventListener('click',async function(){
const btn=this,out=document.getElementById('output'),agent=document.getElementById('agentSelect').value;
btn.disabled=true;out.classList.remove('show');out.textContent='';
try{const r=await fetch('/api/infrastructure/'+agent,{method:'POST'});const d=await r.json();out.textContent=d.success?JSON.stringify(d.result?.output||d.result||d,null,2):'Error: '+(d.error||'');out.classList.add('show')}
catch(e){out.textContent='Error: '+e.message;out.classList.add('show')}
finally{btn.disabled=false}});
</script>
</body>
</html>"""
