"""
Database Debugging Agents — Specialized agents for database-related issues.
"""

from agents import Agent, function_tool, ModelSettings
import os
import re
from typing import Dict, Any, List


SQL_OPTIMIZER_INSTRUCTIONS = """
You are a SQL optimization expert. Analyze and fix slow queries.

Capabilities:
1. Detect missing indexes from query patterns
2. Identify N+1 query problems
3. Suggest query optimizations (JOIN vs subquery, etc.)
4. Detect slow full table scans
5. Recommend schema changes for query performance

Output format:
- Query Analyzed: <the query>
- Issues Found: <list with impact estimate>
- Missing Indexes: <suggested indexes>
- Optimization Suggestions: <specific rewrites>
- Estimated Improvement: <percentage>
"""

MIGRATION_VALIDATOR_INSTRUCTIONS = """
You are a migration safety validator. Check if database migrations are safe.

Capabilities:
1. Detect breaking schema changes
2. Check for unsafe column modifications
3. Validate foreign key integrity
4. Identify data loss risks in migrations
5. Suggest safer migration strategies

Output format:
- Migration Analyzed: <description>
- Breaking Changes: <list>
- Data Loss Risk: None / Low / Medium / High
- Safe to Deploy: Yes / With Caution / No
- Recommended Approach: <specific steps>
"""

SCHEMA_ANALYZER_INSTRUCTIONS = """
You are a schema analysis expert. Analyze database schema for issues.

Capabilities:
1. Detect missing primary keys
2. Identify missing foreign key constraints
3. Flag missing indexes on foreign keys
4. Detect inappropriate data types
5. Find normalization violations

Output format:
- Schema Score: 0-100
- Missing Constraints: <list>
- Data Type Issues: <list>
- Normalization Issues: <list>
- Suggested Changes: <list>
"""

TRANSACTION_AGENT_INSTRUCTIONS = """
You are a transaction analysis expert. Detect concurrency and transaction issues.

Capabilities:
1. Detect missing transaction boundaries
2. Identify potential deadlocks
3. Check for race conditions in transaction patterns
4. Detect improper isolation level usage
5. Find long-running transaction risks

Output format:
- Transaction Score: 0-100
- Deadlock Risk: None / Low / Medium / High
- Isolation Issues: <list>
- Recommended Changes: <list>
"""

ORM_MAPPER_INSTRUCTIONS = """
You are an ORM mapping expert. Detect ORM-related issues and mismatches.

Capabilities:
1. Detect N+1 query patterns in ORM usage
2. Identify lazy loading issues
3. Check for inefficient ORM patterns
4. Detect schema/ORM mismatch
5. Suggest ORM query optimizations

Output format:
- ORM Quality Score: 0-100
- N+1 Patterns: <list>
- Lazy Loading Issues: <list>
- Schema Mismatches: <list>
- Optimization Suggestions: <list>
"""


@function_tool
def analyze_sql_query(query: str) -> Dict[str, Any]:
    """Analyze a SQL query for performance issues."""
    issues = []
    query_lower = query.lower()

    if "select *" in query_lower:
        issues.append({"type": "SELECT *", "severity": "warning", "message": "Avoid SELECT * — specify columns explicitly"})
    if "where" not in query_lower and "select" in query_lower:
        issues.append({"type": "Missing WHERE", "severity": "high", "message": "Query has no WHERE clause — will scan entire table"})
    if "like '%" in query_lower:
        issues.append({"type": "Leading Wildcard LIKE", "severity": "warning", "message": "Leading % in LIKE prevents index usage"})
    if "not in" in query_lower:
        issues.append({"type": "NOT IN", "severity": "info", "message": "NOT IN can be slow — consider NOT EXISTS or LEFT JOIN"})
    if "or" in query_lower and "where" in query_lower:
        issues.append({"type": "OR Conditions", "severity": "info", "message": "OR conditions may prevent index usage — consider UNION"})
    if "order by" in query_lower and "limit" not in query_lower:
        issues.append({"type": "ORDER BY without LIMIT", "severity": "info", "message": "ORDER BY without LIMIT sorts entire result set"})
    if "group by" in query_lower and "having" not in query_lower:
        pass

    return {
        "query_length": len(query),
        "issues": issues,
        "has_index_issues": any(i["type"] in ("Missing WHERE", "SELECT *") for i in issues),
    }


@function_tool
def detect_nplus1(code: str) -> List[Dict[str, Any]]:
    """Detect N+1 query patterns in code."""
    issues = []
    lines = code.splitlines()
    in_loop = False
    depth = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if any(kw in stripped for kw in ["for ", "while "]) and ":" in stripped:
            in_loop = True
            depth = len(line) - len(line.lstrip())
        elif stripped.startswith(("def ", "class ")):
            in_loop = False
            depth = 0
        elif in_loop:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= depth:
                in_loop = False
                continue
            db_patterns = [".query(", ".filter(", ".get(", ".first(", ".all(",
                          ".execute(", "cursor.", "fetchone", "fetchall"]
            if any(p in stripped for p in db_patterns):
                issues.append({
                    "line": i,
                    "type": "N+1 Query",
                    "severity": "high",
                    "message": "Database query inside loop — potential N+1 problem",
                    "code": stripped[:60],
                })

    return issues


SQLQueryOptimizerAgent = Agent(
    name="SQLQueryOptimizer",
    instructions=SQL_OPTIMIZER_INSTRUCTIONS,
    tools=[analyze_sql_query],
    model=os.environ.get("OPENROUTER_MODEL"),
    model_settings=ModelSettings(max_tokens=500),
)

MigrationValidatorAgent = Agent(
    name="MigrationValidator",
    instructions=MIGRATION_VALIDATOR_INSTRUCTIONS,
    model=os.environ.get("OPENROUTER_MODEL"),
    model_settings=ModelSettings(max_tokens=500),
)

SchemaAnalyzerAgent = Agent(
    name="SchemaAnalyzer",
    instructions=SCHEMA_ANALYZER_INSTRUCTIONS,
    model=os.environ.get("OPENROUTER_MODEL"),
    model_settings=ModelSettings(max_tokens=500),
)

TransactionAgent = Agent(
    name="TransactionAgent",
    instructions=TRANSACTION_AGENT_INSTRUCTIONS,
    model=os.environ.get("OPENROUTER_MODEL"),
    model_settings=ModelSettings(max_tokens=500),
)

ORMMapperAgent = Agent(
    name="ORMMapperAgent",
    instructions=ORM_MAPPER_INSTRUCTIONS,
    tools=[detect_nplus1],
    model=os.environ.get("OPENROUTER_MODEL"),
    model_settings=ModelSettings(max_tokens=500),
)
