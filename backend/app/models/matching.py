from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class MatchingScore(BaseModel):
    total_score: float = Field(ge=0, le=100, description="Total matching score from 0 to 100")
    skills_score: float = Field(ge=0, le=100, description="Skills matching score from 0 to 100")
    experience_score: float = Field(ge=0, le=100, description="Experience matching score from 0 to 100")
    education_score: float = Field(ge=0, le=100, description="Education matching score from 0 to 100")
    software_score: float = Field(ge=0, le=100, description="Software matching score from 0 to 100")
    skill_breakdown: Dict[str, float] = Field(default_factory=dict)
    software_breakdown: Dict[str, float] = Field(default_factory=dict)
    missing_skills: List[str] = Field(default_factory=list)
    missing_softwares: List[str] = Field(default_factory=list)


class MatchingRequest(BaseModel):
    cv: Dict
    job: Dict


class MatchingResponse(BaseModel):
    matching: MatchingScore
