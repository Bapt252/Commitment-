#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test simple pour l'algorithme de matching
Point d'entrée direct pour tester votre algorithme sans Docker
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import sys
import os

# Ajouter le répertoire parent pour importer le moteur de matching
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matching_engine import match_candidate_with_jobs

# Configuration de l'application FastAPI
app = FastAPI(
    title="Test API Algorithme de Matching",
    description="Endpoint simple pour tester votre algorithme de matching",
    version="1.0.0"
)

# Modèles de données
class CandidateData(BaseModel):
    competences: List[str] = []
    annees_experience: int = 0
    formation: str = ""

class QuestionnaireData(BaseModel):
    contrats_recherches: List[str] = []
    adresse: str = ""
    temps_trajet_max: int = 60
    date_disponibilite: str = ""
    salaire_min: int = 0
    domaines_interets: List[str] = []

class JobData(BaseModel):
    id: int
    titre: str
    entreprise: str
    localisation: str = ""
    type_contrat: str = ""
    competences: List[str] = []
    experience: str = ""
    date_debut: str = ""
    salaire: str = ""

class MatchingRequest(BaseModel):
    cv_data: CandidateData
    questionnaire_data: QuestionnaireData
    job_data: List[JobData]
    limit: Optional[int] = 10

@app.get("/")
async def root():
    """Page d'accueil de l'API de test"""
    return {
        "message": "API de test pour l'algorithme de matching",
        "endpoints": {
            "health": "/health",
            "test_matching": "/test-matching [POST]",
            "test_simple": "/test-simple [GET]",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé"""
    return {"status": "healthy", "service": "test-matching-algorithm"}

@app.post("/test-matching")
async def test_matching(request: MatchingRequest):
    """
    Test de l'algorithme de matching avec données personnalisées
    
    Args:
        request: Données du candidat et des offres d'emploi
        
    Returns:
        Résultats du matching avec scores
    """
    try:
        # Conversion des données Pydantic vers dict
        cv_data = request.cv_data.dict()
        questionnaire_data = request.questionnaire_data.dict()
        job_data = [job.dict() for job in request.job_data]
        
        # Appel de l'algorithme de matching
        results = match_candidate_with_jobs(
            cv_data=cv_data,
            questionnaire_data=questionnaire_data,
            job_data=job_data,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "candidate_profile": {
                "competences": cv_data.get("competences", []),
                "experience": cv_data.get("annees_experience", 0),
                "formation": cv_data.get("formation", "")
            },
            "total_jobs_analyzed": len(job_data),
            "results_returned": len(results),
            "matches": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul de matching: {str(e)}")

@app.get("/test-simple")
async def test_simple():
    """
    Test simple avec données prédéfinies
    """
    # Données de test intégrées
    cv_data = {
        "competences": ["Python", "Django", "React", "SQL", "Git"],
        "annees_experience": 4,
        "formation": "Master Informatique"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI", "CDD"],
        "adresse": "Paris",
        "temps_trajet_max": 45,
        "date_disponibilite": "01/07/2025",
        "salaire_min": 45000,
        "domaines_interets": ["Web", "Data"]
    }
    
    job_data = [
        {
            "id": 1,
            "titre": "Développeur Full-Stack",
            "entreprise": "TechCorp",
            "localisation": "Paris",
            "type_contrat": "CDI",
            "competences": ["Python", "Django", "React"],
            "experience": "3-5 ans",
            "date_debut": "15/06/2025",
            "salaire": "45K-55K€"
        },
        {
            "id": 2,
            "titre": "Data Engineer",
            "entreprise": "DataCorp",
            "localisation": "Lyon",
            "type_contrat": "CDD",
            "competences": ["Python", "SQL", "Spark"],
            "experience": "2-4 ans",
            "date_debut": "01/08/2025",
            "salaire": "50K-60K€"
        },
        {
            "id": 3,
            "titre": "Frontend Developer",
            "entreprise": "WebCorp",
            "localisation": "Remote",
            "type_contrat": "CDI",
            "competences": ["React", "JavaScript", "CSS"],
            "experience": "1-3 ans",
            "date_debut": "01/06/2025",
            "salaire": "40K-50K€"
        }
    ]
    
    try:
        results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
        
        return {
            "status": "success",
            "test_type": "données prédéfinies",
            "candidate_profile": cv_data,
            "total_jobs": len(job_data),
            "matches": results,
            "best_match": results[0] if results else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/test-algorithm-comparison")
async def test_algorithm_comparison():
    """
    Compare l'algorithme actuel avec des métriques
    """
    cv_data = {
        "competences": ["Python", "Machine Learning", "Data Science"],
        "annees_experience": 3,
        "formation": "Master Data Science"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI"],
        "salaire_min": 50000,
        "adresse": "Paris"
    }
    
    # Jobs avec différents niveaux de correspondance
    job_data = [
        {
            "id": 1,
            "titre": "Data Scientist",
            "competences": ["Python", "Machine Learning", "Statistics"],
            "type_contrat": "CDI",
            "salaire": "55K-65K€"
        },
        {
            "id": 2,
            "titre": "Java Developer",
            "competences": ["Java", "Spring", "MySQL"],
            "type_contrat": "CDI",
            "salaire": "50K-60K€"
        },
        {
            "id": 3,
            "titre": "Python Developer",
            "competences": ["Python", "Django", "PostgreSQL"],
            "type_contrat": "CDD",
            "salaire": "45K-55K€"
        }
    ]
    
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    
    # Analyse des résultats
    analysis = {
        "perfect_match_count": len([r for r in results if r['matching_score'] >= 90]),
        "good_match_count": len([r for r in results if 70 <= r['matching_score'] < 90]),
        "poor_match_count": len([r for r in results if r['matching_score'] < 70]),
        "average_score": sum(r['matching_score'] for r in results) / len(results) if results else 0,
        "score_distribution": [r['matching_score'] for r in results]
    }
    
    return {
        "status": "success",
        "algorithm_analysis": analysis,
        "detailed_results": results
    }

if __name__ == "__main__":
    print("🚀 Démarrage de l'API de test pour l'algorithme de matching")
    print("📋 Endpoints disponibles:")
    print("   • http://localhost:8000/")
    print("   • http://localhost:8000/health")
    print("   • http://localhost:8000/test-simple")
    print("   • http://localhost:8000/docs (documentation interactive)")
    print("\n🔥 Lancement du serveur...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
