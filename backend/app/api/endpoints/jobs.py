from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, Job as JobSchema, JobUpdate
from app.services.job_description_parser import parse_job_description

router = APIRouter()

@router.get("/", response_model=List[JobSchema])
def read_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Récupérer toutes les offres d'emploi"""
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@router.post("/", response_model=JobSchema)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Créer une nouvelle offre d'emploi"""
    job = Job(
        title=job_in.title,
        description=job_in.description,
        requirements=job_in.requirements,
        salary_min=job_in.salary_min,
        salary_max=job_in.salary_max,
        location=job_in.location,
        company_id=job_in.company_id,
        job_type=job_in.job_type,
        experience_level=job_in.experience_level,
        skills=job_in.skills
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.post("/parse", response_model=JobSchema)
async def parse_job_file(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> Any:
    """Analyser une fiche de poste à partir d'un fichier ou de texte"""
    if not file and not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez fournir un fichier ou du texte"
        )
    
    # Analyser la description de poste
    job_data = None
    if file:
        content = await file.read()
        job_data = parse_job_description(content.decode())
    else:
        job_data = parse_job_description(text_content)
    
    # Créer un objet Job temporaire (sans l'enregistrer en DB)
    job = Job(
        title=job_data.get("title", ""),
        description=job_data.get("description", ""),
        requirements=job_data.get("requirements", ""),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        location=job_data.get("location", ""),
        job_type=job_data.get("job_type", ""),
        experience_level=job_data.get("experience_level", ""),
        skills=job_data.get("skills", [])
    )
    
    return job

@router.get("/{job_id}", response_model=JobSchema)
def read_job(job_id: int, db: Session = Depends(get_db)) -> Any:
    """Récupérer une offre d'emploi par ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre d'emploi non trouvée"
        )
    return job

@router.put("/{job_id}", response_model=JobSchema)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """Mettre à jour une offre d'emploi"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre d'emploi non trouvée"
        )
    
    update_data = job_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", response_model=JobSchema)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Supprimer une offre d'emploi"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre d'emploi non trouvée"
        )
    
    db.delete(job)
    db.commit()
    return job