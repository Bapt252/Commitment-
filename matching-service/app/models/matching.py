"""
Modèles de données pour le service de matching.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from datetime import datetime

# SQLAlchemy models
Base = declarative_base()

class MatchingResult(Base):
    """Modèle de base de données pour les résultats de matching"""
    __tablename__ = "matching_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)  # ID du job Redis
    candidate_id = Column(Integer, index=True)
    job_posting_id = Column(Integer, index=True)
    score = Column(Float)  # Score global
    details = Column(JSON)  # Scores détaillés de matching
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Création d'index pour les requêtes rapides
    __table_args__ = (
        Index('ix_matching_results_candidate_job', 'candidate_id', 'job_posting_id', unique=True),
        Index('ix_matching_results_score', 'score'),  # Pour un tri rapide par score
    )

# Pydantic models for API

class QueuePriority(str, Enum):
    """Priorités de file d'attente disponibles"""
    HIGH = "matching_high"
    STANDARD = "matching_standard"
    BULK = "matching_bulk"

class MatchingRequest(BaseModel):
    """Modèle de requête pour le calcul de matching"""
    candidate_id: int
    job_id: int
    webhook_url: Optional[HttpUrl] = None

class MatchingBulkRequest(BaseModel):
    """Modèle de requête pour le calcul de matching en masse"""
    candidate_id: int
    job_ids: List[int]
    webhook_url: Optional[HttpUrl] = None

class MatchingResponse(BaseModel):
    """Modèle de réponse pour un calcul de matching mis en file d'attente"""
    job_id: str
    status: str
    queue: str
    message: str

class MatchingJobStatus(BaseModel):
    """Statut d'un job de matching"""
    job_id: str
    status: str

class MatchingResultResponse(BaseModel):
    """Résultat d'un calcul de matching"""
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
