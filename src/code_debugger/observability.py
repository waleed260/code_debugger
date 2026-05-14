"""
Observability Stack — Track token usage, latency, fix success rate, and more

Provides structured logging, metrics collection, and performance tracking
for the entire debugging pipeline.
"""

import time
import json
import os
import sqlite3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class DebugMetric:
    session_id: str
    agent_name: str
    start_time: float
    end_time: float
    duration_ms: float
    token_count: int = 0
    success: bool = False
    error_type: Optional[str] = None
    confidence_score: float = 0.0
    retry_count: int = 0
    model_used: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityReport:
    total_sessions: int
    success_rate: float
    avg_duration_ms: float
    total_tokens: int
    agent_stats: Dict[str, Any]
    error_distribution: Dict[str, int]
    recent_sessions: List[Dict[str, Any]]
    top_errors: List[tuple]


class ObservabilityTracker:
    def __init__(self, db_path: str = "observability.db"):
        self.db_path = db_path
        self._current_session: Optional[Dict[str, Any]] = None
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS debug_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_name TEXT,
                start_time REAL,
                end_time REAL,
                duration_ms REAL,
                token_count INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT 0,
                error_type TEXT,
                confidence_score REAL DEFAULT 0.0,
                retry_count INTEGER DEFAULT 0,
                model_used TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS debug_sessions_summary (
                session_id TEXT PRIMARY KEY,
                total_duration_ms REAL,
                total_tokens INTEGER DEFAULT 0,
                agents_used INTEGER DEFAULT 0,
                final_status TEXT,
                error_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_session
            ON debug_metrics(session_id)
        """)
        conn.commit()
        conn.close()

    def start_session(self, session_id: str, error_type: str = None):
        self._current_session = {
            "session_id": session_id,
            "error_type": error_type,
            "start_time": time.time(),
            "agent_metrics": [],
        }

    def end_session(self, status: str = "completed"):
        if not self._current_session:
            return
        session = self._current_session
        total_duration = (time.time() - session["start_time"]) * 1000
        total_tokens = sum(m.token_count for m in session.get("agent_metrics", []))

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO debug_sessions_summary
            (session_id, total_duration_ms, total_tokens, agents_used, final_status, error_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["session_id"],
            total_duration,
            total_tokens,
            len(session.get("agent_metrics", [])),
            status,
            session.get("error_type"),
        ))
        conn.commit()
        conn.close()
        self._current_session = None

    def record_agent_run(self, agent_name: str, duration_ms: float,
                          success: bool = False, token_count: int = 0,
                          error_type: str = None, confidence: float = 0.0,
                          retry_count: int = 0, model_used: str = "",
                          metadata: Dict = None):
        if not self._current_session:
            return

        metric = DebugMetric(
            session_id=self._current_session["session_id"],
            agent_name=agent_name,
            start_time=time.time() - duration_ms / 1000,
            end_time=time.time(),
            duration_ms=duration_ms,
            token_count=token_count,
            success=success,
            error_type=error_type or self._current_session.get("error_type"),
            confidence_score=confidence,
            retry_count=retry_count,
            model_used=model_used,
            metadata=metadata or {},
        )

        self._current_session["agent_metrics"].append(metric)

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO debug_metrics
            (session_id, agent_name, start_time, end_time, duration_ms,
             token_count, success, error_type, confidence_score,
             retry_count, model_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric.session_id, metric.agent_name, metric.start_time,
            metric.end_time, metric.duration_ms, metric.token_count,
            int(metric.success), metric.error_type, metric.confidence_score,
            metric.retry_count, metric.model_used,
            json.dumps(metric.metadata),
        ))
        conn.commit()
        conn.close()

    def get_report(self, limit: int = 20) -> ObservabilityReport:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        total = conn.execute("SELECT COUNT(*) FROM debug_sessions_summary").fetchone()[0]
        success_count = conn.execute(
            "SELECT COUNT(*) FROM debug_sessions_summary WHERE final_status = 'completed'"
        ).fetchone()[0]

        avg_duration = conn.execute(
            "SELECT AVG(total_duration_ms) FROM debug_sessions_summary"
        ).fetchone()[0] or 0

        total_tokens = conn.execute(
            "SELECT COALESCE(SUM(total_tokens), 0) FROM debug_sessions_summary"
        ).fetchone()[0]

        agent_rows = conn.execute("""
            SELECT agent_name,
                   COUNT(*) as runs,
                   AVG(duration_ms) as avg_dur,
                   SUM(success) as successes,
                   AVG(confidence_score) as avg_conf,
                   AVG(token_count) as avg_tok
            FROM debug_metrics
            GROUP BY agent_name
        """).fetchall()

        agent_stats = {}
        for row in agent_rows:
            agent_stats[row["agent_name"]] = {
                "runs": row["runs"],
                "avg_duration_ms": round(row["avg_dur"], 1) if row["avg_dur"] else 0,
                "successes": row["successes"],
                "success_rate": round(row["successes"] / row["runs"] * 100, 1) if row["runs"] else 0,
                "avg_confidence": round(row["avg_conf"], 2) if row["avg_conf"] else 0,
                "avg_tokens": round(row["avg_tok"], 0) if row["avg_tok"] else 0,
            }

        error_dist = {}
        error_rows = conn.execute("""
            SELECT error_type, COUNT(*) as count
            FROM debug_metrics
            WHERE error_type IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
        """).fetchall()
        for row in error_rows:
            error_dist[row["error_type"]] = row["count"]

        recent = conn.execute(f"""
            SELECT * FROM debug_sessions_summary
            ORDER BY created_at DESC LIMIT {limit}
        """).fetchall()

        recent_sessions = [dict(r) for r in recent]

        top_errors = sorted(error_dist.items(), key=lambda x: x[1], reverse=True)[:10]

        conn.close()

        return ObservabilityReport(
            total_sessions=total or 0,
            success_rate=round(success_count / total * 100, 1) if total else 0,
            avg_duration_ms=round(avg_duration, 1) if avg_duration else 0,
            total_tokens=total_tokens or 0,
            agent_stats=agent_stats,
            error_distribution=error_dist,
            recent_sessions=recent_sessions,
            top_errors=top_errors,
        )

    def get_timeline(self, session_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT agent_name, start_time, end_time, duration_ms,
                   success, error_type, confidence_score, model_used
            FROM debug_metrics
            WHERE session_id = ?
            ORDER BY start_time
        """, (session_id,))
        results = [dict(r) for r in rows.fetchall()]
        conn.close()
        return results
