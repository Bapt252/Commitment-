"""
Script d'initialisation du système de matching XGBoost
Ce script peut être exécuté manuellement ou lors du démarrage de l'application
pour initialiser et pré-charger le modèle de matching.
"""

import logging
import os
from pathlib import Path
import joblib
import numpy as np

from .xgboost_matching_engine import get_xgboost_matching_engine

logger = logging.getLogger(__name__)

def init_matching_engine():
    """
    Initialise le moteur de matching XGBoost.
    - Vérifie l'existence d'un modèle pré-entraîné
    - Charge le modèle s'il existe, sinon prépare un modèle de base
    """
    logger.info("Initialisation du moteur de matching XGBoost...")
    
    # Obtenir l'instance du moteur
    matching_engine = get_xgboost_matching_engine()
    
    # Chemin pour les modèles sauvegardés
    models_dir = Path(__file__).resolve().parent.parent.parent / "data" / "models"
    candidate_model_path = models_dir / "xgboost_candidate_ranking.model"
    job_model_path = models_dir / "xgboost_job_ranking.model"
    scaler_path = models_dir / "feature_scaler.joblib"
    
    # Créer le répertoire de modèles s'il n'existe pas
    models_dir.mkdir(exist_ok=True, parents=True)
    
    # Vérifier si les modèles existent et les charger
    models_loaded = False
    try:
        if candidate_model_path.exists() and job_model_path.exists() and scaler_path.exists():
            logger.info("Chargement des modèles de matching existants...")
            
            # Charger les modèles
            import xgboost as xgb
            matching_engine.candidate_ranking_model = xgb.Booster()
            matching_engine.candidate_ranking_model.load_model(str(candidate_model_path))
            
            matching_engine.job_ranking_model = xgb.Booster()
            matching_engine.job_ranking_model.load_model(str(job_model_path))
            
            # Charger le scaler
            matching_engine.scaler = joblib.load(scaler_path)
            
            # Initialiser l'explainer SHAP
            try:
                import shap
                matching_engine.explainer = shap.TreeExplainer(matching_engine.candidate_ranking_model)
                logger.info("Explainer SHAP initialisé avec succès.")
            except Exception as e:
                logger.warning(f"Erreur lors de l'initialisation de l'explainer SHAP: {str(e)}. Les explications détaillées ne seront pas disponibles.")
            
            models_loaded = True
            logger.info("Modèles chargés avec succès.")
    except Exception as e:
        logger.warning(f"Erreur lors du chargement des modèles: {str(e)}. Un nouveau modèle sera préparé.")
    
    # Si les modèles n'ont pas été chargés, préparer un nouveau modèle de base
    if not models_loaded:
        logger.info("Préparation d'un modèle de matching de base...")
        
        try:
            # Données factices pour l'initialisation
            # Dans un déploiement réel, ces données proviendraient de la base de données
            dummy_candidates = [
                {"id": i, "name": f"Candidat {i}", "competences": ["Python", "Java"], 
                 "experience_years": 3, "education_level": "Master"}
                for i in range(1, 10)
            ]
            
            dummy_jobs = [
                {"id": i, "job_title": f"Poste {i}", "required_skills": ["Python", "SQL"], 
                 "required_experience_years": 2, "required_education_level": "Bachelor"}
                for i in range(1, 5)
            ]
            
            # Générer quelques données d'entraînement simples
            features_list = []
            y_values = []
            
            for candidate in dummy_candidates:
                for job in dummy_jobs:
                    # Générer les features pour la paire candidat-job
                    features = matching_engine.generate_matching_features(candidate, job)
                    features_list.append(list(features.values()))
                    
                    # Simuler un score basé sur des règles simples
                    skills_match = sum(1 for s in job["required_skills"] if s in candidate["competences"])
                    skills_score = skills_match / len(job["required_skills"]) if job["required_skills"] else 0.5
                    
                    exp_score = min(1.0, candidate["experience_years"] / job["required_experience_years"]) if job["required_experience_years"] > 0 else 0.5
                    
                    edu_levels = {"Bachelor": 3, "Master": 4, "PhD": 5}
                    c_edu = edu_levels.get(candidate["education_level"], 3)
                    j_edu = edu_levels.get(job["required_education_level"], 3)
                    edu_score = 1.0 if c_edu >= j_edu else 0.7 * (c_edu / j_edu)
                    
                    # Score global
                    score = 0.5 * skills_score + 0.3 * exp_score + 0.2 * edu_score
                    y_values.append(score)
            
            # Convertir en arrays numpy et ajuster le scaler
            X = np.array(features_list)
            y = np.array(y_values)
            
            matching_engine.scaler.fit(X)
            
            # Sauvegarder le scaler
            joblib.dump(matching_engine.scaler, scaler_path)
            logger.info(f"Scaler sauvegardé dans {scaler_path}")
            
            logger.info("Modèle de base préparé avec succès. Le modèle sera entraîné lors de la première utilisation.")
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation du modèle de base: {str(e)}")
    
    return matching_engine

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialiser le moteur
    init_matching_engine()
