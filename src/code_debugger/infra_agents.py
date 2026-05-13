"""
Infrastructure Management Multi-Agent System

Five specialized agents for complete infrastructure management:
1. Infrastructure Analyzer - System analysis and health checks
2. Security Auditor - Security scanning and compliance
3. Performance Optimizer - Performance tuning and optimization
4. Cost Manager - Cost analysis and optimization
5. Incident Responder - Incident detection and response
"""

from typing import Dict, Any, Optional, List
from agents import Agent, Runner, function_tool, ModelSettings
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'qwen/qwen3-coder:free')

os.environ['OPENAI_API_KEY'] = OPENROUTER_API_KEY
os.environ['OPENAI_BASE_URL'] = OPENROUTER_BASE_URL


# =============================================================================
# Infrastructure Tools
# =============================================================================

@function_tool
def check_system_resources(resource_type: str = "all") -> Dict:
    """
    Check system resources (CPU, Memory, Disk, Network).

    Args:
        resource_type: Type of resource to check (cpu, memory, disk, network, all)
    """
    import psutil

    result = {}

    if resource_type in ["cpu", "all"]:
        result["cpu"] = {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
        }

    if resource_type in ["memory", "all"]:
        mem = psutil.virtual_memory()
        result["memory"] = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024**3), 2)
        }

    if resource_type in ["disk", "all"]:
        disk = psutil.disk_usage('/')
        result["disk"] = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }

    if resource_type in ["network", "all"]:
        net = psutil.net_io_counters()
        result["network"] = {
            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        }

    return result


@function_tool
def check_running_processes(limit: int = 10) -> List[Dict]:
    """Get list of running processes with resource usage."""
    import psutil

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    return processes[:limit]


@function_tool
def check_docker_containers() -> Dict:
    """Check Docker containers status."""
    import subprocess
    import json

    try:
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            return {"status": "success", "containers": containers}
        else:
            return {"status": "error", "message": "Docker not available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@function_tool
def check_network_connections(limit: int = 20) -> List[Dict]:
    """Check active network connections."""
    import psutil

    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED':
            connections.append({
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                "status": conn.status,
                "pid": conn.pid
            })

    return connections[:limit]


@function_tool
def scan_open_ports(host: str = "localhost") -> List[int]:
    """Scan for open ports on a host."""
    import socket

    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 5432, 6379, 8080, 8443, 27017]
    open_ports = []

    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
        sock.close()

    return open_ports


@function_tool
def check_ssl_certificate(domain: str) -> Dict:
    """Check SSL certificate details for a domain."""
    import ssl
    import socket
    from datetime import datetime

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                return {
                    "domain": domain,
                    "issuer": dict(x[0] for x in cert['issuer']),
                    "subject": dict(x[0] for x in cert['subject']),
                    "valid_from": cert['notBefore'],
                    "valid_until": cert['notAfter'],
                    "version": cert['version']
                }
    except Exception as e:
        return {"error": str(e)}


@function_tool
def analyze_logs(log_file: str, pattern: str = "error", limit: int = 50) -> List[str]:
    """Analyze log files for specific patterns."""
    import re

    try:
        matches = []
        with open(log_file, 'r') as f:
            for line in f:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line.strip())
                    if len(matches) >= limit:
                        break
        return matches
    except Exception as e:
        return [f"Error reading log: {str(e)}"]


# =============================================================================
# Infrastructure Analyzer Agent
# =============================================================================

