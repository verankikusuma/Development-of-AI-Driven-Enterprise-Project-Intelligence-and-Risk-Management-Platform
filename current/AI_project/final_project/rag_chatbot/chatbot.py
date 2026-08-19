"""
chatbot.py — High-impact LLM answer generation for the project RAG assistant.

Accepts pre-retrieved context chunks and generates a structured, executive-ready answer
using the Gemini LLM or fast local fallback.
"""

from google import genai
import os
from utils.local_ai import local_answer

from . import config

_client = None

SYSTEM_INSTRUCTION = (
    "You are an elite AI Project Intelligence Advisor powered by Gemini. Generate a thorough, comprehensive, "
    "highly detailed, real, authentic, and context-aware executive intelligence response strictly grounded in the provided "
    "project document excerpts and conversation history.\n\n"
    "RESPONSE INSTRUCTIONS:\n"
    "1. Directly answer the user's question with deep narrative analysis and comprehensive detail derived strictly from the document excerpts.\n"
    "2. Provide complete explanations, data tables, bulleted lists, and strategic insights for specific queries (e.g. budget, timeline, risks, deliverables, vendors).\n"
    "3. Keep the tone academic, objective, executive-ready, and professional. Avoid decorative emojis or superficial placeholders.\n"
    "4. CITATION STYLE: Keep the main body clean, polished, and readable. Do NOT insert inline source tags like '[Source: ...]' after every sentence or line. If helpful, you may include a single small, subtle citation line at the very end (e.g., '*Source Document: filename.pdf*').\n"
    "5. Synthesize context-aware insights across conversation turns when answering follow-up questions."
)


def _is_greeting(question: str) -> bool:
    q = question.strip().lower()
    greetings = {
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", 
        "who are you", "what can you do", "help", "thanks", "thank you", "hi there", "hello there"
    }
    return q in greetings or q.startswith(("hi ", "hello ", "hey "))


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


def _build_prompt(question: str, context: str, history: list[dict] = None) -> str:
    history_str = ""
    if history:
        recent = [m for m in history if m.get("content")][-6:]
        if recent:
            lines = []
            for m in recent:
                role = "User" if m.get("role") == "user" else "Advisor"
                lines.append(f"{role}: {m.get('content')}")
            history_str = "Recent Conversation History:\n" + "\n".join(lines) + "\n\n"

    return (
        f"{history_str}"
        f"Project document excerpts:\n{'-' * 40}\n{context}\n{'-' * 40}\n\n"
        f"User Question: {question}\n\n"
        f"Provide a clear, accurate, thorough, context-aware answer strictly based on the excerpts and conversation history above."
    )


def answer_with_context(question: str, chunks: list[dict], history: list[dict] = None) -> dict:
    """
    Generate a structured, real, authentic answer using Gemini LLM given pre-retrieved chunks and conversation history.
    """
    if _is_greeting(question):
        doc_name = chunks[0]["filename"] if chunks else "your project dossier"
        return {
            "answer": (
                f"### Welcome to Project Intelligence AI Advisor\n\n"
                f"Hello! I am your AI Project Advisor powered by Gemini, fully grounded in **{doc_name}**.\n\n"
                f"I can help you analyze:\n"
                f"* **Financials & Costs:** Capital allocations, budget variances, and spending.\n"
                f"* **Schedule & Milestones:** Sprint dates, delivery targets, and project delays.\n"
                f"* **Risk & Mitigation:** Identified threat vectors, severities, and governance controls.\n"
                f"* **Scope & Stakeholders:** Core deliverables, microservices, and vendor SLAs.\n\n"
                f"What would you like to explore regarding your project today?"
            ),
            "sources": sorted({c["filename"] for c in chunks}) if chunks else [],
        }

    if not chunks:
        return {
            "answer": (
                "### No Document Context Found\n\n"
                "> **Key Finding:** No relevant document excerpts located.\n\n"
                "I couldn't locate relevant sections in your uploaded documents to answer this question confidently. "
                "Please make sure you have uploaded and processed a project document."
            ),
            "sources": [],
        }

    use_cloud = os.environ.get("USE_CLOUD_AI", "true").lower() in ("true", "1", "yes")
    if not use_cloud or not config.GEMINI_API_KEY:
        return local_answer(question, chunks, history=history)

    context = _build_context(chunks)
    prompt = _build_prompt(question, context, history=history)

    # Candidate Gemini models for robust fallback execution
    candidate_models = [
        config.GEMINI_LLM_MODEL,
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash"
    ]
    # Remove duplicates preserving order
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    client = _get_client()
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"system_instruction": SYSTEM_INSTRUCTION}
            )
            if response and response.text:
                return {
                    "answer": response.text,
                    "sources": sorted({c["filename"] for c in chunks}),
                }
        except Exception as exc:
            last_error = exc
            continue

    # Fallback to local answer generator if all Gemini cloud models failed
    return local_answer(question, chunks, history=history)



