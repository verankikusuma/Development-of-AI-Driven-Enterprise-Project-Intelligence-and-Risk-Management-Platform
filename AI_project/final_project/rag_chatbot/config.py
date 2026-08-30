import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    val = os.environ.get(key, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


# --- Gemini ---
GEMINI_API_KEY = _get("GEMINI_API_KEY", "")
GEMINI_LLM_MODEL = _get("GEMINI_LLM_MODEL", "gemini-3.5-flash")
GEMINI_EMBEDDING_MODEL = _get("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIM = 768

# --- Chunking ---
CHUNK_SIZE = int(_get("RAG_CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(_get("RAG_CHUNK_OVERLAP", "150"))
ROWS_PER_CHUNK = int(_get("RAG_ROWS_PER_CHUNK", "15"))
MAX_CHUNKS_PER_FILE = int(_get("RAG_MAX_CHUNKS_PER_FILE", "1000"))

# --- Retrieval ---
TOP_K = int(_get("RAG_TOP_K", "5"))

# Only Gemini API key is strictly required now.
# Qdrant keys are kept for backward compat but not validated.
REQUIRED_VARS = {
    "GEMINI_API_KEY": GEMINI_API_KEY,
}


def validate_config():
    missing = [k for k, v in REQUIRED_VARS.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Set GEMINI_API_KEY in your .env file before using the AI assistant."
        )