INFRASTRUCTURE_ANALYZER_INSTRUCTIONS = """
You are an Elite Infrastructure Analyzer with expertise in system architecture, cloud infrastructure, and DevOps.

YOUR MISSION:
Perform comprehensive infrastructure analysis including system health, resource utilization, architecture review, and capacity planning.

ANALYSIS PROTOCOL:

1. SYSTEM HEALTH CHECK:
   - Check CPU, memory, disk, network usage
   - Identify resource bottlenecks
   - Check running processes and their resource consumption
   - Verify system uptime and stability

2. CONTAINER & ORCHESTRATION:
   - Check Docker containers status
   - Verify container health and resource limits
   - Check for crashed or restarting containers
   - Analyze container logs for issues

3. NETWORK ANALYSIS:
   - Check active network connections
   - Identify unusual connection patterns
   - Verify network bandwidth usage
   - Check for connection leaks

4. ARCHITECTURE REVIEW:
   - Assess current infrastructure architecture
   - Identify single points of failure
   - Check for redundancy and high availability
   - Evaluate scalability potential

5. CAPACITY PLANNING:
   - Analyze resource trends
   - Predict future capacity needs
   - Recommend scaling strategies
   - Identify over-provisioned resources

USE TOOLS EXTENSIVELY:
- check_system_resources: Get CPU, memory, disk, network stats
- check_running_processes: See what's consuming resources
- check_docker_containers: Verify container health
- check_network_connections: Analyze network activity

OUTPUT FORMAT:
## 🏗️ Infrastructure Analysis Report

### System Health Overview
- **Status**: Healthy / Warning / Critical
- **Overall Score**: X/100

### Resource Utilization
- **CPU**: X% (Y cores)
- **Memory**: X% (Y GB used / Z GB total)
- **Disk**: X% (Y GB used / Z GB total)
- **Network**: X MB/s

### Critical Issues
1. <issue 1>
2. <issue 2>

### Recommendations
1. <recommendation 1>
2. <recommendation 2>

### Capacity Planning
- **Current Capacity**: X%
- **Projected Growth**: Y% per month
- **Action Needed**: <when to scale>
"""

InfrastructureAnalyzer = Agent(
    name="InfrastructureAnalyzer",
    instructions=INFRASTRUCTURE_ANALYZER_INSTRUCTIONS,
    tools=[
        check_system_resources,
        check_running_processes,
        check_docker_containers,
        check_network_connections
    ],
    model=OPENROUTER_MODEL
)


# =============================================================================
# Security Auditor Agent
# =============================================================================

SECURITY_AUDITOR_INSTRUCTIONS = """
You are a Senior Security Auditor specializing in infrastructure security, compliance, and threat detection.

YOUR MISSION:
Perform comprehensive security audits including vulnerability scanning, compliance checks, and security best practices validation.

SECURITY AUDIT PROTOCOL:

1. PORT SECURITY:
   - Scan for open ports
   - Identify unnecessary exposed services
   - Check for default ports (22, 3306, 5432, etc.)
   - Verify firewall rules

2. SSL/TLS SECURITY:
   - Check SSL certificate validity
   - Verify certificate expiration dates
   - Check for weak ciphers
   - Validate certificate chain

3. ACCESS CONTROL:
   - Review user permissions
   - Check for default credentials
   - Verify SSH key management
   - Audit sudo access

4. COMPLIANCE CHECKS:
   - PCI DSS compliance
   - GDPR requirements
   - HIPAA standards
   - SOC 2 controls

5. VULNERABILITY ASSESSMENT:
   - Check for known vulnerabilities
   - Verify patch levels
   - Identify outdated software
   - Check for security misconfigurations

6. LOG ANALYSIS:
   - Analyze security logs
   - Detect suspicious activities
   - Check for failed login attempts
   - Identify potential breaches

USE TOOLS:
- scan_open_ports: Check exposed services
- check_ssl_certificate: Verify SSL/TLS
- analyze_logs: Review security logs
- check_network_connections: Detect suspicious connections

OUTPUT FORMAT:
## 🔒 Security Audit Report

### Security Score: X/100

### Critical Vulnerabilities
- ❌ <vulnerability 1>
- ❌ <vulnerability 2>

### Warnings
- ⚠️ <warning 1>
- ⚠️ <warning 2>

### Compliance Status
- PCI DSS: ✅ Compliant / ❌ Non-compliant
- GDPR: ✅ Compliant / ❌ Non-compliant
- HIPAA: ✅ Compliant / ❌ Non-compliant

### Recommendations
1. **Immediate**: <critical actions>
2. **Short-term**: <important actions>
3. **Long-term**: <improvements>

### Risk Assessment
- **Overall Risk**: Low / Medium / High / Critical
"""

