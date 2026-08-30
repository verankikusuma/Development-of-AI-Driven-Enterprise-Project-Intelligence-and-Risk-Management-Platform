from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    team = Column(String(100), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    planned_end_date = Column(DateTime, nullable=False)
    actual_end_date = Column(DateTime, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    status = Column(String(50), default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED, DELAYED, BLOCKED
    priority = Column(String(50), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    estimated_duration = Column(Integer, default=10) # in days
    remaining_duration = Column(Integer, default=10) # in days
    resource_count = Column(Integer, default=5)
    resource_availability = Column(Float, default=1.0) # 0.0 to 1.0
    pending_tasks = Column(Integer, default=0)
    bugs_reported = Column(Integer, default=0)
    requirement_changes = Column(Integer, default=0)
    delay_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    upstream_dependencies = relationship("Dependency", foreign_keys="Dependency.dependent_task_id", back_populates="dependent_task", cascade="all, delete-orphan")
    downstream_dependencies = relationship("Dependency", foreign_keys="Dependency.source_task_id", back_populates="source_task", cascade="all, delete-orphan")
