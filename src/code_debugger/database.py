import sqlite3
import json
from typing import List, Dict, Any


class SessionDatabase:
    """SQLite database for storing debugging session data."""

    def __init__(self, db_path: str = "debug_sessions.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        ''')

        # Agent interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                interaction_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')

        # Bugs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                bug_description TEXT,
                root_cause TEXT,
                fix_proposal TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_session(self, session_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new debugging session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO sessions (session_id, metadata) VALUES (?, ?)",
                (session_id, json.dumps(metadata) if metadata else "{}")
            )

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False

    def add_interaction(self, session_id: str, agent_role: str, interaction_data: Dict[str, Any]) -> bool:
        """Add an agent interaction to a session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO agent_interactions (session_id, agent_role, interaction_data) VALUES (?, ?, ?)",
                (session_id, agent_role, json.dumps(interaction_data))
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding interaction: {e}")
            return False

    def add_bug(self, session_id: str, bug_description: str, root_cause: str = None, fix_proposal: str = None) -> int:
        """Add a bug record to a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO bugs (session_id, bug_description, root_cause, fix_proposal) VALUES (?, ?, ?, ?)",
            (session_id, bug_description, root_cause, fix_proposal)
        )

        bug_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return bug_id

    def update_bug(self, bug_id: int, **kwargs) -> bool:
        """Update bug information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['bug_description', 'root_cause', 'fix_proposal', 'status']:
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            conn.close()
            return False

        query = f"UPDATE bugs SET {', '.join(fields)} WHERE id = ?"
        values.append(bug_id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True

    def get_session_bugs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all bugs for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bugs WHERE session_id = ? ORDER BY created_at",
            (session_id,)
        )

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        bugs = []
        for row in rows:
            bug_dict = dict(zip(columns, row))
            bugs.append(bug_dict)

        conn.close()
        return bugs

    def get_session_interactions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all interactions for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM agent_interactions WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        interactions = []
        for row in rows:
            interaction_dict = dict(zip(columns, row))
            interaction_dict['interaction_data'] = json.loads(interaction_dict['interaction_data'])
            interactions.append(interaction_dict)

        conn.close()
        return interactions