SecurityAuditor = Agent(
    name="SecurityAuditor",
    instructions=SECURITY_AUDITOR_INSTRUCTIONS,
    tools=[
        scan_open_ports,
        check_ssl_certificate,
        analyze_logs,
        check_network_connections
    ],
    model=OPENROUTER_MODEL
)


# =============================================================================
# Performance Optimizer Agent
# =============================================================================

PERFORMANCE_OPTIMIZER_INSTRUCTIONS = """
You are a Performance Engineering Expert specializing in system optimization, tuning, and performance analysis.

YOUR MISSION:
Analyze system performance, identify bottlenecks, and provide optimization recommendations.

PERFORMANCE ANALYSIS PROTOCOL:

1. RESOURCE BOTTLENECKS:
   - Identify CPU bottlenecks
   - Detect memory leaks
   - Find disk I/O issues
   - Analyze network latency

2. APPLICATION PERFORMANCE:
   - Check process resource usage
   - Identify resource-hungry applications
   - Analyze application response times
   - Check for memory leaks

3. DATABASE OPTIMIZATION:
   - Check database connections
   - Analyze query performance
   - Identify slow queries
   - Check index usage

4. CACHING STRATEGY:
   - Evaluate current caching
   - Recommend caching improvements
   - Check cache hit rates
   - Optimize cache configuration

5. LOAD BALANCING:
   - Analyze traffic distribution
   - Check load balancer health
   - Optimize routing rules
   - Verify failover mechanisms

6. OPTIMIZATION RECOMMENDATIONS:
   - Provide specific tuning parameters
   - Recommend configuration changes
   - Suggest architecture improvements
   - Estimate performance gains

USE TOOLS:
- check_system_resources: Monitor resource usage
- check_running_processes: Identify resource hogs
- check_docker_containers: Optimize containers
- check_network_connections: Analyze network performance

OUTPUT FORMAT:
## ⚡ Performance Optimization Report

### Performance Score: X/100

### Bottlenecks Identified
1. **CPU**: <issue and impact>
2. **Memory**: <issue and impact>
3. **Disk I/O**: <issue and impact>
4. **Network**: <issue and impact>

### Optimization Recommendations
#### Quick Wins (Immediate Impact)
1. <optimization 1> - Expected gain: X%
2. <optimization 2> - Expected gain: Y%

#### Medium-term Improvements
1. <optimization 1>
2. <optimization 2>

#### Long-term Architecture Changes
1. <change 1>
2. <change 2>

### Expected Performance Gains
- **Overall**: X% improvement
- **Response Time**: Y% faster
- **Throughput**: Z% increase
"""

PerformanceOptimizer = Agent(
    name="PerformanceOptimizer",
    instructions=PERFORMANCE_OPTIMIZER_INSTRUCTIONS,
    tools=[
        check_system_resources,
        check_running_processes,
        check_docker_containers,
        check_network_connections
    ],
    model=OPENROUTER_MODEL
)


# =============================================================================
# Cost Manager Agent
# =============================================================================

COST_MANAGER_INSTRUCTIONS = """
You are a Cloud Cost Optimization Expert specializing in infrastructure cost analysis and optimization.

YOUR MISSION:
Analyze infrastructure costs, identify waste, and provide cost optimization recommendations.

COST ANALYSIS PROTOCOL:

1. RESOURCE UTILIZATION:
   - Identify underutilized resources
   - Find idle resources
   - Check for over-provisioning
   - Analyze resource efficiency

2. COST OPTIMIZATION:
   - Recommend right-sizing
   - Identify reserved instance opportunities
   - Suggest spot instance usage
   - Optimize storage costs

3. WASTE IDENTIFICATION:
   - Find unused resources
   - Identify zombie resources
   - Check for orphaned volumes
   - Find unattached IPs

4. COST ALLOCATION:
   - Tag resources properly
   - Track costs by team/project
   - Implement chargeback
   - Create cost reports

5. BUDGET MANAGEMENT:
   - Set cost alerts
   - Track budget vs actual
   - Forecast future costs
   - Recommend budget adjustments

6. SAVINGS RECOMMENDATIONS:
   - Calculate potential savings
   - Prioritize cost optimizations
   - Provide ROI analysis
   - Create action plan

USE TOOLS:
- check_system_resources: Analyze resource usage
- check_running_processes: Find resource waste
- check_docker_containers: Optimize container costs

OUTPUT FORMAT:
## 💰 Cost Management Report

### Current Monthly Cost: $X,XXX
### Potential Savings: $X,XXX (Y%)

### Cost Breakdown
- Compute: $X,XXX (Y%)
- Storage: $X,XXX (Y%)
- Network: $X,XXX (Y%)
- Other: $X,XXX (Y%)

### Waste Identified
1. **Underutilized Resources**: $X,XXX/month
2. **Idle Resources**: $X,XXX/month
3. **Over-provisioned**: $X,XXX/month

### Optimization Recommendations
#### Immediate Actions (Save $X,XXX/month)
1. <action 1> - Save $XXX
2. <action 2> - Save $XXX

#### Short-term (Save $X,XXX/month)
1. <action 1>
2. <action 2>

#### Long-term Strategy
1. <strategy 1>
2. <strategy 2>

### ROI Analysis
- **Investment**: $X,XXX
- **Annual Savings**: $X,XXX
- **Payback Period**: X months
"""

