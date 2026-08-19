# RAG Chatbot package
# Public API — use session_store for indexing and chatbot for answering.
from .session_store import build_index, retrieve, is_indexed, clear_index
from .chatbot import answer_with_context

__all__ = [
    "build_index",
    "retrieve",
    "is_indexed",
    "clear_index",
    "answer_with_context",
]
