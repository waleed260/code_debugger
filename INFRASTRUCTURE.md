# 🏗️ Infrastructure Management System

## Overview

A comprehensive AI-powered infrastructure management system with **5 specialized agents** that monitor, analyze, and optimize your infrastructure in real-time.

---

## 🤖 The 5 Infrastructure Agents

### 1. 🏗️ Infrastructure Analyzer
**Role**: System Health & Architecture Analysis

**Capabilities**:
- Real-time resource monitoring (CPU, Memory, Disk, Network)
- Container health checks (Docker)
- Network connection analysis
- Process monitoring
- Capacity planning
- Architecture review
- Health scoring (0-100)

**Use Cases**:
- Daily health checks
- Capacity planning
- Architecture reviews
- Resource utilization tracking

---

### 2. 🔒 Security Auditor
**Role**: Security & Compliance

**Capabilities**:
- Port scanning (detects exposed services)
- SSL/TLS certificate validation
- Security vulnerability assessment
- Compliance checks (PCI DSS, GDPR, HIPAA)
- Network security analysis
- Log analysis for security events
- Security scoring (0-100)

**Use Cases**:
- Security audits
- Compliance reporting
- Vulnerability scanning
- Certificate expiration monitoring

---

### 3. ⚡ Performance Optimizer
**Role**: Performance Tuning & Optimization

**Capabilities**:
- Bottleneck detection (CPU, Memory, Disk, Network)
- Resource optimization recommendations
- Process performance analysis
- Container performance tuning
- Load balancing review
- Performance scoring with expected gains

**Use Cases**:
- Performance troubleshooting
- Resource optimization
- Application tuning
- Cost reduction through efficiency

---

### 4. 💰 Cost Manager
**Role**: Cost Analysis & Optimization

**Capabilities**:
- Resource utilization analysis
- Waste identification (idle resources)
- Cost breakdown by resource type
- Savings recommendations
- ROI analysis
- Budget forecasting

**Use Cases**:
- Cost optimization
- Budget planning
- Waste elimination
- Resource right-sizing

---

### 5. 🚨 Incident Responder
**Role**: Incident Detection & Response

**Capabilities**:
- Proactive incident detection
- Anomaly detection
- Root cause analysis
- Severity assessment (P0-P4)
- Mitigation recommendations
- Prevention measures
- Postmortem templates

**Use Cases**:
- Incident response
- Outage investigation
- Performance degradation analysis
- Proactive monitoring

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or with uv
uv sync
```

### Configuration

Create a `.env` file:

```bash
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-3.5-turbo
```

### Run Locally

```bash
# Start the API server
python api/index.py

# Visit the web interface
open http://localhost:5000/infrastructure
```

---

## 🌐 Web Interface

The infrastructure management system includes a beautiful web interface with:

### Features:
- **Dashboard**: Quick access to all 5 agents
- **Full Audit**: Run all agents at once
- **Incident Response**: Custom incident analysis
- **Real-time Results**: Live agent outputs
- **Responsive Design**: Works on desktop and mobile

### Access:
- Local: `http://localhost:5000/infrastructure`
- Deployed: `https://your-app.vercel.app/infrastructure`

---

## 📡 API Endpoints

### Run Individual Agent

```bash
POST /api/infrastructure/<agent_type>

# Agent types: infrastructure, security, performance, cost, incident
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/infrastructure/security \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "success": true,
  "result": {
    "agent": "SecurityAuditor",
    "output": "## 🔒 Security Audit Report\n..."
  }
}
```

### Run Full Infrastructure Audit

```bash
POST /api/infrastructure/full-audit
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/infrastructure/full-audit \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "success": true,
  "result": {
    "infrastructure_analysis": {...},
    "security_audit": {...},
    "performance_optimization": {...},
    "cost_analysis": {...},
    "incident_response": {...}
  }
}
```

### Respond to Incident

```bash
POST /api/infrastructure/incident
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/infrastructure/incident \
  -H "Content-Type: application/json" \
  -d '{
    "description": "High CPU usage on production server, response times increased by 300%"
  }'
```

---

## 🧪 Testing

### Run Infrastructure Tests

```bash
# Test all agents
python test_infrastructure.py

# Or with uv
uv run python test_infrastructure.py
```

### Test Individual Agents

```python
from code_debugger.infra_orchestrator import SyncInfrastructureOrchestrator

orchestrator = SyncInfrastructureOrchestrator()

# Test Infrastructure Analyzer
result = orchestrator.run_infrastructure_analysis()
print(result['output'])

# Test Security Auditor
result = orchestrator.run_security_audit()
print(result['output'])

# Test Performance Optimizer
result = orchestrator.run_performance_optimization()
print(result['output'])

# Test Cost Manager
result = orchestrator.run_cost_analysis()
print(result['output'])

# Test Incident Responder
result = orchestrator.run_incident_response("High CPU usage")
print(result['output'])

# Run full audit
result = orchestrator.run_full_infrastructure_audit()
```

---

## 🛠️ Tools & Capabilities

### System Monitoring Tools

| Tool | Description |
|------|-------------|
| `check_system_resources` | Monitor CPU, memory, disk, network usage |
| `check_running_processes` | List processes with resource consumption |
| `check_docker_containers` | Check Docker container status |
| `check_network_connections` | Analyze active network connections |

### Security Tools

| Tool | Description |
|------|-------------|
| `scan_open_ports` | Scan for open ports on a host |
| `check_ssl_certificate` | Validate SSL/TLS certificates |
| `analyze_logs` | Search logs for patterns |

---

## 📊 Example Outputs

### Infrastructure Analysis

