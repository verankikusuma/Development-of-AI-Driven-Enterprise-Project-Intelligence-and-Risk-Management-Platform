"""SQLite persistence for users, sessions, documents, and chat history.

User-scoped: conversations and documents are never visible across accounts.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

_LOCK = threading.Lock()

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "app_store.db")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
PBKDF2_ITERS = 210_000


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERS)
    return f"pbkdf2${PBKDF2_ITERS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        _, iters, salt, digest = stored.split("$", 3)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iters))
        return secrets.compare_digest(check.hex(), digest)
    # Legacy plaintext from users.json
    return secrets.compare_digest(password, stored)


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _LOCK, connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                job_role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_id TEXT,
                filename TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                mime TEXT,
                size_bytes INTEGER NOT NULL,
                extracted_text TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_docs_user_hash
                ON documents(user_id, content_hash);
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        
        # Safely add last_workspace to users if it doesn't exist
        try:
            columns = [row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
            if "last_workspace" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN last_workspace TEXT")
        except Exception:
            pass
    _migrate_users_json()


def _migrate_users_json() -> None:
    path = os.path.join(_ROOT, "users.json")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return
    from utils.roles import normalize_job_role

    with _LOCK, connect() as conn:
        for username, rec in (raw or {}).items():
            if not username or not isinstance(rec, dict):
                continue
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                continue
            password = rec.get("password", "")
            role = normalize_job_role(rec.get("job_role") or rec.get("role"))
            conn.execute(
                "INSERT INTO users (id, username, password_hash, job_role, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), username, hash_password(password) if password else hash_password(secrets.token_hex(8)), role, _now()),
            )
    _seed_demo_users()


def _seed_demo_users() -> None:
    demos = [
        ("it_user", "it123", "Full Stack Developer"),
        ("nonit_user", "nonit123", "Management"),
        ("pm_user", "pm123", "Project Manager"),
        ("ml_user", "ml123", "ML/AI Developer"),
        ("qa_user", "qa123", "Tester / QA Engineer"),
        ("devops_user", "devops123", "DevOps Engineer"),
        ("be_user", "be123", "Backend Developer"),
        ("fe_user", "fe123", "Frontend Developer"),
    ]
    with _LOCK, connect() as conn:
        for username, password, role in demos:
            row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if row:
                continue
            conn.execute(
                "INSERT INTO users (id, username, password_hash, job_role, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), username, hash_password(password), role, _now()),
            )


def create_user(username: str, password: str, job_role: str) -> dict[str, Any]:
    from utils.roles import JOB_ROLES, normalize_job_role

    username = (username or "").strip()
    if not username or not password:
        raise ValueError("Username and password are required.")
    if job_role not in JOB_ROLES:
        raise ValueError("Invalid job role.")
    init_db()
    with _LOCK, connect() as conn:
        exists = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if exists:
            raise ValueError("Username already exists.")
        user_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO users (id, username, password_hash, job_role, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, hash_password(password), normalize_job_role(job_role), _now()),
        )
        return {"id": user_id, "username": username, "job_role": job_role}


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    init_db()
    with _LOCK, connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            return None
        if not row["password_hash"].startswith("pbkdf2$"):
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(password), row["id"]))
        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, row["id"], _now()),
        )
        return {
            "token": token,
            "id": row["id"],
            "username": row["username"],
            "job_role": row["job_role"],
        }


def get_user_by_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    init_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username, u.job_role
            FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "username": row["username"], "job_role": row["job_role"]}


def revoke_token(token: str | None) -> None:
    if not token:
        return
    with _LOCK, connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def save_document(
    user_id: str,
    filename: str,
    content: bytes,
    extracted_text: str,
    metadata: dict[str, Any],
    project_id: str | None = None,
    mime: str = "",
) -> dict[str, Any]:
    init_db()
    content_hash = hashlib.sha256(content).hexdigest()
    with _LOCK, connect() as conn:
        existing = conn.execute(
            "SELECT * FROM documents WHERE user_id = ? AND content_hash = ?",
            (user_id, content_hash),
        ).fetchone()
        if existing:
            return _doc_row(existing, duplicate=True)
        doc_id = str(uuid.uuid4())
        dest_dir = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{doc_id}_{os.path.basename(filename)}")
        with open(dest, "wb") as f:
            f.write(content)
        meta = dict(metadata or {})
        meta["storage_path"] = dest
        conn.execute(
            """
            INSERT INTO documents
            (id, user_id, project_id, filename, content_hash, mime, size_bytes, extracted_text, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                user_id,
                project_id,
                filename,
                content_hash,
                mime,
                len(content),
                extracted_text,
                json.dumps(meta),
                _now(),
            ),
        )
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return _doc_row(row, duplicate=False)


