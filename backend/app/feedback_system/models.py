from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from app.core.database import Base


class Matching(Base):
    __tablename__ = "matchings"
    
    id = Column(Integer, primary_key=True)
    job_post_id = Column(Integer, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    matching_score = Column(Float, nullable=False)
    matching_date = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String(50), nullable=False)
    
    # Relation avec les feedbacks
    feedbacks = relationship("MatchingFeedback", back_populates="matching")
    

class MatchingFeedback(Base):
    __tablename__ = "matching_feedbacks"
    
    id = Column(Integer, primary_key=True)
    matching_id = Column(Integer, ForeignKey("matchings.id"))
    user_id = Column(Integer, nullable=False)  # Qui a donné le feedback
    rating = Column(Integer, nullable=False)   # 1-5
    comment = Column(Text, nullable=True)
    interaction_happened = Column(Boolean, default=False)
    feedback_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Métriques implicites
    time_to_first_message = Column(Integer, nullable=True)  # en minutes
    message_count = Column(Integer, default=0)
    engagement_duration = Column(Integer, nullable=True)    # en jours
    
    # Relation avec le matching
    matching = relationship("Matching", back_populates="feedbacks")


class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'matching', 'job_parsing', etc.
    training_date = Column(DateTime, default=datetime.datetime.utcnow)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    auc_roc = Column(Float, nullable=True)
    
    # Métriques business
    avg_satisfaction = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    
    # Métadonnées
    dataset_size = Column(Integer, nullable=False)
    is_deployed = Column(Boolean, default=False)
    
    # Config du modèle (stockée en JSON)
    model_config = Column(Text, nullable=True)
    

class FeedbackAlert(Base):
    __tablename__ = "feedback_alerts"
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # 'performance_drop', 'high_negative_rate', etc.
    severity = Column(String(20), nullable=False)  # 'info', 'warning', 'critical'
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
