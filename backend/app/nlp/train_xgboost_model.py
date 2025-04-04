#!/usr/bin/env python
"""
Module d'entraînement du modèle XGBoost pour le moteur de matching.
Génère des données synthétiques pour l'entraînement en l'absence de données réelles.
"""

import os
import logging
import json
import random
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, ndcg_score

from app.nlp.xgboost_matching_engine import XGBoostMatchingEngine, get_xgboost_matching_engine

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("train_xgboost")

class XGBoostModelTrainer:
    """
    Classe pour l'entraînement du modèle XGBoost de matching candidat-entreprise.
    """
    
    def __init__(self, data_path=None, models_path=None):
        """
        Initialise le trainer avec les chemins des données et modèles.
        
        Args:
            data_path: Chemin vers le répertoire de données (optionnel)
            models_path: Chemin vers le répertoire des modèles (optionnel)
        """
        # Initialiser les chemins
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = data_path or base_dir / "data"
        self.models_path = models_path or base_dir / "models"
        
        # Créer les répertoires s'ils n'existent pas
        self.data_path.mkdir(exist_ok=True, parents=True)
        self.models_path.mkdir(exist_ok=True, parents=True)
        
        # Initialiser le moteur de matching
        self.matching_engine = get_xgboost_matching_engine()
        
        # Scaler pour les features
        self.scaler = StandardScaler()
        
        logger.info(f"Trainer initialisé avec chemin de données: {self.data_path}")
        logger.info(f"Chemin des modèles: {self.models_path}")
    
    def generate_synthetic_data(self, num_candidates=100, num_jobs=50) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Génère des données synthétiques pour l'entraînement du modèle.
        
        Args:
            num_candidates: Nombre de profils candidats à générer
            num_jobs: Nombre d'offres d'emploi à générer
            
        Returns:
            Tuple: (liste de profils candidats, liste d'offres d'emploi)
        """
        logger.info(f"Génération de {num_candidates} profils candidats et {num_jobs} offres d'emploi synthétiques")
        
        # Listes de données pour la génération aléatoire
        tech_skills = [
            "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "React",
            "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "ASP.NET",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git",
            "TensorFlow", "PyTorch", "Scikit-learn", "SQL", "MongoDB", "Redis",
            "Elasticsearch", "HTML", "CSS", "PHP", "Ruby", "Swift", "Kotlin"
        ]
        
        job_titles = [
            "Développeur Full Stack", "Développeur Frontend", "Développeur Backend",
            "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
            "Architecte Logiciel", "Lead Developer", "CTO", "Développeur Mobile",
            "Ingénieur QA", "Product Manager", "Scrum Master", "UX Designer",
            "UI Designer", "Administrateur Système", "Administrateur Base de Données",
            "Développeur Java", "Développeur Python", "Développeur JavaScript"
        ]
        
        locations = ["Paris", "Lyon", "Bordeaux", "Marseille", "Lille", "Toulouse", "Nantes", "Remote"]
        
        work_modes = ["remote", "hybrid", "onsite"]
        
        company_values = [
            "innovation", "collaboration", "excellence", "qualité", "respect",
            "intégrité", "transparence", "client", "performance", "agilité",
            "diversité", "inclusion", "responsabilité", "créativité", "apprentissage"
        ]
        
        # Génération de profils candidats synthétiques
        candidates = []
        for i in range(num_candidates):
            # Sélection aléatoire de compétences
            num_skills = random.randint(3, 10)
            competences = random.sample(tech_skills, num_skills)
            
            # Sélection d'années d'expérience
            experience_years = random.randint(0, 15)
            
            # Création d'expériences professionnelles
            experiences = []
            remaining_years = experience_years
            current_year = 2024
            
            while remaining_years > 0:
                duration = min(remaining_years, random.randint(1, 4))
                end_year = current_year
                start_year = end_year - duration
                
                job_title = random.choice(job_titles)
                company_name = f"Entreprise {random.randint(1, 100)}"
                
                experiences.append({
                    "period": f"{start_year} - {end_year}",
                    "title": job_title,
                    "company": company_name,
                    "description": f"Expérience en tant que {job_title} chez {company_name} utilisant {', '.join(random.sample(competences, min(3, len(competences))))}"
                })
                
                current_year = start_year
                remaining_years -= duration
            
            # Création des niveaux de compétence
            skill_levels = {}
            for skill in competences:
                level_options = ["débutant", "intermédiaire", "avancé", "expert"]
                weights = [0.2, 0.4, 0.3, 0.1]
                skill_levels[skill] = random.choices(level_options, weights=weights)[0]
            
            # Création de valeurs détectées
            values = {
                "detected_values": {
                    value: random.random() for value in random.sample(company_values, random.randint(3, 6))
                }
            }
            
            # Construction du profil complet
            candidate = {
                "id": f"candidate_{i+1}",
                "name": f"Candidat {i+1}",
                "titre": random.choice(job_titles),
                "competences": competences,
                "skills_with_level": skill_levels,
                "experience": experiences,
                "experience_years": experience_years,
                "education_level": random.choice(["Bac+2", "Bac+3", "Bac+5", "Doctorat"]),
                "education_field": random.choice(["Informatique", "Mathématiques", "Génie logiciel", "Sciences des données"]),
                "values": values,
                "preferred_location": random.choice(locations),
                "preferred_work_mode": random.choice(work_modes),
                "expected_salary": {
                    "min": random.randint(30, 50) * 1000,
                    "max": random.randint(50, 80) * 1000
                },
                "work_preferences": {
                    "team_size": random.choice(["small", "medium", "large"]),
                    "management_style": random.choice(["directive", "collaborative", "hands-off"]),
                    "company_culture": random.choice(["startup", "corporate", "scale-up"])
                }
            }
            
            candidates.append(candidate)
        
        # Génération d'offres d'emploi synthétiques
        jobs = []
        for i in range(num_jobs):
            # Sélection aléatoire de compétences requises
            num_required_skills = random.randint(3, 8)
            required_skills = random.sample(tech_skills, num_required_skills)
            
            # Années d'expérience requises
            required_experience_years = random.randint(0, 10)
            
            # Niveaux de compétence requis
            required_skill_levels = {}
            for skill in required_skills:
                level_options = ["débutant", "intermédiaire", "avancé", "expert"]
                weights = [0.1, 0.3, 0.4, 0.2]
                required_skill_levels[skill] = random.choices(level_options, weights=weights)[0]
            
            # Valeurs d'entreprise
            company_detected_values = {
                "detected_values": {
                    value: random.random() for value in random.sample(company_values, random.randint(3, 6))
                }
            }
            
            # Construction de l'offre d'emploi
            job = {
                "id": f"job_{i+1}",
                "job_title": random.choice(job_titles),
                "company_name": f"Entreprise {random.randint(1, 50)}",
                "required_skills": required_skills,
                "required_skills_with_level": required_skill_levels,
                "required_experience_years": required_experience_years,
                "required_education_level": random.choice(["Bac+2", "Bac+3", "Bac+5", "Doctorat"]),
                "preferred_education_field": random.choice(["Informatique", "Mathématiques", "Génie logiciel", "Sciences des données"]),
                "location": random.choice(locations),
                "work_mode": random.choice(work_modes),
                "company_values": company_detected_values,
                "salary_range": {
                    "min": random.randint(30, 50) * 1000,
                    "max": random.randint(50, 90) * 1000
                },
                "job_description": f"Offre pour un poste de {random.choice(job_titles)} nécessitant des compétences en {', '.join(required_skills)}.",
                "company_size": random.choice(["startup", "PME", "grande entreprise"]),
                "industry": random.choice(["Tech", "Finance", "Santé", "E-commerce", "Industrie"]),
                "work_environment": {
                    "team_size": random.choice(["small", "medium", "large"]),
                    "management_style": random.choice(["directive", "collaborative", "hands-off"]),
                    "company_culture": random.choice(["startup", "corporate", "scale-up"])
                }
            }
            
            jobs.append(job)
        
        # Sauvegarde des données synthétiques pour référence
        with open(self.data_path / "synthetic_candidates.json", "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        
        with open(self.data_path / "synthetic_jobs.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Données synthétiques générées et sauvegardées dans {self.data_path}")
        
        return candidates, jobs
    
    def generate_synthetic_matches(self, candidates, jobs, num_matches=1000) -> List[Dict[str, Any]]:
        """
        Génère des paires de matching synthétiques candidat-job avec scores.
        
        Args:
            candidates: Liste des profils candidats
            jobs: Liste des offres d'emploi
            num_matches: Nombre de matchs à générer
            
        Returns:
            List: Liste de matchs avec scores
        """
        logger.info(f"Génération de {num_matches} matchs synthétiques")
        
        matches = []
        
        for _ in range(num_matches):
            # Sélection aléatoire d'un candidat et d'un job
            candidate = random.choice(candidates)
            job = random.choice(jobs)
            
            # Calcul d'un score par le moteur de matching
            features = self.matching_engine.generate_matching_features(candidate, job)
            
            # Création d'un facteur aléatoire pour introduire de la variabilité
            random_factor = random.uniform(0.85, 1.15)
            
            # Calcul du score final (limité entre 0 et 1)
            # Nous utilisons une somme pondérée des features pour un score synthétique
            score = min(1.0, max(0.0, 
                features["skills_similarity"] * 0.3 * random_factor +
                features["experience_years_match"] * 0.2 * random_factor +
                features["education_level_match"] * 0.15 * random_factor +
                features["values_alignment"] * 0.2 * random_factor +
                features["work_mode_match"] * 0.15 * random_factor
            ))
            
            match = {
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                "relevance": score,
                "features": features
            }
            
            matches.append(match)
        
        # Sauvegarde des matchs synthétiques
        with open(self.data_path / "synthetic_matches.json", "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Matchs synthétiques générés et sauvegardés dans {self.data_path}")
        
        return matches
    
    def prepare_training_data(self, candidates, jobs, matches):
        """
        Prépare les données d'entraînement pour le modèle XGBoost.
        
        Args:
            candidates: Liste des profils candidats
            jobs: Liste des offres d'emploi
            matches: Liste des matchs avec scores
            
        Returns:
            Tuple: (X_train, X_test, y_train, y_test)
        """
        logger.info("Préparation des données d'entraînement")
        
        # Création d'un dictionnaire pour accéder rapidement aux profils
        candidate_dict = {c["id"]: c for c in candidates}
        job_dict = {j["id"]: j for j in jobs}
        
        # Extraction des features et labels pour l'entraînement
        features_list = []
        labels = []
        
        for match in matches:
            candidate_id = match["candidate_id"]
            job_id = match["job_id"]
            relevance = match["relevance"]
            
            # Récupérer les profils correspondants
            candidate = candidate_dict.get(candidate_id)
            job = job_dict.get(job_id)
            
            if candidate and job:
                # Récupérer les features précalculées si disponibles, sinon les générer
                if "features" in match:
                    features = match["features"]
                    features_array = np.array([list(features.values())])
                else:
                    # Générer les features
                    features = self.matching_engine.generate_matching_features(candidate, job)
                    features_array = np.array([list(features.values())])
                
                features_list.append(features_array[0])
                labels.append(relevance)
        
        # Conversion en arrays numpy
        X = np.array(features_list)
        y = np.array(labels)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normalisation des features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Sauvegarde du scaler pour utilisation future
        from joblib import dump
        dump(self.scaler, self.models_path / "feature_scaler.joblib")
        
        logger.info(f"Données d'entraînement préparées: {X_train_scaled.shape[0]} exemples d'entraînement, {X_test_scaled.shape[0]} exemples de test")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_model(self, X_train, y_train, X_test, y_test, model_type="candidate_ranking"):
        """
        Entraîne le modèle XGBoost avec les données préparées.
        
        Args:
            X_train: Features d'entraînement
            y_train: Labels d'entraînement
            X_test: Features de test
            y_test: Labels de test
            model_type: Type de modèle à entraîner ("candidate_ranking" ou "job_ranking")
            
        Returns:
            model: Modèle XGBoost entraîné
        """
        logger.info(f"Entraînement du modèle {model_type}")
        
        # Création des ensembles de données XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        # Paramètres XGBoost
        params = self.matching_engine.xgboost_params.copy()
        
        # Pour l'optimisation des paramètres sur des données réelles, ajustez ces valeurs
        if model_type == "candidate_ranking":
            params["objective"] = "rank:pairwise"
            model_name = "candidate_ranking_model.json"
        else:
            params["objective"] = "rank:pairwise"
            model_name = "job_ranking_model.json"
        
        # Liste d'évaluation pour early stopping
        evallist = [(dtrain, 'train'), (dtest, 'eval')]
        
        # Entraînement du modèle
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=200,  # Réduit pour les données synthétiques
            evals=evallist,
            early_stopping_rounds=20,
            verbose_eval=10
        )
        
        # Sauvegarde du modèle
        model_path = self.models_path / model_name
        model.save_model(str(model_path))
        
        # Évaluation du modèle
        predictions = model.predict(dtest)
        mse = mean_squared_error(y_test, predictions)
        logger.info(f"Erreur quadratique moyenne sur l'ensemble de test: {mse:.4f}")
        
        # Pour les modèles de ranking, calculer NDCG
        try:
            # Pour le calcul de NDCG, nous avons besoin de grouper les prédictions
            # Dans un cas réel, vous auriez des groupes de candidats pour chaque job
            # Ici, nous simplifions en créant des groupes artificiels
            group_size = 5
            n_groups = len(y_test) // group_size
            
            ndcg_scores = []
            for i in range(n_groups):
                start_idx = i * group_size
                end_idx = start_idx + group_size
                
                if end_idx <= len(y_test):
                    group_true = y_test[start_idx:end_idx]
                    group_pred = predictions[start_idx:end_idx]
                    
                    # Éviter les groupes avec tous les mêmes valeurs
                    if len(set(group_true)) > 1:
                        ndcg = ndcg_score([group_true], [group_pred], k=group_size)
                        ndcg_scores.append(ndcg)
            
            if ndcg_scores:
                avg_ndcg = sum(ndcg_scores) / len(ndcg_scores)
                logger.info(f"Score NDCG moyen: {avg_ndcg:.4f}")
        except Exception as e:
            logger.warning(f"Impossible de calculer NDCG: {e}")
        
        logger.info(f"Modèle entraîné et sauvegardé sous {model_path}")
        
        # Sauvegarde des informations du modèle
        model_info = {
            "type": model_type,
            "params": params,
            "features": list(self.matching_engine.feature_weights.keys()),
            "performance": {
                "mse": float(mse),
                "ndcg": float(avg_ndcg) if 'avg_ndcg' in locals() else None,
                "n_samples": len(X_train) + len(X_test)
            },
            "training_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(self.models_path / f"{model_type}_info.json", "w") as f:
            json.dump(model_info, f, indent=2)
        
        return model
    
    def train_both_models(self, candidates=None, jobs=None, matches=None, num_candidates=100, num_jobs=50, num_matches=1000):
        """
        Entraîne les deux modèles (candidat et job) sur des données synthétiques ou fournies.
        
        Args:
            candidates: Liste de profils candidats (optionnel)
            jobs: Liste d'offres d'emploi (optionnel)
            matches: Liste de matchs avec scores (optionnel)
            num_candidates: Nombre de candidats à générer si données non fournies
            num_jobs: Nombre d'offres à générer si données non fournies
            num_matches: Nombre de matchs à générer si données non fournies
            
        Returns:
            Dict: Résultats de l'entraînement
        """
        # Génération ou utilisation des données fournies
        if candidates is None or jobs is None:
            candidates, jobs = self.generate_synthetic_data(num_candidates, num_jobs)
        
        if matches is None:
            matches = self.generate_synthetic_matches(candidates, jobs, num_matches)
        
        # Préparation des données
        X_train, X_test, y_train, y_test = self.prepare_training_data(candidates, jobs, matches)
        
        # Entraînement des modèles
        candidate_model = self.train_model(X_train, y_train, X_test, y_test, "candidate_ranking")
        job_model = self.train_model(X_train, y_train, X_test, y_test, "job_ranking")
        
        # Mettre à jour le moteur de matching pour utiliser les nouveaux modèles
        self.matching_engine.load_models(
            str(self.models_path / "candidate_ranking_model.json"),
            str(self.models_path / "job_ranking_model.json")
        )
        
        logger.info("Entraînement des deux modèles terminé avec succès")
        
        return {
            "candidate_model": candidate_model,
            "job_model": job_model,
            "scaler": self.scaler,
            "data_summary": {
                "n_candidates": len(candidates),
                "n_jobs": len(jobs),
                "n_matches": len(matches),
                "n_train": len(X_train),
                "n_test": len(X_test)
            }
        }


def train_models():
    """
    Fonction principale pour l'entraînement des modèles
    """
    trainer = XGBoostModelTrainer()
    result = trainer.train_both_models()
    
    logger.info("Modèles entraînés avec succès")
    logger.info(f"Résumé des données: {result['data_summary']}")
    
    return result


if __name__ == "__main__":
    try:
        train_models()
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement des modèles: {e}", exc_info=True)