```markdown
## 🏗️ Infrastructure Analysis Report

### System Health Overview
- **Status**: Healthy
- **Overall Score**: 85/100

### Resource Utilization
- **CPU**: 45% (8 cores)
- **Memory**: 62% (12.5 GB used / 20 GB total)
- **Disk**: 58% (290 GB used / 500 GB total)
- **Network**: 125 MB/s

### Critical Issues
1. Memory usage trending upward
2. Disk space will be full in 45 days

### Recommendations
1. Add 8GB RAM for headroom
2. Clean up old logs and temp files
3. Consider scaling horizontally

### Capacity Planning
- **Current Capacity**: 75%
- **Projected Growth**: 5% per month
- **Action Needed**: Scale in 3 months
```

### Security Audit

```markdown
## 🔒 Security Audit Report

### Security Score: 78/100

### Critical Vulnerabilities
- ❌ Port 3306 (MySQL) exposed to internet
- ❌ SSL certificate expires in 15 days

### Warnings
- ⚠️ Port 22 (SSH) open on default port
- ⚠️ 5 failed login attempts detected

### Compliance Status
- PCI DSS: ❌ Non-compliant (exposed database)
- GDPR: ✅ Compliant
- HIPAA: ⚠️ Needs review

### Recommendations
1. **Immediate**: Close port 3306 or restrict to VPN
2. **Immediate**: Renew SSL certificate
3. **Short-term**: Move SSH to non-standard port
4. **Short-term**: Implement fail2ban
```

### Performance Optimization

```markdown
## ⚡ Performance Optimization Report

### Performance Score: 72/100

### Bottlenecks Identified
1. **CPU**: High usage by process "node" (85%)
2. **Memory**: Memory leak detected in "app.py"
3. **Disk I/O**: Slow disk writes (15 MB/s)
4. **Network**: No issues detected

### Optimization Recommendations
#### Quick Wins (Immediate Impact)
1. Restart "node" process - Expected gain: 40% CPU reduction
2. Add swap space - Expected gain: 20% memory headroom

#### Medium-term Improvements
1. Fix memory leak in app.py
2. Upgrade to SSD storage
3. Enable gzip compression

### Expected Performance Gains
- **Overall**: 45% improvement
- **Response Time**: 60% faster
- **Throughput**: 35% increase
```

---

## 🚀 Deployment

### Deploy to Vercel

The infrastructure management system is included in your Vercel deployment:

```bash
# Push to GitHub
git push origin HEAD:main

# Deploy to Vercel
vercel --prod
```

### Access After Deployment

- **Main App**: `https://your-app.vercel.app`
- **Infrastructure UI**: `https://your-app.vercel.app/infrastructure`
- **API**: `https://your-app.vercel.app/api/infrastructure/*`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `OPENROUTER_BASE_URL` | OpenRouter API endpoint | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | Model to use | `gpt-3.5-turbo` |

### Supported Models

- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-4o` - More powerful analysis
- `google/gemini-2.0-flash-exp:free` - Free tier option

---

## 📈 Use Cases

### 1. Daily Health Checks
Run Infrastructure Analyzer every morning to check system health.

### 2. Security Audits
Run Security Auditor weekly for compliance and vulnerability scanning.

### 3. Performance Troubleshooting
Use Performance Optimizer when users report slowness.

### 4. Cost Optimization
Run Cost Manager monthly to identify savings opportunities.

### 5. Incident Response
Use Incident Responder during outages for quick root cause analysis.

### 6. Comprehensive Audits
Run Full Audit quarterly for complete infrastructure assessment.

---

## 🎯 Best Practices

1. **Regular Monitoring**: Run agents on a schedule
2. **Act on Recommendations**: Implement high-priority suggestions
3. **Track Metrics**: Monitor scores over time
4. **Document Incidents**: Use postmortem templates
5. **Automate**: Integrate with CI/CD pipelines

---

## 🔗 Integration Examples

### Slack Integration

```python
import requests

# Run audit
result = orchestrator.run_full_infrastructure_audit()

# Send to Slack
requests.post('https://hooks.slack.com/services/YOUR/WEBHOOK/URL', json={
    'text': f"Infrastructure Audit Complete\n{result['infrastructure_analysis']['output'][:500]}"
})
```

### Cron Job

```bash
# Add to crontab for daily health checks
0 9 * * * cd /path/to/code_debugger && python -c "from code_debugger.infra_orchestrator import SyncInfrastructureOrchestrator; SyncInfrastructureOrchestrator().run_infrastructure_analysis()"
```

### Monitoring Dashboard

```python
# Create custom dashboard
from flask import Flask, render_template

@app.route('/dashboard')
def dashboard():
    orchestrator = SyncInfrastructureOrchestrator()
    health = orchestrator.run_infrastructure_analysis()
    security = orchestrator.run_security_audit()
    
    return render_template('dashboard.html', 
                         health=health, 
                         security=security)
```

---

## 📞 Support

- **Documentation**: See this file
- **API Docs**: Visit `/` endpoint
- **Issues**: GitHub Issues
- **Testing**: Run `python test_infrastructure.py`

---

## 🏆 Features Summary

✅ **5 Specialized AI Agents**
✅ **Real-time System Monitoring**
✅ **Security & Compliance Auditing**
✅ **Performance Optimization**
✅ **Cost Management**
✅ **Incident Response**
✅ **Beautiful Web Interface**
✅ **RESTful API**
✅ **Docker Support**
✅ **Network Analysis**
✅ **SSL Certificate Monitoring**
✅ **Log Analysis**
✅ **Comprehensive Reporting**

---

**Your infrastructure is now managed by AI! 🚀**

*Last Updated: May 11, 2026*
