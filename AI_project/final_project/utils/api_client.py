import requests


def _url(base_url, path):
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def api_get(path, base_url="http://127.0.0.1:8000", timeout=20):
    try:
        r = requests.get(_url(base_url, path), timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"_error": str(e), "status_code": getattr(e.response, "status_code", None)}
    except ValueError as e:
        return {"_error": f"Invalid JSON response: {e}"}


def api_post(path, base_url="http://127.0.0.1:8000", payload=None, timeout=45, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Auth-Token"] = token
        r = requests.post(_url(base_url, path), json=payload, timeout=timeout, headers=headers or None)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        detail = None
        if getattr(e, "response", None) is not None:
            try:
                detail = e.response.json().get("detail")
            except Exception:
                detail = e.response.text
        return {"_error": detail or str(e), "status_code": getattr(e.response, "status_code", None)}
    except ValueError as e:
        return {"_error": f"Invalid JSON response: {e}"}


def backend_health(base_url="http://127.0.0.1:8000"):
    try:
        r = requests.get(_url(base_url, "/health"), timeout=0.3)
        return r.ok
    except requests.RequestException:
        return False


# ============================================================
# API CLIENT METHODS FOR FRONTEND-BACKEND COMMUNICATION
# ============================================================

def _auth_token():
    try:
        import streamlit as st
        return st.session_state.get("auth_token")
    except Exception:
        return None


def api_predict_it_risk(features: dict, base_url="http://127.0.0.1:8000"):
    """Call backend API for IT Risk Prediction."""
    token = _auth_token()
    res = api_post("/api/v1/predict/it", base_url=base_url, payload={"features": features}, token=token)
    if "_error" in res:
        res = api_post("/api/predict/it", base_url=base_url, payload={"features": features}, token=token)
    if "_error" in res:
        return None
    return res


def api_predict_non_it_risk(features: dict, base_url="http://127.0.0.1:8000"):
    """Call backend API for Non-IT Risk Prediction."""
    token = _auth_token()
    payload = {"features": features}
    res = api_post("/api/v1/predict/non-it", base_url=base_url, payload=payload, token=token)
    if "_error" in res:
        res = api_post("/api/predict/non-it", base_url=base_url, payload=payload, token=token)
    if "_error" in res:
        return None
    return res


def api_parse_document(document_text: str, is_csv: bool = False, project_kind: str = "IT", base_url="http://127.0.0.1:8000"):
    """Call backend API for autonomous document signal parsing."""
    payload = {
        "document_text": document_text,
        "is_csv": is_csv,
        "project_kind": project_kind
    }
    res = api_post("/api/v1/parse/document", base_url=base_url, payload=payload, timeout=60, token=_auth_token())
    if "_error" in res:
        res = api_post("/api/parse/document", base_url=base_url, payload=payload, timeout=60, token=_auth_token())
    if "_error" in res:
        return None
    return res


def api_simulate_scenario(baseline_score: float, delay_days: int = 0, budget_change_pct: float = 0.0, team_reduction_pct: float = 0.0, base_url="http://127.0.0.1:8000"):
    """Call backend API for What-If scenario risk simulation."""
    payload = {
        "baseline_score": float(baseline_score),
        "delay_days": int(delay_days),
        "budget_change_percent": float(budget_change_pct),
        "team_reduction_percent": float(team_reduction_pct)
    }
    res = api_post("/api/v1/scenario/simulate", base_url=base_url, payload=payload, token=_auth_token())
    if "_error" in res:
        res = api_post("/api/scenario/simulate", base_url=base_url, payload=payload, token=_auth_token())
    if "_error" in res:
        return None
    return res


def api_query_rag(question: str, chunks: list, chat_history: list = None, base_url="http://127.0.0.1:8000", project=None, prediction=None):
    """Call backend API for RAG chatbot answer generation."""
    payload = {
        "question": question,
        "chunks": chunks,
        "chat_history": chat_history,
        "project": project,
        "prediction": prediction,
    }
    res = api_post("/api/v1/rag/query", base_url=base_url, payload=payload, timeout=40, token=_auth_token())
    if "_error" in res:
        res = api_post("/api/rag/query", base_url=base_url, payload=payload, timeout=40, token=_auth_token())
    if "_error" in res:
        return None
    return res


def api_generate_document(project_data: dict, document_type: str, audience: str = "IT", base_url="http://127.0.0.1:8000"):
    """Call backend API for AI Document Generation."""
    payload = {
        "project_data": project_data,
        "document_type": document_type,
        "audience": audience
    }
    res = api_post("/api/v1/generate/document", base_url=base_url, payload=payload, timeout=40, token=_auth_token())
    if "_error" in res:
        res = api_post("/api/generate/document", base_url=base_url, payload=payload, timeout=40, token=_auth_token())
    if "_error" in res:
        return None
    return res.get("content")
