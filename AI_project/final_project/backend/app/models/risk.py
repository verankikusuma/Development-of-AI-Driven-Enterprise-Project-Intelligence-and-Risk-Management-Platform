from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), default="1.0.0")
    risk_probability = Column(Float, nullable=False) # 0.0 to 1.0
    risk_level = Column(String(50), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    feature_snapshot = Column(JSON, nullable=True) # key-value pair of feature vector used
    contributing_factors = Column(JSON, nullable=True) # list/dict of feature impact scores

    project = relationship("Project", back_populates="risk_predictions")
