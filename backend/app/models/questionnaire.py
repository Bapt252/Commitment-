from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Types de questions supportés dans les questionnaires"""
    TEXT = "text"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    RATING = "rating"
    BOOLEAN = "boolean"
    SKILLS = "skills"


class Question(BaseModel):
    """Modèle pour une question de questionnaire"""
    id: Optional[int] = None
    text: str
    type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    description: Optional[str] = None


class QuestionnaireBase(BaseModel):
    """Modèle de base pour un questionnaire"""
    title: str
    description: Optional[str] = None
    type: str = Field(description="Type de questionnaire (ex: 'candidate', 'employer')")
    questions: List[Question]


class QuestionnaireCreate(QuestionnaireBase):
    """Modèle pour la création d'un questionnaire"""
    pass


class QuestionnaireUpdate(BaseModel):
    """Modèle pour la mise à jour d'un questionnaire"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    questions: Optional[List[Question]] = None


class QuestionnaireInDB(QuestionnaireBase):
    """Modèle pour un questionnaire stocké en base de données"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class QuestionnaireResponse(QuestionnaireInDB):
    """Modèle de réponse pour un questionnaire"""
    pass


class Answer(BaseModel):
    """Modèle pour une réponse à une question"""
    question_id: int
    value: Union[str, int, bool, List[str], Dict[str, Any]]


class QuestionnaireSubmissionBase(BaseModel):
    """Modèle de base pour la soumission d'un questionnaire"""
    questionnaire_id: int
    candidate_id: int
    answers: List[Answer]


class QuestionnaireSubmissionCreate(QuestionnaireSubmissionBase):
    """Modèle pour la création d'une soumission de questionnaire"""
    pass


class QuestionnaireSubmissionInDB(QuestionnaireSubmissionBase):
    """Modèle pour une soumission de questionnaire en base de données"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class QuestionnaireAnalysisRequest(BaseModel):
    """Modèle pour une requête d'analyse de questionnaire"""
    candidate_id: int
    answers: List[Answer]


class SkillAssessment(BaseModel):
    """Évaluation d'une compétence basée sur les réponses au questionnaire"""
    name: str
    level: int
    confidence: float
    source_questions: List[int]


class QuestionnaireAnalysisResponse(BaseModel):
    """Modèle de réponse pour l'analyse d'un questionnaire"""
    candidate_id: int
    questionnaire_id: int
    skills_assessment: List[SkillAssessment]
    experience_assessment: Dict[str, Any]
    education_assessment: Dict[str, Any]
    personality_traits: Optional[Dict[str, float]] = None
    recommendations: List[str]
    analysis_completed_at: datetime
