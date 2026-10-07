import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone

APP_DIR = Path.home() / ".programming_tutor"
DB_PATH = APP_DIR / "app.db"

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,       -- 'lesson' | 'quiz' | 'challenge'
    item_id TEXT NOT NULL,
    status TEXT NOT NULL,          -- 'viewed' | 'passed' | 'attempted'
    score INTEGER DEFAULT 0,
    max_score INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    related_lesson_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    box INTEGER NOT NULL DEFAULT 1,             -- Leitner box (1..5)
    next_review TEXT NOT NULL,                  -- ISO datetime
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS achievements (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    achieved_at TEXT
);
"""

def _utc_now() -> datetime:
    """The current UTC time without timezone info, the form the database stores."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

@contextmanager
def _connect(db_path: Optional[str] = None):
    """Open the database, save the changes on success, and always close it again."""
    conn = sqlite3.connect(db_path or str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()

class Storage:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db()

    def _ensure_db(self):
        # The folder is only created when the database is really about to be used.
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with _connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    # Progress
    def record_progress(self, item_type: str, item_id: str, status: str,
                        score: int = 0, max_score: int = 0) -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO progress(item_type, item_id, status, score, max_score) VALUES (?, ?, ?, ?, ?)",
                (item_type, item_id, status, score, max_score)
            )

    def get_totals(self) -> Dict[str, int]:
        with _connect(self.db_path) as conn:
            cur = conn.execute("SELECT SUM(score) s, SUM(max_score) m FROM progress;")
            row = cur.fetchone()
            return {"score": (row["s"] or 0), "max_score": (row["m"] or 0)}

    def list_progress(self) -> List[Tuple[Any, ...]]:
        with _connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT item_type, item_id, status, score, max_score, created_at FROM progress ORDER BY created_at DESC, id DESC;"
            )
            return [tuple(r) for r in cur.fetchall()]

    def reset_all_progress(self) -> None:
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM progress;")

    # Notes
    def add_note(self, title: str, content: str, related_lesson_id: Optional[str]) -> int:
        with _connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO notes(title, content, related_lesson_id) VALUES (?,?,?)",
                (title, content, related_lesson_id)
            )
            return cur.lastrowid

    def list_notes(self, query: Optional[str] = None):
        with _connect(self.db_path) as conn:
            if query:
                cur = conn.execute(
                    "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC, id DESC",
                    (f"%{query}%", f"%{query}%")
                )
            else:
                cur = conn.execute("SELECT * FROM notes ORDER BY created_at DESC, id DESC")
            return [dict(r) for r in cur.fetchall()]

    def delete_note(self, note_id: int):
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM notes WHERE id=?", (note_id,))

    # Drafts
    def save_draft(self, challenge_id: str, code: str):
        with _connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO drafts(challenge_id, code) VALUES(?, ?)",
                (challenge_id, code)
            )

    def latest_draft(self, challenge_id: str) -> Optional[str]:
        with _connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT code FROM drafts WHERE challenge_id=? ORDER BY created_at DESC, id DESC LIMIT 1",
                (challenge_id,)
            )
            row = cur.fetchone()
            return row["code"] if row else None

    # Flashcards (SRS)
    def add_flashcard(self, front: str, back: str):
        now = _utc_now()
        with _connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO flashcards(front, back, box, next_review) VALUES(?,?,1,?)",
                (front, back, (now.isoformat()))
            )

    def list_due_flashcards(self) -> List[Dict[str, Any]]:
        now = _utc_now().isoformat()
        with _connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT * FROM flashcards WHERE next_review <= ? ORDER BY next_review ASC, id ASC LIMIT 50", (now,)
            )
            return [dict(r) for r in cur.fetchall()]

    def promote_or_demote_card(self, card_id: int, correct: bool):
        # Leitner: box 1..5; intervals: 1d, 2d, 4d, 7d, 14d (simple)
        with _connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM flashcards WHERE id=?", (card_id,))
            row = cur.fetchone()
            if not row: return
            box = row["box"]
            box = min(5, box + 1) if correct else 1
            days = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}.get(box, 1)
            next_review = (_utc_now() + timedelta(days=days)).isoformat()
            conn.execute("UPDATE flashcards SET box=?, next_review=? WHERE id=?", (box, next_review, card_id))

    def list_all_flashcards(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        with _connect(self.db_path) as conn:
            if query:
                cur = conn.execute(
                    "SELECT * FROM flashcards WHERE front LIKE ? OR back LIKE ? ORDER BY created_at DESC, id DESC",
                    (f"%{query}%", f"%{query}%")
                )
            else:
                cur = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC, id DESC")
            return [dict(r) for r in cur.fetchall()]

    def delete_flashcard(self, card_id: int):
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM flashcards WHERE id=?", (card_id,))

    # Settings
    def set_setting(self, key: str, value: str):
        with _connect(self.db_path) as conn:
            conn.execute("INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                         (key, value))

    def get_setting(self, key: str, default: str = "") -> str:
        with _connect(self.db_path) as conn:
            cur = conn.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    # Achievements
    def ensure_achievement(self, code: str, name: str):
        with _connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO achievements(code, name) VALUES(?, ?) ON CONFLICT(code) DO NOTHING",
                (code, name)
            )

    def grant_achievement(self, code: str):
        with _connect(self.db_path) as conn:
            conn.execute("UPDATE achievements SET achieved_at=CURRENT_TIMESTAMP WHERE code=?", (code,))

    def list_achievements(self):
        with _connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM achievements ORDER BY name ASC")
            return [dict(r) for r in cur.fetchall()]

    def reset_all(self):
        """Danger zone: nuke data but keep schema."""
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM progress;")
            conn.execute("DELETE FROM notes;")
            conn.execute("DELETE FROM drafts;")
            conn.execute("DELETE FROM flashcards;")
            conn.execute("DELETE FROM achievements;")
            conn.execute("DELETE FROM settings;")