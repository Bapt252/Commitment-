from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class Experiment(Base):
    __tablename__ = 'experiments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(String(20), default='draft')  # draft, running, completed, paused
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    traffic_allocation = Column(JSONB, nullable=False)  # {"control": 50, "variants": [{"name": "v1", "percentage": 25, "algorithm": "algo_v1"}]}
    metrics = Column(JSONB)  # ["match_count", "feedback_score", "conversion_rate"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ExperimentMetric(Base):
    __tablename__ = 'experiment_metrics'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    variant = Column(String(50), nullable=False)
    match_count = Column(Integer, default=0)
    feedback_score = Column(Float)
    conversion_count = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSONB)  # Informations supplémentaires