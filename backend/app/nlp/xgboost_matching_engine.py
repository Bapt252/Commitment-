import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path
import json
import re
import spacy
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split, GridSearchCV
import shap

class XGBoostMatchingEngine:
    """
    Moteur de matching avancé basé sur XGBoost pour la recommandation
    entre candidats et offres d'emploi.
    """
    
    def __init__(self, config_path=None):
        """
        Initialise le moteur de matching avec les configurations nécessaires.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.logger = logging.getLogger(__name__)
        
        # Chargement des configurations de matching
        self.load_matching_config(config_path)
        
        # Initialisation des modèles XGBoost
        self.candidate_ranking_model = None
        self.job_ranking_model = None
        
        # Vectorizer pour le calcul de similarité textuelle
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.85,
            stop_words=['french', 'english'],
            use_idf=True
        )
        
        # Scaler pour normaliser les features numériques
        self.scaler = StandardScaler()
        
        # Modèle spaCy pour l'analyse linguistique
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except:
            self.logger.warning("Modèle fr_core_news_md non trouvé, téléchargement en cours...")
            spacy.cli.download("fr_core_news_md")
            self.nlp = spacy.load("fr_core_news_md")
        
        # Initialisation de l'explainer SHAP
        self.explainer = None
    
    def load_matching_config(self, config_path=None):
        """
        Charge les paramètres de configuration pour le matching
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        try:
            # Chemin par défaut si non spécifié
            if not config_path:
                config_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_matching_config.json"
            
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.feature_weights = config.get("feature_weights", {})
                    self.xgboost_params = config.get("xgboost_params", {})
            else:
                # Configuration par défaut
                self.feature_weights = {
                    "skills_similarity": 1.0,
                    "experience_match": 0.8,
                    "education_match": 0.7,
                    "values_alignment": 0.8,
                    "cultural_fit": 0.6,
                    "location_match": 0.5,
                    "salary_match": 0.6,
                    "job_title_similarity": 0.9,
                    "work_mode_match": 0.5,
                    "role_requirements_match": 0.7
                }
                
                self.xgboost_params = {
                    "objective": "rank:pairwise",
                    "eval_metric": "ndcg@10",
                    "learning_rate": 0.1,
                    "max_depth": 6,
                    "min_child_weight": 1,
                    "gamma": 0.1,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "tree_method": "hist",
                    "random_state": 42
                }
                
                # Créer le répertoire data s'il n'existe pas
                data_dir = Path(config_path).parent
                data_dir.mkdir(exist_ok=True, parents=True)
                
                # Sauvegarder la configuration par défaut
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "feature_weights": self.feature_weights,
                        "xgboost_params": self.xgboost_params
                    }, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration de matching: {e}")
            
            # Utiliser des valeurs par défaut
            self.feature_weights = {
                "skills_similarity": 1.0,
                "experience_match": 0.8,
                "education_match": 0.7,
                "values_alignment": 0.8,
                "cultural_fit": 0.6,
                "location_match": 0.5,
                "salary_match": 0.6,
                "job_title_similarity": 0.9,
                "work_mode_match": 0.5,
                "role_requirements_match": 0.7
            }
            
            self.xgboost_params = {
                "objective": "rank:pairwise",
                "eval_metric": "ndcg@10",
                "learning_rate": 0.1,
                "max_depth": 6,
                "min_child_weight": 1,
                "gamma": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "tree_method": "hist",
                "random_state": 42
            }
    
    ## 2. Génération et normalisation des features
    
    def generate_matching_features(self, candidate_profile, job_profile):
        """
        Génère l'ensemble des features pour l'évaluation du matching entre un candidat et une offre
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Features normalisées pour le matching
        """
        features = {}
        
        # 1. Matching technique des compétences
        features["skills_similarity"] = self.calculate_skills_similarity(
            candidate_profile.get("competences", []),
            job_profile.get("required_skills", [])
        )
        
        features["skills_coverage"] = self.calculate_skills_coverage(
            candidate_profile.get("competences", []),
            job_profile.get("required_skills", [])
        )
        
        features["skills_expertise_match"] = self.calculate_skills_expertise_match(
            candidate_profile.get("skills_with_level", {}),
            job_profile.get("required_skills_with_level", {})
        )
        
        # 2. Matching d'expérience
        features["experience_years_match"] = self.calculate_experience_years_match(
            candidate_profile.get("experience_years", 0),
            job_profile.get("required_experience_years", 0)
        )
        
        features["relevant_experience_match"] = self.calculate_relevant_experience_match(
            candidate_profile.get("experience", []),
            job_profile.get("job_description", "")
        )
        
        # 3. Matching de formation
        features["education_level_match"] = self.calculate_education_level_match(
            candidate_profile.get("education_level", ""),
            job_profile.get("required_education_level", "")
        )
        
        features["education_field_match"] = self.calculate_education_field_match(
            candidate_profile.get("education_field", ""),
            job_profile.get("preferred_education_field", "")
        )
        
        # 4. Alignement culturel et préférentiel
        features["values_alignment"] = self.calculate_values_alignment(
            candidate_profile.get("values", {}),
            job_profile.get("company_values", {})
        )
        
        features["work_environment_match"] = self.calculate_work_environment_match(
            candidate_profile.get("work_preferences", {}),
            job_profile.get("work_environment", {})
        )
        
        features["location_match"] = self.calculate_location_match(
            candidate_profile.get("preferred_location", ""),
            job_profile.get("location", "")
        )
        
        features["work_mode_match"] = self.calculate_work_mode_match(
            candidate_profile.get("preferred_work_mode", ""),
            job_profile.get("work_mode", "")
        )
        
        features["salary_match"] = self.calculate_salary_match(
            candidate_profile.get("expected_salary", {}),
            job_profile.get("salary_range", {})
        )
        
        # 5. Similarité textuelle
        features["job_title_similarity"] = self.calculate_text_similarity(
            candidate_profile.get("job_title", ""),
            job_profile.get("job_title", "")
        )
        
        features["job_description_similarity"] = self.calculate_text_similarity(
            " ".join([exp.get("description", "") for exp in candidate_profile.get("experience", [])]),
            job_profile.get("job_description", "")
        )
        
        # 6. Variables contextuelles
        features["company_size_preference_match"] = self.calculate_company_size_preference(
            candidate_profile.get("preferred_company_size", ""),
            job_profile.get("company_size", "")
        )
        
        features["industry_preference_match"] = self.calculate_industry_preference(
            candidate_profile.get("preferred_industries", []),
            job_profile.get("industry", "")
        )
        
        return features
    
    def normalize_features(self, features_dict):
        """
        Normalise les features pour l'entrée du modèle XGBoost
        
        Args:
            features_dict: Dictionnaire de features brutes
            
        Returns:
            np.array: Array de features normalisées
        """
        features_array = np.array([[
            features_dict["skills_similarity"],
            features_dict["skills_coverage"],
            features_dict["skills_expertise_match"],
            features_dict["experience_years_match"],
            features_dict["relevant_experience_match"],
            features_dict["education_level_match"],
            features_dict["education_field_match"],
            features_dict["values_alignment"],
            features_dict["work_environment_match"],
            features_dict["location_match"],
            features_dict["work_mode_match"],
            features_dict["salary_match"],
            features_dict["job_title_similarity"],
            features_dict["job_description_similarity"],
            features_dict["company_size_preference_match"],
            features_dict["industry_preference_match"]
        ]])
        
        # Appliquer la normalisation si le scaler est ajusté
        if hasattr(self.scaler, 'mean_'):
            return self.scaler.transform(features_array)
        else:
            return features_array
    
    # Méthodes détaillées de calcul des features
    
    def calculate_skills_similarity(self, candidate_skills, job_skills):
        """Calcule la similarité des compétences basée sur TF-IDF"""
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Normaliser les compétences
        candidate_skills_text = " ".join([s.lower() for s in candidate_skills if s])
        job_skills_text = " ".join([s.lower() for s in job_skills if s])
        
        if not candidate_skills_text or not job_skills_text:
            return 0.0
        
        # Vectoriser les textes
        try:
            tfidf_matrix = self.vectorizer.fit_transform([candidate_skills_text, job_skills_text])
            # Calculer la similarité cosinus
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except:
            # Fallback en cas d'erreur avec TF-IDF
            common_skills = sum(1 for s in job_skills if any(s.lower() in c.lower() or c.lower() in s.lower() 
                                                           for c in candidate_skills))
            return common_skills / max(len(job_skills), 1)
    
    def calculate_skills_coverage(self, candidate_skills, job_skills):
        """Calcule le pourcentage de compétences requises couvertes par le candidat"""
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Normaliser les compétences
        candidate_skills_norm = [s.lower() for s in candidate_skills if s]
        job_skills_norm = [s.lower() for s in job_skills if s]
        
        if not candidate_skills_norm or not job_skills_norm:
            return 0.0
        
        # Compter les compétences requises couvertes
        covered_skills = sum(1 for skill in job_skills_norm 
                           if any(skill in c_skill or c_skill in skill 
                                for c_skill in candidate_skills_norm))
        
        return covered_skills / len(job_skills_norm)
    
    def calculate_skills_expertise_match(self, candidate_skills_levels, job_skills_levels):
        """Compare les niveaux d'expertise des compétences"""
        if not candidate_skills_levels or not job_skills_levels:
            return 0.5
        
        # Normaliser les niveaux
        level_values = {
            "débutant": 1, "beginner": 1, "junior": 1,
            "intermédiaire": 2, "intermediate": 2, "medium": 2,
            "avancé": 3, "advanced": 3, "confirmé": 3,
            "expert": 4, "maître": 4, "master": 4, "senior": 4
        }
        
        # Évaluer les correspondances de niveau
        match_scores = []
        
        for job_skill, job_level in job_skills_levels.items():
            job_level_value = level_values.get(job_level.lower(), 2)
            
            # Chercher la meilleure correspondance
            best_match = 0
            for cand_skill, cand_level in candidate_skills_levels.items():
                if job_skill.lower() in cand_skill.lower() or cand_skill.lower() in job_skill.lower():
                    cand_level_value = level_values.get(cand_level.lower(), 2)
                    
                    # Calculer la correspondance (1.0 si exact, 0.8 si supérieur, 0.5 si un niveau en dessous)
                    if cand_level_value >= job_level_value:
                        best_match = max(best_match, 1.0)
                    elif cand_level_value == job_level_value - 1:
                        best_match = max(best_match, 0.5)
                    else:
                        best_match = max(best_match, 0.2)
            
            if best_match > 0:
                match_scores.append(best_match)
        
        # Retourner la moyenne des correspondances
        return sum(match_scores) / max(len(match_scores), 1)
    
    def calculate_experience_years_match(self, candidate_years, required_years):
        """Compare les années d'expérience"""
        if candidate_years is None or required_years is None:
            return 0.5
        
        # Si le candidat répond aux exigences
        if candidate_years >= required_years:
            # Pénalité légère pour surqualification importante
            if candidate_years > required_years * 2:
                return 0.85
            else:
                return 1.0
        else:
            # Score proportionnel
            return min(0.95, candidate_years / max(required_years, 1))
    
    def calculate_relevant_experience_match(self, candidate_experiences, job_description):
        """Évalue la pertinence de l'expérience du candidat pour le poste"""
        if not candidate_experiences or not job_description:
            return 0.5
        
        # Extraire les descriptions des expériences
        experience_texts = []
        for exp in candidate_experiences:
            if isinstance(exp, dict) and "description" in exp:
                experience_texts.append(exp["description"])
            elif isinstance(exp, str):
                experience_texts.append(exp)
        
        if not experience_texts:
            return 0.5
        
        # Calculer la similarité avec la description du poste
        combined_experience = " ".join(experience_texts)
        return self.calculate_text_similarity(combined_experience, job_description)
    
    def calculate_education_level_match(self, candidate_level, required_level):
        """Compare les niveaux d'éducation"""
        if not candidate_level or not required_level:
            return 0.5
        
        # Niveaux d'éducation normalisés
        education_levels = {
            "bac": 1, "high school": 1, "secondary": 1,
            "bac+2": 2, "associate": 2, "dut": 2, "bts": 2,
            "bac+3": 3, "bachelor": 3, "licence": 3, "graduate": 3,
            "bac+4": 3.5, "maîtrise": 3.5,
            "bac+5": 4, "master": 4, "msc": 4, "mba": 4, "ingénieur": 4,
            "phd": 5, "doctorat": 5, "doctorate": 5
        }
        
        # Convertir en valeurs numériques
        candidate_value = 3  # Valeur par défaut (niveau licence)
        required_value = 3  # Valeur par défaut
        
        # Rechercher les niveaux dans les textes
        for level_name, level_value in education_levels.items():
            if level_name in candidate_level.lower():
                candidate_value = level_value
            if level_name in required_level.lower():
                required_value = level_value
        
        # Calculer la correspondance
        if candidate_value >= required_value:
            # Pénalité légère pour surqualification
            if candidate_value > required_value + 1:
                return 0.9
            else:
                return 1.0
        else:
            # Score proportionnel
            return 0.7 * (candidate_value / required_value)
    
    def calculate_education_field_match(self, candidate_field, job_field):
        """Évalue la correspondance des domaines d'étude"""
        if not candidate_field or not job_field:
            return 0.5
        
        return self.calculate_text_similarity(candidate_field, job_field)
    
    def calculate_values_alignment(self, candidate_values, company_values):
        """Mesure l'alignement des valeurs personnelles et d'entreprise"""
        if not candidate_values or not company_values:
            return 0.5
        
        # Extraire les valeurs explicites
        candidate_values_list = []
        company_values_list = []
        
        # Extraction des valeurs du candidat
        if isinstance(candidate_values, dict):
            if "explicit_values" in candidate_values:
                candidate_values_list = candidate_values["explicit_values"]
            elif "detected_values" in candidate_values:
                candidate_values_list = list(candidate_values["detected_values"].keys())
        elif isinstance(candidate_values, list):
            candidate_values_list = candidate_values
        elif isinstance(candidate_values, str):
            candidate_values_list = [v.strip() for v in candidate_values.split(',')]
        
        # Extraction des valeurs de l'entreprise
        if isinstance(company_values, dict):
            if "explicit_values" in company_values:
                company_values_list = company_values["explicit_values"]
            elif "detected_values" in company_values:
                company_values_list = list(company_values["detected_values"].keys())
        elif isinstance(company_values, list):
            company_values_list = company_values
        elif isinstance(company_values, str):
            company_values_list = [v.strip() for v in company_values.split(',')]
        
        # Si on a des valeurs des deux côtés
        if candidate_values_list and company_values_list:
            # Normalisation
            candidate_norm = [v.lower() for v in candidate_values_list]
            company_norm = [v.lower() for v in company_values_list]
            
            # Calcul de correspondance directe
            matches = sum(1 for v in company_norm 
                         if any(v in c or c in v for c in candidate_norm))
            
            return matches / max(len(company_norm), 1)
        else:
            return 0.5
    
    def calculate_work_environment_match(self, candidate_prefs, job_env):
        """Évalue la compatibilité entre préférences et environnement de travail"""
        if not candidate_prefs or not job_env:
            return 0.5
        
        match_points = 0
        total_factors = 0
        
        # Facteurs d'environnement de travail à comparer
        factors = ["team_size", "management_style", "company_culture", "pace"]
        
        for factor in factors:
            if factor in candidate_prefs and factor in job_env:
                total_factors += 1
                candidate_val = candidate_prefs[factor]
                job_val = job_env[factor]
                
                # Correspondance exacte
                if candidate_val == job_val:
                    match_points += 1
                # Correspondance partielle pour certains facteurs
                elif factor == "team_size":
                    # Petite différence de taille
                    sizes = ["small", "medium", "large"]
                    if abs(sizes.index(candidate_val) - sizes.index(job_val)) == 1:
                        match_points += 0.5
                elif factor == "pace":
                    paces = ["relaxed", "balanced", "fast-paced"]
                    if abs(paces.index(candidate_val) - paces.index(job_val)) == 1:
                        match_points += 0.5
        
        return match_points / max(total_factors, 1) if total_factors > 0 else 0.5
    
    def calculate_location_match(self, candidate_location, job_location):
        """Évalue la correspondance géographique"""
        if not candidate_location or not job_location:
            return 0.5
        
        # Simplification: check basique de correspondance de texte
        # Dans un système réel, on utiliserait une API de géocodage
        candidate_location = candidate_location.lower()
        job_location = job_location.lower()
        
        # Correspondance exacte ou partielle
        if candidate_location == job_location:
            return 1.0
        elif candidate_location in job_location or job_location in candidate_location:
            return 0.8
        else:
            # Vérifier les correspondances de ville/région/pays
            tokens_candidate = set(re.findall(r'\w+', candidate_location))
            tokens_job = set(re.findall(r'\w+', job_location))
            common_tokens = tokens_candidate.intersection(tokens_job)
            
            if common_tokens:
                return 0.6
            else:
                return 0.2
    
    def calculate_work_mode_match(self, candidate_mode, job_mode):
        """Compare les modes de travail (remote, hybrid, onsite)"""
        if not candidate_mode or not job_mode:
            return 0.5
        
        # Normaliser
        if isinstance(candidate_mode, str):
            candidate_mode = [candidate_mode.lower()]
        else:
            candidate_mode = [m.lower() for m in candidate_mode]
            
        if isinstance(job_mode, str):
            job_mode = [job_mode.lower()]
        else:
            job_mode = [m.lower() for m in job_mode]
        
        # Mapper les différents termes
        remote_terms = ["remote", "télétravail", "teletravail", "à distance", "a distance"]
        hybrid_terms = ["hybrid", "hybride", "mixed", "mixte", "flexible"]
        onsite_terms = ["onsite", "sur site", "office", "bureau", "présentiel", "presentiel"]
        
        # Déterminer les catégories
        def categorize_mode(modes):
            categories = set()
            for mode in modes:
                if any(term in mode for term in remote_terms):
                    categories.add("remote")
                if any(term in mode for term in hybrid_terms):
                    categories.add("hybrid")
                if any(term in mode for term in onsite_terms):
                    categories.add("onsite")
            return categories
        
        candidate_categories = categorize_mode(candidate_mode)
        job_categories = categorize_mode(job_mode)
        
        # Évaluer la correspondance
        if not candidate_categories or not job_categories:
            return 0.5
        
        if candidate_categories.intersection(job_categories):
            return 1.0
        elif "hybrid" in job_categories:
            return 0.8  # Hybride est souvent un bon compromis
        else:
            return 0.3
    
    def calculate_salary_match(self, candidate_salary, job_salary):
        """Évalue la correspondance des attentes salariales"""
        if not candidate_salary or not job_salary:
            return 0.5
        
        # Extraire les valeurs min et max
        candidate_min = candidate_salary.get("min", 0)
        candidate_max = candidate_salary.get("max", 0) or candidate_salary.get("expected", 0)
        
        job_min = job_salary.get("min", 0)
        job_max = job_salary.get("max", 0)
        
        # Si on n'a pas assez d'informations
        if (candidate_min == 0 and candidate_max == 0) or (job_min == 0 and job_max == 0):
            return 0.5
        
        # Si le candidat a seulement une valeur attendue
        if candidate_min == 0 and candidate_max > 0:
            candidate_min = candidate_max * 0.9
        
        # Si l'offre a seulement une valeur
        if job_min > 0 and job_max == 0:
            job_max = job_min * 1.2
        
        # Évaluer le chevauchement
        if candidate_max < job_min:
            # Candidat demande moins que le minimum offert
            return 1.0  # Excellent pour l'entreprise
        elif candidate_min > job_max:
            # Candidat demande plus que le maximum offert
            overlap_ratio = job_max / candidate_min
            return max(0.1, overlap_ratio * 0.8)  # Mauvais match
        else:
            # Chevauchement des fourchettes
            range_overlap = min(candidate_max, job_max) - max(candidate_min, job_min)
            candidate_range = candidate_max - candidate_min
            job_range = job_max - job_min
            
            overlap_ratio = range_overlap / min(candidate_range, job_range)
            return min(1.0, overlap_ratio + 0.3)  # Bonus pour l'intersection
    
    def calculate_text_similarity(self, text1, text2):
        """Calcule la similarité entre deux textes"""
        if not text1 or not text2:
            return 0.0
        
        # Nettoyage basique
        text1 = str(text1).lower()
        text2 = str(text2).lower()
        
        # Vectorisation TF-IDF et similarité cosinus
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            return float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except:
            # Fallback simple
            words1 = set(re.findall(r'\w+', text1))
            words2 = set(re.findall(r'\w+', text2))
            
            if not words1 or not words2:
                return 0.0
                
            common_words = words1.intersection(words2)
            return len(common_words) / max(len(words1), len(words2))
    
    def calculate_company_size_preference(self, preferred_size, actual_size):
        """Évalue la correspondance de taille d'entreprise"""
        if not preferred_size or not actual_size:
            return 0.5
        
        # Normaliser les tailles
        size_values = {
            "startup": 1, "petite": 1, "small": 1,
            "pme": 2, "moyenne": 2, "medium": 2, "sme": 2,
            "grande": 3, "large": 3, "big": 3,
            "très grande": 4, "very large": 4, "corporate": 4, "enterprise": 4
        }
        
        # Convertir en valeurs numériques
        preferred_value = 0
        actual_value = 0
        
        for size_name, size_value in size_values.items():
            if size_name in str(preferred_size).lower():
                preferred_value = size_value
            if size_name in str(actual_size).lower():
                actual_value = size_value
        
        # Si une valeur manque
        if preferred_value == 0 or actual_value == 0:
            return 0.5
        
        # Calculer la proximité
        difference = abs(preferred_value - actual_value)
        if difference == 0:
            return 1.0
        elif difference == 1:
            return 0.7
        elif difference == 2:
            return 0.4
        else:
            return 0.2
    
    def calculate_industry_preference(self, preferred_industries, actual_industry):
        """Vérifie si l'industrie du poste correspond aux préférences du candidat"""
        if not preferred_industries or not actual_industry:
            return 0.5
        
        if isinstance(preferred_industries, str):
            preferred_industries = [preferred_industries]
        
        actual_industry = actual_industry.lower()
        
        # Vérifier les correspondances
        for industry in preferred_industries:
            industry = industry.lower()
            if industry in actual_industry or actual_industry in industry:
                return 1.0
        
        # Vérifier les correspondances partielles
        for industry in preferred_industries:
            tokens_preferred = set(re.findall(r'\w+', industry.lower()))
            tokens_actual = set(re.findall(r'\w+', actual_industry))
            
            common_tokens = tokens_preferred.intersection(tokens_actual)
            if common_tokens:
                return 0.7
        
        return 0.3
    
    ## 3. Stratégie d'entraînement du modèle
    
    def prepare_training_data(self, candidates, jobs, matches=None):
        """
        Prépare les données d'entraînement pour le modèle XGBoost
        
        Args:
            candidates: Liste des profils de candidats
            jobs: Liste des profils de postes
            matches: Données de matching existantes (optionnel)
            
        Returns:
            Tuple: (X_train, y_train) pour l'entraînement du modèle
        """
        # Données de features et labels
        features_list = []
        labels = []
        
        if matches:
            # Utiliser des données de matching existantes
            for match in matches:
                candidate_id = match.get("candidate_id")
                job_id = match.get("job_id")
                relevance = match.get("relevance", 0)
                
                # Trouver les profils correspondants
                candidate = next((c for c in candidates if c.get("id") == candidate_id), None)
                job = next((j for j in jobs if j.get("id") == job_id), None)
                
                if candidate and job:
                    # Générer les features pour cette paire
                    features = self.generate_matching_features(candidate, job)
                    features_list.append(list(features.values()))
                    labels.append(relevance)
        else:
            # Générer des données de matching synthétiques
            for candidate in candidates:
                for job in jobs:
                    # Générer les features
                    features = self.generate_matching_features(candidate, job)
                    features_list.append(list(features.values()))
                    
                    # Générer un score synthétique basé sur les heuristiques
                    synthetic_score = (
                        features["skills_similarity"] * 0.3 +
                        features["experience_years_match"] * 0.2 +
                        features["education_level_match"] * 0.15 +
                        features["job_title_similarity"] * 0.2 +
                        features["values_alignment"] * 0.15
                    )
                    
                    labels.append(synthetic_score)
        
        # Convertir en arrays numpy
        X = np.array(features_list)
        y = np.array(labels)
        
        # Normaliser les features
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        return X_scaled, y
    
    def train_model(self, X_train, y_train, model_type="candidate_ranking"):
        """
        Entraîne le modèle XGBoost pour le ranking
        
        Args:
            X_train: Features d'entraînement
            y_train: Labels d'entraînement
            model_type: Type de modèle à entraîner (candidate_ranking ou job_ranking)
            
        Returns:
            model: Modèle XGBoost entraîné
        """
        try:
            # Séparation train/validation
            X_train_split, X_val, y_train_split, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42
            )
            
            # Préparation des ensembles de données XGBoost
            dtrain = xgb.DMatrix(X_train_split, label=y_train_split)
            dval = xgb.DMatrix(X_val, label=y_val)
            
            # Définir les paramètres de base
            params = self.xgboost_params.copy()
            
            # Adapter les paramètres selon le type de modèle
            if model_type == "candidate_ranking":
                params["objective"] = "rank:pairwise"
            else:
                params["objective"] = "rank:pairwise"
            
            # Entrainement avec early stopping
            model = xgb.train(
                params,
                dtrain,
                num_boost_round=1000,
                evals=[(dtrain, 'train'), (dval, 'val')],
                early_stopping_rounds=50,
                verbose_eval=100
            )
            
            # Enregistrement du modèle selon son type
            if model_type == "candidate_ranking":
                self.candidate_ranking_model = model
            else:
                self.job_ranking_model = model
            
            # Initialiser l'explainer SHAP pour ce modèle
            self.explainer = shap.TreeExplainer(model)
            
            return model
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'entraînement du modèle: {e}")
            return None
    
    def tune_hyperparameters(self, X_train, y_train):
        """
        Optimise les hyperparamètres du modèle XGBoost
        
        Args:
            X_train: Features d'entraînement
            y_train: Labels d'entraînement
            
        Returns:
            Dict: Meilleurs hyperparamètres
        """
        # Définir l'espace de recherche
        param_grid = {
            'max_depth': [3, 4, 5, 6],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'min_child_weight': [1, 3, 5],
            'gamma': [0, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0]
        }
        
        # Initialiser le modèle de base
        model = xgb.XGBRanker(
            objective='rank:pairwise',
            eval_metric='ndcg@10',
            tree_method='hist',
            random_state=42
        )
        
        # Recherche par grille avec validation croisée
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            scoring='neg_mean_squared_error',
            cv=3,
            verbose=1
        )
        
        # Exécuter la recherche
        grid_search.fit(X_train, y_train)
        
        # Mettre à jour les paramètres XGBoost
        self.xgboost_params.update(grid_search.best_params_)
        
        # Sauvegarder la configuration
        config_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_matching_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({
                "feature_weights": self.feature_weights,
                "xgboost_params": self.xgboost_params
            }, f, indent=2)
        
        return grid_search.best_params_
    
    ## 4. Méthodes de prédiction et ranking
    
    def rank_candidates_for_job(self, candidates, job_profile, limit=10):
        """
        Classe les candidats par pertinence pour une offre d'emploi
        
        Args:
            candidates: Liste des profils de candidats
            job_profile: Profil de l'offre d'emploi
            limit: Nombre maximum de résultats
            
        Returns:
            List: Candidats classés avec scores et explications
        """
        try:
            # Vérifier si le modèle est entraîné
            if self.candidate_ranking_model is None:
                # Utiliser une approche basée sur les heuristiques
                return self._rank_candidates_heuristic(candidates, job_profile, limit)
            
            # Générer les features pour chaque candidat
            candidates_features = []
            for candidate in candidates:
                features = self.generate_matching_features(candidate, job_profile)
                candidates_features.append(features)
            
            # Normaliser les features
            features_array = np.array([[list(f.values()) for f in candidates_features]])
            features_normalized = self.scaler.transform(features_array[0])
            
            # Prédire les scores de pertinence
            dmatrix = xgb.DMatrix(features_normalized)
            relevance_scores = self.candidate_ranking_model.predict(dmatrix)
            
            # Créer les explications
            explanations = []
            for i, candidate in enumerate(candidates):
                # Générer les explications SHAP
                shap_values = self.explainer.shap_values(features_normalized[i:i+1])[0]
                
                # Obtenir les features les plus importantes
                feature_names = list(candidates_features[i].keys())
                feature_importance = [(feature_names[j], shap_values[j]) for j in range(len(feature_names))]
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
                # Traduire en explications lisibles
                top_factors = self._generate_explanations(feature_importance[:3], candidates_features[i], "candidate")
                
                explanations.append({
                    "top_factors": top_factors,
                    "feature_importance": {k: float(v) for k, v in feature_importance[:5]}
                })
            
            # Créer le classement
            ranked_candidates = []
            for i, (candidate, score) in enumerate(zip(candidates, relevance_scores)):
                ranked_candidates.append({
                    "candidate_id": candidate.get("id", f"candidate_{i}"),
                    "candidate_name": candidate.get("name", f"Candidat {i+1}"),
                    "relevance_score": float(score),
                    "normalized_score": min(100, max(0, float(score * 100))),
                    "explanation": explanations[i]
                })
            
            # Trier par score de pertinence décroissant
            ranked_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_candidates[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement des candidats: {e}")
            return []
    
    def _rank_candidates_heuristic(self, candidates, job_profile, limit=10):
        """
        Méthode de repli utilisée lorsque le modèle n'est pas entraîné
        """
        try:
            ranked_candidates = []
            
            for i, candidate in enumerate(candidates):
                # Générer les features
                features = self.generate_matching_features(candidate, job_profile)
                
                # Calcul heuristique du score de pertinence
                relevance_score = (
                    features["skills_similarity"] * 0.3 +
                    features["experience_years_match"] * 0.2 +
                    features["education_level_match"] * 0.15 +
                    features["job_title_similarity"] * 0.2 +
                    features["values_alignment"] * 0.15
                )
                
                # Générer des explications simples
                top_factors = []
                
                # Compétences
                skills_match = features["skills_similarity"]
                if skills_match > 0.7:
                    top_factors.append(f"Forte correspondance de compétences ({int(skills_match*100)}%)")
                elif skills_match > 0.4:
                    top_factors.append(f"Correspondance moyenne de compétences ({int(skills_match*100)}%)")
                else:
                    top_factors.append(f"Faible correspondance de compétences ({int(skills_match*100)}%)")
                
                # Expérience
                exp_match = features["experience_years_match"]
                if exp_match > 0.8:
                    top_factors.append("Expérience parfaitement adaptée au poste")
                elif exp_match > 0.5:
                    top_factors.append("Expérience partiellement adaptée au poste")
                else:
                    top_factors.append("Expérience insuffisante pour le poste")
                
                # Formation
                edu_match = features["education_level_match"]
                if edu_match > 0.8:
                    top_factors.append("Formation correspondant aux exigences")
                elif edu_match > 0.5:
                    top_factors.append("Formation partiellement adaptée")
                else:
                    top_factors.append("Formation ne correspondant pas aux exigences")
                
                ranked_candidates.append({
                    "candidate_id": candidate.get("id", f"candidate_{i}"),
                    "candidate_name": candidate.get("name", f"Candidat {i+1}"),
                    "relevance_score": float(relevance_score),
                    "normalized_score": min(100, max(0, float(relevance_score * 100))),
                    "explanation": {
                        "top_factors": top_factors,
                        "feature_importance": {
                            "skills_similarity": 0.3,
                            "experience_years_match": 0.2,
                            "education_level_match": 0.15,
                            "job_title_similarity": 0.2,
                            "values_alignment": 0.15
                        }
                    }
                })
            
            # Trier par score de pertinence décroissant
            ranked_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_candidates[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement heuristique des candidats: {e}")
            return []
    
    def rank_jobs_for_candidate(self, jobs, candidate_profile, limit=10):
        """
        Classe les offres d'emploi par pertinence pour un candidat
        
        Args:
            jobs: Liste des profils d'offres d'emploi
            candidate_profile: Profil du candidat
            limit: Nombre maximum de résultats
            
        Returns:
            List: Offres classées avec scores et explications
        """
        try:
            # Vérifier si le modèle est entraîné
            if self.job_ranking_model is None:
                # Utiliser le modèle de ranking candidat à l'envers ou une approche heuristique
                return self._rank_jobs_heuristic(jobs, candidate_profile, limit)
            
            # Générer les features pour chaque offre
            jobs_features = []
            for job in jobs:
                features = self.generate_matching_features(candidate_profile, job)
                jobs_features.append(features)
            
            # Normaliser les features
            features_array = np.array([[list(f.values()) for f in jobs_features]])
            features_normalized = self.scaler.transform(features_array[0])
            
            # Prédire les scores de pertinence
            dmatrix = xgb.DMatrix(features_normalized)
            relevance_scores = self.job_ranking_model.predict(dmatrix)
            
            # Créer les explications
            explanations = []
            for i, job in enumerate(jobs):
                # Générer les explications SHAP
                shap_values = self.explainer.shap_values(features_normalized[i:i+1])[0]
                
                # Obtenir les features les plus importantes
                feature_names = list(jobs_features[i].keys())
                feature_importance = [(feature_names[j], shap_values[j]) for j in range(len(feature_names))]
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
                # Traduire en explications lisibles
                top_factors = self._generate_explanations(feature_importance[:3], jobs_features[i], "job")
                
                explanations.append({
                    "top_factors": top_factors,
                    "feature_importance": {k: float(v) for k, v in feature_importance[:5]}
                })
            
            # Créer le classement
            ranked_jobs = []
            for i, (job, score) in enumerate(zip(jobs, relevance_scores)):
                ranked_jobs.append({
                    "job_id": job.get("id", f"job_{i}"),
                    "job_title": job.get("job_title", f"Poste {i+1}"),
                    "company_name": job.get("company_name", "Entreprise"),
                    "relevance_score": float(score),
                    "normalized_score": min(100, max(0, float(score * 100))),
                    "explanation": explanations[i]
                })
            
            # Trier par score de pertinence décroissant
            ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement des offres: {e}")
            return []
    
    def _rank_jobs_heuristic(self, jobs, candidate_profile, limit=10):
        """
        Méthode de repli utilisée lorsque le modèle n'est pas entraîné
        """
        try:
            ranked_jobs = []
            
            for i, job in enumerate(jobs):
                # Générer les features
                features = self.generate_matching_features(candidate_profile, job)
                
                # Calcul heuristique du score de pertinence
                relevance_score = (
                    features["skills_similarity"] * 0.3 +
                    features["experience_years_match"] * 0.2 +
                    features["education_level_match"] * 0.15 +
                    features["job_title_similarity"] * 0.2 +
                    features["values_alignment"] * 0.15
                )
                
                # Générer des explications simples
                top_factors = []
                
                # Compétences
                skills_match = features["skills_similarity"]
                if skills_match > 0.7:
                    top_factors.append(f"Vos compétences correspondent parfaitement ({int(skills_match*100)}%)")
                elif skills_match > 0.4:
                    top_factors.append(f"Vos compétences correspondent partiellement ({int(skills_match*100)}%)")
                else:
                    top_factors.append(f"Peu de correspondance avec vos compétences ({int(skills_match*100)}%)")
                
                # Expérience
                exp_match = features["experience_years_match"]
                if exp_match > 0.8:
                    top_factors.append("Votre expérience est parfaitement adaptée")
                elif exp_match > 0.5:
                    top_factors.append("Votre expérience est partiellement adaptée")
                else:
                    top_factors.append("Votre expérience est inférieure aux exigences")
                
                # Titre du poste
                title_match = features["job_title_similarity"]
                if title_match > 0.7:
                    top_factors.append("Ce poste correspond à votre profil professionnel")
                elif title_match > 0.4:
                    top_factors.append("Ce poste est similaire à votre profil")
                else:
                    top_factors.append("Ce poste diffère de votre profil habituel")
                
                ranked_jobs.append({
                    "job_id": job.get("id", f"job_{i}"),
                    "job_title": job.get("job_title", f"Poste {i+1}"),
                    "company_name": job.get("company_name", "Entreprise"),
                    "relevance_score": float(relevance_score),
                    "normalized_score": min(100, max(0, float(relevance_score * 100))),
                    "explanation": {
                        "top_factors": top_factors,
                        "feature_importance": {
                            "skills_similarity": 0.3,
                            "experience_years_match": 0.2,
                            "education_level_match": 0.15,
                            "job_title_similarity": 0.2,
                            "values_alignment": 0.15
                        }
                    }
                })
            
            # Trier par score de pertinence décroissant
            ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement heuristique des offres: {e}")
            return []
    
    ## 5. Méthodes d'explication du matching
    
    def _generate_explanations(self, feature_importance, features, context_type):
        """
        Traduit les valeurs d'importance des features en explications lisibles
        
        Args:
            feature_importance: Liste de tuples (feature_name, importance_value)
            features: Dictionnaire des valeurs de features
            context_type: 'candidate' ou 'job' pour adapter le contexte
            
        Returns:
            List: Explications en langage naturel des facteurs principaux
        """
        explanations = []
        
        # Mappings pour traduire les noms de features en explications
        explanation_templates = {
            "candidate": {
                "skills_similarity": [
                    (0.8, "Forte correspondance des compétences techniques ({value}%)"),
                    (0.5, "Correspondance moyenne des compétences techniques ({value}%)"),
                    (0.0, "Faible correspondance des compétences techniques ({value}%)")
                ],
                "skills_coverage": [
                    (0.8, "Couvre {value}% des compétences requises pour le poste"),
                    (0.5, "Couvre partiellement les compétences requises ({value}%)"),
                    (0.0, "Ne couvre pas suffisamment les compétences requises ({value}%)")
                ],
                "skills_expertise_match": [
                    (0.8, "Niveau d'expertise technique parfaitement adapté"),
                    (0.5, "Niveau d'expertise technique partiellement adapté"),
                    (0.0, "Niveau d'expertise technique insuffisant")
                ],
                "experience_years_match": [
                    (0.8, "Expérience professionnelle parfaitement adaptée"),
                    (0.5, "Expérience professionnelle partiellement adaptée"),
                    (0.0, "Expérience professionnelle insuffisante")
                ],
                "relevant_experience_match": [
                    (0.8, "Expérience très pertinente pour ce poste"),
                    (0.5, "Expérience moyennement pertinente pour ce poste"),
                    (0.0, "Expérience peu pertinente pour ce poste")
                ],
                "education_level_match": [
                    (0.8, "Formation académique parfaitement adaptée"),
                    (0.5, "Formation académique partiellement adaptée"),
                    (0.0, "Formation académique inférieure aux exigences")
                ],
                "education_field_match": [
                    (0.8, "Domaine d'études parfaitement adapté"),
                    (0.5, "Domaine d'études partiellement adapté"),
                    (0.0, "Domaine d'études peu adapté")
                ],
                "values_alignment": [
                    (0.8, "Valeurs personnelles alignées avec la culture d'entreprise"),
                    (0.5, "Valeurs personnelles partiellement alignées"),
                    (0.0, "Valeurs personnelles peu alignées")
                ],
                "work_environment_match": [
                    (0.8, "Environnement de travail adapté aux préférences"),
                    (0.5, "Environnement de travail partiellement adapté"),
                    (0.0, "Environnement de travail peu adapté aux préférences")
                ],
                "location_match": [
                    (0.8, "Localisation idéale"),
                    (0.5, "Localisation acceptable"),
                    (0.0, "Localisation peu favorable")
                ],
                "work_mode_match": [
                    (0.8, "Mode de travail (présentiel/remote) parfaitement adapté"),
                    (0.5, "Mode de travail acceptable"),
                    (0.0, "Mode de travail peu adapté aux préférences")
                ],
                "salary_match": [
                    (0.8, "Salaire correspondant aux attentes"),
                    (0.5, "Salaire partiellement adapté aux attentes"),
                    (0.0, "Salaire inférieur aux attentes")
                ],
                "job_title_similarity": [
                    (0.8, "Poste correspondant parfaitement au profil professionnel"),
                    (0.5, "Poste partiellement similaire au profil"),
                    (0.0, "Poste différent du profil habituel")
                ],
                "job_description_similarity": [
                    (0.8, "Expérience passée très alignée avec le poste"),
                    (0.5, "Expérience passée partiellement alignée"),
                    (0.0, "Expérience passée peu alignée avec le poste")
                ]
            },
            "job": {
                "skills_similarity": [
                    (0.8, "Vos compétences correspondent parfaitement à cette offre ({value}%)"),
                    (0.5, "Vos compétences correspondent partiellement ({value}%)"),
                    (0.0, "Vos compétences correspondent peu à cette offre ({value}%)")
                ],
                "skills_coverage": [
                    (0.8, "Vous possédez {value}% des compétences demandées"),
                    (0.5, "Vous possédez partiellement les compétences demandées ({value}%)"),
                    (0.0, "Vous possédez peu des compétences demandées ({value}%)")
                ],
                "skills_expertise_match": [
                    (0.8, "Votre niveau d'expertise technique est parfaitement adapté"),
                    (0.5, "Votre niveau d'expertise technique est partiellement adapté"),
                    (0.0, "Votre niveau d'expertise technique est en dessous des attentes")
                ],
                "experience_years_match": [
                    (0.8, "Votre expérience professionnelle est parfaitement adaptée"),
                    (0.5, "Votre expérience professionnelle est partiellement adaptée"),
                    (0.0, "Votre expérience professionnelle est en dessous des attentes")
                ],
                "relevant_experience_match": [
                    (0.8, "Votre expérience est très pertinente pour ce poste"),
                    (0.5, "Votre expérience est moyennement pertinente"),
                    (0.0, "Votre expérience est peu pertinente pour ce poste")
                ],
                "education_level_match": [
                    (0.8, "Votre formation académique est parfaitement adaptée"),
                    (0.5, "Votre formation académique est partiellement adaptée"),
                    (0.0, "Votre formation académique est en dessous des attentes")
                ],
                "education_field_match": [
                    (0.8, "Votre domaine d'études est parfaitement adapté"),
                    (0.5, "Votre domaine d'études est partiellement adapté"),
                    (0.0, "Votre domaine d'études est peu adapté")
                ],
                "values_alignment": [
                    (0.8, "Vos valeurs personnelles s'alignent avec la culture d'entreprise"),
                    (0.5, "Vos valeurs personnelles s'alignent partiellement"),
                    (0.0, "Vos valeurs personnelles s'alignent peu")
                ],
                "work_environment_match": [
                    (0.8, "L'environnement de travail correspond à vos préférences"),
                    (0.5, "L'environnement de travail correspond partiellement"),
                    (0.0, "L'environnement de travail correspond peu à vos préférences")
                ],
                "location_match": [
                    (0.8, "Localisation idéale selon vos préférences"),
                    (0.5, "Localisation acceptable selon vos préférences"),
                    (0.0, "Localisation peu favorable selon vos préférences")
                ],
                "work_mode_match": [
                    (0.8, "Mode de travail parfaitement adapté à vos préférences"),
                    (0.5, "Mode de travail acceptable selon vos préférences"),
                    (0.0, "Mode de travail peu adapté à vos préférences")
                ],
                "salary_match": [
                    (0.8, "Salaire correspondant à vos attentes"),
                    (0.5, "Salaire partiellement adapté à vos attentes"),
                    (0.0, "Salaire inférieur à vos attentes")
                ],
                "job_title_similarity": [
                    (0.8, "Ce poste correspond parfaitement à votre profil professionnel"),
                    (0.5, "Ce poste est partiellement similaire à votre profil"),
                    (0.0, "Ce poste diffère de votre profil habituel")
                ],
                "job_description_similarity": [
                    (0.8, "Votre expérience passée est très pertinente pour ce poste"),
                    (0.5, "Votre expérience passée est partiellement pertinente"),
                    (0.0, "Votre expérience passée est peu pertinente pour ce poste")
                ]
            }
        }
        
        # Générer des explications pour chaque feature importante
        for feature_name, importance in feature_importance:
            if feature_name not in explanation_templates[context_type]:
                continue
                
            # Obtenir la valeur réelle de la feature
            feature_value = features.get(feature_name, 0)
            
            # Pour les features qui nécessitent une valeur en pourcentage
            value_as_percentage = int(feature_value * 100)
            
            # Trouver le bon modèle d'explication selon la valeur
            for threshold, template in explanation_templates[context_type][feature_name]:
                if feature_value >= threshold:
                    explanation = template.format(value=value_as_percentage)
                    explanations.append(explanation)
                    break
        
        return explanations
    
    def explain_matching(self, candidate_profile, job_profile):
        """
        Génère une explication détaillée du matching entre un candidat et une offre
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Explication détaillée du matching
        """
        try:
            # Générer les features
            features = self.generate_matching_features(candidate_profile, job_profile)
            
            # Normaliser les features
            features_array = np.array([list(features.values())])
            features_normalized = self.scaler.transform(features_array)
            
            # Prédire le score de pertinence
            relevance_score = 0
            feature_importance = []
            
            if self.candidate_ranking_model is not None:
                # Utiliser le modèle XGBoost et SHAP
                dmatrix = xgb.DMatrix(features_normalized)
                relevance_score = float(self.candidate_ranking_model.predict(dmatrix)[0])
                
                # Générer les explications SHAP
                shap_values = self.explainer.shap_values(features_normalized)[0]
                
                # Créer la liste d'importance des features
                feature_names = list(features.keys())
                feature_importance = [(feature_names[i], float(shap_values[i])) 
                                     for i in range(len(feature_names))]
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            else:
                # Utiliser une approche heuristique
                relevance_score = (
                    features["skills_similarity"] * 0.3 +
                    features["experience_years_match"] * 0.2 +
                    features["education_level_match"] * 0.15 +
                    features["job_title_similarity"] * 0.2 +
                    features["values_alignment"] * 0.15
                )
                
                # Créer une liste d'importance simulée
                importance_mapping = {
                    "skills_similarity": 0.3,
                    "experience_years_match": 0.2,
                    "education_level_match": 0.15, 
                    "job_title_similarity": 0.2,
                    "values_alignment": 0.15
                }
                
                feature_importance = [(k, v * features.get(k, 0)) 
                                     for k, v in importance_mapping.items()]
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            
            # Générer les explications détaillées
            detailed_explanations = {}
            
            # 1. Compétences techniques
            detailed_explanations["technical_skills"] = {
                "score": int(features["skills_similarity"] * 100),
                "details": self._explain_skills_match(
                    candidate_profile.get("competences", []),
                    job_profile.get("required_skills", [])
                )
            }
            
            # 2. Expérience professionnelle
            detailed_explanations["experience"] = {
                "score": int(features["experience_years_match"] * 100),
                "details": self._explain_experience_match(
                    candidate_profile.get("experience", []),
                    candidate_profile.get("experience_years", 0),
                    job_profile.get("required_experience_years", 0),
                    job_profile.get("job_description", "")
                )
            }
            
            # 3. Formation académique
            detailed_explanations["education"] = {
                "score": int(features["education_level_match"] * 100),
                "details": self._explain_education_match(
                    candidate_profile.get("education_level", ""),
                    candidate_profile.get("education_field", ""),
                    job_profile.get("required_education_level", ""),
                    job_profile.get("preferred_education_field", "")
                )
            }
            
            # 4. Alignement culturel
            detailed_explanations["cultural_fit"] = {
                "score": int(features["values_alignment"] * 100),
                "details": self._explain_cultural_fit(
                    candidate_profile.get("values", {}),
                    job_profile.get("company_values", {})
                )
            }
            
            # 5. Préférences professionnelles
            detailed_explanations["preferences"] = {
                "score": int((features["work_mode_match"] + features["location_match"] + 
                            features["work_environment_match"]) / 3 * 100),
                "details": self._explain_preferences_match(
                    candidate_profile.get("preferred_location", ""),
                    candidate_profile.get("preferred_work_mode", ""),
                    candidate_profile.get("work_preferences", {}),
                    job_profile.get("location", ""),
                    job_profile.get("work_mode", ""),
                    job_profile.get("work_environment", {})
                )
            }
            
            # Identifier les forces et les points à améliorer
            strengths = []
            areas_to_improve = []
            
            for section, data in detailed_explanations.items():
                if data["score"] >= 75:
                    strengths.append({
                        "category": section,
                        "score": data["score"],
                        "detail": data["details"]["summary"] if "summary" in data["details"] else ""
                    })
                elif data["score"] < 50:
                    areas_to_improve.append({
                        "category": section,
                        "score": data["score"],
                        "detail": data["details"]["recommendations"] if "recommendations" in data["details"] else ""
                    })
            
            # Trier par score
            strengths.sort(key=lambda x: x["score"], reverse=True)
            areas_to_improve.sort(key=lambda x: x["score"])
            
            # Créer le résumé global
            if relevance_score >= 0.8:
                match_summary = "Excellente compatibilité entre le profil et le poste"
            elif relevance_score >= 0.6:
                match_summary = "Bonne compatibilité avec quelques points d'amélioration"
            elif relevance_score >= 0.4:
                match_summary = "Compatibilité moyenne, des aspects importants pourraient ne pas correspondre"
            else:
                match_summary = "Faible compatibilité, ce poste ne semble pas adapté au profil"
            
            return {
                "match_score": min(100, max(0, int(relevance_score * 100))),
                "match_summary": match_summary,
                "strengths": strengths[:3],
                "areas_to_improve": areas_to_improve[:3],
                "feature_importance": {k: float(v) for k, v in feature_importance[:8]},
                "detailed_explanations": detailed_explanations
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de l'explication: {e}")
            return {
                "match_score": 0,
                "match_summary": "Impossible de générer une explication",
                "error": str(e)
            }
    
    def _explain_skills_match(self, candidate_skills, job_skills):
        """Génère une explication détaillée du matching des compétences"""
        if not candidate_skills or not job_skills:
            return {
                "summary": "Impossible d'évaluer les compétences",
                "recommendations": "Complétez votre profil de compétences"
            }
        
        # Normaliser les compétences
        candidate_skills_norm = [s.lower() for s in candidate_skills if s]
        job_skills_norm = [s.lower() for s in job_skills if s]
        
        # Identifier les compétences correspondantes et manquantes
        matching_skills = []
        missing_skills = []
        
        for job_skill in job_skills_norm:
            matched = False
            for candidate_skill in candidate_skills_norm:
                if job_skill in candidate_skill or candidate_skill in job_skill:
                    matching_skills.append(job_skill)
                    matched = True
                    break
            
            if not matched:
                missing_skills.append(job_skill)
        
        # Identifier les compétences supplémentaires du candidat
        additional_skills = []
        for candidate_skill in candidate_skills_norm:
            if not any(candidate_skill in job_skill or job_skill in candidate_skill for job_skill in job_skills_norm):
                additional_skills.append(candidate_skill)
        
        # Calculer les pourcentages
        coverage_percentage = len(matching_skills) / max(len(job_skills_norm), 1) * 100
        
        # Générer le résumé
        if coverage_percentage >= 80:
            summary = f"Excellent matching de compétences ({int(coverage_percentage)}%)"
        elif coverage_percentage >= 60:
            summary = f"Bon matching de compétences ({int(coverage_percentage)}%)"
        elif coverage_percentage >= 40:
            summary = f"Matching moyen des compétences ({int(coverage_percentage)}%)"
        else:
            summary = f"Faible matching des compétences ({int(coverage_percentage)}%)"
        
        # Générer des recommandations
        if missing_skills:
            if len(missing_skills) <= 3:
                recommendations = f"Développez les compétences suivantes: {', '.join(missing_skills)}"
            else:
                recommendations = f"Développez les compétences clés manquantes: {', '.join(missing_skills[:3])} et {len(missing_skills) - 3} autres"
        else:
            recommendations = "Votre profil de compétences correspond parfaitement aux exigences"
        
        return {
            "summary": summary,
            "coverage_percentage": int(coverage_percentage),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "additional_skills": additional_skills[:5],  # Limiter pour rester concis
            "recommendations": recommendations
        }
    
    def _explain_experience_match(self, experiences, experience_years, required_years, job_description):
        """Génère une explication détaillée du matching d'expérience"""
        if experience_years is None or required_years is None:
            return {
                "summary": "Impossible d'évaluer l'expérience",
                "recommendations": "Précisez vos années d'expérience"
            }
        
        # Évaluer les années d'expérience
        years_match_percentage = min(100, (experience_years / max(required_years, 1)) * 100)
        
        # Évaluer la pertinence de l'expérience
        relevance_score = 0
        if experiences and job_description:
            experience_texts = []
            for exp in experiences:
                if isinstance(exp, dict) and "description" in exp:
                    experience_texts.append(exp["description"])
                elif isinstance(exp, str):
                    experience_texts.append(exp)
            
            if experience_texts:
                combined_experience = " ".join(experience_texts)
                relevance_score = self.calculate_text_similarity(combined_experience, job_description)
        
        # Générer le résumé d'expérience
        if years_match_percentage >= 100:
            if experience_years > required_years * 1.5:
                summary = f"Expérience supérieure aux exigences ({experience_years} ans vs {required_years} ans requis)"
            else:
                summary = f"Expérience conforme aux exigences ({experience_years} ans vs {required_years} ans requis)"
        elif years_match_percentage >= 75:
            summary = f"Expérience proche des exigences ({experience_years} ans vs {required_years} ans requis)"
        else:
            summary = f"Expérience inférieure aux exigences ({experience_years} ans vs {required_years} ans requis)"
        
        # Évaluer la pertinence
        if relevance_score >= 0.7:
            relevance_summary = "Expérience professionnelle très pertinente pour ce poste"
        elif relevance_score >= 0.5:
            relevance_summary = "Expérience professionnelle moyennement pertinente pour ce poste"
        else:
            relevance_summary = "Expérience professionnelle peu pertinente pour ce poste"
        
        # Générer des recommandations
        if years_match_percentage < 75:
            if relevance_score >= 0.5:
                recommendations = "Mettez en avant la pertinence de votre expérience pour compenser le manque d'années"
            else:
                recommendations = f"Enrichissez votre expérience professionnelle pour atteindre les {required_years} années requises"
        elif relevance_score < 0.5:
            recommendations = "Mettez en avant les aspects de votre expérience qui sont les plus pertinents pour ce poste"
        else:
            recommendations = "Votre expérience est bien adaptée à ce poste"
        
        return {
            "summary": summary,
            "relevance_summary": relevance_summary,
            "years_match_percentage": int(years_match_percentage),
            "relevance_score": int(relevance_score * 100),
            "experience_years": experience_years,
            "required_years": required_years,
            "recommendations": recommendations
        }
    
    def _explain_education_match(self, education_level, education_field, required_level, preferred_field):
        """Génère une explication détaillée du matching de formation"""
        if not education_level:
            return {
                "summary": "Impossible d'évaluer la formation",
                "recommendations": "Précisez votre niveau et domaine de formation"
            }
        
        # Mapping des niveaux d'éducation
        education_levels = {
            "bac": 1, "high school": 1, "secondary": 1,
            "bac+2": 2, "associate": 2, "dut": 2, "bts": 2,
            "bac+3": 3, "bachelor": 3, "licence": 3, "graduate": 3,
            "bac+4": 3.5, "maîtrise": 3.5,
            "bac+5": 4, "master": 4, "msc": 4, "mba": 4, "ingénieur": 4,
            "phd": 5, "doctorat": 5, "doctorate": 5
        }
        
        # Determiner les niveaux
        candidate_value = 3  # Valeur par défaut
        required_value = 3  # Valeur par défaut
        
        for level_name, level_value in education_levels.items():
            if level_name in education_level.lower():
                candidate_value = level_value
            if required_level and level_name in required_level.lower():
                required_value = level_value
        
        # Calculer le pourcentage de match du niveau
        level_match_percentage = min(100, (candidate_value / max(required_value, 1)) * 100)
        
        # Calculer le match du domaine
        field_match_score = 0
        if education_field and preferred_field:
            field_match_score = self.calculate_text_similarity(education_field, preferred_field)
        
        # Générer le résumé du niveau
        if candidate_value > required_value:
            level_summary = "Formation supérieure aux exigences"
        elif candidate_value == required_value:
            level_summary = "Formation conforme aux exigences"
        elif candidate_value >= required_value - 1:
            level_summary = "Formation légèrement inférieure aux exigences"
        else:
            level_summary = "Formation significativement inférieure aux exigences"
        
        # Générer le résumé du domaine
        if field_match_score >= 0.7:
            field_summary = "Domaine de formation parfaitement adapté"
        elif field_match_score >= 0.4:
            field_summary = "Domaine de formation partiellement adapté"
        else:
            field_summary = "Domaine de formation peu adapté"
        
        # Créer un résumé global
        if level_match_percentage >= 100 and field_match_score >= 0.7:
            summary = "Formation parfaitement adaptée aux exigences"
        elif level_match_percentage >= 80 and field_match_score >= 0.4:
            summary = "Formation bien adaptée aux exigences"
        elif level_match_percentage >= 70 or field_match_score >= 0.4:
            summary = "Formation partiellement adaptée aux exigences"
        else:
            summary = "Formation peu adaptée aux exigences"
        
        # Générer des recommandations
        if level_match_percentage < 80:
            recommendations = "Envisagez de compléter votre formation pour atteindre le niveau requis"
        elif field_match_score < 0.4:
            recommendations = "Mettez en avant les aspects de votre formation qui sont pertinents pour ce poste"
        else:
            recommendations = "Votre formation est bien adaptée à ce poste"
        
        return {
            "summary": summary,
            "level_summary": level_summary,
            "field_summary": field_summary,
            "level_match_percentage": int(level_match_percentage),
            "field_match_score": int(field_match_score * 100),
            "education_level": education_level,
            "education_field": education_field,
            "required_level": required_level,
            "preferred_field": preferred_field,
            "recommendations": recommendations
        }
    
    def _explain_cultural_fit(self, candidate_values, company_values):
        """Génère une explication détaillée de l'alignement culturel"""
        # Extraire les valeurs
        candidate_values_list = []
        company_values_list = []
        
        # Extraction des valeurs du candidat
        if isinstance(candidate_values, dict):
            if "explicit_values" in candidate_values:
                candidate_values_list = candidate_values["explicit_values"]
            elif "detected_values" in candidate_values:
                candidate_values_list = list(candidate_values["detected_values"].keys())
        elif isinstance(candidate_values, list):
            candidate_values_list = candidate_values
        elif isinstance(candidate_values, str):
            candidate_values_list = [v.strip() for v in candidate_values.split(',')]
        
        # Extraction des valeurs de l'entreprise
        if isinstance(company_values, dict):
            if "explicit_values" in company_values:
                company_values_list = company_values["explicit_values"]
            elif "detected_values" in company_values:
                company_values_list = list(company_values["detected_values"].keys())
        elif isinstance(company_values, list):
            company_values_list = company_values
        elif isinstance(company_values, str):
            company_values_list = [v.strip() for v in company_values.split(',')]
        
        if not candidate_values_list or not company_values_list:
            return {
                "summary": "Données insuffisantes pour évaluer l'alignement culturel",
                "recommendations": "Précisez vos valeurs personnelles pour améliorer le matching"
            }
        
        # Normalisation
        candidate_norm = [v.lower() for v in candidate_values_list]
        company_norm = [v.lower() for v in company_values_list]
        
        # Identifier les valeurs correspondantes et divergentes
        matching_values = []
        missing_values = []
        
        for company_value in company_norm:
            matched = False
            for candidate_value in candidate_norm:
                if company_value in candidate_value or candidate_value in company_value:
                    matching_values.append(company_value)
                    matched = True
                    break
            
            if not matched:
                missing_values.append(company_value)
        
        # Calculer le pourcentage d'alignement
        alignment_percentage = len(matching_values) / max(len(company_norm), 1) * 100
        
        # Générer le résumé
        if alignment_percentage >= 75:
            summary = f"Excellent alignement avec la culture d'entreprise ({int(alignment_percentage)}%)"
        elif alignment_percentage >= 50:
            summary = f"Bon alignement avec la culture d'entreprise ({int(alignment_percentage)}%)"
        elif alignment_percentage >= 25:
            summary = f"Alignement partiel avec la culture d'entreprise ({int(alignment_percentage)}%)"
        else:
            summary = f"Faible alignement avec la culture d'entreprise ({int(alignment_percentage)}%)"
        
        # Générer des recommandations
        if missing_values:
            recommendations = f"Réfléchissez à votre alignement avec les valeurs de l'entreprise: {', '.join(missing_values[:3])}"
            if len(missing_values) > 3:
                recommendations += f" et {len(missing_values) - 3} autres"
        else:
            recommendations = "Vos valeurs s'alignent bien avec celles de l'entreprise"
        
        return {
            "summary": summary,
            "alignment_percentage": int(alignment_percentage),
            "matching_values": matching_values,
            "missing_values": missing_values,
            "candidate_values": candidate_values_list,
            "company_values": company_values_list,
            "recommendations": recommendations
        }
    
    def _explain_preferences_match(self, preferred_location, preferred_work_mode, 
                                 work_preferences, job_location, job_work_mode, 
                                 work_environment):
        """Génère une explication détaillée du matching des préférences"""
        explanations = {}
        
        # 1. Évaluer la localisation
        if preferred_location and job_location:
            location_score = self.calculate_location_match(preferred_location, job_location)
            
            if location_score >= 0.8:
                location_summary = "Localisation idéale"
            elif location_score >= 0.5:
                location_summary = "Localisation acceptable"
            else:
                location_summary = "Localisation peu favorable"
                
            explanations["location"] = {
                "score": int(location_score * 100),
                "summary": location_summary,
                "preferred": preferred_location,
                "actual": job_location
            }
        
        # 2. Évaluer le mode de travail
        if preferred_work_mode and job_work_mode:
            work_mode_score = self.calculate_work_mode_match(preferred_work_mode, job_work_mode)
            
            if work_mode_score >= 0.8:
                work_mode_summary = "Mode de travail parfaitement adapté"
            elif work_mode_score >= 0.5:
                work_mode_summary = "Mode de travail acceptable"
            else:
                work_mode_summary = "Mode de travail peu adapté"
                
            explanations["work_mode"] = {
                "score": int(work_mode_score * 100),
                "summary": work_mode_summary,
                "preferred": preferred_work_mode,
                "actual": job_work_mode
            }
        
        # 3. Évaluer d'autres facteurs d'environnement de travail
        if work_preferences and work_environment:
            environment_factors = {}
            
            factors = ["team_size", "management_style", "company_culture", "pace"]
            for factor in factors:
                if factor in work_preferences and factor in work_environment:
                    pref_val = work_preferences[factor]
                    actual_val = work_environment[factor]
                    
                    if pref_val == actual_val:
                        environment_factors[factor] = {
                            "match": True,
                            "preferred": pref_val,
                            "actual": actual_val
                        }
                    else:
                        environment_factors[factor] = {
                            "match": False,
                            "preferred": pref_val,
                            "actual": actual_val
                        }
            
            # Calculer un score global d'environnement
            if environment_factors:
                matches = sum(1 for f in environment_factors.values() if f["match"])
                env_score = matches / len(environment_factors)
                
                if env_score >= 0.7:
                    env_summary = "Environnement de travail bien adapté à vos préférences"
                elif env_score >= 0.4:
                    env_summary = "Environnement de travail partiellement adapté"
                else:
                    env_summary = "Environnement de travail peu adapté à vos préférences"
                    
                explanations["work_environment"] = {
                    "score": int(env_score * 100),
                    "summary": env_summary,
                    "factors": environment_factors
                }
        
        # Calculer un score global et créer un résumé
        preferences_scores = [e["score"] for e in explanations.values()]
        if preferences_scores:
            avg_score = sum(preferences_scores) / len(preferences_scores)
            
            if avg_score >= 75:
                summary = "Très bonne adéquation avec vos préférences professionnelles"
            elif avg_score >= 50:
                summary = "Adéquation moyenne avec vos préférences professionnelles"
            else:
                summary = "Faible adéquation avec vos préférences professionnelles"
                
            # Générer des recommandations
            mismatches = []
            for category, data in explanations.items():
                if data["score"] < 50:
                    mismatches.append(category)
            
            if mismatches:
                recommendations = f"Évaluez si vous pouvez vous adapter aux différences de {', '.join(mismatches)}"
            else:
                recommendations = "Ce poste correspond bien à vos préférences"
        else:
            summary = "Données insuffisantes pour évaluer les préférences"
            recommendations = "Précisez vos préférences professionnelles pour améliorer le matching"
            avg_score = 50
        
        return {
            "summary": summary,
            "score": int(avg_score),
            "recommendations": recommendations,
            "details": explanations
        }

# Instance singleton du moteur de matching
_xgboost_matching_engine = None

def get_xgboost_matching_engine():
    """
    Récupère l'instance unique du moteur de matching XGBoost
    
    Returns:
        XGBoostMatchingEngine: Instance du moteur de matching
    """
    global _xgboost_matching_engine
    if _xgboost_matching_engine is None:
        _xgboost_matching_engine = XGBoostMatchingEngine()
    return _xgboost_matching_engine