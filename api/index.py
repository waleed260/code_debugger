from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from html_content import INDEX_HTML, INFRASTRUCTURE_HTML

# Lazy imports - only load when needed to avoid cold start failures
_orchestrator = None
_infra_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from code_debugger import SyncDebuggingOrchestrator
        _orchestrator = SyncDebuggingOrchestrator(db_path="/tmp/debug_sessions.db")
    return _orchestrator

def get_infra_orchestrator():
    global _infra_orchestrator
    if _infra_orchestrator is None:
        from code_debugger.infra_orchestrator import SyncInfrastructureOrchestrator
        _infra_orchestrator = SyncInfrastructureOrchestrator()
    return _infra_orchestrator

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return INDEX_HTML

@app.route('/infrastructure')
def infrastructure_ui():
    return INFRASTRUCTURE_HTML

@app.route('/api')
def api_docs():
    return jsonify({
        "name": "Code Debugger & Infrastructure Management API",
        "version": "2.0",
        "description": "Multi-agent system for debugging and infrastructure management",
        "endpoints": {
            "/": "Web UI",
            "/api": "API documentation",
            "/health": "Health check",
            "/debug": "POST - Debug an error",
            "/api/debug": "POST - Debug an error (alias)",
            "/api/agents": "GET - Get debugging agents info",
            "/api/infrastructure/<agent>": "POST - Run infrastructure agent",
            "/api/infrastructure/full-audit": "POST - Run full infrastructure audit",
            "/api/infrastructure/incident": "POST - Respond to incident",
            "/infrastructure": "GET - Infrastructure management UI"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "code-debugger-infrastructure",
        "version": "2.0"
    })

@app.route('/debug', methods=['POST'])
@app.route('/api/debug', methods=['POST'])
def debug_error():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        if 'error_trace' not in data:
            return jsonify({"error": "Missing required field: error_trace"}), 400

        error_context = {
            'error_trace': data.get('error_trace'),
            'failing_file': data.get('failing_file', 'unknown'),
            'failing_line': data.get('failing_line'),
            'inputs': data.get('inputs', {}),
            'codebase_path': data.get('codebase_path', '.')
        }

        orchestrator = get_orchestrator()
        result = orchestrator.run_full_debugging_cycle(error_context)

        return jsonify({
            "success": True,
            "validation_passed": result['validation_passed'],
            "final_report": result['final_report'],
            "agents_used": [item['agent'] for item in result['session_history']],
            "root_cause_analysis": result['root_cause_analysis']['final_output'],
            "solution_architecture": result['solution_architecture']['final_output'],
            "reliability_validation": result['reliability_validation']['final_output']
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify({
        "debugging_agents": [
            {
                "name": "Debug Sleuth",
                "role": "Root Cause Analysis",
                "capabilities": [
                    "Forensic-level stack trace analysis",
                    "Extended code context (20-30 lines)",
                    "Dependency & import analysis",
                    "Data flow tracing",
                    "Pattern recognition",
                    "Concurrency detection",
                    "Multiple hypotheses with confidence"
                ]
            },
            {
                "name": "Solution Architect",
                "role": "Fix Generation",
                "capabilities": [
                    "Multiple solution approaches (Quick/Robust/Ideal)",
                    "SOLID principles application",
                    "Comprehensive test suites",
                    "Performance analysis",
                    "Backward compatibility",
                    "Security-first design"
                ]
            },
            {
                "name": "Reliability Engineer",
                "role": "Validation",
                "capabilities": [
                    "10+ code smell patterns",
                    "8+ security checks",
                    "5-category quality scoring",
                    "Operational readiness",
                    "Compliance verification",
                    "Pass/fail with feedback"
                ]
            }
        ],
        "infrastructure_agents": [
            {
                "name": "Infrastructure Analyzer",
                "role": "System Health & Architecture",
                "capabilities": [
                    "Resource monitoring (CPU, Memory, Disk, Network)",
                    "Container health checks",
                    "Network analysis",
                    "Capacity planning",
                    "Architecture review"
                ]
            },
            {
                "name": "Security Auditor",
                "role": "Security & Compliance",
                "capabilities": [
                    "Port scanning",
                    "SSL/TLS certificate checks",
                    "Vulnerability assessment",
                    "Compliance auditing (PCI DSS, GDPR, HIPAA)",
                    "Security scoring"
                ]
            },
            {
                "name": "Performance Optimizer",
                "role": "Performance Tuning",
                "capabilities": [
                    "Bottleneck detection",
                    "Resource optimization",
                    "Performance analysis",
                    "Load balancing review",
                    "Optimization recommendations"
                ]
            },
            {
                "name": "Cost Manager",
                "role": "Cost Optimization",
                "capabilities": [
                    "Cost breakdown analysis",
                    "Waste identification",
                    "Savings recommendations",
                    "ROI analysis",
                    "Budget management"
                ]
            },
            {
                "name": "Incident Responder",
                "role": "Incident Management",
                "capabilities": [
                    "Proactive monitoring",
                    "Anomaly detection",
                    "Root cause analysis",
                    "Mitigation steps",
                    "Prevention measures"
                ]
            }
        ]
    })

@app.route('/api/infrastructure/<agent_type>', methods=['POST'])
def run_infrastructure_agent(agent_type):
    try:
        orch = get_infra_orchestrator()
        agents = {
            'infrastructure': orch.run_infrastructure_analysis,
            'security': orch.run_security_audit,
            'performance': orch.run_performance_optimization,
            'cost': orch.run_cost_analysis,
            'incident': orch.run_incident_response,
        }
        if agent_type not in agents:
            return jsonify({"success": False, "error": f"Unknown agent type: {agent_type}"}), 400
        result = agents[agent_type]()
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "type": type(e).__name__}), 500

@app.route('/api/infrastructure/full-audit', methods=['POST'])
def run_full_infrastructure_audit():
    try:
        result = get_infra_orchestrator().run_full_infrastructure_audit()
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "type": type(e).__name__}), 500

@app.route('/api/infrastructure/incident', methods=['POST'])
def respond_to_incident():
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({"success": False, "error": "Missing incident description"}), 400
        result = get_infra_orchestrator().run_incident_response(data['description'])
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "type": type(e).__name__}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
