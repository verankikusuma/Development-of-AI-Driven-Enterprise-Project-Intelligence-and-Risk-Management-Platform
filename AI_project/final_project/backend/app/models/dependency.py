from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    source_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dependent_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), default="FINISH_TO_START") # FINISH_TO_START, START_TO_START, FINISH_TO_FINISH
    dependency_strength = Column(Float, default=1.0) # 0.1 to 1.0 (Criticality multiplier)

    # Relationships
    project = relationship("Project", back_populates="dependencies")
    source_task = relationship("Task", foreign_keys=[source_task_id], back_populates="downstream_dependencies")
    dependent_task = relationship("Task", foreign_keys=[dependent_task_id], back_populates="upstream_dependencies")
