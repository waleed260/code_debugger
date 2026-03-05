"""
Session Management for Multi-Agent Debugging System

Provides persistent storage of debugging sessions using SQLite.
Integrates with OpenAI Agents SDK for conversation tracking.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
# from datetime import datetime
# from pathlib import Path


class SessionManager:
    """
    Manages debugging sessions with SQLite persistence.
    
    Features:
    - Create/load sessions
    - Store agent interactions
    - Store conversation turns
    - Query session history
    - Export/import sessions
    """
    
    def __init__(self, db_path: str = "debug_sessions.db"):
        """
        Initialize session manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT DEFAULT '{}',
                error_context TEXT,
                final_report TEXT,
                validation_passed BOOLEAN
            )
        ''')
        
        # Agent interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                tool_calls TEXT DEFAULT '[]',
                duration_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Conversation turns table (for OpenAI Agents SDK traces)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                turn_index INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls TEXT DEFAULT '[]',
                tool_responses TEXT DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Agent traces table (OpenAI Agents SDK specific)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                trace_id TEXT UNIQUE NOT NULL,
                parent_id TEXT,
                span_id TEXT,
                agent_name TEXT,
                span_type TEXT,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                output TEXT,
                error TEXT,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Bug reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                bug_description TEXT,
                root_cause TEXT,
                fix_proposal TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sessions_status 
            ON sessions(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_interactions_session 
            ON agent_interactions(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_session 
            ON conversation_turns(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_traces_session 
            ON agent_traces(session_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, 
                       error_context: Dict[str, Any] = None,
                       metadata: Dict[str, Any] = None) -> bool:
        """
        Create a new debugging session.
        
        Args:
            session_id: Unique session identifier
            error_context: Initial error context
            metadata: Additional session metadata
            
        Returns:
            True if created successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (session_id, metadata, error_context, status)
                VALUES (?, ?, ?, 'active')
            ''', (
                session_id,
                json.dumps(metadata or {}),
                json.dumps(error_context) if error_context else None
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            session = dict(row)
            # Parse JSON fields
            session['metadata'] = json.loads(session['metadata'])
            if session.get('error_context'):
                session['error_context'] = json.loads(session['error_context'])
            if session.get('final_report'):
                session['final_report'] = session['final_report']
            return session
        
        return None
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """
        Update session fields.
        
        Args:
            session_id: Session identifier
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update
            fields = []
            values = []
            
            allowed_fields = ['status', 'metadata', 'final_report', 'validation_passed']
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    if key == 'metadata':
                        value = json.dumps(value)
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            # Always update timestamp
            fields.append("updated_at = CURRENT_TIMESTAMP")
            
            if not fields:
                conn.close()
                return False
            
            query = f"UPDATE sessions SET {', '.join(fields)} WHERE session_id = ?"
            values.append(session_id)
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def add_interaction(self, session_id: str,
                       agent_name: str,
                       interaction_type: str,
                       input_data: Any = None,
                       output_data: Any = None,
                       tool_calls: List[Dict] = None,
                       duration_ms: int = None) -> int:
        """
        Add an agent interaction.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent (DebugSleuth, SolutionArchitect, etc.)
            interaction_type: Type of interaction (run, handoff, etc.)
            input_data: Input to the agent
            output_data: Output from the agent
            tool_calls: List of tool calls made
            duration_ms: Duration in milliseconds
            
        Returns:
            Interaction ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_interactions 
            (session_id, agent_name, interaction_type, input_data, output_data, tool_calls, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            agent_name,
            interaction_type,
            json.dumps(input_data) if input_data else None,
            json.dumps(output_data) if output_data else None,
            json.dumps(tool_calls or []),
            duration_ms
        ))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interaction_id
    
    def add_conversation_turn(self, session_id: str,
                             turn_index: int,
                             role: str,
                             content: str,
                             tool_calls: List[Dict] = None,
                             tool_responses: List[Dict] = None) -> int:
        """
        Add a conversation turn (for OpenAI Agents SDK traces).
        
        Args:
            session_id: Session identifier
            turn_index: Turn number in conversation
            role: Role (user, assistant, system, tool)
            content: Message content
            tool_calls: Tool calls if any
            tool_responses: Tool responses if any
            
        Returns:
            Turn ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_turns 
            (session_id, turn_index, role, content, tool_calls, tool_responses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            turn_index,
            role,
            content,
            json.dumps(tool_calls or []),
            json.dumps(tool_responses or [])
        ))
        
        turn_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return turn_id
    
    def add_agent_trace(self, session_id: str,
                       trace_id: str,
                       span_id: str,
                       agent_name: str,
                       span_type: str,
                       output: Any = None,
                       error: str = None,
                       metadata: Dict = None,
                       parent_id: str = None) -> int:
        """
        Add an agent trace (OpenAI Agents SDK specific).
        
        Args:
            session_id: Session identifier
            trace_id: Unique trace identifier
            span_id: Span identifier
            agent_name: Agent name
            span_type: Type of span
            output: Output data
            error: Error message if any
            metadata: Additional metadata
            parent_id: Parent trace ID
            
        Returns:
            Trace ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_traces 
            (session_id, trace_id, parent_id, span_id, agent_name, span_type, 
             started_at, output, error, metadata)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
        ''', (
            session_id,
            trace_id,
            parent_id,
            span_id,
            agent_name,
            span_type,
            json.dumps(output) if output else None,
            error,
            json.dumps(metadata or {})
        ))
        
        trace_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trace_db_id
    
    def update_trace_end(self, trace_id: str, output: Any = None, error: str = None) -> bool:
        """
        Update a trace when it ends.
        
        Args:
            trace_id: Trace identifier (from database)
            output: Final output
            error: Error if any
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_traces 
            SET ended_at = CURRENT_TIMESTAMP, output = ?, error = ?
            WHERE id = ?
        ''', (
            json.dumps(output) if output else None,
            error,
            trace_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_session_interactions(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all interactions for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of interactions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM agent_interactions 
            WHERE session_id = ? 
            ORDER BY timestamp
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        interactions = []
        for row in rows:
            interaction = dict(row)
            # Parse JSON fields
            if interaction.get('input_data'):
                interaction['input_data'] = json.loads(interaction['input_data'])
            if interaction.get('output_data'):
                interaction['output_data'] = json.loads(interaction['output_data'])
            if interaction.get('tool_calls'):
                interaction['tool_calls'] = json.loads(interaction['tool_calls'])
            interactions.append(interaction)
        
        return interactions
    
    def get_conversation_turns(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversation turns for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of conversation turns
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversation_turns 
            WHERE session_id = ? 
            ORDER BY turn_index
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        turns = []
        for row in rows:
            turn = dict(row)
            # Parse JSON fields
            if turn.get('tool_calls'):
                turn['tool_calls'] = json.loads(turn['tool_calls'])
            if turn.get('tool_responses'):
                turn['tool_responses'] = json.loads(turn['tool_responses'])
            turns.append(turn)
        
        return turns
    
    def get_agent_traces(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all agent traces for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of agent traces
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM agent_traces 
            WHERE session_id = ? 
            ORDER BY started_at
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        traces = []
        for row in rows:
            trace = dict(row)
            # Parse JSON fields
            if trace.get('output'):
                trace['output'] = json.loads(trace['output'])
            if trace.get('metadata'):
                trace['metadata'] = json.loads(trace['metadata'])
            traces.append(trace)
        
        return traces
    
    def get_session_bugs(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all bug reports for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of bug reports
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bug_reports 
            WHERE session_id = ? 
            ORDER BY created_at
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        bugs = [dict(row) for row in rows]
        return bugs
    
    def add_bug_report(self, session_id: str,
                      bug_description: str,
                      root_cause: str = None,
                      fix_proposal: str = None) -> int:
        """
        Add a bug report to a session.
        
        Args:
            session_id: Session identifier
            bug_description: Description of the bug
            root_cause: Root cause analysis
            fix_proposal: Proposed fix
            
        Returns:
            Bug report ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bug_reports 
            (session_id, bug_description, root_cause, fix_proposal)
            VALUES (?, ?, ?, ?)
        ''', (
            session_id,
            bug_description,
            root_cause,
            fix_proposal
        ))
        
        bug_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return bug_id
    
    def update_bug_status(self, bug_id: int, status: str) -> bool:
        """
        Update bug report status.
        
        Args:
            bug_id: Bug report ID
            status: New status (open, in_progress, resolved, closed)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bug_reports 
            SET status = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status != 'resolved'
        ''', (status, bug_id))
        
        conn.commit()
        conn.close()
    
    def list_sessions(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List sessions with optional filtering.
        
        Args:
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of sessions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE status = ? 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT * FROM sessions 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session = dict(row)
            session['metadata'] = json.loads(session['metadata'])
            sessions.append(session)
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all related data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete related records first (foreign keys)
        cursor.execute('DELETE FROM agent_interactions WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM conversation_turns WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM agent_traces WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM bug_reports WHERE session_id = ?', (session_id,))
        
        # Delete session
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        stats['total_sessions'] = cursor.fetchone()[0]
        
        # Sessions by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM sessions 
            GROUP BY status
        ''')
        stats['sessions_by_status'] = {
            row[0]: row[1] for row in cursor.fetchall()
        }
        
        # Total interactions
        cursor.execute('SELECT COUNT(*) FROM agent_interactions')
        stats['total_interactions'] = cursor.fetchone()[0]
        
        # Agents usage
        cursor.execute('''
            SELECT agent_name, COUNT(*) as count 
            FROM agent_interactions 
            GROUP BY agent_name
        ''')
        stats['agents_usage'] = {
            row[0]: row[1] for row in cursor.fetchall()
        }
        
        # Validation pass rate
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN validation_passed = 1 THEN 1 END) as passed,
                COUNT(*) as total
            FROM sessions 
            WHERE validation_passed IS NOT NULL
        ''')
        row = cursor.fetchone()
        if row[1] > 0:
            stats['validation_pass_rate'] = row[0] / row[1]
        else:
            stats['validation_pass_rate'] = 0
        
        conn.close()
        
        return stats
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """
        Export a complete session for backup or sharing.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete session data
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        session['interactions'] = self.get_session_interactions(session_id)
        session['conversation_turns'] = self.get_conversation_turns(session_id)
        session['agent_traces'] = self.get_agent_traces(session_id)
        session['bugs'] = self.get_session_bugs(session_id)
        
        return session
    
    def import_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Import a session from export data.
        
        Args:
            session_data: Session data from export_session
            
        Returns:
            True if imported successfully
        """
        # Create session
        self.create_session(
            session_data['session_id'],
            session_data.get('error_context'),
            session_data.get('metadata', {})
        )
        
        # Update session fields
        self.update_session(
            session_data['session_id'],
            status=session_data.get('status', 'imported'),
            final_report=session_data.get('final_report'),
            validation_passed=session_data.get('validation_passed')
        )
        
        # Import interactions
        for interaction in session_data.get('interactions', []):
            self.add_interaction(
                session_data['session_id'],
                interaction['agent_name'],
                interaction['interaction_type'],
                interaction.get('input_data'),
                interaction.get('output_data'),
                interaction.get('tool_calls'),
                interaction.get('duration_ms')
            )
        
        # Import conversation turns
        for turn in session_data.get('conversation_turns', []):
            self.add_conversation_turn(
                session_data['session_id'],
                turn['turn_index'],
                turn['role'],
                turn['content'],
                turn.get('tool_calls'),
                turn.get('tool_responses')
            )
        
        # Import bug reports
        for bug in session_data.get('bugs', []):
            self.add_bug_report(
                session_data['session_id'],
                bug['bug_description'],
                bug.get('root_cause'),
                bug.get('fix_proposal')
            )
        
        return True
    
    def close(self):
        """Close database connections (cleanup)."""
        # SQLite connections auto-close, but this is here for completeness
        pass
