from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.metrics import ProjectMetrics
from app.models.project import Project
from app.schemas.schemas import ProjectMetricsCreate, ProjectMetricsResponse

router = APIRouter()

@router.post("/projects/{project_id}/metrics", response_model=ProjectMetricsResponse)
def log_project_metrics(project_id: int, metrics_in: ProjectMetricsCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_metrics = ProjectMetrics(**metrics_in.model_dump(), project_id=project_id)
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

@router.get("/projects/{project_id}/metrics", response_model=List[ProjectMetricsResponse])
def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectMetrics).filter(ProjectMetrics.project_id == project_id).order_by(ProjectMetrics.timestamp.asc()).all()
