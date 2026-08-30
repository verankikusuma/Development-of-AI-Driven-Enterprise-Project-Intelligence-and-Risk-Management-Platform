"""Grounding, out-of-scope detection, and source typing for the RAG assistant."""

from __future__ import annotations

import re
from typing import Any

OUT_OF_SCOPE_ANSWER = (
    "This question is outside the available project knowledge base. "
    "I can answer questions related to the project, uploaded documents, "
    "project risks, predictions, and available project information."
)

MISSING_INFO_ANSWER = (
    "I couldn't find this information in the available project knowledge."
)

PROJECT_HINTS = (
    "project", "risk", "budget", "schedule", "milestone", "deadline", "vendor",
    "stakeholder", "requirement", "deliverable", "scope", "sprint", "defect",
    "bug", "test", "deploy", "devops", "api", "database", "model", "xgboost",
    "prediction", "forecast", "document", "task", "dependency", "resource",
    "team", "architecture", "security", "compliance", "upload", "rag",
    "why", "who", "what", "how", "when", "where", "this", "that", "it",
)

UNRELATED_HINTS = (
    "capital of", "weather", "recipe", "movie", "sports score", "celebrity",
    "who won the", "write a poem", "joke", "stock ticker",
)

GREETINGS = {
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "who are you", "what can you do", "help", "thanks", "thank you",
}


SYSTEM_INSTRUCTION = """You are the project intelligence assistant for an AI-Based Project Risk Forecasting System.

GROUNDING RULES (mandatory):
1. Never invent project information, employee names, risk values, document content, or citations.
2. Never claim information came from a document unless that document is in the provided excerpts.
3. Never present an assumption as a project fact.
4. If the excerpts and system data do not contain the answer, say exactly:
   "I couldn't find this information in the available project knowledge."
5. If the question is unrelated to this project, documents, risks, predictions, or system data, say:
   "This question is outside the available project knowledge base. I can answer questions related to the project, uploaded documents, project risks, predictions, and available project information."
6. If a question is partly related, answer only the supported project-related part and state which part is unsupported.
7. Use conversation history so follow-ups like "Why?" refer to the previous topic. Do not invent the previous topic.
8. Keep ML forecasting separate from document RAG. Clearly label sections:
   **Document Information**
   **Project/System Data**
   **ML Prediction**
   **AI Recommendation**
   Only include a section if you actually used that source type.
9. When using documents, list sources as filename plus section/chunk hint. Never fabricate a section name.
10. Graph/chart numbers marked value_kind=estimated or interpretation must be labeled as estimated or interpretation, not exact facts.
11. Do not pad answers with generic project-management advice that is not in the sources.
"""


def is_greeting(question: str) -> bool:
    q = (question or "").strip().lower()
    return q in GREETINGS or q.startswith(("hi ", "hello ", "hey "))


def classify_question(question: str, history: list[dict] | None = None) -> str:
    q = (question or "").strip().lower()
    if not q:
        return "unrelated"
    if is_greeting(q):
        return "greeting"
    if any(h in q for h in UNRELATED_HINTS):
        # mixed?
        if any(h in q for h in PROJECT_HINTS):
            return "partial"
        return "unrelated"
    trivia = re.search(r"\b(capital of|population of|who is the president)\b", q)
    if trivia and not any(h in q for h in ("project", "risk", "document", "budget")):
        return "unrelated"
    short_followup = len(q.split()) <= 6
    if short_followup and history:
        return "related"
    if any(h in q for h in PROJECT_HINTS):
        return "related"
    if history:
        return "related"
    return "unrelated"


def format_ml_context(prediction: dict | None, project: dict | None) -> str:
    if not prediction and not project:
        return ""
    lines = ["[Source Type: ML Prediction / Project System Data]"]
    if project:
        lines.append(f"Project name: {project.get('name', 'Unknown')}")
        if project.get("risk_level"):
            lines.append(f"Stored risk level: {project.get('risk_level')}")
        if project.get("risk_score") is not None:
            lines.append(f"Stored risk score: {project.get('risk_score')}")
        feats = project.get("features") or {}
        if feats:
            lines.append("Planning-stage attributes used by the forecasting model (not document RAG):")
            for k, v in list(feats.items())[:19]:
                lines.append(f"- {k}: {v}")
    if prediction:
        lines.append(f"Predicted class: {prediction.get('risk_level')}")
        if prediction.get("confidence") is not None:
            lines.append(f"Confidence: {prediction.get('confidence')}")
        if prediction.get("probabilities"):
            lines.append(f"Probability distribution: {prediction.get('probabilities')}")
        factors = prediction.get("contributing_factors") or []
        if factors:
            lines.append("Contributing factors:")
            for f in factors[:8]:
                if isinstance(f, dict):
                    lines.append(f"- {f.get('name', f.get('feature', ''))}: {f.get('impact', f.get('contribution', ''))}")
                else:
                    lines.append(f"- {f}")
        lines.append(
            "Note: This forecast comes from the existing XGBoost pipeline on planning-stage features, "
            "not from uploaded document text."
        )
    return "\n".join(lines)


def build_sources(chunks: list[dict], used_ml: bool) -> list[dict[str, Any]]:
    seen = []
    names = set()
    for c in chunks:
        fn = c.get("filename", "document")
        section = c.get("section") or f"chunk {c.get('chunk_index', 0)}"
        key = (fn, section)
        if key in names:
            continue
        names.add(key)
        seen.append(
            {
                "type": "document",
                "filename": fn,
                "section": section,
                "label": f"{fn} — {section}",
            }
        )
    if used_ml:
        seen.append(
            {
                "type": "ml_prediction",
                "filename": "XGBoost Risk Forecast",
                "section": "model output",
                "label": "ML Prediction — XGBoost risk forecast (planning-stage features)",
            }
        )
    return seen
