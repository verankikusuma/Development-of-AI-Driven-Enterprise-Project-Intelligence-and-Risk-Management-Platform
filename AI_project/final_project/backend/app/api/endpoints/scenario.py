from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.dependency import Dependency
from app.schemas.schemas import ScenarioRequest, ScenarioResponse
from app.services.scenario_service import simulate_what_if_scenario

router = APIRouter()

@router.post("/projects/{project_id}/scenario", response_model=ScenarioResponse)
def run_scenario_simulation(project_id: int, req: ScenarioRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == project_id).all()
    
    try:
        res = simulate_what_if_scenario(
            project=project,
            tasks=tasks,
            dependencies=deps,
            task_id=req.task_id,
            additional_delay_days=req.delay_days,
            resource_reduction_percent=req.resource_reduction_percent or 0.0
        )
        return ScenarioResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
