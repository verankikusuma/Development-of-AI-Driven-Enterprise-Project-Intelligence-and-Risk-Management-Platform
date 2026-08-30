from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.models.risk import RiskPrediction
from app.models.project import Project
from app.models.task import Task
from app.models.dependency import Dependency
from app.models.metrics import ProjectMetrics
from app.schemas.schemas import RiskPredictionResponse, RiskFactor
from app.ml.feature_extractor import extract_features_from_project_state
from app.ml.predict import predict_project_risk

router = APIRouter()

@router.post("/projects/{project_id}/risk/predict", response_model=RiskPredictionResponse)
def trigger_risk_prediction(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == project_id).all()
    latest_metrics = db.query(ProjectMetrics).filter(ProjectMetrics.project_id == project_id).order_by(ProjectMetrics.timestamp.desc()).first()
    
    features = extract_features_from_project_state(tasks, deps, latest_metrics)
    prob, level, factors = predict_project_risk(features)
    
    pred_record = RiskPrediction(
        project_id=project_id,
        prediction_timestamp=datetime.utcnow(),
        model_version="1.0.0",
        risk_probability=prob,
        risk_level=level,
        feature_snapshot=features,
        contributing_factors=factors
    )
    db.add(pred_record)
    db.commit()
    db.refresh(pred_record)
    
    factors_typed = [RiskFactor(**f) for f in factors]
    
    return RiskPredictionResponse(
        project_id=project_id,
        prediction_timestamp=pred_record.prediction_timestamp,
        model_version=pred_record.model_version,
        risk_probability=prob,
        risk_level=level,
        feature_snapshot=features,
        contributing_factors=factors_typed
    )

@router.get("/projects/{project_id}/risk/latest", response_model=RiskPredictionResponse)
def get_latest_risk(project_id: int, db: Session = Depends(get_db)):
    latest = db.query(RiskPrediction).filter(RiskPrediction.project_id == project_id).order_by(RiskPrediction.prediction_timestamp.desc()).first()
    if not latest:
        # If no prediction stored yet, compute on the fly
        return trigger_risk_prediction(project_id, db)
        
    factors_typed = [RiskFactor(**f) for f in (latest.contributing_factors or [])]
    return RiskPredictionResponse(
        project_id=project_id,
        prediction_timestamp=latest.prediction_timestamp,
        model_version=latest.model_version,
        risk_probability=latest.risk_probability,
        risk_level=latest.risk_level,
        feature_snapshot=latest.feature_snapshot or {},
        contributing_factors=factors_typed
    )

@router.get("/projects/{project_id}/risk/history")
def get_risk_history(project_id: int, db: Session = Depends(get_db)):
    records = db.query(RiskPrediction).filter(RiskPrediction.project_id == project_id).order_by(RiskPrediction.prediction_timestamp.asc()).all()
    history = []
    for r in records:
        history.append({
            "id": r.id,
            "timestamp": r.prediction_timestamp.isoformat(),
            "risk_probability": round(r.risk_probability, 4),
            "risk_level": r.risk_level
        })
    return history

@router.get("/projects/{project_id}/risk/factors", response_model=List[RiskFactor])
def get_risk_factors(project_id: int, db: Session = Depends(get_db)):
    latest = db.query(RiskPrediction).filter(RiskPrediction.project_id == project_id).order_by(RiskPrediction.prediction_timestamp.desc()).first()
    if not latest or not latest.contributing_factors:
        resp = trigger_risk_prediction(project_id, db)
        return resp.contributing_factors
    return [RiskFactor(**f) for f in latest.contributing_factors]
