from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: datetime
    budget: float = 0.0
    current_budget_used: float = 0.0
    status: str = "IN_PROGRESS"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    current_budget_used: Optional[float] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    team: str
    start_date: Optional[datetime] = None
    planned_end_date: datetime
    actual_end_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    status: str = "NOT_STARTED"
    priority: str = "MEDIUM"
    estimated_duration: int = 10
    remaining_duration: int = 10
    resource_count: int = 5
    resource_availability: float = 1.0
    pending_tasks: int = 0
    bugs_reported: int = 0
    requirement_changes: int = 0
    delay_days: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    team: Optional[str] = None
    start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    progress_percentage: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_duration: Optional[int] = None
    remaining_duration: Optional[int] = None
    resource_count: Optional[int] = None
    resource_availability: Optional[float] = None
    pending_tasks: Optional[int] = None
    bugs_reported: Optional[int] = None
    requirement_changes: Optional[int] = None
    delay_days: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dependency Schemas
class DependencyBase(BaseModel):
    source_task_id: int
    dependent_task_id: int
    dependency_type: str = "FINISH_TO_START"
    dependency_strength: float = 1.0

class DependencyCreate(DependencyBase):
    pass

class DependencyResponse(DependencyBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True

class DependencyImpactResponse(BaseModel):
    task_id: int
    task_name: str
    current_delay_days: int
    direct_dependents: List[Dict[str, Any]]
    downstream_tasks: List[Dict[str, Any]]
    dependency_depth: int
    is_on_critical_path: bool
    total_downstream_impact_days: int
    cascade_chain: List[str]

# Metrics Schemas
class ProjectMetricsBase(BaseModel):
    project_progress: float
    pending_tasks: int = 0
    completed_tasks: int = 0
    delayed_tasks: int = 0
    budget_utilization: float = 0.0
    resource_availability: float = 1.0
    team_productivity: float = 1.0
    testing_progress: float = 0.0
    testing_failures: int = 0
    bugs: int = 0
    requirement_changes: int = 0
    technical_issues: int = 0
    security_audit_progress: float = 0.0
    communication_failures: int = 0
    external_risk: float = 0.0
    dependency_delay: int = 0
    schedule_variance: float = 0.0

class ProjectMetricsCreate(ProjectMetricsBase):
    pass

class ProjectMetricsResponse(ProjectMetricsBase):
    id: int
    project_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Risk Schemas
class RiskFactor(BaseModel):
    name: str
    feature_key: str
    contribution_score: float # 0.0 to 1.0
    level: str # LOW, MEDIUM, HIGH, CRITICAL
    value: float
    unit: str
    description: str

class RiskPredictionResponse(BaseModel):
    project_id: int
    prediction_timestamp: datetime
    model_version: str
    risk_probability: float
    risk_level: str
    feature_snapshot: Dict[str, float]
    contributing_factors: List[RiskFactor]
    model_attribution_disclaimer: str = (
        "These factors represent model feature contributions to the probabilistic risk forecast and do not automatically establish direct physical causation."
    )

    class Config:
        from_attributes = True

# Project Health Schemas
class ProjectHealthResponse(BaseModel):
    project_id: int
    overall_health_score: float # 0 to 100
    health_status: str # EXCELLENT, GOOD, AT_RISK, CRITICAL
    risk_probability: float
    risk_level: str
    schedule_health: float
    budget_health: float
    resource_health: float
    testing_health: float
    dependency_health: float
    summary_message: str
    calculation_method: str = "Multi-criteria weighted index evaluated alongside ML probability"

# Deadline Schemas
class DeadlineForecastResponse(BaseModel):
    project_id: int
    original_deadline: str
    forecast_completion_date: str
    expected_delay_days: int
    delay_probability: float
    status: str # ON_TRACK, AT_RISK, LIKELY_DELAYED, CRITICALLY_DELAYED
    critical_path_tasks: List[Dict[str, Any]]
    total_schedule_buffer_days: int
    methodology: str

# Scenario Schemas
class ScenarioRequest(BaseModel):
    task_id: int
    delay_days: int = Field(ge=0, le=90, description="Additional delay in days to simulate")
    resource_reduction_percent: Optional[float] = 0.0

class ScenarioResponse(BaseModel):
    project_id: int
    simulated_task_id: int
    simulated_task_name: str
    simulated_delay_days: int
    current_risk_probability: float
    scenario_risk_probability: float
    risk_increase_percentage: float
    affected_tasks_count: int
    affected_tasks: List[Dict[str, Any]]
    estimated_schedule_impact_days: int
    forecast_completion_date: str
    disclaimer: str = "Scenario Simulation — not a guaranteed future outcome."

# Recommendation Schemas
class RecommendationItem(BaseModel):
    id: str
    priority: str # HIGH, MEDIUM, LOW, CRITICAL
    title: str
    action: str
    reason: str
    category: str # TESTING, SENSOR_HARDWARE, CYBERSECURITY, DEPENDENCY, RESOURCE
    affected_teams: List[str]
    impact_reduction_estimate: str

class RecommendationsResponse(BaseModel):
    project_id: int
    total_recommendations: int
    critical_count: int
    high_count: int
    recommendations: List[RecommendationItem]
    generated_at: datetime
