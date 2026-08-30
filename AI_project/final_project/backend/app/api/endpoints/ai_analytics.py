"""
ai_analytics.py — FastAPI endpoints for ML predictions, document parsing, RAG queries, scenario simulations, and document generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from utils.predictor import predict_it_risk as local_predict_it
from utils.predictor import predict_non_it_risk as local_predict_non_it
from utils.local_ai import parse_project_locally, local_answer, generate_local_document
from utils.llm_parser import parse_document_with_gemini, parse_batch_with_gemini
from utils.dataset_analyzer import get_dataset_metadata
from utils.roles import can_access_page, filter_chunks_for_role
from app.api.deps import get_current_user

router = APIRouter()


class PredictionRequest(BaseModel):
    features: Dict[str, Any]


class DocumentParseRequest(BaseModel):
    document_text: str
    is_csv: Optional[bool] = False
    project_kind: Optional[str] = "IT"


class ScenarioSimulationRequest(BaseModel):
    baseline_score: float
    delay_days: Optional[int] = 0
    budget_change_percent: Optional[float] = 0.0
    team_reduction_percent: Optional[float] = 0.0


class RAGQueryRequest(BaseModel):
    question: str
    chunks: List[Dict[str, Any]]
    chat_history: Optional[List[Dict[str, Any]]] = None
    project: Optional[Dict[str, Any]] = None
    prediction: Optional[Dict[str, Any]] = None


class DocumentGenerateRequest(BaseModel):
    project_data: Dict[str, Any]
    document_type: str
    audience: Optional[str] = "IT"


def _require_page(user: dict, page_key: str) -> None:
    if not can_access_page(user["job_role"], page_key):
        raise HTTPException(status_code=403, detail=f"Role {user['job_role']} cannot access {page_key}")


@router.post("/predict/it")
@router.post("/v1/predict/it")
def predict_it_endpoint(req: PredictionRequest, user=Depends(get_current_user)):
    _require_page(user, "risk")
    try:
        return local_predict_it(req.features, skip_api=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IT prediction error: {str(e)}")


@router.post("/predict/non-it")
@router.post("/v1/predict/non-it")
def predict_non_it_endpoint(req: PredictionRequest, user=Depends(get_current_user)):
    _require_page(user, "risk")
    try:
        return local_predict_non_it(req.features, skip_api=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Non-IT prediction error: {str(e)}")


@router.post("/parse/document")
@router.post("/v1/parse/document")
def parse_document_endpoint(req: DocumentParseRequest, user=Depends(get_current_user)):
    _require_page(user, "upload")
    try:
        if req.is_csv:
            return parse_batch_with_gemini(req.document_text, req.project_kind or "IT")
        return parse_document_with_gemini(req.document_text, req.project_kind or "IT")
    except Exception:
        return parse_project_locally(req.document_text, req.project_kind or "IT")


@router.post("/scenario/simulate")
@router.post("/v1/scenario/simulate")
def simulate_scenario_endpoint(req: ScenarioSimulationRequest, user=Depends(get_current_user)):
    _require_page(user, "what_if")
    score = float(req.baseline_score)
    score = score + (req.delay_days or 0) * 0.35
    score = score + (req.budget_change_percent or 0) * 0.2
    score = score + (req.team_reduction_percent or 0) * 0.25
    score = max(0.0, min(100.0, score))
    return {"baseline_score": req.baseline_score, "simulated_score": round(score, 1)}


@router.post("/rag/query", tags=["AI Analytics API"])
@router.post("/v1/rag/query", tags=["AI Analytics API"])
def rag_query_endpoint(req: RAGQueryRequest, user=Depends(get_current_user)):
    """RAG Chatbot Answer Generation API Endpoint. Role-filters retrieved chunks."""
    _require_page(user, "ragbot")
    chunks = filter_chunks_for_role(req.chunks or [], user["job_role"])
    try:
        from rag_chatbot.chatbot import answer_with_context
        res = answer_with_context(
            req.question,
            chunks,
            history=req.chat_history,
            project=req.project,
            prediction=req.prediction,
        )
        return res
    except Exception:
        res = local_answer(req.question, chunks, history=req.chat_history)
        return res


@router.post("/generate/document", tags=["AI Analytics API"])
@router.post("/v1/generate/document", tags=["AI Analytics API"])
def generate_document_endpoint(req: DocumentGenerateRequest, user=Depends(get_current_user)):
    _require_page(user, "documentation")
    try:
        doc = generate_local_document(req.project_data, req.document_type, req.audience or "IT")
        return {"document_type": req.document_type, "content": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation error: {str(e)}")


@router.get("/dataset/telemetry", tags=["AI Analytics API"])
@router.get("/v1/dataset/telemetry", tags=["AI Analytics API"])
def dataset_telemetry_endpoint(user=Depends(get_current_user)):
    _require_page(user, "analysis")
    try:
        return get_dataset_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry error: {str(e)}")
