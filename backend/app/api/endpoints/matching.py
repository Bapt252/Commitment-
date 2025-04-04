from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from ...nlp.xgboost_matching_engine import get_xgboost_matching_engine
from ...core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Modèles Pydantic pour la validation des données
class MatchRequestBase(BaseModel):
    limit: int = Field(10, description="Nombre maximum de résultats à retourner")

class CandidatesMatchRequest(MatchRequestBase):
    job_profile: Dict[str, Any] = Field(..., description="Profil de l'offre d'emploi")
    candidate_ids: List[str] = Field(None, description="Liste des IDs de candidats à évaluer (optionnel)")
    
class JobsMatchRequest(MatchRequestBase):
    candidate_profile: Dict[str, Any] = Field(..., description="Profil du candidat")
    job_ids: List[str] = Field(None, description="Liste des IDs d'offres à évaluer (optionnel)")

class ExplainMatchRequest(BaseModel):
    candidate_profile: Dict[str, Any] = Field(..., description="Profil du candidat")
    job_profile: Dict[str, Any] = Field(..., description="Profil de l'offre d'emploi")

class CandidateRankingResponse(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Candidats classés par pertinence")
    
class JobRankingResponse(BaseModel):
    jobs: List[Dict[str, Any]] = Field(..., description="Offres classées par pertinence")
    
class MatchExplanationResponse(BaseModel):
    explanation: Dict[str, Any] = Field(..., description="Explication détaillée du matching")

@router.post("/rank-candidates", response_model=CandidateRankingResponse)
async def rank_candidates_for_job(
    request: CandidatesMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Classe les candidats par pertinence pour une offre d'emploi.
    
    Si candidate_ids est fourni, seuls les candidats correspondants sont évalués.
    Sinon, tous les candidats disponibles sont évalués.
    """
    try:
        # Récupérer l'instance du moteur de matching
        matching_engine = get_xgboost_matching_engine()
        
        # Récupérer les candidats depuis la base de données
        candidates = []
        if request.candidate_ids:
            # Récupérer seulement les candidats spécifiés
            # Note: Implémenter la récupération des candidats par ID depuis la BD
            for candidate_id in request.candidate_ids:
                # Exemple: candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
                # Simuler pour l'instant avec des données factices
                candidates.append({
                    "id": candidate_id,
                    "name": f"Candidat {candidate_id}",
                    # Autres attributs du candidat
                })
        else:
            # Récupérer tous les candidats (limité à un nombre raisonnable)
            # Note: Implémenter la récupération de tous les candidats depuis la BD
            # Simuler pour l'instant avec des données factices
            candidates = [
                {"id": f"candidate_{i}", "name": f"Candidat {i}"}
                for i in range(1, 21)  # Limiter à 20 candidats pour l'exemple
            ]
        
        # Effectuer le classement
        ranked_candidates = matching_engine.rank_candidates_for_job(
            candidates=candidates,
            job_profile=request.job_profile,
            limit=request.limit
        )
        
        return {"candidates": ranked_candidates}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du classement des candidats: {str(e)}"
        )

@router.post("/rank-jobs", response_model=JobRankingResponse)
async def rank_jobs_for_candidate(
    request: JobsMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Classe les offres d'emploi par pertinence pour un candidat.
    
    Si job_ids est fourni, seules les offres correspondantes sont évaluées.
    Sinon, toutes les offres disponibles sont évaluées.
    """
    try:
        # Récupérer l'instance du moteur de matching
        matching_engine = get_xgboost_matching_engine()
        
        # Récupérer les offres d'emploi depuis la base de données
        jobs = []
        if request.job_ids:
            # Récupérer seulement les offres spécifiées
            # Note: Implémenter la récupération des offres par ID depuis la BD
            for job_id in request.job_ids:
                # Exemple: job = db.query(JobModel).filter(JobModel.id == job_id).first()
                # Simuler pour l'instant avec des données factices
                jobs.append({
                    "id": job_id,
                    "job_title": f"Poste {job_id}",
                    "company_name": f"Entreprise {job_id}"
                    # Autres attributs de l'offre
                })
        else:
            # Récupérer toutes les offres (limité à un nombre raisonnable)
            # Note: Implémenter la récupération de toutes les offres depuis la BD
            # Simuler pour l'instant avec des données factices
            jobs = [
                {
                    "id": f"job_{i}", 
                    "job_title": f"Poste {i}",
                    "company_name": f"Entreprise {i}"
                }
                for i in range(1, 21)  # Limiter à 20 offres pour l'exemple
            ]
        
        # Effectuer le classement
        ranked_jobs = matching_engine.rank_jobs_for_candidate(
            jobs=jobs,
            candidate_profile=request.candidate_profile,
            limit=request.limit
        )
        
        return {"jobs": ranked_jobs}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du classement des offres d'emploi: {str(e)}"
        )

@router.post("/explain-match", response_model=MatchExplanationResponse)
async def explain_candidate_job_match(
    request: ExplainMatchRequest
):
    """
    Génère une explication détaillée du matching entre un candidat et une offre
    """
    try:
        # Récupérer l'instance du moteur de matching
        matching_engine = get_xgboost_matching_engine()
        
        # Générer l'explication
        explanation = matching_engine.explain_matching(
            candidate_profile=request.candidate_profile,
            job_profile=request.job_profile
        )
        
        return {"explanation": explanation}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'explication: {str(e)}"
        )

