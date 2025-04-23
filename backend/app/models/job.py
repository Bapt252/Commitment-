from typing import List, Optional
from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    name: str
    importance: int = Field(ge=1, le=10, description="Importance from 1 to 10")


class JobPosition(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    required_skills: List[JobRequirement] = Field(default_factory=list)
    required_experience: Optional[int] = None
    required_education: Optional[str] = None
    required_softwares: List[JobRequirement] = Field(default_factory=list)
