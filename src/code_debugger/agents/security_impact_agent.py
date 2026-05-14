"""
SecurityImpactAgent — Checks if the bug or fix introduces security vulnerabilities.
"""

from agents import Agent, function_tool, ModelSettings
import os
import re
from typing import Dict, Any, List


SECURITY_INSTRUCTIONS = """
You are a security impact analyst. Assess security risks in bugs and fixes.

Capabilities:
1. Detect injection vulnerabilities (SQL, command, XSS)
2. Identify exposure of sensitive data in errors
3. Check authentication/authorization bypasses
4. Detect insecure deserialization
5. Flag path traversal and unsafe file operations

Output format:
- Security Score: 0-100
- Vulnerabilities Found: <list with severity>
- Exploitability: Low / Medium / High / Critical
- CVSS Estimate: <0-10>
- Recommended Security Improvements: <list>
"""


@function_tool
def scan_security_issues(code: str) -> List[Dict[str, Any]]:
    """Scan code for common security vulnerabilities."""
    issues = []
    patterns = [
        (r"(?i)sql.*execute\(.*\+", "SQL Injection", "high", "String concatenation in SQL query"),
        (r"(?i)subprocess\.(call|Popen|run)\(.*shell=True", "Command Injection", "critical", "Shell=True enables command injection"),
        (r"(?i)eval\(.*\)", "Code Injection", "critical", "eval() executes arbitrary code"),
        (r"(?i)exec\(.*\)", "Code Injection", "critical", "exec() executes arbitrary code"),
        (r"(?i)pickle\.loads?", "Insecure Deserialization", "high", "Pickle can execute arbitrary code during deserialization"),
        (r"(?i)yaml\.load\(.*\)", "Insecure Deserialization", "high", "yaml.load() without SafeLoader is dangerous"),
        (r"(?i)os\.system\(.*\)", "Command Injection", "high", "os.system() executes shell commands"),
        (r"(?i)request\.(GET|POST|args|cookies|headers)", "User Input", "info", "User input should be validated"),
        (r"(?i)(password|secret|key|token|credential)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded Secret", "high", "Hardcoded credentials in source"),
        (r"(?i)open\(.*['\"].*\.\.", "Path Traversal", "high", "Path traversal in file operations"),
        (r"(?i)render_template_string\(.*\+", "SSTI", "high", "String concatenation in template may cause SSTI"),
        (r"(?i)session\[.*\]\s*=\s*request\.", "Session Injection", "medium", "Storing user input directly in session"),
        (r"(?i)@app\.route.*methods=\[.*POST", "Endpoint", "info", "POST endpoint - ensure CSRF protection"),
        (r"(?i)mysql|postgresql|psycopg2.*execute\(.*%", "SQL Injection", "high", "Parameterized queries should use ?, not %s or string formatting"),
    ]

    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        for pattern, vuln_type, severity, message in patterns:
            if re.search(pattern, line):
                issues.append({
                    "line": i,
                    "type": vuln_type,
                    "severity": severity,
                    "message": message,
                    "code": line.strip()[:80],
                })

    return issues


@function_tool
def check_security_score(issues_json: str) -> Dict[str, Any]:
    """Calculate a security score based on found issues (JSON string)."""
    import json
    severity_weights = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3,
        "info": 1,
    }

    try:
        issues = json.loads(issues_json)
    except (json.JSONDecodeError, TypeError):
        issues = []

    score = 100
    for issue in issues:
        score -= severity_weights.get(issue.get("severity", "info"), 1)

    has_critical = any(i.get("severity") == "critical" for i in issues)
    has_high = any(i.get("severity") == "high" for i in issues)

    return {
        "score": max(0, score),
        "has_critical": has_critical,
        "has_high": has_high,
        "risk_level": "Critical" if has_critical else "High" if has_high else "Medium" if score < 70 else "Low" if score < 90 else "Minimal",
        "total_issues": len(issues),
    }


SecurityImpactAgent = Agent(
    name="SecurityImpactAgent",
    instructions=SECURITY_INSTRUCTIONS,
    tools=[scan_security_issues, check_security_score],
    model=os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
    model_settings=ModelSettings(max_tokens=400),
)