@router.post("/train-model")
async def train_matching_model(
    db: Session = Depends(get_db)
):
    """
    Entraîne le modèle de matching XGBoost avec les données existantes
    """
    try:
        # Récupérer l'instance du moteur de matching
        matching_engine = get_xgboost_matching_engine()
        
        # Récupérer les données d'entraînement depuis la BD
        # Note: Implémenter la récupération des données depuis la BD
        # Pour l'instant, utilisons des données factices
        candidates = [
            {"id": f"candidate_{i}", "name": f"Candidat {i}"}
            for i in range(1, 51)  # 50 candidats pour l'exemple
        ]
        
        jobs = [
            {
                "id": f"job_{i}", 
                "job_title": f"Poste {i}",
                "company_name": f"Entreprise {i}"
            }
            for i in range(1, 31)  # 30 offres pour l'exemple
        ]
        
        # Générer les données d'entraînement
        X_train, y_train = matching_engine.prepare_training_data(
            candidates=candidates,
            jobs=jobs
        )
        
        # Entraîner le modèle
        matching_engine.train_model(
            X_train=X_train,
            y_train=y_train,
            model_type="candidate_ranking"
        )
        
        # Optionnel: Entraînement d'un second modèle pour le ranking des offres
        matching_engine.train_model(
            X_train=X_train,
            y_train=y_train,
            model_type="job_ranking"
        )
        
        return {"status": "success", "message": "Modèle entraîné avec succès"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'entraînement du modèle: {str(e)}"
        )

@router.post("/tune-hyperparameters")
async def tune_model_hyperparameters(
    db: Session = Depends(get_db)
):
    """
    Optimise les hyperparamètres du modèle de matching XGBoost
    """
    try:
        # Récupérer l'instance du moteur de matching
        matching_engine = get_xgboost_matching_engine()
        
        # Récupérer les données d'entraînement depuis la BD
        # Note: Implémenter la récupération des données depuis la BD
        # Pour l'instant, utilisons des données factices
        candidates = [
            {"id": f"candidate_{i}", "name": f"Candidat {i}"}
            for i in range(1, 51)  # 50 candidats pour l'exemple
        ]
        
        jobs = [
            {
                "id": f"job_{i}", 
                "job_title": f"Poste {i}",
                "company_name": f"Entreprise {i}"
            }
            for i in range(1, 31)  # 30 offres pour l'exemple
        ]
        
        # Générer les données d'entraînement
        X_train, y_train = matching_engine.prepare_training_data(
            candidates=candidates,
            jobs=jobs
        )
        
        # Optimiser les hyperparamètres
        best_params = matching_engine.tune_hyperparameters(
            X_train=X_train,
            y_train=y_train
        )
        
        return {
            "status": "success", 
            "message": "Hyperparamètres optimisés avec succès",
            "best_params": best_params
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'optimisation des hyperparamètres: {str(e)}"
        )
