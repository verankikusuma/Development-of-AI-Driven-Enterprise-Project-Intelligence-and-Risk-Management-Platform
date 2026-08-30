from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=False)
    budget = Column(Float, default=0.0)
    current_budget_used = Column(Float, default=0.0)
    status = Column(String(50), default="IN_PROGRESS") # IN_PROGRESS, DELAYED, COMPLETED, AT_RISK
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    dependencies = relationship("Dependency", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("ProjectMetrics", back_populates="project", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="project", cascade="all, delete-orphan")