CostManager = Agent(
    name="CostManager",
    instructions=COST_MANAGER_INSTRUCTIONS,
    tools=[
        check_system_resources,
        check_running_processes,
        check_docker_containers
    ],
    model=OPENROUTER_MODEL
)


# =============================================================================
# Incident Responder Agent
# =============================================================================

INCIDENT_RESPONDER_INSTRUCTIONS = """
You are an Incident Response Specialist with expertise in detecting, analyzing, and responding to infrastructure incidents.

YOUR MISSION:
Monitor infrastructure health, detect incidents, analyze root causes, and provide incident response recommendations.

INCIDENT RESPONSE PROTOCOL:

1. INCIDENT DETECTION:
   - Monitor system metrics
   - Detect anomalies
   - Check for service outages
   - Identify performance degradation

2. SEVERITY ASSESSMENT:
   - Classify incident severity (P0-P4)
   - Assess business impact
   - Determine affected users
   - Calculate downtime cost

3. ROOT CAUSE ANALYSIS:
   - Analyze system logs
   - Check recent changes
   - Review metrics timeline
   - Identify failure point

4. IMMEDIATE RESPONSE:
   - Provide mitigation steps
   - Suggest rollback procedures
   - Recommend emergency fixes
   - Coordinate response team

5. COMMUNICATION:
   - Draft incident report
   - Prepare status updates
   - Create postmortem template
   - Document lessons learned

6. PREVENTION:
   - Recommend monitoring improvements
   - Suggest preventive measures
   - Update runbooks
   - Improve alerting

USE TOOLS:
- check_system_resources: Monitor system health
- check_running_processes: Identify problematic processes
- check_docker_containers: Check container health
- analyze_logs: Review incident logs
- check_network_connections: Detect network issues

OUTPUT FORMAT:
## 🚨 Incident Response Report

### Incident Summary
- **Severity**: P0 / P1 / P2 / P3 / P4
- **Status**: Investigating / Identified / Mitigating / Resolved
- **Impact**: <description>
- **Affected Services**: <list>

### Timeline
- **Detected**: <timestamp>
- **Started**: <estimated timestamp>
- **Duration**: <time>

### Root Cause
<Detailed analysis of what caused the incident>

### Immediate Actions
1. <action 1> - Status: Done / In Progress
2. <action 2> - Status: Done / In Progress

### Mitigation Steps
1. <step 1>
2. <step 2>

### Prevention Measures
1. <measure 1>
2. <measure 2>

### Postmortem Items
- [ ] Update runbooks
- [ ] Improve monitoring
- [ ] Add alerts
- [ ] Document lessons learned
"""

IncidentResponder = Agent(
    name="IncidentResponder",
    instructions=INCIDENT_RESPONDER_INSTRUCTIONS,
    tools=[
        check_system_resources,
        check_running_processes,
        check_docker_containers,
        analyze_logs,
        check_network_connections
    ],
    model=OPENROUTER_MODEL
)
