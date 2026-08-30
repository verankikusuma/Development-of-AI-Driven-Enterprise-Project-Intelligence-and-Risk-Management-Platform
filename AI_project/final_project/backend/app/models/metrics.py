from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ProjectMetrics(Base):
    __tablename__ = "project_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Quantitative measurements
    project_progress = Column(Float, default=0.0) # 0.0 to 100.0
    pending_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    delayed_tasks = Column(Integer, default=0)
    budget_utilization = Column(Float, default=0.0) # 0.0 to 1.0 (or %)
    resource_availability = Column(Float, default=1.0) # 0.0 to 1.0
    team_productivity = Column(Float, default=1.0) # 0.0 to 2.0 index
    testing_progress = Column(Float, default=0.0) # 0.0 to 100.0
    testing_failures = Column(Integer, default=0)
    bugs = Column(Integer, default=0)
    requirement_changes = Column(Integer, default=0)
    technical_issues = Column(Integer, default=0)
    security_audit_progress = Column(Float, default=0.0) # 0.0 to 100.0
    communication_failures = Column(Integer, default=0)
    external_risk = Column(Float, default=0.0) # 0.0 to 1.0
    dependency_delay = Column(Integer, default=0) # sum of downstream impacted days
    schedule_variance = Column(Float, default=0.0) # in days (+ or -)

    project = relationship("Project", back_populates="metrics")
