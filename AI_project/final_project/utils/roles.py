"""Job-role definitions, workspace routing, and authorization scopes.

Roles are employee job functions stored on the user account. They cannot be
changed at login. Authorization is enforced by page key and API scope.
"""

from __future__ import annotations

from typing import Any

# Canonical job roles (stored on the user record)
JOB_ROLES = [
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "ML/AI Developer",
    "Data Engineer",
    "UI/UX Designer",
    "Tester / QA Engineer",
    "DevOps Engineer",
    "Cybersecurity Engineer",
    "Database Administrator",
    "Project Manager",
    "Team Lead",
    "Business Analyst",
    "Management",
]

PAGE_KEYS = [
    "upload",
    "dashboard",
    "analysis",
    "risk",
    "schedule",
    "dependencies",
    "what_if",
    "documentation",
    "ragbot",
]

ALL_PAGES = set(PAGE_KEYS)

# Knowledge scopes used to filter RAG chunks and dashboard panels
ROLE_SCOPES: dict[str, dict[str, Any]] = {
    "Backend Developer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "risk", "dependencies", "documentation", "ragbot"},
        "knowledge": {"backend", "api", "database", "server", "integration"},
        "dashboard_focus": "backend",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Frontend Developer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "risk", "documentation", "ragbot"},
        "knowledge": {"frontend", "ui", "ux", "integration", "client"},
        "dashboard_focus": "frontend",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Full Stack Developer": {
        "workspace": "IT",
        "pages": ALL_PAGES - {"what_if"},
        "knowledge": {"backend", "frontend", "api", "database", "integration", "ui"},
        "dashboard_focus": "fullstack",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "ML/AI Developer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "risk", "documentation", "ragbot"},
        "knowledge": {"ml", "ai", "model", "data-quality", "prediction"},
        "dashboard_focus": "ml",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": True,
        "can_see_management_reports": False,
    },
    "Data Engineer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "documentation", "ragbot"},
        "knowledge": {"data", "pipeline", "database", "csv", "quality"},
        "dashboard_focus": "data",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "UI/UX Designer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "documentation", "ragbot"},
        "knowledge": {"ui", "ux", "frontend", "design"},
        "dashboard_focus": "ux",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Tester / QA Engineer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "risk", "documentation", "ragbot"},
        "knowledge": {"qa", "testing", "defect", "bug", "quality"},
        "dashboard_focus": "qa",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "DevOps Engineer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "schedule", "dependencies", "what_if", "documentation", "ragbot"},
        "knowledge": {"devops", "deploy", "infrastructure", "cicd", "server"},
        "dashboard_focus": "devops",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Cybersecurity Engineer": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "risk", "documentation", "ragbot"},
        "knowledge": {"security", "cyber", "compliance", "vulnerability"},
        "dashboard_focus": "security",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Database Administrator": {
        "workspace": "IT",
        "pages": {"upload", "dashboard", "analysis", "risk", "documentation", "ragbot"},
        "knowledge": {"database", "backend", "data"},
        "dashboard_focus": "database",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Project Manager": {
        "workspace": "BOTH",
        "pages": ALL_PAGES,
        "knowledge": {"all"},
        "dashboard_focus": "pm",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": True,
        "can_see_management_reports": True,
    },
    "Team Lead": {
        "workspace": "BOTH",
        "pages": ALL_PAGES,
        "knowledge": {"all"},
        "dashboard_focus": "lead",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": True,
        "can_see_management_reports": True,
    },
    "Business Analyst": {
        "workspace": "NON_IT",
        "pages": {"upload", "dashboard", "analysis", "documentation", "ragbot"},
        "knowledge": {"requirements", "scope", "business", "process"},
        "dashboard_focus": "ba",
        "can_delete_docs": True,
        "can_delete_chats": True,
        "can_see_ml_full": False,
        "can_see_management_reports": False,
    },
    "Management": {
        "workspace": "BOTH",
        "pages": {"upload", "dashboard", "risk", "documentation", "ragbot"},
        "knowledge": {"all"},
        "dashboard_focus": "management",
        "can_delete_docs": False,
        "can_delete_chats": True,
        "can_see_ml_full": True,
        "can_see_management_reports": True,
    },
}

LEGACY_ROLE_MAP = {
    "IT": "Full Stack Developer",
    "Non-IT": "Management",
    "NON_IT": "Management",
}

SCOPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "backend": ("backend", "api", "server", "endpoint", "service", "microservice", "auth"),
    "api": ("api", "endpoint", "rest", "graphql", "openapi"),
    "database": ("database", "sql", "schema", "postgres", "sqlite", "migration", "query"),
    "server": ("server", "latency", "throughput", "runtime"),
    "frontend": ("frontend", "ui", "react", "css", "browser", "client"),
    "ui": ("ui", "interface", "layout", "component", "screen"),
    "ux": ("ux", "usability", "wireframe", "prototype"),
    "integration": ("integration", "interface", "webhook", "sdk"),
    "ml": ("xgboost", "model", "classifier", "training", "feature", "accuracy"),
    "ai": ("ai", "llm", "rag", "embedding", "assistant"),
    "model": ("model", "prediction", "inference", "hold-out"),
    "data-quality": ("missing", "null", "quality", "schema", "outlier"),
    "prediction": ("prediction", "forecast", "risk level", "confidence"),
    "data": ("dataset", "pipeline", "etl", "warehouse"),
    "pipeline": ("pipeline", "etl", "ingest"),
    "csv": ("csv", "tabular", "spreadsheet"),
    "quality": ("quality", "defect", "coverage"),
    "qa": ("qa", "test", "uat", "regression", "defect"),
    "testing": ("test", "qa", "selenium", "pytest", "coverage"),
    "defect": ("bug", "defect", "issue", "failure"),
    "bug": ("bug", "defect", "ticket"),
    "devops": ("devops", "deploy", "kubernetes", "docker", "pipeline"),
    "deploy": ("deploy", "release", "production", "staging"),
    "infrastructure": ("infrastructure", "cloud", "aws", "azure", "network"),
    "cicd": ("ci/cd", "github actions", "jenkins", "pipeline"),
    "security": ("security", "cve", "auth", "encryption", "iam"),
    "cyber": ("cyber", "threat", "malware", "phishing"),
    "compliance": ("gdpr", "hipaa", "sox", "audit", "compliance"),
    "vulnerability": ("vulnerability", "cve", "patch"),
    "requirements": ("requirement", "user story", "acceptance"),
    "scope": ("scope", "deliverable", "charter"),
    "business": ("business", "stakeholder", "roi", "process"),
    "process": ("process", "workflow", "sop"),
    "client": ("client", "browser", "frontend"),
    "design": ("design", "figma", "wireframe"),
}


def normalize_job_role(role: str | None) -> str:
    if not role:
        return "Full Stack Developer"
    if role in ROLE_SCOPES:
        return role
    return LEGACY_ROLE_MAP.get(role, "Full Stack Developer")


def get_role_config(role: str | None) -> dict[str, Any]:
    return ROLE_SCOPES[normalize_job_role(role)]


def can_access_page(role: str | None, page_key: str) -> bool:
    return page_key in get_role_config(role)["pages"]


def default_workspace(role: str | None, selected: str | None = None) -> str:
    ws = get_role_config(role)["workspace"]
    if ws == "BOTH":
        if selected in ("IT", "NON_IT"):
            return selected
        return "IT"
    return ws


def role_may_choose_workspace(role: str | None) -> bool:
    return get_role_config(role)["workspace"] == "BOTH"


def allowed_knowledge_scopes(role: str | None) -> set[str]:
    scopes = set(get_role_config(role)["knowledge"])
    return scopes


def chunk_matches_role(text: str, filename: str, role: str | None) -> bool:
    """Return True if a chunk is in-scope for the role. 'all' sees everything."""
    scopes = allowed_knowledge_scopes(role)
    if "all" in scopes:
        return True
    hay = f"{filename} {text}".lower()
    for scope in scopes:
        keywords = SCOPE_KEYWORDS.get(scope, (scope,))
        if any(k in hay for k in keywords):
            return True
    # Always allow general project charter / overview material
    overview = ("project", "risk", "scope", "milestone", "budget", "schedule", "overview", "charter")
    return any(k in hay for k in overview)


def filter_chunks_for_role(chunks: list[dict], role: str | None) -> list[dict]:
    scoped = [c for c in chunks if chunk_matches_role(c.get("text", ""), c.get("filename", ""), role)]
    return scoped if scoped else chunks[: min(3, len(chunks))]
