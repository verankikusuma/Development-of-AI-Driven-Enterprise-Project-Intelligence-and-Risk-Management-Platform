import os
import json
import streamlit as st
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from utils.local_ai import parse_project_locally

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
USE_CLOUD_AI = os.environ.get("USE_CLOUD_AI", "false").strip().lower() == "true"

class ExtractedFeatures(BaseModel):
    project_type: str = Field(default="Unknown")
    industry_sector: str = Field(default="Unknown")
    methodology: str = Field(default="Unknown")
    region: str = Field(default="Unknown")
    contract_type: str = Field(default="Unknown")
    priority: str = Field(default="Unknown")
    
    planned_duration_days: float = Field(default=0.0)
    actual_duration_days: float = Field(default=0.0)
    team_size: float = Field(default=0.0)
    team_avg_experience_years: float = Field(default=0.0)
    team_turnover_pct: float = Field(default=0.0)
    stakeholder_count: float = Field(default=0.0)
    requirement_changes_count: float = Field(default=0.0)
    budget_usd: float = Field(default=0.0)
    actual_cost_usd: float = Field(default=0.0)
    cost_overrun_pct: float = Field(default=0.0)
    schedule_overrun_pct: float = Field(default=0.0)
    resource_availability_pct: float = Field(default=100.0)
    vendor_dependency_count: float = Field(default=0.0)
    communication_score: float = Field(default=100.0)
    sponsor_engagement_score: float = Field(default=100.0)
    previous_project_success_rate_pct: float = Field(default=100.0)
    tech_complexity_score: float = Field(default=0.0)
    regulatory_compliance_load: float = Field(default=0.0)
    scope_clarity_score: float = Field(default=100.0)
    external_dependency_score: float = Field(default=0.0)
    safety_incidents: float = Field(default=0.0)
    defect_count: float = Field(default=0.0)
    milestones_missed: float = Field(default=0.0)

class ProjectActionItem(BaseModel):
    task: str = Field(description="The action item or task")
    owner: str = Field(default="Unassigned")
    status: str = Field(default="Pending")

class ProjectMilestone(BaseModel):
    name: str = Field(description="Name of milestone")
    progress_pct: float = Field(default=0.0)

class ProjectDependency(BaseModel):
    name: str = Field(description="Name of dependency")
    status: str = Field(default="Unknown")
    impact: str = Field(default="Unknown")

class DocumentInsights(BaseModel):
    project_name: str = Field(default="IT Project")
    project_scope: str = Field(default="Not explicitly defined.")
    deliverables: List[str] = Field(default=[])
    action_items: List[ProjectActionItem] = Field(default=[])
    milestones: List[ProjectMilestone] = Field(default=[])
    dependencies: List[ProjectDependency] = Field(default=[])
    missing_info: List[str] = Field(default=[])
    potential_risks: List[str] = Field(default=[])
    features: ExtractedFeatures

def parse_document_with_gemini(document_text: str, project_kind: str = "IT") -> dict:
    """
    Passes document text to Gemini or backend API endpoint to extract features & insights.
    """
    # 1. Try FastAPI Backend API endpoint if connected
    try:
        from utils.api_client import backend_health, api_parse_document
        api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
        if backend_health(api_base):
            parsed = api_parse_document(document_text, is_csv=False, project_kind=project_kind, base_url=api_base)
            if parsed and isinstance(parsed, dict) and "features" in parsed:
                return parsed
    except Exception:
        pass

    # 2. Direct Gemini or Local Parsing Fallback
    if not USE_CLOUD_AI or not GEMINI_API_KEY:
        return parse_project_locally(document_text, project_kind)

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    You are an expert IT Project Manager and Data Analyst. Read the following project document/meeting notes carefully.
    Extract the requested project insights and map them to the schema.
    
    Document Text:
    {document_text[:30000]}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', contents=prompt,
            config={'response_mime_type': 'application/json', 'response_schema': DocumentInsights, 'temperature': 0.1},
        )
        return json.loads(response.text)
    except Exception:
        return parse_project_locally(document_text, project_kind)

class BatchDocumentInsights(BaseModel):
    projects: List[DocumentInsights]

def parse_batch_with_gemini(document_text: str, project_kind: str = "IT") -> dict:
    """
    Passes a batch document (like a CSV) to Gemini or backend API endpoint to extract insights.
    """
    # 1. Try FastAPI Backend API endpoint if connected
    try:
        from utils.api_client import backend_health, api_parse_document
        api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
        if backend_health(api_base):
            parsed = api_parse_document(document_text, is_csv=True, project_kind=project_kind, base_url=api_base)
            if parsed and isinstance(parsed, dict) and "projects" in parsed:
                return parsed
    except Exception:
        pass

    # 2. Direct Gemini or Local Parsing Fallback
    if not USE_CLOUD_AI or not GEMINI_API_KEY:
        return {"projects": [parse_project_locally(document_text, project_kind)]}

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    Read the following batch project document (e.g. CSV).
    Extract project insights for EACH project found in the text and map them to the schema.
    
    Batch Document Text:
    {document_text[:30000]}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', contents=prompt,
            config={'response_mime_type': 'application/json', 'response_schema': BatchDocumentInsights, 'temperature': 0.1},
        )
        return json.loads(response.text)
    except Exception:
        return {"projects": [parse_project_locally(document_text, project_kind)]}
