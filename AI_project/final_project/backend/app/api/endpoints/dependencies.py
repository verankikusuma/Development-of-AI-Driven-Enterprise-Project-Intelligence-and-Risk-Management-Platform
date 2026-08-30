from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.dependency import Dependency
from app.models.task import Task
from app.models.project import Project
from app.schemas.schemas import DependencyCreate, DependencyResponse, DependencyImpactResponse
from app.services.dependency_service import analyze_task_dependency_impact, get_graph_export
from app.services.cpm_service import calculate_critical_path

router = APIRouter()

@router.post("/projects/{project_id}/dependencies", response_model=DependencyResponse)
def create_dependency(project_id: int, dep_in: DependencyCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_dep = Dependency(**dep_in.model_dump(), project_id=project_id)
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)
    return db_dep

@router.get("/projects/{project_id}/dependencies", response_model=List[DependencyResponse])
def get_project_dependencies(project_id: int, db: Session = Depends(get_db)):
    return db.query(Dependency).filter(Dependency.project_id == project_id).all()

@router.get("/projects/{project_id}/dependency-graph")
def get_full_dependency_graph(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == project_id).all()
    cpm = calculate_critical_path(tasks, deps)
    return get_graph_export(tasks, deps, cpm.get("critical_task_ids", []))

@router.get("/tasks/{task_id}/dependency-impact", response_model=DependencyImpactResponse)
def get_task_dependency_impact(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    tasks = db.query(Task).filter(Task.project_id == task.project_id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == task.project_id).all()
    
    try:
        impact = analyze_task_dependency_impact(task_id, tasks, deps)
        return impact
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
