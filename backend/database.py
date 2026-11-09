"""
SQLite database layer for P2S — stores triage sessions for analytics.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'p2s_data.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                domain      TEXT,
                urgency     TEXT,
                status      TEXT,
                issue       TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                domain        TEXT NOT NULL,
                role          TEXT,
                official_link TEXT,
                is_free       INTEGER DEFAULT 1,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def log_session(session_id: str, domain: str, urgency: str, status: str, issue: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, domain, urgency, status, issue) VALUES (?,?,?,?,?)",
            (session_id, domain, urgency, status, issue)
        )
        conn.commit()

def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        resolved = conn.execute("SELECT COUNT(*) FROM sessions WHERE status='resolved'").fetchone()[0]
        clarified = conn.execute("SELECT COUNT(*) FROM sessions WHERE status='needs_clarification'").fetchone()[0]

        by_domain = {}
        for row in conn.execute("SELECT domain, COUNT(*) as cnt FROM sessions GROUP BY domain"):
            by_domain[row['domain']] = row['cnt']

        by_urgency = {}
        for row in conn.execute("SELECT urgency, COUNT(*) as cnt FROM sessions GROUP BY urgency"):
            by_urgency[row['urgency']] = row['cnt']

        recent = []
        for row in conn.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 20"):
            recent.append(dict(row))

        return {
            "total_sessions": total,
            "resolved": resolved,
            "needs_clarification": clarified,
            "by_domain": by_domain,
            "by_urgency": by_urgency,
            "recent_sessions": recent
        }

def clear_sessions():
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions")
        conn.commit()

def add_service_db(name, domain, role, official_link, is_free):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO services (name, domain, role, official_link, is_free) VALUES (?,?,?,?,?)",
            (name, domain, role, official_link, int(is_free))
        )
        conn.commit()
