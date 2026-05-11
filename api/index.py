from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_debugger import SyncDebuggingOrchestrator
from code_debugger.infra_orchestrator import SyncInfrastructureOrchestrator

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Home endpoint with API documentation."""
    return jsonify({
        "name": "Code Debugger & Infrastructure Management API",
        "version": "2.0",
        "description": "Multi-agent system for debugging and infrastructure management",
        "endpoints": {
            "/": "API documentation",
            "/health": "Health check",
            "/debug": "POST - Debug an error",
            "/api/debug": "POST - Debug an error (alias)",
            "/api/agents": "GET - Get debugging agents info",
            "/api/infrastructure/<agent>": "POST - Run infrastructure agent",
            "/api/infrastructure/full-audit": "POST - Run full infrastructure audit",
            "/api/infrastructure/incident": "POST - Respond to incident",
            "/infrastructure": "GET - Infrastructure management UI"
        },
        "debugging_agents": [
            "Debug Sleuth - Root Cause Analysis",
            "Solution Architect - Fix Generation",
            "Reliability Engineer - Validation"
        ],
        "infrastructure_agents": [
            "Infrastructure Analyzer - System Health",
            "Security Auditor - Security & Compliance",
            "Performance Optimizer - Performance Tuning",
            "Cost Manager - Cost Optimization",
            "Incident Responder - Incident Management"
        ]
    })

@app.route('/infrastructure')
def infrastructure_ui():
    """Infrastructure management UI."""
    return app.send_static_file('infrastructure.html')

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
    """
    Debug an error using the multi-agent system.

    Expected JSON body:
    {
        "error_trace": "Full error trace/stack trace",
        "failing_file": "path/to/file.py",
        "failing_line": 42,
        "inputs": {"var1": "value1"},
        "codebase_path": "."
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "example": {
                    "error_trace": "Traceback (most recent call last)...",
                    "failing_file": "app.py",
                    "failing_line": 42,
                    "inputs": {"items": [1, 2, 3], "index": 5}
                }
            }), 400

        # Validate required fields
        if 'error_trace' not in data:
            return jsonify({
                "error": "Missing required field: error_trace"
            }), 400

        # Build error context
        error_context = {
            'error_trace': data.get('error_trace'),
            'failing_file': data.get('failing_file', 'unknown'),
            'failing_line': data.get('failing_line'),
            'inputs': data.get('inputs', {}),
            'codebase_path': data.get('codebase_path', '.')
        }

        # Run debugging cycle
        orchestrator = SyncDebuggingOrchestrator()
        result = orchestrator.run_full_debugging_cycle(error_context)

        # Return results
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
    """Get information about available agents."""
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
    """Run a specific infrastructure agent."""
    try:
        orchestrator = SyncInfrastructureOrchestrator()

        if agent_type == 'infrastructure':
            result = orchestrator.run_infrastructure_analysis()
        elif agent_type == 'security':
            result = orchestrator.run_security_audit()
        elif agent_type == 'performance':
            result = orchestrator.run_performance_optimization()
        elif agent_type == 'cost':
            result = orchestrator.run_cost_analysis()
        elif agent_type == 'incident':
            result = orchestrator.run_incident_response()
        else:
            return jsonify({
                "success": False,
                "error": f"Unknown agent type: {agent_type}"
            }), 400

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/infrastructure/full-audit', methods=['POST'])
def run_full_infrastructure_audit():
    """Run complete infrastructure audit with all agents."""
    try:
        orchestrator = SyncInfrastructureOrchestrator()
        result = orchestrator.run_full_infrastructure_audit()

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/infrastructure/incident', methods=['POST'])
def respond_to_incident():
    """Respond to a specific incident."""
    try:
        data = request.get_json()

        if not data or 'description' not in data:
            return jsonify({
                "success": False,
                "error": "Missing incident description"
            }), 400

        orchestrator = SyncInfrastructureOrchestrator()
        result = orchestrator.run_incident_response(data['description'])

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500

# For Vercel serverless functions
def handler(request):
    """Vercel serverless function handler."""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
