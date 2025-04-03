from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Schéma de base pour une offre d'emploi
class JobBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    location: Optional[str] = None
    company_id: Optional[int] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = []

# Schéma pour la création d'une offre d'emploi
class JobCreate(JobBase):
    title: str

# Schéma pour la mise à jour d'une offre d'emploi
class JobUpdate(JobBase):
    pass

# Schéma pour afficher une offre d'emploi
class Job(JobBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True