def list_documents(user_id: str) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [_doc_row(r) for r in rows]


def get_document(user_id: str, doc_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id),
        ).fetchone()
        return _doc_row(row) if row else None


def delete_document(user_id: str, doc_id: str) -> bool:
    with _LOCK, connect() as conn:
        row = conn.execute(
            "SELECT metadata_json FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id),
        ).fetchone()
        if not row:
            return False
        try:
            path = json.loads(row["metadata_json"] or "{}").get("storage_path")
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        conn.execute("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        return True


def documents_as_text_map(user_id: str) -> dict[str, str]:
    docs = list_documents(user_id)
    out: dict[str, str] = {}
    for d in docs:
        name = d["filename"]
        if name in out:
            name = f"{d['id'][:8]}_{name}"
        out[name] = d.get("extracted_text") or ""
    return out


def _doc_row(row: sqlite3.Row, duplicate: bool = False) -> dict[str, Any]:
    meta = {}
    try:
        meta = json.loads(row["metadata_json"] or "{}")
    except Exception:
        meta = {}
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "project_id": row["project_id"],
        "filename": row["filename"],
        "content_hash": row["content_hash"],
        "mime": row["mime"],
        "size_bytes": row["size_bytes"],
        "extracted_text": row["extracted_text"],
        "metadata": meta,
        "created_at": row["created_at"],
        "duplicate": duplicate,
    }


def create_conversation(user_id: str, title: str = "New chat") -> dict[str, Any]:
    init_db()
    cid = str(uuid.uuid4())
    ts = _now()
    with _LOCK, connect() as conn:
        conn.execute(
            "INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (cid, user_id, title or "New chat", ts, ts),
        )
    return {"id": cid, "user_id": user_id, "title": title or "New chat", "created_at": ts, "updated_at": ts}


def list_conversations(user_id: str) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_conversation(user_id: str, conversation_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        ).fetchone()
        return dict(row) if row else None


def delete_conversation(user_id: str, conversation_id: str) -> bool:
    with _LOCK, connect() as conn:
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id),
        ).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM messages WHERE conversation_id = ? AND user_id = ?", (conversation_id, user_id))
        conn.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id))
        return True


def add_message(
    user_id: str,
    conversation_id: str,
    role: str,
    content: str,
    sources: list[Any] | None = None,
) -> dict[str, Any]:
    conv = get_conversation(user_id, conversation_id)
    if not conv:
        raise PermissionError("Conversation not found.")
    mid = str(uuid.uuid4())
    ts = _now()
    with _LOCK, connect() as conn:
        conn.execute(
            """
            INSERT INTO messages (id, conversation_id, user_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (mid, conversation_id, user_id, role, content, json.dumps(sources or []), ts),
        )
        title = conv["title"]
        if title == "New chat" and role == "user":
            title = (content or "New chat").strip().splitlines()[0][:72] or "New chat"
        conn.execute(
            "UPDATE conversations SET updated_at = ?, title = ? WHERE id = ? AND user_id = ?",
            (ts, title, conversation_id, user_id),
        )
    return {"id": mid, "role": role, "content": content, "sources": sources or [], "created_at": ts}


def list_messages(user_id: str, conversation_id: str) -> list[dict[str, Any]]:
    if not get_conversation(user_id, conversation_id):
        return []
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? AND user_id = ? ORDER BY created_at ASC",
            (conversation_id, user_id),
        ).fetchall()
        out = []
        for r in rows:
            try:
                sources = json.loads(r["sources_json"] or "[]")
            except Exception:
                sources = []
            out.append(
                {
                    "id": r["id"],
                    "role": r["role"],
                    "content": r["content"],
                    "sources": sources,
                    "created_at": r["created_at"],
                }
            )
        return out


def get_user_workspace(user_id: str) -> str | None:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT last_workspace FROM users WHERE id = ?", (user_id,)).fetchone()
        if row and row["last_workspace"]:
            return row["last_workspace"]
        return None


def set_user_workspace(user_id: str, workspace: str) -> None:
    init_db()
    with _LOCK, connect() as conn:
        conn.execute("UPDATE users SET last_workspace = ? WHERE id = ?", (workspace, user_id))

