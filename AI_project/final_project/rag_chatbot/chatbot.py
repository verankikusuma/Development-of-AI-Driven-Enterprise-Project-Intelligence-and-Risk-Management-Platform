"""
chatbot.py — High-impact LLM answer generation for the project RAG assistant.

Accepts pre-retrieved context chunks and generates a structured, executive-ready answer
using the Gemini LLM or fast local fallback.
"""

from google import genai
import os
from utils.local_ai import local_answer

from . import config
from .grounding import (
    MISSING_INFO_ANSWER,
    OUT_OF_SCOPE_ANSWER,
    SYSTEM_INSTRUCTION,
    build_sources,
    classify_question,
    format_ml_context,
    is_greeting,
)

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        config.validate_config()
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(
            f"[Source {i}: {c['filename']}, Section {c['chunk_index']}]\n{c['text']}"
        )
    return "\n\n".join(blocks)


def _build_prompt(question: str, context: str, history: list[dict] = None, ml_context: str = "") -> str:
    history_str = ""
    if history:
        recent = [m for m in history if m.get("content")][-8:]
        if recent:
            lines = []
            for m in recent:
                role = "User" if m.get("role") == "user" else "Advisor"
                lines.append(f"{role}: {m.get('content')}")
            history_str = "Recent Conversation History:\n" + "\n".join(lines) + "\n\n"

    ml_block = f"System / ML context:\n{ml_context}\n\n" if ml_context else ""
    return (
        f"{history_str}"
        f"{ml_block}"
        f"Project document excerpts (may come from multiple files):\n{'-' * 40}\n{context}\n{'-' * 40}\n\n"
        f"User Question: {question}\n\n"
        f"Answer only from the excerpts, conversation history, and labeled ML/system context. "
        f"If those sources do not contain the answer, say you could not find it."
    )


def answer_with_context(
    question: str,
    chunks: list[dict],
    history: list[dict] = None,
    project: dict = None,
    prediction: dict = None,
) -> dict:
    """
    Generate a grounded answer from retrieved chunks, optional ML forecast, and conversation history.
    Does not retrain or replace the XGBoost forecasting pipeline.
    """
    kind = classify_question(question, history)
    if kind == "greeting" or is_greeting(question):
        return {
            "answer": (
                "Hello. I answer from your uploaded project documents, stored project data, "
                "and the existing XGBoost risk forecast when available. "
                "Ask about risks, documents, predictions, or project information."
            ),
            "sources": [],
            "source_details": [],
            "question_kind": kind,
        }

    ml_context = format_ml_context(prediction, project)
    used_ml = bool(ml_context) and any(
        w in (question or "").lower()
        for w in ("predict", "forecast", "classif", "xgboost", "confidence", "contribut", "why", "risk level", "probability")
    )
    if kind == "unrelated" and not used_ml:
        return {
            "answer": OUT_OF_SCOPE_ANSWER,
            "sources": [],
            "source_details": [],
            "question_kind": kind,
        }

    if not chunks and not ml_context:
        return {
            "answer": "This question doesn't appear to be covered by the uploaded document(s). Please rephrase your question, or ask about risks, project details, or other available information.",
            "sources": [],
            "source_details": [],
            "question_kind": kind,
        }

    if not chunks and ml_context and not used_ml and kind != "related":
        return {
            "answer": "This question doesn't appear to be covered by the uploaded document(s). Please rephrase your question, or ask about risks, project details, or other available information.",
            "sources": [],
            "source_details": [],
            "question_kind": kind,
        }

    source_details = build_sources(chunks, used_ml=bool(ml_context and (used_ml or kind == "related")))
    filenames = [s["filename"] for s in source_details if s.get("type") == "document"]

    def _pack(answer: str) -> dict:
        return {
            "answer": answer,
            "sources": filenames,
            "source_details": source_details,
            "question_kind": kind,
        }

    use_cloud = os.environ.get("USE_CLOUD_AI", "true").lower() in ("true", "1", "yes")
    context = _build_context(chunks) if chunks else "(no document excerpts retrieved)"
    prompt = _build_prompt(question, context, history=history, ml_context=ml_context)

    if not use_cloud or not config.GEMINI_API_KEY:
        if not chunks:
            if ml_context and used_ml:
                return _pack(
                    "**ML Prediction**\n\n"
                    + ml_context
                    + "\n\n**AI Recommendation**\n\nThis explanation uses the stored XGBoost forecast only. "
                    "No matching document excerpts were retrieved."
                )
            return _pack(MISSING_INFO_ANSWER)
        local = local_answer(question, chunks, history=history)
        local["source_details"] = source_details
        local["question_kind"] = kind
        return local

    candidate_models = [
        config.GEMINI_LLM_MODEL,
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash"
    ]
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    client = _get_client()
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"system_instruction": SYSTEM_INSTRUCTION}
            )
            if response and response.text:
                return _pack(response.text)
        except Exception:
            continue

    if not chunks:
        return _pack(MISSING_INFO_ANSWER if not (ml_context and used_ml) else ml_context)
    local = local_answer(question, chunks, history=history)
    local["source_details"] = source_details
    local["question_kind"] = kind
    return local




