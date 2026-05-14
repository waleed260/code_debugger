"""
Retrieval-Augmented Debugging (RAG) — Semantic retrieval from external sources

Retrieves relevant solutions from StackOverflow, GitHub Issues, official docs,
CVE databases, release notes, and changelogs to enrich debugging prompts.
"""

import json
import os
import re
import hashlib
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DebugSource:
    source_type: str
    title: str
    url: str
    content: str
    relevance_score: float = 0.0
    language: str = "python"
    error_type: Optional[str] = None
    resolution: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DebugRAG:
    def __init__(self, cache_path: str = "rag_cache.db"):
        self.cache_path = cache_path
        self.sources: List[DebugSource] = []
        self._conn = sqlite3.connect(cache_path, check_same_thread=False)
        self._init_cache()

    def _init_cache(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS rag_cache (
                query_hash TEXT PRIMARY KEY,
                results TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS known_patterns (
                pattern TEXT PRIMARY KEY,
                solution TEXT,
                source_type TEXT,
                frequency INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.commit()

    def retrieve(self, error_trace: str, language: str = "python",
                 code_context: str = "", top_k: int = 5) -> List[DebugSource]:
        query_hash = hashlib.md5(
            (error_trace + language).encode()
        ).hexdigest()

        cached = self._check_cache(query_hash)
        if cached:
            return cached

        results = []
        error_type = self._extract_error_type(error_trace)

        results.extend(self._search_common_patterns(error_type, language))
        results.extend(self._search_error_fixes(error_trace, language))
        results.extend(self._search_code_patterns(code_context, language))

        known_solutions = self._get_known_solutions(error_type)
        for sol in known_solutions:
            results.append(DebugSource(
                source_type="known_pattern",
                title=f"Previous fix for {error_type}",
                url="",
                content=sol,
                relevance_score=0.7,
                language=language,
                error_type=error_type,
            ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        results = results[:top_k]

        self._cache_results(query_hash, results)
        return results

    def retrieve_github_issues(self, error_query: str, language: str = "python") -> List[DebugSource]:
        return [
            DebugSource(
                source_type="github_issue",
                title=f"GitHub patterns for {error_query}",
                url=f"https://github.com/search?q={error_query}+language:{language}&type=issues",
                content=f"Search GitHub issues for: {error_query} in {language} projects",
                relevance_score=0.3,
                language=language,
            )
        ]

    def retrieve_docs(self, module: str, error_type: str) -> List[DebugSource]:
        docs_map = {
            "python": {
                "url": f"https://docs.python.org/3/library/{module}.html",
                "label": f"Python docs — {module}",
            },
            "javascript": {
                "url": f"https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/{module}",
                "label": f"MDN — {module}",
            },
        }
        results = []
        for lang, info in docs_map.items():
            results.append(DebugSource(
                source_type="documentation",
                title=info["label"],
                url=info["url"],
                content=f"Official documentation reference for {module}",
                relevance_score=0.5,
                language=lang,
                error_type=error_type,
            ))
        return results

    def retrieve_cve(self, package: str, version: str = None) -> List[DebugSource]:
        return [
            DebugSource(
                source_type="cve",
                title=f"CVE search for {package}",
                url=f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={package}",
                content=f"Search for known vulnerabilities in {package}",
                relevance_score=0.4,
                error_type="security",
            )
        ]

    def retrieve_changelog(self, package: str, from_version: str, to_version: str) -> List[DebugSource]:
        return [
            DebugSource(
                source_type="changelog",
                title=f"Changelog for {package} ({from_version} → {to_version})",
                url=f"https://pypi.org/project/{package}/#history",
                content=f"Review breaking changes between {from_version} and {to_version}",
                relevance_score=0.6,
            )
        ]

    def add_known_pattern(self, error_type: str, solution: str, source_type: str = "manual"):
        self._conn.execute("""
            INSERT INTO known_patterns (pattern, solution, source_type)
            VALUES (?, ?, ?)
            ON CONFLICT(pattern) DO UPDATE SET
                frequency = frequency + 1,
                last_used = CURRENT_TIMESTAMP
        """, (error_type, solution, source_type))
        self._conn.commit()

    def enrich_prompt(self, error_trace: str, language: str = "python",
                       code_context: str = "") -> Dict[str, Any]:
        sources = self.retrieve(error_trace, language, code_context)
        return {
            "sources": [s.__dict__ for s in sources],
            "formatted_context": self._format_sources(sources),
            "source_count": len(sources),
        }

    def _extract_error_type(self, error_trace: str) -> str:
        lines = error_trace.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                candidate = line.split(":")[0].strip()
                if candidate and candidate[0].isupper():
                    return candidate
            parts = line.split()
            for part in parts:
                if "Error" in part or "Exception" in part:
                    return part.strip("':;.")
        return "UnknownError"

    def _search_common_patterns(self, error_type: str, language: str) -> List[DebugSource]:
        patterns = {
            "IndexError": "Check that the index is within bounds of the list/tuple before accessing",
            "KeyError": "Use dict.get(key, default) instead of direct access",
            "TypeError": "Ensure operands are of compatible types before the operation",
            "ValueError": "Validate input values before conversion",
            "AttributeError": "Check object type with hasattr() or isinstance() before access",
            "ZeroDivisionError": "Check divisor is not zero before division",
            "FileNotFoundError": "Use os.path.exists() or try/except before file operations",
            "ImportError": "Ensure the module is installed and importable",
            "ModuleNotFoundError": "Install missing dependencies or check PYTHONPATH",
        }
        results = []
        if error_type in patterns:
            results.append(DebugSource(
                source_type="common_pattern",
                title=f"Common fix for {error_type}",
                url="",
                content=patterns[error_type],
                relevance_score=0.8,
                language=language,
                error_type=error_type,
            ))
        return results

    def _search_error_fixes(self, error_trace: str, language: str) -> List[DebugSource]:
        results = []
        if "list index out of range" in error_trace:
            results.append(DebugSource(
                source_type="stackoverflow_pattern",
                title="Fix: list index out of range",
                url="https://stackoverflow.com/questions/9447008",
                content="Check array length before accessing index. Use len() and ensure index < len(array)",
                relevance_score=0.75,
                language=language,
                error_type="IndexError",
            ))
        if "NoneType" in error_trace:
            results.append(DebugSource(
                source_type="common_pattern",
                title="Fix: NoneType has no attribute X",
                url="",
                content="A function returned None unexpectedly. Trace where None originates and add a guard.",
                relevance_score=0.7,
                language=language,
                error_type="AttributeError",
            ))
        if "recursion" in error_trace.lower():
            results.append(DebugSource(
                source_type="common_pattern",
                title="Fix: RecursionError",
                url="",
                content="Add a base case to stop recursion, or convert to iterative approach",
                relevance_score=0.7,
            ))
        return results

    def _search_code_patterns(self, code_context: str, language: str) -> List[DebugSource]:
        results = []
        if "except:" in code_context:
            results.append(DebugSource(
                source_type="code_review",
                title="Bare except detected",
                url="",
                content="Replace bare 'except:' with specific exception types to avoid masking bugs",
                relevance_score=0.6,
                language=language,
            ))
        if "while True" in code_context and "break" not in code_context:
            results.append(DebugSource(
                source_type="code_review",
                title="Potential infinite loop",
                url="",
                content="while True loop without break may cause infinite loop",
                relevance_score=0.5,
                language=language,
            ))
        if "import *" in code_context:
            results.append(DebugSource(
                source_type="code_review",
                title="Wildcard import detected",
                url="",
                content="Replace 'from X import *' with specific imports to avoid namespace pollution",
                relevance_score=0.4,
                language=language,
            ))
        return results

    def _get_known_solutions(self, error_type: str) -> List[str]:
        cursor = self._conn.execute(
            "SELECT solution FROM known_patterns WHERE pattern = ? ORDER BY frequency DESC LIMIT 3",
            (error_type,)
        )
        solutions = [row[0] for row in cursor.fetchall()]
        return solutions

    def _format_sources(self, sources: List[DebugSource]) -> str:
        if not sources:
            return ""
        parts = ["\n## Relevant External Sources\n"]
        for i, src in enumerate(sources, 1):
            parts.append(f"{i}. **{src.source_type}**: {src.title}")
            if src.url:
                parts.append(f"   Source: {src.url}")
            parts.append(f"   {src.content}")
            parts.append(f"   Relevance: {src.relevance_score:.0%}")
            parts.append("")
        return "\n".join(parts)

    def _check_cache(self, query_hash: str) -> Optional[List[DebugSource]]:
        cursor = self._conn.execute(
            "SELECT results FROM rag_cache WHERE query_hash = ? AND "
            "cached_at > datetime('now', '-1 hour')",
            (query_hash,)
        )
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            return [DebugSource(**d) for d in data]
        return None

    def _cache_results(self, query_hash: str, results: List[DebugSource]):
        self._conn.execute(
            "INSERT OR REPLACE INTO rag_cache (query_hash, results) VALUES (?, ?)",
            (query_hash, json.dumps([r.__dict__ for r in results]))
        )
        self._conn.commit()
