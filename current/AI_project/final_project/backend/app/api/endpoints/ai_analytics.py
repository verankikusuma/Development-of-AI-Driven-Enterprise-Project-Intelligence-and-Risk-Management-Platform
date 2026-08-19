"""
ai_analytics.py — FastAPI endpoints for ML predictions, document parsing, RAG queries, scenario simulations, and document generation.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from utils.predictor import predict_it_risk as local_predict_it
from utils.predictor import predict_non_it_risk as local_predict_non_it
from utils.local_ai import parse_project_locally, local_answer, generate_local_document
from utils.llm_parser import parse_document_with_gemini, parse_batch_with_gemini
from utils.dataset_analyzer import get_dataset_metadata

router = APIRouter()

# Request schemas
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

class DocumentGenerateRequest(BaseModel):
    project_data: Dict[str, Any]
    document_type: str
    audience: Optional[str] = "IT"

# ... (keep other endpoints unchanged)

@router.post("/rag/query", tags=["AI Analytics API"])
def rag_query_endpoint(req: RAGQueryRequest):
    """RAG Chatbot Answer Generation API Endpoint."""
    try:
        from rag_chatbot.chatbot import answer_with_context
        res = answer_with_context(req.question, req.chunks, history=req.chat_history)
        return res
    except Exception as e:
        res = local_answer(req.question, req.chunks, history=req.chat_history)
        return res


@router.post("/generate/document", tags=["AI Analytics API"])
def generate_document_endpoint(req: DocumentGenerateRequest):
    """AI Document Generation API Endpoint."""
    try:
        doc = generate_local_document(req.project_data, req.document_type, req.audience or "IT")
        return {"document_type": req.document_type, "content": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation error: {str(e)}")


@router.get("/dataset/telemetry", tags=["AI Analytics API"])
def dataset_telemetry_endpoint():
    """Returns dataset metrics and statistics."""
    try:
        meta = get_dataset_metadata()
        return meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry error: {str(e)}")
