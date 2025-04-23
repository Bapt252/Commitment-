from typing import List, Optional
from pydantic import BaseModel, Field


class CVSkill(BaseModel):
    name: str
    level: Optional[str] = None


class CVExperience(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class CVEducation(BaseModel):
    degree: str
    institution: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CV(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    summary: Optional[str] = None
    skills: List[CVSkill] = Field(default_factory=list)
    experiences: List[CVExperience] = Field(default_factory=list)
    education: List[CVEducation] = Field(default_factory=list)
    softwares: List[str] = Field(default_factory=list)
