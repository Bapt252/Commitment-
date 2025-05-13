#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API de matching candidat-emploi

Cette API expose des endpoints pour :
1. Parser un CV
2. Enregistrer les réponses du questionnaire
3. Calculer le matching entre un candidat et des offres d'emploi
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import tempfile
import os
import sys
import json
import logging
import datetime

# Importer le moteur de matching
from matching_engine import match_candidate_with_jobs

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limiter aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter les fichiers statiques (templates HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Base de données simulée (en production, utiliser une vraie base de données)
CANDIDATES_DB = {}
JOBS_DB = []

# Charger les offres d'emploi de test
try:
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        JOBS_DB = json.load(f)
    logger.info(f"Offres d'emploi chargées: {len(JOBS_DB)} offres")
except (FileNotFoundError, json.JSONDecodeError):
    # Créer quelques offres de test
    JOBS_DB = [
        {
            "id": 1,
            "titre": "Développeur Front-End Senior",
            "entreprise": "TechVision",
            "localisation": "15 Rue de Rivoli, 75004 Paris",
            "type_contrat": "CDI",
            "competences": ["JavaScript", "React", "TypeScript", "HTML", "CSS"],
            "experience": "3-5 ans",
            "date_debut": "01/05/2025",
            "salaire": "45K-55K€",
            "description": "Nous recherchons un développeur Front-End expérimenté pour renforcer notre équipe technique en pleine croissance."
        },
        {
            "id": 2,
            "titre": "Développeur Full-Stack",
            "entreprise": "InnovateTech",
            "localisation": "92 Avenue des Champs-Élysées, 75008 Paris",
            "type_contrat": "CDI",
            "competences": ["JavaScript", "React", "Node.js", "Express", "MongoDB"],
            "experience": "2-4 ans",
            "date_debut": "15/04/2025",
            "salaire": "42K-48K€",
            "description": "Notre entreprise cherche un développeur Full-Stack talentueux pour participer au développement de notre plateforme innovante."
        },
        {
            "id": 3,
            "titre": "Développeur Back-End",
            "entreprise": "Data Solutions",
            "localisation": "56 Rue du Faubourg Saint-Honoré, 75008 Paris",
            "type_contrat": "CDI",
            "competences": ["Python", "Django", "SQL", "Docker", "AWS"],
            "experience": "2-5 ans",
            "date_debut": "01/06/2025",
            "salaire": "40K-50K€",
            "description": "Data Solutions recherche un développeur Back-End pour renforcer son équipe tech."
        }
    ]
    
    # Sauvegarder pour réutilisation future
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(JOBS_DB, f, ensure_ascii=False, indent=2)
    
    logger.info("Fichier jobs_data.json créé avec des données de test")

# Modèles de données
class QuestionnaireData(BaseModel):
    email: str
    contrats_recherches: List[str]
    adresse: str
    temps_trajet_max: int
    date_disponibilite: str
    salaire_min: int
    domaines_interets: List[str]

class MatchingRequest(BaseModel):
    email: str
    limit: Optional[int] = 10

@app.get("/")
async def read_root():
    return {"message": "API de matching candidat-emploi"}

@app.get("/api/status")
async def check_status():
    return {"status": "ok", "jobs_loaded": len(JOBS_DB)}

@app.post("/api/parse-cv")
async def parse_cv(file: UploadFile = File(...), email: str = Form(...)):
    """
    Parse un CV et stocke les données extraites
    """
    try:
        logger.info(f"Réception d'un CV pour {email}: {file.filename}")
        
        # Vérifier le type de fichier
        allowed_extensions = [".pdf", ".docx", ".txt"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Extension de fichier non supportée: {file_ext}")
            raise HTTPException(
                status_code=400, 
                detail=f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
            )
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"Fichier temporaire créé: {temp_file_path}")
        
        try:
            # Essayer d'importer et d'utiliser le module de parsing de CV
            try:
                # Importez votre script de parsing de CV
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from parse_cv_gpt import parse_cv
                logger.info("Module parse_cv_gpt importé avec succès")
                
                # Utiliser la fonction de parsing réelle
                cv_data = parse_cv(temp_file_path)
                logger.info("Analyse du CV effectuée avec succès")
                
            except ImportError:
                # Si le module n'est pas trouvé, utiliser une fonction de simulation
                logger.warning("Module parse_cv_gpt non trouvé, utilisation du mode simulation")
                cv_data = _mock_parse_cv(temp_file_path)
            
            # Stocker les données du CV
            if email not in CANDIDATES_DB:
                CANDIDATES_DB[email] = {}
            
            CANDIDATES_DB[email]['cv_data'] = cv_data
            CANDIDATES_DB[email]['cv_uploaded_at'] = datetime.datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "CV analysé avec succès",
                "data": cv_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing du CV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du CV: {str(e)}")
            
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"Fichier temporaire supprimé: {temp_file_path}")
    
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/api/save-questionnaire")
async def save_questionnaire(data: QuestionnaireData):
    """
    Sauvegarde les réponses du questionnaire
    """
    try:
        email = data.email
        
        # Créer l'entrée si elle n'existe pas
        if email not in CANDIDATES_DB:
            CANDIDATES_DB[email] = {}
        
        # Stocker les données du questionnaire
        CANDIDATES_DB[email]['questionnaire_data'] = data.dict()
        CANDIDATES_DB[email]['questionnaire_completed_at'] = datetime.datetime.now().isoformat()
        
        logger.info(f"Questionnaire sauvegardé pour {email}")
        
        return {
            "success": True,
            "message": "Questionnaire sauvegardé avec succès"
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du questionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/api/get-matching-jobs")
async def get_matching_jobs(request: MatchingRequest):
    """
    Calcule et retourne les offres d'emploi qui correspondent le mieux au candidat
    """
    try:
        email = request.email
        limit = request.limit
        
        # Vérifier que le candidat existe
        if email not in CANDIDATES_DB:
            raise HTTPException(status_code=404, detail="Candidat non trouvé")
        
        # Vérifier que le CV et le questionnaire sont disponibles
        if 'cv_data' not in CANDIDATES_DB[email]:
            raise HTTPException(status_code=400, detail="CV non analysé")
        
        if 'questionnaire_data' not in CANDIDATES_DB[email]:
            raise HTTPException(status_code=400, detail="Questionnaire non complété")
        
        # Récupérer les données
        cv_data = CANDIDATES_DB[email]['cv_data']
        questionnaire_data = CANDIDATES_DB[email]['questionnaire_data']
        
        # Calculer le matching
        matching_results = match_candidate_with_jobs(cv_data, questionnaire_data, JOBS_DB, limit)
        
        # Stocker les résultats pour référence future
        CANDIDATES_DB[email]['matching_results'] = matching_results
        CANDIDATES_DB[email]['matching_calculated_at'] = datetime.datetime.now().isoformat()
        
        logger.info(f"Matching calculé pour {email}: {len(matching_results)} résultats")
        
        return {
            "success": True,
            "count": len(matching_results),
            "data": matching_results
        }
    
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul du matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/api/jobs")
async def get_all_jobs():
    """
    Retourne toutes les offres d'emploi disponibles
    """
    return {
        "success": True,
        "count": len(JOBS_DB),
        "data": JOBS_DB
    }

def _mock_parse_cv(file_path: str) -> Dict[str, Any]:
    """
    Fonction de simulation pour tester l'API sans le module de parsing réel
    """
    logger.info(f"Analyse simulée du CV: {file_path}")
    
    # Extraire juste le nom du fichier pour les tests
    file_name = os.path.basename(file_path)
    
    # Résultats simulés
    mock_data = {
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com",
        "telephone": "+33 6 12 34 56 78",
        "adresse": "123 Rue de Paris, 75001 Paris",
        "competences": ["Python", "JavaScript", "React", "SQL", "Git", "Docker"],
        "annees_experience": 4,
        "formation": "Master en Informatique, Université Paris-Saclay (2021)",
        "langues": ["Français (Natif)", "Anglais (Courant)"],
        "postes_precedents": [
            {
                "titre": "Développeur Full Stack",
                "entreprise": "TechCorp",
                "date_debut": "01/2022",
                "date_fin": "Présent",
                "description": "Développement d'applications web avec React et Node.js"
            },
            {
                "titre": "Développeur Frontend",
                "entreprise": "WebAgency",
                "date_debut": "06/2020",
                "date_fin": "12/2021",
                "description": "Développement de sites web avec HTML, CSS et JavaScript"
            }
        ]
    }
    
    return mock_data

if __name__ == "__main__":
    import uvicorn
    
    # Afficher un message d'information sur le démarrage du serveur
    print("=" * 50)
    print("Démarrage du serveur de matching candidat-emploi...")
    print("Accédez à l'API via: http://localhost:8000")
    print("Pour tester l'API: http://localhost:8000/api/status")
    print("=" * 50)
    
    # Démarrer le serveur
    uvicorn.run(app, host="0.0.0.0", port=8000)
