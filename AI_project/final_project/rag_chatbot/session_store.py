"""
session_store.py — In-memory, session-scoped RAG engine.

Workflow:
  1. build_index(documents_dict)  — call once after document upload.
     Chunks all document text, embeds each chunk via Gemini, and stores
     the resulting vectors + metadata in st.session_state["rag_index"].

  2. retrieve(question, top_k)   — embed the question and return the
     top_k most similar chunks via cosine similarity.

  3. is_indexed()                — True if an index exists for this session.

No external vector database required. Works entirely in session memory.
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from . import config, embeddings

if TYPE_CHECKING:
    pass

# Key used inside st.session_state
_INDEX_KEY = "rag_index"


# ---------------------------------------------------------------------------
# Chunking helpers (standalone so this module has no import cycle)
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s for s in re.split(r"(?<=[.!?\n])\s+", text) if s.strip()]


def _chunk_text(text: str, chunk_size: int = config.CHUNK_SIZE,
                overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    sentences = _split_sentences(text)
    if not sentences:
        return []
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            overlap_text = current[-overlap:] if overlap and current else ""
            current = f"{overlap_text} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


def _chunk_csv(text: str, rows_per_chunk: int = config.ROWS_PER_CHUNK) -> list[str]:
    rows = [line for line in text.splitlines() if line.strip()]
    if not rows:
        return []
    return [
        "\n".join(rows[i: i + rows_per_chunk])
        for i in range(0, len(rows), rows_per_chunk)
    ]


# ---------------------------------------------------------------------------
# Cosine similarity (pure Python / math — no scipy/numpy needed)
# ---------------------------------------------------------------------------

def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_indexed() -> bool:
    """Return True if a RAG index is present in the current Streamlit session."""
    try:
        import streamlit as st
        index = st.session_state.get(_INDEX_KEY)
        return bool(index and index.get("chunks"))
    except Exception:
        return False


def build_index(documents: dict[str, str], progress_callback=None) -> int:
    """
    Build an in-memory RAG index from uploaded document texts.

    Parameters
    ----------
    documents : dict mapping filename -> full extracted text.
    progress_callback : optional callable(done, total) for Streamlit progress bars.

    Returns
    -------
    int — total number of chunks indexed.
    """
    import streamlit as st

    all_chunks: list[dict] = []

    for filename, text in documents.items():
        if not text or not text.strip():
            continue
        is_csv = filename.lower().endswith(".csv")
        pieces = _chunk_csv(text) if is_csv else _chunk_text(text)
        # respect MAX_CHUNKS_PER_FILE
        pieces = pieces[: config.MAX_CHUNKS_PER_FILE]
        for i, piece in enumerate(pieces):
            section = "table" if piece.strip().startswith("|") or "### Sheet:" in piece else f"section {i + 1}"
            all_chunks.append({
                "filename": filename,
                "chunk_index": i,
                "section": section,
                "text": piece,
                "vector": None,  # filled below
            })

    if not all_chunks:
        return 0

    # A lexical index is instant and works without a network connection. Cloud
    # embeddings are an optional enhancement, not an upload prerequisite.
    import os
    # A lexical index is instant and works without a network connection. Cloud
    # embeddings are an optional enhancement, not an upload prerequisite.
    import os
    use_cloud_embeddings = os.environ.get("USE_CLOUD_AI", "true").lower() in ("true", "1", "yes") and bool(config.GEMINI_API_KEY)
    if not use_cloud_embeddings:
        for chunk in all_chunks:
            chunk["terms"] = set(re.findall(r"[a-zA-Z]{3,}", chunk["text"].lower()))
        st.session_state[_INDEX_KEY] = {"chunks": all_chunks, "mode": "local"}
        return len(all_chunks)

    # Embed all chunk texts
    try:
        texts = [c["text"] for c in all_chunks]
        vectors = embeddings.embed_texts(
            texts,
            task_type="RETRIEVAL_DOCUMENT",
            progress_callback=progress_callback,
        )

        for chunk, vector in zip(all_chunks, vectors):
            chunk["vector"] = vector

        st.session_state[_INDEX_KEY] = {"chunks": all_chunks, "mode": "cloud"}
    except Exception:
        # Fall back to local mode if embedding API call fails
        for chunk in all_chunks:
            chunk["terms"] = set(re.findall(r"[a-zA-Z]{3,}", chunk["text"].lower()))
        st.session_state[_INDEX_KEY] = {"chunks": all_chunks, "mode": "local"}

    return len(all_chunks)


def retrieve(question: str, top_k: int = config.TOP_K, history: list[dict] = None, role: str = None) -> list[dict]:
    """
    Retrieve the top_k most relevant chunks for the given question and conversation context.

    Returns a list of dicts with keys: text, filename, chunk_index, score.
    """
    import streamlit as st

    index = st.session_state.get(_INDEX_KEY)
    if not index or not index.get("chunks"):
        return []

    chunks = index["chunks"]

    # Contextualize query if history contains recent user queries and current question is short/follow-up
    search_query = question
    if history:
        user_msgs = [m.get("content", "") for m in history if m.get("role") == "user" and m.get("content")]
        if user_msgs and (len(question.split()) < 5 or any(w in question.lower() for w in ("it", "that", "this", "why", "who", "they", "them", "more", "explain"))):
            search_query = f"{user_msgs[-1]} {question}"

    if index.get("mode") == "local":
        stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "of", "in", "to", "for", 
            "with", "on", "at", "by", "from", "up", "about", "into", "over", "after", "summarize", 
            "status", "what", "how", "why", "when", "where", "tell", "me", "show", "give", "list", 
            "does", "this", "that", "these", "those", "have", "has", "had", "project", "document", "can", "you", "please"
        }
        raw_words = re.findall(r"[a-zA-Z]{3,}", search_query.lower())
        keywords = [w for w in raw_words if w not in stopwords]
        if not keywords:
            keywords = raw_words
            
        high_priority = {"budget", "cost", "overrun", "schedule", "delay", "timeline", "risk", "vendor", "milestone", "sponsor", "team", "scope", "deliverable", "health", "variance", "financial"}
        
        scored = []
        for idx, chunk in enumerate(chunks):
            text_lower = chunk["text"].lower()
            score = 0.0
            for kw in keywords:
                count = text_lower.count(kw)
                weight = 3.0 if kw in high_priority else 1.5
                score += count * weight
            
            # Phrase bonus for matching full question or multiple keywords
            for kw in keywords:
                if kw in text_lower:
                    score += 0.5

            scored.append({
                "text": chunk["text"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "section": chunk.get("section", f"section {chunk['chunk_index'] + 1}"),
                "score": score,
                "orig_idx": idx
            })
            
        # Sort by score descending; fallback to original order for ties
        scored.sort(key=lambda item: (item["score"], -item["orig_idx"]), reverse=True)
        # Scope Gate: only return chunks with at least some term matches
        scored = [x for x in scored if x["score"] > 0]
        picked = _diversify_and_filter(scored, top_k, role)
        return picked

    config.validate_config()
    try:
        query_vector = embeddings.embed_query(search_query)

        scored = [
            {
                "text": c["text"],
                "filename": c["filename"],
                "chunk_index": c["chunk_index"],
                "section": c.get("section", f"section {c['chunk_index'] + 1}"),
                "score": _cosine(query_vector, c["vector"]),
            }
            for c in chunks
            if c.get("vector")
        ]
        # Scope Gate: Require a minimum cosine similarity threshold
        scored = [x for x in scored if x["score"] >= 0.35]
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return _diversify_and_filter(scored, top_k, role)
    except Exception:
        # Fallback to local term match if cloud query embedding fails
        raw_words = re.findall(r"[a-zA-Z]{3,}", search_query.lower())
        scored = []
        for c in chunks:
            text_lower = c["text"].lower()
            score = sum(text_lower.count(w) for w in raw_words)
            scored.append({
                "text": c["text"],
                "filename": c["filename"],
                "chunk_index": c["chunk_index"],
                "section": c.get("section", f"section {c['chunk_index'] + 1}"),
                "score": score,
            })
        
        # Scope Gate: must have at least one keyword match
        scored = [x for x in scored if x["score"] > 0]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return _diversify_and_filter(scored, top_k, role)


def _diversify_and_filter(scored: list[dict], top_k: int, role: str | None) -> list[dict]:
    from utils.roles import filter_chunks_for_role

    filtered = filter_chunks_for_role(scored, role)
    picked: list[dict] = []
    seen_files: set[str] = set()
    for item in filtered:
        fn = item.get("filename", "")
        if fn not in seen_files or len(picked) < max(2, top_k // 2):
            picked.append(item)
            seen_files.add(fn)
        if len(picked) >= top_k:
            break
    if len(picked) < top_k:
        for item in filtered:
            if item not in picked:
                picked.append(item)
            if len(picked) >= top_k:
                break
    return [
        {
            "text": s["text"],
            "filename": s["filename"],
            "chunk_index": s["chunk_index"],
            "section": s.get("section", f"section {s.get('chunk_index', 0) + 1}"),
            "score": s.get("score", 0),
        }
        for s in picked
    ]


def clear_index() -> None:
    """Remove the RAG index from the current session (e.g., on new upload)."""
    try:
        import streamlit as st
        st.session_state.pop(_INDEX_KEY, None)
    except Exception:
        pass
