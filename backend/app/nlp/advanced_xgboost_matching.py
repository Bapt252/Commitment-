"""
Moteur de matching avancé basé sur XGBoost.
Ce module intègre tous les générateurs de features et fournit une API complète
pour le matching candidat-offre.
"""

import logging
import numpy as np
import pandas as pd
import json
import pickle
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Union
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GroupKFold

# Import des générateurs de features
from .feature_generators.skills_features import SkillsFeatureGenerator
from .feature_generators.cultural_features import CulturalAlignmentGenerator
from .feature_generators.textual_features import TextualSimilarityGenerator
from .feature_generators.preference_features import PreferenceFeatureGenerator

# Import des composants d'explication
from .matching_explainer import MatchingExplainer

class AdvancedXGBoostMatching:
    """
    Moteur de matching avancé basé sur XGBoost, intégrant plusieurs
    générateurs de features spécialisés.
    """
    
    def __init__(self, config_path=None):
        """
        Initialise le moteur de matching XGBoost.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.logger = logging.getLogger(__name__)
        
        # Chargement de la configuration
        self.config = self._load_config(config_path)
        
        # Initialisation des générateurs de features
        self.skills_generator = SkillsFeatureGenerator()
        self.cultural_generator = CulturalAlignmentGenerator()
        self.textual_generator = TextualSimilarityGenerator()
        self.preference_generator = PreferenceFeatureGenerator()
        
        # Scaler pour la normalisation des features
        self.feature_scaler = StandardScaler()
        
        # Initialisation des modèles
        self.candidate_ranking_model = None
        self.job_ranking_model = None
        
        # Chargement des modèles existants
        self._load_models()
        
        # Initialisation de l'explainer
        self.explainer = None
        if self.candidate_ranking_model or self.job_ranking_model:
            model_to_use = self.candidate_ranking_model or self.job_ranking_model
            self.explainer = MatchingExplainer(model_to_use)
    
    def _load_config(self, config_path=None):
        """
        Charge la configuration du moteur de matching.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Dict: Configuration du moteur
        """
        default_config = {
            "model_paths": {
                "candidate_ranking": "data/models/candidate_ranking_model.json",
                "job_ranking": "data/models/job_ranking_model.json",
                "feature_scaler": "data/models/feature_scaler.pkl"
            },
            "xgboost_params": {
                "objective": "rank:ndcg",
                "eval_metric": ["ndcg@5", "ndcg@10"],
                "learning_rate": 0.05,
                "max_depth": 6,
                "min_child_weight": 1,
                "gamma": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "tree_method": "hist",
                "random_state": 42
            },
            "feature_weights": {
                "skills": 1.0,
                "cultural": 0.8,
                "textual": 0.7,
                "preference": 0.9
            },
            "matching": {
                "default_limit": 10,
                "min_score": 0.3,  # Score minimum pour considérer un match
                "use_cache": True,
                "cache_ttl": 3600  # Durée de vie du cache en secondes
            }
        }
        
        # Si un chemin est spécifié, essayer de charger la configuration
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Fusion avec la configuration par défaut
                    for section, items in loaded_config.items():
                        if section in default_config and isinstance(default_config[section], dict):
                            default_config[section].update(items)
                        else:
                            default_config[section] = items
            except Exception as e:
                self.logger.warning(f"Impossible de charger la configuration depuis {config_path}: {e}")
                self.logger.warning("Utilisation de la configuration par défaut.")
        
        return default_config
    
    def _load_models(self):
        """
        Charge les modèles XGBoost existants et le scaler.
        """
        # Chemins des modèles
        base_path = Path(__file__).resolve().parent.parent.parent
        candidate_model_path = base_path / self.config["model_paths"]["candidate_ranking"]
        job_model_path = base_path / self.config["model_paths"]["job_ranking"]
        scaler_path = base_path / self.config["model_paths"]["feature_scaler"]
        
        # Charger le modèle de ranking candidat
        try:
            if candidate_model_path.exists():
                self.candidate_ranking_model = xgb.Booster()
                self.candidate_ranking_model.load_model(str(candidate_model_path))
                self.logger.info(f"Modèle de ranking candidat chargé depuis {candidate_model_path}")
            else:
                self.logger.warning(f"Modèle de ranking candidat non trouvé à {candidate_model_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle de ranking candidat: {e}")
        
        # Charger le modèle de ranking job
        try:
            if job_model_path.exists():
                self.job_ranking_model = xgb.Booster()
                self.job_ranking_model.load_model(str(job_model_path))
                self.logger.info(f"Modèle de ranking job chargé depuis {job_model_path}")
            else:
                self.logger.warning(f"Modèle de ranking job non trouvé à {job_model_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle de ranking job: {e}")
        
        # Charger le scaler
        try:
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.feature_scaler = pickle.load(f)
                self.logger.info(f"Scaler chargé depuis {scaler_path}")
            else:
                self.logger.warning(f"Scaler non trouvé à {scaler_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du scaler: {e}")
    
    def generate_features(self, candidate_profile, job_profile):
        """
        Génère toutes les features pour une paire candidat-offre.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Features combinées
        """
        features = {}
        
        # 1. Features de compétences
        try:
            skills_features = self.skills_generator.generate_skill_features(
                candidate_profile.get("competences", []), 
                job_profile.get("required_skills", [])
            )
            
            for key, value in skills_features.items():
                features[f"skills_{key}"] = value
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des features de compétences: {e}")
        
        # 2. Features d'alignement culturel
        try:
            cultural_features = self.cultural_generator.generate_cultural_features(
                candidate_profile, job_profile
            )
            
            for key, value in cultural_features.items():
                features[f"cultural_{key}"] = value
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des features culturelles: {e}")
        
        # 3. Features de similarité textuelle
        try:
            textual_features = self.textual_generator.generate_text_features(
                candidate_profile, job_profile
            )
            
            for key, value in textual_features.items():
                features[f"text_{key}"] = value
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des features textuelles: {e}")
        
        # 4. Features de préférences
        try:
            preference_features = self.preference_generator.generate_preference_features(
                candidate_profile, job_profile
            )
            
            for key, value in preference_features.items():
                features[f"pref_{key}"] = value
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des features de préférences: {e}")
        
        # Vérification et nettoyage des features
        features = self._clean_features(features)
        
        return features
    
    def _clean_features(self, features):
        """
        Nettoie et valide les features générées.
        
        Args:
            features: Dictionnaire de features
            
        Returns:
            Dict: Features nettoyées
        """
        cleaned_features = {}
        
        for key, value in features.items():
            # Convertir en nombre si possible
            if value is None:
                cleaned_features[key] = 0.0
            elif isinstance(value, (int, float)):
                cleaned_features[key] = float(value)
            else:
                try:
                    cleaned_features[key] = float(value)
                except (ValueError, TypeError):
                    self.logger.warning(f"Feature non numérique ignorée: {key}={value}")
                    cleaned_features[key] = 0.0
        
        return cleaned_features
    
    def prepare_features_for_model(self, features_dict):
        """
        Prépare les features pour l'entrée du modèle XGBoost.
        
        Args:
            features_dict: Dictionnaire de features
            
        Returns:
            np.ndarray: Array de features normalisées
        """
        # Convertir en DataFrame pour faciliter la manipulation
        features_df = pd.DataFrame([features_dict])
        
        # Remplir les valeurs manquantes
        features_df = features_df.fillna(0.0)
        
        # Normaliser si le scaler est déjà ajusté
        if hasattr(self.feature_scaler, 'mean_'):
            try:
                features_array = self.feature_scaler.transform(features_df)
            except Exception as e:
                self.logger.error(f"Erreur lors de la normalisation des features: {e}")
                # Si erreur, essayer d'aligner les colonnes
                known_columns = self.feature_scaler.get_feature_names_out()
                for col in known_columns:
                    if col not in features_df.columns:
                        features_df[col] = 0.0
                features_array = self.feature_scaler.transform(features_df[known_columns])
        else:
            # Sinon, retourner les features brutes
            features_array = features_df.values
        
        return features_array
    
    def rank_candidates_for_job(self, candidates, job_profile, limit=None):
        """
        Classe les candidats par pertinence pour une offre d'emploi.
        
        Args:
            candidates: Liste des profils candidats
            job_profile: Profil de l'offre d'emploi
            limit: Nombre maximum de candidats à retourner
            
        Returns:
            List: Candidats classés avec scores et explications
        """
        if not limit:
            limit = self.config["matching"]["default_limit"]
        
        if not candidates or not job_profile:
            return []
        
        # Si le modèle n'est pas chargé, utiliser une approche heuristique
        if self.candidate_ranking_model is None:
            return self._rank_candidates_heuristic(candidates, job_profile, limit)
        
        try:
            # Générer les features pour chaque candidat
            candidates_features = []
            feature_dicts = []
            
            for candidate in candidates:
                features = self.generate_features(candidate, job_profile)
                candidates_features.append(self.prepare_features_for_model(features))
                feature_dicts.append(features)
            
            # Prédire les scores de pertinence
            ranked_candidates = []
            for i, candidate in enumerate(candidates):
                feature_matrix = xgb.DMatrix(candidates_features[i])
                score = float(self.candidate_ranking_model.predict(feature_matrix)[0])
                
                # Normaliser le score (0-100)
                normalized_score = min(100, max(0, score * 100))
                
                # Ne considérer que les candidats au-dessus du score minimum
                if normalized_score >= self.config["matching"]["min_score"] * 100:
                    # Générer des explications
                    explanation = {}
                    if self.explainer:
                        explanation = self.explainer.explain_candidate_match(
                            candidate, job_profile, feature_dicts[i]
                        )
                    
                    ranked_candidates.append({
                        "candidate_id": candidate.get("id", f"candidate_{i}"),
                        "candidate_name": candidate.get("name", f"Candidat {i+1}"),
                        "title": candidate.get("job_title", ""),
                        "relevance_score": normalized_score,
                        "explanation": explanation,
                        "match_categories": self._calculate_category_scores(feature_dicts[i])
                    })
            
            # Trier par score décroissant
            ranked_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_candidates[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement des candidats: {e}")
            return self._rank_candidates_heuristic(candidates, job_profile, limit)
    
    def _rank_candidates_heuristic(self, candidates, job_profile, limit):
        """
        Classe les candidats par une approche heuristique (fallback).
        
        Args:
            candidates: Liste des profils candidats
            job_profile: Profil de l'offre d'emploi
            limit: Nombre maximum de candidats à retourner
            
        Returns:
            List: Candidats classés avec scores et explications
        """
        ranked_candidates = []
        
        for i, candidate in enumerate(candidates):
            # Générer les features
            features = self.generate_features(candidate, job_profile)
            
            # Calculer un score heuristique pondéré
            total_score = 0.0
            total_weight = 0.0
            
            # Regrouper les features par catégorie
            skill_features = {k: v for k, v in features.items() if k.startswith('skills_')}
            cultural_features = {k: v for k, v in features.items() if k.startswith('cultural_')}
            text_features = {k: v for k, v in features.items() if k.startswith('text_')}
            pref_features = {k: v for k, v in features.items() if k.startswith('pref_')}
            
            # Calculer les scores par catégorie
            if skill_features:
                skill_score = sum(skill_features.values()) / len(skill_features)
                total_score += skill_score * self.config["feature_weights"]["skills"]
                total_weight += self.config["feature_weights"]["skills"]
            
            if cultural_features:
                cultural_score = sum(cultural_features.values()) / len(cultural_features)
                total_score += cultural_score * self.config["feature_weights"]["cultural"]
                total_weight += self.config["feature_weights"]["cultural"]
            
            if text_features:
                text_score = sum(text_features.values()) / len(text_features)
                total_score += text_score * self.config["feature_weights"]["textual"]
                total_weight += self.config["feature_weights"]["textual"]
            
            if pref_features:
                pref_score = sum(pref_features.values()) / len(pref_features)
                total_score += pref_score * self.config["feature_weights"]["preference"]
                total_weight += self.config["feature_weights"]["preference"]
            
            # Calculer le score final normalisé
            final_score = (total_score / total_weight) if total_weight > 0 else 0
            normalized_score = min(100, max(0, final_score * 100))
            
            # Ne considérer que les candidats au-dessus du score minimum
            if normalized_score >= self.config["matching"]["min_score"] * 100:
                # Créer une explication simplifiée
                top_features = sorted(
                    [(k, v) for k, v in features.items()], 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                
                explanation = {
                    "top_matching_factors": [
                        self._format_feature_name(f[0]) for f in top_features
                    ],
                    "feature_scores": {
                        self._format_feature_name(f[0]): f[1] for f in top_features
                    }
                }
                
                ranked_candidates.append({
                    "candidate_id": candidate.get("id", f"candidate_{i}"),
                    "candidate_name": candidate.get("name", f"Candidat {i+1}"),
                    "title": candidate.get("job_title", ""),
                    "relevance_score": normalized_score,
                    "explanation": explanation,
                    "match_categories": self._calculate_category_scores(features)
                })
        
        # Trier par score décroissant
        ranked_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked_candidates[:limit]
    
    def rank_jobs_for_candidate(self, jobs, candidate_profile, limit=None):
        """
        Classe les offres d'emploi par pertinence pour un candidat.
        
        Args:
            jobs: Liste des offres d'emploi
            candidate_profile: Profil du candidat
            limit: Nombre maximum d'offres à retourner
            
        Returns:
            List: Offres classées avec scores et explications
        """
        if not limit:
            limit = self.config["matching"]["default_limit"]
        
        if not jobs or not candidate_profile:
            return []
        
        # Si le modèle n'est pas chargé, utiliser une approche heuristique
        if self.job_ranking_model is None:
            # Si le modèle de candidat est disponible, l'utiliser à la place
            if self.candidate_ranking_model is not None:
                return self._rank_jobs_with_candidate_model(jobs, candidate_profile, limit)
            else:
                return self._rank_jobs_heuristic(jobs, candidate_profile, limit)
        
        try:
            # Générer les features pour chaque offre
            jobs_features = []
            feature_dicts = []
            
            for job in jobs:
                features = self.generate_features(candidate_profile, job)
                jobs_features.append(self.prepare_features_for_model(features))
                feature_dicts.append(features)
            
            # Prédire les scores de pertinence
            ranked_jobs = []
            for i, job in enumerate(jobs):
                feature_matrix = xgb.DMatrix(jobs_features[i])
                score = float(self.job_ranking_model.predict(feature_matrix)[0])
                
                # Normaliser le score (0-100)
                normalized_score = min(100, max(0, score * 100))
                
                # Ne considérer que les offres au-dessus du score minimum
                if normalized_score >= self.config["matching"]["min_score"] * 100:
                    # Générer des explications
                    explanation = {}
                    if self.explainer:
                        explanation = self.explainer.explain_job_match(
                            candidate_profile, job, feature_dicts[i]
                        )
                    
                    ranked_jobs.append({
                        "job_id": job.get("id", f"job_{i}"),
                        "title": job.get("job_title", job.get("title", f"Poste {i+1}")),
                        "company_name": job.get("company_name", job.get("company", "Entreprise")),
                        "relevance_score": normalized_score,
                        "explanation": explanation,
                        "match_categories": self._calculate_category_scores(feature_dicts[i])
                    })
            
            # Trier par score décroissant
            ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement des offres: {e}")
            
            # Si le modèle de candidat est disponible, l'utiliser à la place
            if self.candidate_ranking_model is not None:
                return self._rank_jobs_with_candidate_model(jobs, candidate_profile, limit)
            else:
                return self._rank_jobs_heuristic(jobs, candidate_profile, limit)
    
    def _rank_jobs_with_candidate_model(self, jobs, candidate_profile, limit):
        """
        Classe les offres en utilisant le modèle de ranking candidat à l'envers.
        
        Args:
            jobs: Liste des offres d'emploi
            candidate_profile: Profil du candidat
            limit: Nombre maximum d'offres à retourner
            
        Returns:
            List: Offres classées avec scores et explications
        """
        try:
            # Générer les features pour chaque offre
            jobs_features = []
            feature_dicts = []
            
            for job in jobs:
                features = self.generate_features(candidate_profile, job)
                jobs_features.append(self.prepare_features_for_model(features))
                feature_dicts.append(features)
            
            # Prédire les scores de pertinence en utilisant le modèle candidat
            ranked_jobs = []
            for i, job in enumerate(jobs):
                feature_matrix = xgb.DMatrix(jobs_features[i])
                score = float(self.candidate_ranking_model.predict(feature_matrix)[0])
                
                # Normaliser le score (0-100)
                normalized_score = min(100, max(0, score * 100))
                
                # Ne considérer que les offres au-dessus du score minimum
                if normalized_score >= self.config["matching"]["min_score"] * 100:
                    # Générer des explications
                    explanation = {}
                    if self.explainer:
                        explanation = self.explainer.explain_job_match(
                            candidate_profile, job, feature_dicts[i]
                        )
                    
                    ranked_jobs.append({
                        "job_id": job.get("id", f"job_{i}"),
                        "title": job.get("job_title", job.get("title", f"Poste {i+1}")),
                        "company_name": job.get("company_name", job.get("company", "Entreprise")),
                        "relevance_score": normalized_score,
                        "explanation": explanation,
                        "match_categories": self._calculate_category_scores(feature_dicts[i])
                    })
            
            # Trier par score décroissant
            ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du classement des offres avec le modèle candidat: {e}")
            return self._rank_jobs_heuristic(jobs, candidate_profile, limit)
    
    def _rank_jobs_heuristic(self, jobs, candidate_profile, limit):
        """
        Classe les offres par une approche heuristique (fallback).
        
        Args:
            jobs: Liste des offres d'emploi
            candidate_profile: Profil du candidat
            limit: Nombre maximum d'offres à retourner
            
        Returns:
            List: Offres classées avec scores et explications
        """
        ranked_jobs = []
        
        for i, job in enumerate(jobs):
            # Générer les features
            features = self.generate_features(candidate_profile, job)
            
            # Calculer un score heuristique pondéré
            total_score = 0.0
            total_weight = 0.0
            
            # Regrouper les features par catégorie
            skill_features = {k: v for k, v in features.items() if k.startswith('skills_')}
            cultural_features = {k: v for k, v in features.items() if k.startswith('cultural_')}
            text_features = {k: v for k, v in features.items() if k.startswith('text_')}
            pref_features = {k: v for k, v in features.items() if k.startswith('pref_')}
            
            # Calculer les scores par catégorie
            if skill_features:
                skill_score = sum(skill_features.values()) / len(skill_features)
                total_score += skill_score * self.config["feature_weights"]["skills"]
                total_weight += self.config["feature_weights"]["skills"]
            
            if cultural_features:
                cultural_score = sum(cultural_features.values()) / len(cultural_features)
                total_score += cultural_score * self.config["feature_weights"]["cultural"]
                total_weight += self.config["feature_weights"]["cultural"]
            
            if text_features:
                text_score = sum(text_features.values()) / len(text_features)
                total_score += text_score * self.config["feature_weights"]["textual"]
                total_weight += self.config["feature_weights"]["textual"]
            
            if pref_features:
                pref_score = sum(pref_features.values()) / len(pref_features)
                total_score += pref_score * self.config["feature_weights"]["preference"]
                total_weight += self.config["feature_weights"]["preference"]
            
            # Calculer le score final normalisé
            final_score = (total_score / total_weight) if total_weight > 0 else 0
            normalized_score = min(100, max(0, final_score * 100))
            
            # Ne considérer que les offres au-dessus du score minimum
            if normalized_score >= self.config["matching"]["min_score"] * 100:
                # Créer une explication simplifiée
                top_features = sorted(
                    [(k, v) for k, v in features.items()], 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                
                explanation = {
                    "top_matching_factors": [
                        self._format_feature_name(f[0]) for f in top_features
                    ],
                    "feature_scores": {
                        self._format_feature_name(f[0]): f[1] for f in top_features
                    }
                }
                
                ranked_jobs.append({
                    "job_id": job.get("id", f"job_{i}"),
                    "title": job.get("job_title", job.get("title", f"Poste {i+1}")),
                    "company_name": job.get("company_name", job.get("company", "Entreprise")),
                    "relevance_score": normalized_score,
                    "explanation": explanation,
                    "match_categories": self._calculate_category_scores(features)
                })
        
        # Trier par score décroissant
        ranked_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked_jobs[:limit]
    
    def _format_feature_name(self, feature_name):
        """
        Formate le nom d'une feature en texte lisible.
        
        Args:
            feature_name: Nom technique de la feature
            
        Returns:
            str: Nom lisible
        """
        # Supprimer le préfixe de catégorie
        if '_' in feature_name:
            category, name = feature_name.split('_', 1)
        else:
            name = feature_name
        
        # Remplacer les underscores par des espaces
        name = name.replace('_', ' ')
        
        # Mettre en majuscule la première lettre de chaque mot
        return name.title()
    
    def _calculate_category_scores(self, features):
        """
        Calcule les scores par catégorie de features.
        
        Args:
            features: Dictionnaire de features
            
        Returns:
            Dict: Scores par catégorie
        """
        category_scores = {}
        
        # Regrouper les features par catégorie
        skill_features = {k: v for k, v in features.items() if k.startswith('skills_')}
        cultural_features = {k: v for k, v in features.items() if k.startswith('cultural_')}
        text_features = {k: v for k, v in features.items() if k.startswith('text_')}
        pref_features = {k: v for k, v in features.items() if k.startswith('pref_')}
        
        # Calculer les scores moyens par catégorie
        if skill_features:
            category_scores["technical_skills"] = min(100, sum(skill_features.values()) / len(skill_features) * 100)
        
        if cultural_features:
            category_scores["cultural_fit"] = min(100, sum(cultural_features.values()) / len(cultural_features) * 100)
        
        if text_features:
            category_scores["experience_relevance"] = min(100, sum(text_features.values()) / len(text_features) * 100)
        
        if pref_features:
            category_scores["work_preferences"] = min(100, sum(pref_features.values()) / len(pref_features) * 100)
        
        # Calcul du score global (moyenne pondérée)
        weights = {
            "technical_skills": self.config["feature_weights"]["skills"],
            "cultural_fit": self.config["feature_weights"]["cultural"],
            "experience_relevance": self.config["feature_weights"]["textual"],
            "work_preferences": self.config["feature_weights"]["preference"]
        }
        
        total_score = 0
        total_weight = 0
        
        for category, score in category_scores.items():
            weight = weights.get(category, 1.0)
            total_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            category_scores["overall"] = min(100, total_score / total_weight)
        
        return category_scores
    
    def explain_match(self, candidate_profile, job_profile):
        """
        Génère une explication détaillée du matching entre un candidat et une offre.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Explication détaillée du matching
        """
        # Générer les features
        features = self.generate_features(candidate_profile, job_profile)
        
        # Si l'explainer est disponible, utiliser SHAP
        if self.explainer and (self.candidate_ranking_model or self.job_ranking_model):
            model_to_use = self.candidate_ranking_model or self.job_ranking_model
            explanation = self.explainer.explain_detailed_match(
                candidate_profile, job_profile, features, model_to_use
            )
            return explanation
        
        # Sinon, générer une explication basique
        return self._generate_basic_explanation(candidate_profile, job_profile, features)
    
    def _generate_basic_explanation(self, candidate_profile, job_profile, features):
        """
        Génère une explication basique du matching sans modèle.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            features: Features générées
            
        Returns:
            Dict: Explication du matching
        """
        # Calculer les scores par catégorie
        category_scores = self._calculate_category_scores(features)
        
        # Trier les features par valeur décroissante
        sorted_features = sorted(
            [(k, v) for k, v in features.items()], 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Extraire les facteurs positifs (meilleurs scores)
        top_factors = [
            {
                "factor": self._format_feature_name(f[0]),
                "score": min(100, f[1] * 100),
                "description": self._generate_factor_description(f[0], f[1], True)
            }
            for f in sorted_features[:5]
        ]
        
        # Extraire les facteurs à améliorer (scores les plus bas)
        bottom_sorted = sorted(
            [(k, v) for k, v in features.items()], 
            key=lambda x: x[1]
        )
        
        areas_to_improve = [
            {
                "factor": self._format_feature_name(f[0]),
                "score": min(100, f[1] * 100),
                "description": self._generate_factor_description(f[0], f[1], False)
            }
            for f in bottom_sorted[:3] if f[1] < 0.7  # Ne garder que les scores vraiment bas
        ]
        
        # Déterminer le score global et le résumé
        overall_score = category_scores.get("overall", 0)
        
        if overall_score >= 80:
            summary = "Excellente compatibilité entre le profil et le poste"
        elif overall_score >= 60:
            summary = "Bonne compatibilité avec quelques points d'amélioration"
        elif overall_score >= 40:
            summary = "Compatibilité moyenne, des aspects importants pourraient ne pas correspondre"
        else:
            summary = "Faible compatibilité, ce poste ne semble pas adapté au profil"
        
        # Créer l'explication complète
        explanation = {
            "match_score": overall_score,
            "match_summary": summary,
            "category_scores": category_scores,
            "strengths": top_factors,
            "areas_to_improve": areas_to_improve,
            "detailed_features": {
                self._format_feature_name(f[0]): f[1] for f in sorted_features[:10]
            }
        }
        
        return explanation
    
    def _generate_factor_description(self, feature_name, feature_value, is_positive):
        """
        Génère une description textuelle pour un facteur de matching.
        
        Args:
            feature_name: Nom de la feature
            feature_value: Valeur de la feature
            is_positive: Si c'est un facteur positif ou négatif
            
        Returns:
            str: Description du facteur
        """
        score_percent = min(100, feature_value * 100)
        
        # Features de compétences
        if "skills_exact_match" in feature_name:
            if is_positive:
                return f"Correspondance directe de {score_percent:.0f}% entre les compétences"
            else:
                return "Faible correspondance directe entre les compétences requises"
        
        if "skills_coverage" in feature_name:
            if is_positive:
                return f"Le candidat couvre {score_percent:.0f}% des compétences requises"
            else:
                return "Plusieurs compétences requises ne sont pas couvertes par le candidat"
        
        if "skills_semantic" in feature_name:
            if is_positive:
                return "Les compétences du candidat sont sémantiquement très proches de celles requises"
            else:
                return "Les compétences du candidat sont éloignées de celles requises pour le poste"
        
        # Features culturelles
        if "cultural_values_explicit_match" in feature_name:
            if is_positive:
                return "Forte correspondance entre les valeurs du candidat et de l'entreprise"
            else:
                return "Faible alignement des valeurs avec la culture d'entreprise"
        
        if "cultural_overall_culture_match" in feature_name:
            if is_positive:
                return "Excellente compatibilité culturelle globale"
            else:
                return "Culture d'entreprise potentiellement incompatible avec les préférences"
        
        # Features textuelles
        if "text_job_title_similarity" in feature_name:
            if is_positive:
                return "L'intitulé du poste correspond parfaitement à l'expérience précédente"
            else:
                return "L'intitulé du poste diffère significativement de l'expérience précédente"
        
        if "text_experience_job" in feature_name:
            if is_positive:
                return "L'expérience professionnelle est très pertinente pour ce poste"
            else:
                return "L'expérience professionnelle semble peu pertinente pour ce poste"
        
        # Features de préférence
        if "pref_location_match" in feature_name:
            if is_positive:
                return "Localisation idéale correspondant aux préférences"
            else:
                return "Localisation éloignée des préférences du candidat"
        
        if "pref_salary_match" in feature_name:
            if is_positive:
                return "Rémunération alignée avec les attentes salariales"
            else:
                return "Écart important entre l'offre salariale et les attentes"
        
        if "pref_work_mode_match" in feature_name:
            if is_positive:
                return "Mode de travail parfaitement adapté aux préférences"
            else:
                return "Mode de travail en contradiction avec les préférences"
        
        # Description générique
        if is_positive:
            return f"Forte correspondance ({score_percent:.0f}%)"
        else:
            return f"Faible correspondance ({score_percent:.0f}%)"
    
    def train_models(self, training_data, validation_split=0.2):
        """
        Entraîne les modèles XGBoost de ranking.
        
        Args:
            training_data: Données d'entraînement
            validation_split: Proportion de données à utiliser pour la validation
            
        Returns:
            Dict: Résultats de l'entraînement
        """
        # Structure des données d'entraînement attendue:
        # {
        #   "candidates": [...],  # Liste de profils candidats
        #   "jobs": [...],        # Liste d'offres d'emploi
        #   "matches": [...]      # Liste de correspondances évaluées
        # }
        
        if not training_data or not all(k in training_data for k in ["candidates", "jobs", "matches"]):
            raise ValueError("Format de données d'entraînement invalide")
        
        candidates = training_data["candidates"]
        jobs = training_data["jobs"]
        matches = training_data["matches"]
        
        if not candidates or not jobs or not matches:
            raise ValueError("Données d'entraînement vides")
        
        # Étape 1: Génération des features pour toutes les paires
        self.logger.info("Génération des features pour l'entraînement...")
        features_data = []
        
        for match in matches:
            candidate_id = match["candidate_id"]
            job_id = match["job_id"]
            relevance = match["relevance"]
            
            # Trouver les profils correspondants
            candidate = next((c for c in candidates if c["id"] == candidate_id), None)
            job = next((j for j in jobs if j["id"] == job_id), None)
            
            if not candidate or not job:
                continue
            
            # Générer les features
            features = self.generate_features(candidate, job)
            
            # Ajouter aux données d'entraînement
            features_data.append({
                "features": features,
                "relevance": relevance,
                "candidate_id": candidate_id,
                "job_id": job_id
            })
        
        if not features_data:
            raise ValueError("Impossible de générer des features pour l'entraînement")
        
        # Étape 2: Préparation des données pour le ranking
        self.logger.info("Préparation des données pour le ranking...")
        
        # 2.1 Pour le modèle de ranking candidat (par offre)
        job_groups = {}
        for item in features_data:
            job_id = item["job_id"]
            if job_id not in job_groups:
                job_groups[job_id] = []
            job_groups[job_id].append(item)
        
        # 2.2 Pour le modèle de ranking offre (par candidat)
        candidate_groups = {}
        for item in features_data:
            candidate_id = item["candidate_id"]
            if candidate_id not in candidate_groups:
                candidate_groups[candidate_id] = []
            candidate_groups[candidate_id].append(item)
        
        # Étape 3: Entraînement du modèle de ranking candidat
        self.logger.info("Entraînement du modèle de ranking candidat...")
        candidate_model_result = self._train_ranking_model(job_groups, "candidate")
        
        # Étape 4: Entraînement du modèle de ranking offre
        self.logger.info("Entraînement du modèle de ranking offre...")
        job_model_result = self._train_ranking_model(candidate_groups, "job")
        
        # Étape 5: Sauvegarde des modèles
        self.logger.info("Sauvegarde des modèles...")
        self._save_models()
        
        return {
            "candidate_model": candidate_model_result,
            "job_model": job_model_result
        }
    
    def _train_ranking_model(self, groups, model_type):
        """
        Entraîne un modèle de ranking XGBoost.
        
        Args:
            groups: Groupes de données pour l'entraînement de ranking
            model_type: Type de modèle ("candidate" ou "job")
            
        Returns:
            Dict: Résultats de l'entraînement
        """
        # Préparation des données
        X_list = []
        y_list = []
        qid_list = []
        
        for group_id, items in groups.items():
            # Trier par pertinence décroissante
            items.sort(key=lambda x: x["relevance"], reverse=True)
            
            # Extraire les features et labels
            for item in items:
                # Convertir le dictionnaire de features en liste
                feature_values = list(item["features"].values())
                X_list.append(feature_values)
                y_list.append(item["relevance"])
                qid_list.append(group_id)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Normalisation des features
        self.feature_scaler.fit(X)
        X_scaled = self.feature_scaler.transform(X)
        
        # Sauvegarde des noms de features
        feature_names = list(groups[list(groups.keys())[0]][0]["features"].keys())
        
        # Division train/validation
        X_train, X_val, y_train, y_val, qid_train, qid_val = train_test_split(
            X_scaled, y, qid_list, test_size=0.2, random_state=42
        )
        
        # Conversion vers le format de groupe XGBoost
        qid_train_dict = {}
        for i, qid in enumerate(qid_train):
            if qid not in qid_train_dict:
                qid_train_dict[qid] = []
            qid_train_dict[qid].append(i)
        
        qid_val_dict = {}
        for i, qid in enumerate(qid_val):
            if qid not in qid_val_dict:
                qid_val_dict[qid] = []
            qid_val_dict[qid].append(i)
        
        # Création des matrices DMatrix
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)
        
        # Définir les groupes pour le ranking
        dtrain.set_group([len(indices) for qid, indices in qid_train_dict.items()])
        dval.set_group([len(indices) for qid, indices in qid_val_dict.items()])
        
        # Entraînement du modèle
        params = self.config["xgboost_params"].copy()
        
        # Paramètres spécifiques au type de modèle
        if model_type == "candidate":
            params["eval_metric"] = ["ndcg@5", "ndcg@10"]
        else:
            params["eval_metric"] = ["ndcg@10", "map@10"]
        
        # Entraînement avec early stopping
        evals_result = {}
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=1000,
            evals=[(dtrain, 'train'), (dval, 'val')],
            early_stopping_rounds=50,
            verbose_eval=10,
            evals_result=evals_result
        )
        
        # Sauvegarder le modèle selon son type
        if model_type == "candidate":
            self.candidate_ranking_model = model
        else:
            self.job_ranking_model = model
        
        # Initialiser l'explainer avec le nouveau modèle
        self.explainer = MatchingExplainer(model, feature_names)
        
        return {
            "best_iteration": model.best_iteration,
            "best_score": model.best_score,
            "feature_importance": dict(zip(feature_names, model.get_score(importance_type='gain'))),
            "validation_metrics": evals_result
        }
    
    def _save_models(self):
        """
        Sauvegarde les modèles et le scaler sur disque.
        """
        # Créer le répertoire de modèles si nécessaire
        base_path = Path(__file__).resolve().parent.parent.parent / "data" / "models"
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Chemin des modèles
        candidate_model_path = base_path / "candidate_ranking_model.json"
        job_model_path = base_path / "job_ranking_model.json"
        scaler_path = base_path / "feature_scaler.pkl"
        
        # Sauvegarder le modèle de ranking candidat
        if self.candidate_ranking_model:
            self.candidate_ranking_model.save_model(str(candidate_model_path))
            self.logger.info(f"Modèle de ranking candidat sauvegardé à {candidate_model_path}")
        
        # Sauvegarder le modèle de ranking job
        if self.job_ranking_model:
            self.job_ranking_model.save_model(str(job_model_path))
            self.logger.info(f"Modèle de ranking job sauvegardé à {job_model_path}")
        
        # Sauvegarder le scaler
        if hasattr(self.feature_scaler, 'mean_'):
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.feature_scaler, f)
            self.logger.info(f"Scaler sauvegardé à {scaler_path}")

# Instance unique pour l'application
_matching_engine = None

def get_matching_engine(config_path=None):
    """
    Récupère l'instance unique du moteur de matching.
    
    Args:
        config_path: Chemin vers le fichier de configuration (optionnel)
        
    Returns:
        AdvancedXGBoostMatching: Instance du moteur de matching
    """
    global _matching_engine
    if _matching_engine is None:
        _matching_engine = AdvancedXGBoostMatching(config_path)
    return _matching_engine
