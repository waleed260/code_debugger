from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_debugger import SyncDebuggingOrchestrator

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Home endpoint with API documentation."""
    return jsonify({
        "name": "Code Debugger API",
        "version": "2.0",
        "description": "Multi-agent debugging system with enterprise-grade analysis",
        "endpoints": {
            "/": "API documentation",
            "/health": "Health check",
            "/debug": "POST - Debug an error",
            "/api/debug": "POST - Debug an error (alias)"
        },
        "agents": [
            "Debug Sleuth - Root Cause Analysis",
            "Solution Architect - Fix Generation",
            "Reliability Engineer - Validation"
        ],
        "features": [
            "10x deeper analysis",
            "Multiple solution approaches",
            "Comprehensive security audits",
            "Production-ready validation",
            "Quality scoring (0-100)"
        ]
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "code-debugger",
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
        "agents": [
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
        ]
    })

# For Vercel serverless functions
def handler(request):
    """Vercel serverless function handler."""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
