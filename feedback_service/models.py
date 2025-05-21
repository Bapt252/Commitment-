"""
Module de modèles et schémas pour le service de feedback.
Définit les structures de données et les schémas de base de données.
"""

from datetime import datetime
from enum import Enum
import json
from typing import Dict, List, Optional, Union
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Boolean, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class FeedbackType(str, Enum):
    """Types de feedback supportés par le système."""
    EXPLICIT = "explicit"  # Feedback explicite donné par l'utilisateur
    IMPLICIT = "implicit"  # Feedback implicite basé sur le comportement
    SYSTEM = "system"      # Feedback généré par le système


class FeedbackChannel(str, Enum):
    """Canaux par lesquels le feedback est collecté."""
    RATING = "rating"          # Évaluation (1-5 étoiles)
    THUMBS = "thumbs"          # Pouce haut/bas
    COMMENT = "comment"        # Commentaire textuel
    SUGGESTION = "suggestion"  # Suggestion d'amélioration
    SURVEY = "survey"          # Réponse à un sondage
    BEHAVIOR = "behavior"      # Comportement utilisateur
    OTHER = "other"            # Autre source


class Sentiment(str, Enum):
    """Sentiment associé au feedback."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class Feedback(Base):
    """Modèle de base de données pour le feedback utilisateur."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    channel = Column(SQLEnum(FeedbackChannel), nullable=False)
    content = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    sentiment = Column(SQLEnum(Sentiment), nullable=False, default=Sentiment.UNKNOWN)
    context = Column(JSON, nullable=True)  # Contexte JSON (page, action, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)  # Si le feedback a été traité
    
    # Relations
    analyses = relationship("FeedbackAnalysis", back_populates="feedback")

    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type,
            "channel": self.channel,
            "content": self.content,
            "rating": self.rating,
            "sentiment": self.sentiment,
            "context": json.loads(self.context) if isinstance(self.context, str) else self.context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed": self.processed
        }


class FeedbackAnalysis(Base):
    """Modèle pour l'analyse de feedback."""
    __tablename__ = "feedback_analysis"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # sentiment, topic, etc.
    result = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    feedback = relationship("Feedback", back_populates="analyses")

    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "feedback_id": self.feedback_id,
            "analysis_type": self.analysis_type,
            "result": json.loads(self.result) if isinstance(self.result, str) else self.result,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserSatisfactionModel(Base):
    """Modèle de prédiction de satisfaction utilisateur."""
    __tablename__ = "user_satisfaction_model"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    satisfaction_score = Column(Float, nullable=False)
    factors = Column(JSON, nullable=False)  # Facteurs influençant le score
    confidence = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "satisfaction_score": self.satisfaction_score,
            "factors": json.loads(self.factors) if isinstance(self.factors, str) else self.factors,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class ModelTrainingLog(Base):
    """Journal d'entraînement des modèles."""
    __tablename__ = "model_training_log"

    id = Column(Integer, primary_key=True)
    model_type = Column(String(50), nullable=False)  # satisfaction, sentiment, etc.
    version = Column(String(20), nullable=False)
    metrics = Column(JSON, nullable=False)  # Métriques d'évaluation
    parameters = Column(JSON, nullable=False)  # Paramètres utilisés
    training_time = Column(Float, nullable=False)  # Temps d'entraînement en secondes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "model_type": self.model_type,
            "version": self.version,
            "metrics": json.loads(self.metrics) if isinstance(self.metrics, str) else self.metrics,
            "parameters": json.loads(self.parameters) if isinstance(self.parameters, str) else self.parameters,
            "training_time": self.training_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FeedbackRule(Base):
    """Règles de traitement automatique du feedback."""
    __tablename__ = "feedback_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    conditions = Column(JSON, nullable=False)  # Conditions d'activation
    actions = Column(JSON, nullable=False)  # Actions à effectuer
    priority = Column(Integer, default=0)  # Priorité d'exécution
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conditions": json.loads(self.conditions) if isinstance(self.conditions, str) else self.conditions,
            "actions": json.loads(self.actions) if isinstance(self.actions, str) else self.actions,
            "priority": self.priority,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FeedbackTrend(Base):
    """Tendances de feedback agrégées."""
    __tablename__ = "feedback_trends"

    id = Column(Integer, primary_key=True)
    trend_type = Column(String(50), nullable=False)  # daily, weekly, topic, etc.
    dimension = Column(String(50), nullable=False)  # sentiment, canal, etc.
    value = Column(String(50), nullable=False)  # valeur de la dimension
    count = Column(Integer, nullable=False)
    average_rating = Column(Float, nullable=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convertit l'instance en dictionnaire."""
        return {
            "id": self.id,
            "trend_type": self.trend_type,
            "dimension": self.dimension,
            "value": self.value,
            "count": self.count,
            "average_rating": self.average_rating,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
