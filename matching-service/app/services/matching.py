"""
Service pour la gestion des calculs de matching entre candidats et offres d'emploi.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from app.models.matching import MatchingResult as DBMatchingResult

logger = logging.getLogger(__name__)

class MatchingService:
    """Service pour la gestion des calculs de matching entre candidats et offres d'emploi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_matching_score(self, candidate_id: int, job_id: int) -> Dict[str, Any]:
        """
        Calcule le score de matching entre un candidat et une offre d'emploi
        
        Args:
            candidate_id: ID du candidat
            job_id: ID de l'offre d'emploi
            
        Returns:
            dict: Résultats du matching avec score et détails
        """
        logger.info(f"Calcul du score de matching pour le candidat {candidate_id} et l'offre {job_id}")
        
        # C'est ici que votre algorithme de matching serait implémenté
        # Pour cet exemple, nous retournons une structure simple
        
        # Récupération des données du candidat depuis la DB
        # candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        # Récupération des données de l'offre depuis la DB
        # job = self.db.query(JobPosting).filter(JobPosting.id == job_id).first()
        
        # Exemple de logique de scoring (à remplacer par votre algorithme réel)
        skills_score = 0.85  # Score exemple
        experience_score = 0.75
        education_score = 0.90
        
        # Calcul de la moyenne pondérée
        overall_score = (skills_score * 0.5) + (experience_score * 0.3) + (education_score * 0.2)
        
        # Retourne un résultat structuré
        return {
            "score": overall_score,
            "details": {
                "skills_score": skills_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "skills_matching": {
                    "matched": ["Python", "FastAPI", "Docker"],
                    "missing": ["Kubernetes"],
                    "additional": ["PostgreSQL", "Redis"]
                },
                "experience_matching": {
                    "years_required": 3,
                    "years_actual": 4,
                    "relevance": 0.8
                },
                "education_matching": {
                    "level_required": "Master",
                    "level_actual": "Master",
                    "field_match": 0.9
                }
            }
        }
    
    def store_matching_result(self, job_id: str, candidate_id: int, job_posting_id: int, 
                             score: float, details: Dict[str, Any]) -> DBMatchingResult:
        """
        Stocke le résultat du matching dans la base de données
        
        Args:
            job_id: ID du job Redis
            candidate_id: ID du candidat
            job_posting_id: ID de l'offre d'emploi
            score: Score global de matching
            details: Résultats détaillés du matching
            
        Returns:
            DBMatchingResult: Enregistrement stocké dans la base de données
        """
        # Vérifier si on a déjà un résultat pour ce candidat et cette offre
        existing = self.db.query(DBMatchingResult).filter(
            DBMatchingResult.candidate_id == candidate_id,
            DBMatchingResult.job_posting_id == job_posting_id
        ).first()
        
        if existing:
            # Mise à jour de l'enregistrement existant
            existing.job_id = job_id
            existing.score = score
            existing.details = details
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Création d'un nouvel enregistrement
            db_result = DBMatchingResult(
                job_id=job_id,
                candidate_id=candidate_id,
                job_posting_id=job_posting_id,
                score=score,
                details=details
            )
            self.db.add(db_result)
            self.db.commit()
            self.db.refresh(db_result)
            return db_result
