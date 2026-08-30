from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.dependency import Dependency
from app.models.metrics import ProjectMetrics
from app.models.risk import RiskPrediction
from app.schemas.schemas import ProjectHealthResponse
from app.services.health_service import calculate_project_health
from app.ml.feature_extractor import extract_features_from_project_state
from app.ml.predict import predict_project_risk

router = APIRouter()

@router.get("/projects/{project_id}/health", response_model=ProjectHealthResponse)
def get_project_health_status(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == project_id).all()
    latest_metrics = db.query(ProjectMetrics).filter(ProjectMetrics.project_id == project_id).order_by(ProjectMetrics.timestamp.desc()).first()
    
    # Calculate or retrieve risk prob
    features = extract_features_from_project_state(tasks, deps, latest_metrics)
    risk_prob, _, _ = predict_project_risk(features)
    
    health_data = calculate_project_health(project, tasks, deps, risk_prob, latest_metrics)
    return ProjectHealthResponse(**health_data)
