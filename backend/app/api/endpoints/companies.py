from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from app.nlp.company_questionnaire_parser import parse_company_questionnaire
from app.nlp.matching_engine import get_matching_engine

router = APIRouter()
logger = logging.getLogger(__name__)

class CompanyQuestionnaireInput(BaseModel):
    """Modèle pour les données d'entrée du questionnaire entreprise"""
    company_info: Dict[str, Any] = Field(..., description="Informations de base sur l'entreprise")
    company_values: Optional[str] = Field(None, description="Valeurs et culture d'entreprise")
    work_environment: Optional[Dict[str, Any]] = Field(None, description="Environnement de travail")
    technologies: Optional[List[str]] = Field(None, description="Technologies et stack technique")
    sector: Optional[str] = Field(None, description="Secteur d'activité")
    company_size: Optional[str] = Field(None, description="Taille de l'entreprise")
    
    class Config:
        schema_extra = {
            "example": {
                "company_info": {
                    "name": "TechInnovate",
                    "website": "https://techinnovate.com",
                    "contact_email": "contact@techinnovate.com"
                },
                "company_values": "Nous valorisons l'innovation, la collaboration et le bien-être des employés. Notre culture est basée sur l'autonomie et la responsabilisation.",
                "work_environment": {
                    "remote_policy": "hybrid",
                    "office_locations": ["Paris", "Lyon"],
                    "benefits": ["Télétravail", "Horaires flexibles", "Formation continue"]
                },
                "technologies": ["Python", "React", "AWS", "Docker", "MongoDB"],
                "sector": "Tech - Développement logiciel",
                "company_size": "50-100 employés"
            }
        }

class CompanyAnalysisResponse(BaseModel):
    """Modèle pour les résultats d'analyse du questionnaire entreprise"""
    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]

class MatchingInput(BaseModel):
    """Modèle pour la requête de matching"""
    company_id: str = Field(..., description="Identifiant de l'entreprise")
    limit: Optional[int] = Field(10, description="Nombre maximum de candidats à retourner")
    min_score: Optional[float] = Field(50.0, description="Score minimal de matching (en %)")

class MatchingResult(BaseModel):
    """Modèle pour le résultat de matching"""
    candidate_id: str
    candidate_name: str
    match_score: float
    category_scores: Dict[str, float]
    title: Optional[str] = None

class MatchingResponse(BaseModel):
    """Modèle pour la réponse de l'API de matching"""
    results: List[MatchingResult]
    count: int
    company_id: str

@router.post("/questionnaire", response_model=CompanyAnalysisResponse)
async def analyze_company_questionnaire(
    questionnaire: CompanyQuestionnaireInput = Body(..., description="Données du questionnaire entreprise")
):
    """
    Analyse un questionnaire d'entreprise et extrait les informations pertinentes
    pour le matching avec les candidats.
    """
    try:
        logger.info(f"Analyse du questionnaire pour l'entreprise: {questionnaire.company_info.get('name', 'Inconnue')}")
        
        # Convertir le modèle Pydantic en dictionnaire
        questionnaire_data = questionnaire.dict()
        
        # Analyser le questionnaire
        result = parse_company_questionnaire(questionnaire_data)
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du questionnaire: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )

@router.get("/match/{company_id}/candidates", response_model=MatchingResponse)
async def match_candidates_for_company(
    company_id: str,
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum de résultats"),
    min_score: float = Query(50.0, ge=0.0, le=100.0, description="Score minimal (%)"),
):
    """
    Génère des recommandations de candidats pour une entreprise spécifique
    basées sur les critères de matching.
    """
    try:
        logger.info(f"Recherche de candidats pour l'entreprise ID: {company_id}")
        
        # TODO: Remplacer par une vraie recherche en base de données
        # Ici, on simule des données pour la démonstration
        company_profile = {
            "id": company_id,
            "name": "Entreprise de démonstration",
            "extracted_data": {
                "values": {
                    "detected_values": {
                        "innovation": 0.8,
                        "collaboration": 0.7,
                        "autonomie": 0.6
                    }
                },
                "work_environment": {
                    "work_mode": ["hybrid"],
                    "locations": ["Paris"]
                },
                "experience": "3 ans"
            },
            "technologies": ["Python", "JavaScript", "AWS", "Docker"]
        }
        
        # Obtenir des candidats simulés
        # Dans une vraie implémentation, ces données viendraient d'une base de données
        candidate_profiles = [
            {
                "id": "c1",
                "name": "Jean Dupont",
                "titre": "Développeur Full Stack",
                "competences": ["Python", "JavaScript", "React", "Node.js"],
                "experience": [
                    {"period": "2020 - 2024", "title": "Développeur Full Stack chez TechCorp"}
                ],
                "values": {"detected_values": {"innovation": 0.9, "collaboration": 0.8}},
                "work_preferences": {"preferred_work_mode": "hybrid", "preferred_location": "Paris"}
            },
            {
                "id": "c2",
                "name": "Marie Martin",
                "titre": "DevOps Engineer",
                "competences": ["Docker", "AWS", "Python", "Kubernetes"],
                "experience": [
                    {"period": "2019 - 2024", "title": "DevOps Engineer chez CloudServices"}
                ],
                "values": {"detected_values": {"autonomie": 0.9, "excellence": 0.8}},
                "work_preferences": {"preferred_work_mode": "remote", "preferred_location": "Lyon"}
            }
            # Dans une implémentation réelle, il y aurait plus de candidats
        ]
        
        # Obtenir le moteur de matching
        matching_engine = get_matching_engine()
        
        # Générer les recommandations
        recommendations = matching_engine.generate_candidate_recommendations(
            company_profile, 
            candidate_profiles, 
            limit=limit
        )
        
        # Filtrer par score minimal
        filtered_recommendations = [r for r in recommendations if r["match_score"] >= min_score]
        
        # Construire la réponse
        response = {
            "results": filtered_recommendations,
            "count": len(filtered_recommendations),
            "company_id": company_id
        }
        
        return response
    except Exception as e:
        logger.error(f"Erreur lors du matching: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
def get_companies():
    """
    Liste des entreprises enregistrées
    """
    # Cette fonction servirait à récupérer les entreprises depuis une base de données
    # Pour la démonstration, on retourne des données statiques
    return [
        {"id": "1", "name": "TechInnovate", "sector": "Tech"}
    ]
