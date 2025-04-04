"""
Module d'explication des matchings basé sur SHAP.
Permet de générer des explications interprétables pour les prédictions du modèle XGBoost.
"""

import logging
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import xgboost as xgb

# Importer SHAP avec gestion d'erreur (package optionnel)
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


class MatchingExplainer:
    """
    Générateur d'explications pour les prédictions du modèle de matching XGBoost.
    Utilise SHAP (SHapley Additive exPlanations) pour analyser les contributions
    de chaque feature à la prédiction.
    """
    
    def __init__(self, model, feature_names=None):
        """
        Initialise l'explainer avec un modèle et des noms de features.
        
        Args:
            model: Modèle XGBoost entraîné
            feature_names: Liste des noms de features (optionnel)
        """
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        
        # Initialiser l'explainer SHAP si disponible
        if SHAP_AVAILABLE and model:
            try:
                self.explainer = shap.TreeExplainer(model)
                self.logger.info("Explainer SHAP initialisé avec succès")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'initialisation de l'explainer SHAP: {e}")
    
    def explain_candidate_match(self, candidate, job, features):
        """
        Génère une explication pour le matching d'un candidat avec une offre.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            features: Features générées pour la paire
            
        Returns:
            Dict: Explication du matching
        """
        if not self.explainer or not SHAP_AVAILABLE:
            return self._generate_fallback_explanation(features, "candidate")
        
        try:
            # Convertir les features en format compatible avec XGBoost
            features_array = self._prepare_features(features)
            
            # Calculer les valeurs SHAP
            shap_values = self.explainer.shap_values(features_array)
            
            if isinstance(shap_values, list):
                # Cas multi-classes: prendre la première classe
                shap_values = shap_values[0]
            
            # Calculer l'importance des features
            feature_importance = self._process_shap_values(features, shap_values)
            
            # Générer une explication structurée pour un candidat
            explanation = self._format_candidate_explanation(
                candidate, job, feature_importance
            )
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de l'explication SHAP: {e}")
            return self._generate_fallback_explanation(features, "candidate")
    
    def explain_job_match(self, candidate, job, features):
        """
        Génère une explication pour le matching d'une offre avec un candidat.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            features: Features générées pour la paire
            
        Returns:
            Dict: Explication du matching
        """
        if not self.explainer or not SHAP_AVAILABLE:
            return self._generate_fallback_explanation(features, "job")
        
        try:
            # Convertir les features en format compatible avec XGBoost
            features_array = self._prepare_features(features)
            
            # Calculer les valeurs SHAP
            shap_values = self.explainer.shap_values(features_array)
            
            if isinstance(shap_values, list):
                # Cas multi-classes: prendre la première classe
                shap_values = shap_values[0]
            
            # Calculer l'importance des features
            feature_importance = self._process_shap_values(features, shap_values)
            
            # Générer une explication structurée pour une offre
            explanation = self._format_job_explanation(
                candidate, job, feature_importance
            )
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de l'explication SHAP: {e}")
            return self._generate_fallback_explanation(features, "job")
    
    def explain_detailed_match(self, candidate, job, features, model=None):
        """
        Génère une explication détaillée pour une analyse approfondie du matching.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            features: Features générées pour la paire
            model: Modèle à utiliser pour l'explication (optionnel)
            
        Returns:
            Dict: Explication détaillée du matching
        """
        if not SHAP_AVAILABLE:
            return self._generate_detailed_fallback(candidate, job, features)
        
        try:
            # Utiliser le modèle spécifié ou celui par défaut
            model_to_use = model or self.model
            
            if not model_to_use:
                return self._generate_detailed_fallback(candidate, job, features)
            
            # Créer un explainer spécifique si un nouveau modèle est fourni
            explainer = self.explainer
            if model is not None and model is not self.model:
                explainer = shap.TreeExplainer(model)
            
            # Convertir les features en format compatible avec XGBoost
            features_array = self._prepare_features(features)
            
            # Calculer les valeurs SHAP
            shap_values = explainer.shap_values(features_array)
            
            if isinstance(shap_values, list):
                # Cas multi-classes: prendre la première classe
                shap_values = shap_values[0]
            
            # Calculer l'importance des features
            feature_importance = self._process_shap_values(features, shap_values)
            
            # Structurer les facteurs positifs et négatifs
            positive_factors = []
            negative_factors = []
            
            for feature, importance in feature_importance:
                factor = {
                    "factor": self._format_feature_name(feature),
                    "importance": abs(importance),
                    "impact": importance,
                    "value": features.get(feature, 0),
                    "description": self._generate_feature_description(feature, features.get(feature, 0), importance > 0)
                }
                
                if importance > 0:
                    positive_factors.append(factor)
                else:
                    negative_factors.append(factor)
            
            # Trier par importance absolue
            positive_factors.sort(key=lambda x: x["importance"], reverse=True)
            negative_factors.sort(key=lambda x: x["importance"], reverse=True)
            
            # Calculer les scores par catégorie
            category_scores = self._calculate_category_scores(features)
            
            # Déterminer le score global et le résumé
            overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 50
            
            if overall_score >= 80:
                summary = "Excellente compatibilité entre le profil et le poste"
                recommendation = "Ce profil est très bien adapté pour ce poste"
            elif overall_score >= 60:
                summary = "Bonne compatibilité avec quelques points d'amélioration"
                recommendation = "Ce profil est adapté pour ce poste avec quelques réserves"
            elif overall_score >= 40:
                summary = "Compatibilité moyenne, certains aspects importants pourraient ne pas correspondre"
                recommendation = "Ce profil présente des lacunes pour ce poste, mais pourrait convenir avec des adaptations"
            else:
                summary = "Faible compatibilité, ce poste ne semble pas adapté au profil"
                recommendation = "Ce profil n'est pas recommandé pour ce poste"
            
            # Créer l'explication détaillée
            detailed_explanation = {
                "match_score": overall_score,
                "match_summary": summary,
                "recommendation": recommendation,
                "category_scores": category_scores,
                "positive_factors": positive_factors[:5],  # Limiter aux 5 principaux facteurs
                "negative_factors": negative_factors[:5],  # Limiter aux 5 principaux facteurs
                "candidate_highlights": self._extract_candidate_highlights(candidate, positive_factors),
                "job_requirements": self._extract_job_requirements(job, features),
                "improvement_suggestions": self._generate_improvement_suggestions(candidate, job, negative_factors),
                "feature_importance": {self._format_feature_name(f): i for f, i in feature_importance[:10]}
            }
            
            return detailed_explanation
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de l'explication détaillée: {e}")
            return self._generate_detailed_fallback(candidate, job, features)
    
    def _prepare_features(self, features):
        """
        Prépare les features au format attendu par le modèle.
        
        Args:
            features: Dictionnaire de features
            
        Returns:
            Object: Features au format approprié pour l'explainer
        """
        # S'assurer que les features sont un dictionnaire de valeurs numériques
        clean_features = {}
        for key, value in features.items():
            if value is None:
                clean_features[key] = 0.0
            elif isinstance(value, (int, float)):
                clean_features[key] = float(value)
            else:
                try:
                    clean_features[key] = float(value)
                except (ValueError, TypeError):
                    clean_features[key] = 0.0
        
        # Option 1: Format DMatrix de XGBoost
        try:
            if self.feature_names:
                # Ordonner les features selon feature_names
                ordered_features = [clean_features.get(name, 0.0) for name in self.feature_names]
                return xgb.DMatrix([ordered_features])
            else:
                return xgb.DMatrix([list(clean_features.values())])
        except Exception:
            # Option 2: Format numpy/pandas pour SHAP
            if self.feature_names:
                df = pd.DataFrame([clean_features])
                return df
            else:
                return np.array([list(clean_features.values())])
    
    def _process_shap_values(self, features, shap_values):
        """
        Traite les valeurs SHAP et les ordonne par importance.
        
        Args:
            features: Dictionnaire de features
            shap_values: Valeurs SHAP calculées
            
        Returns:
            List: Features triées par importance SHAP [(feature_name, importance)]
        """
        # Si les valeurs SHAP sont un tableau 2D, prendre la première ligne
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        # Associer les noms de features avec les valeurs SHAP
        if self.feature_names and len(self.feature_names) == len(shap_values):
            feature_importance = [(name, float(value)) for name, value in zip(self.feature_names, shap_values)]
        else:
            feature_names = list(features.keys())
            if len(feature_names) == len(shap_values):
                feature_importance = [(name, float(value)) for name, value in zip(feature_names, shap_values)]
            else:
                # Fallback: utiliser des indices comme noms
                feature_importance = [(f"feature_{i}", float(value)) for i, value in enumerate(shap_values)]
        
        # Trier par importance absolue décroissante
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return feature_importance
    
    def _format_candidate_explanation(self, candidate, job, feature_importance):
        """
        Formate une explication pour un candidat.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            feature_importance: Liste triée d'importance des features
            
        Returns:
            Dict: Explication formatée
        """
        # Extraire les facteurs positifs et négatifs
        positive_factors = []
        for feature, value in feature_importance:
            if value > 0:
                # Facteur positif
                positive_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": value,
                    "description": self._generate_feature_description(feature, None, True)
                })
                if len(positive_factors) >= 3:
                    break
        
        negative_factors = []
        for feature, value in feature_importance:
            if value < 0:
                # Facteur négatif
                negative_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": abs(value),
                    "description": self._generate_feature_description(feature, None, False)
                })
                if len(negative_factors) >= 2:
                    break
        
        # Créer l'explication
        explanation = {
            "strengths": [factor["description"] for factor in positive_factors],
            "areas_to_improve": [factor["description"] for factor in negative_factors],
            "top_factors": positive_factors + negative_factors
        }
        
        return explanation
    
    def _format_job_explanation(self, candidate, job, feature_importance):
        """
        Formate une explication pour une offre d'emploi.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            feature_importance: Liste triée d'importance des features
            
        Returns:
            Dict: Explication formatée
        """
        # Extraire les facteurs positifs et négatifs
        positive_factors = []
        for feature, value in feature_importance:
            if value > 0:
                # Facteur positif
                positive_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": value,
                    "description": self._generate_feature_description(feature, None, True, for_job=True)
                })
                if len(positive_factors) >= 3:
                    break
        
        negative_factors = []
        for feature, value in feature_importance:
            if value < 0:
                # Facteur négatif
                negative_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": abs(value),
                    "description": self._generate_feature_description(feature, None, False, for_job=True)
                })
                if len(negative_factors) >= 2:
                    break
        
        # Créer l'explication
        explanation = {
            "matching_points": [factor["description"] for factor in positive_factors],
            "gaps": [factor["description"] for factor in negative_factors],
            "top_factors": positive_factors + negative_factors
        }
        
        return explanation
    
    def _generate_fallback_explanation(self, features, explanation_type):
        """
        Génère une explication de repli quand SHAP n'est pas disponible.
        
        Args:
            features: Dictionnaire de features
            explanation_type: Type d'explication ("candidate" ou "job")
            
        Returns:
            Dict: Explication de repli
        """
        # Trier les features par valeur décroissante
        sorted_features = sorted(
            features.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Extraire les facteurs positifs (meilleurs scores)
        positive_factors = []
        for feature, value in sorted_features[:3]:
            if value >= 0.5:
                positive_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": value,
                    "description": self._generate_feature_description(
                        feature, value, True, 
                        for_job=(explanation_type == "job")
                    )
                })
        
        # Extraire les facteurs négatifs (scores les plus bas)
        negative_factors = []
        for feature, value in sorted(features.items(), key=lambda x: x[1])[:2]:
            if value < 0.5:
                negative_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": 1.0 - value,
                    "description": self._generate_feature_description(
                        feature, value, False, 
                        for_job=(explanation_type == "job")
                    )
                })
        
        if explanation_type == "candidate":
            return {
                "strengths": [factor["description"] for factor in positive_factors],
                "areas_to_improve": [factor["description"] for factor in negative_factors],
                "top_factors": positive_factors + negative_factors
            }
        else:
            return {
                "matching_points": [factor["description"] for factor in positive_factors],
                "gaps": [factor["description"] for factor in negative_factors],
                "top_factors": positive_factors + negative_factors
            }
    
    def _generate_detailed_fallback(self, candidate, job, features):
        """
        Génère une explication détaillée de repli quand SHAP n'est pas disponible.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            features: Features générées pour la paire
            
        Returns:
            Dict: Explication détaillée de repli
        """
        # Calculer les scores par catégorie
        category_scores = self._calculate_category_scores(features)
        
        # Déterminer le score global et le résumé
        overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 50
        
        if overall_score >= 80:
            summary = "Excellente compatibilité entre le profil et le poste"
            recommendation = "Ce profil est très bien adapté pour ce poste"
        elif overall_score >= 60:
            summary = "Bonne compatibilité avec quelques points d'amélioration"
            recommendation = "Ce profil est adapté pour ce poste avec quelques réserves"
        elif overall_score >= 40:
            summary = "Compatibilité moyenne, certains aspects importants pourraient ne pas correspondre"
            recommendation = "Ce profil présente des lacunes pour ce poste, mais pourrait convenir avec des adaptations"
        else:
            summary = "Faible compatibilité, ce poste ne semble pas adapté au profil"
            recommendation = "Ce profil n'est pas recommandé pour ce poste"
        
        # Trier les features par valeur décroissante
        sorted_features = sorted(
            features.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Extraire les facteurs positifs (meilleurs scores)
        positive_factors = []
        for feature, value in sorted_features[:5]:
            if value >= 0.5:
                positive_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": abs(value),
                    "impact": value,
                    "value": value,
                    "description": self._generate_feature_description(feature, value, True)
                })
        
        # Extraire les facteurs négatifs (scores les plus bas)
        negative_factors = []
        reverse_sorted_features = sorted(
            features.items(), 
            key=lambda x: x[1]
        )
        for feature, value in reverse_sorted_features[:5]:
            if value < 0.5:
                negative_factors.append({
                    "factor": self._format_feature_name(feature),
                    "importance": abs(0.5 - value),
                    "impact": value - 0.5,
                    "value": value,
                    "description": self._generate_feature_description(feature, value, False)
                })
        
        # Créer l'explication détaillée
        detailed_explanation = {
            "match_score": overall_score,
            "match_summary": summary,
            "recommendation": recommendation,
            "category_scores": category_scores,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "candidate_highlights": self._extract_candidate_highlights(candidate, positive_factors),
            "job_requirements": self._extract_job_requirements(job, features),
            "improvement_suggestions": self._generate_improvement_suggestions(candidate, job, negative_factors),
            "feature_importance": {self._format_feature_name(f): v for f, v in sorted_features[:10]}
        }
        
        return detailed_explanation
    
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
    
    def _generate_feature_description(self, feature_name, feature_value=None, is_positive=True, for_job=False):
        """
        Génère une description textuelle pour une feature.
        
        Args:
            feature_name: Nom de la feature
            feature_value: Valeur de la feature (optionnel)
            is_positive: Si c'est un facteur positif ou négatif
            for_job: Si l'explication est orientée offre d'emploi
            
        Returns:
            str: Description lisible
        """
        # Convertir la valeur en pourcentage si fournie
        score_text = ""
        if feature_value is not None:
            score_percent = min(100, feature_value * 100)
            score_text = f" ({score_percent:.0f}%)"
        
        # Description adaptée au type de feature et au contexte
        
        # Features de compétences
        if "skills_exact_match" in feature_name or "skills_similarity" in feature_name:
            if is_positive:
                return f"Forte correspondance des compétences techniques{score_text}" if not for_job else \
                       f"Vos compétences correspondent bien aux exigences du poste{score_text}"
            else:
                return f"Faible correspondance des compétences techniques{score_text}" if not for_job else \
                       f"Vos compétences ne correspondent pas totalement aux exigences{score_text}"
        
        if "skills_coverage" in feature_name:
            if is_positive:
                return f"Couverture satisfaisante des compétences requises{score_text}" if not for_job else \
                       f"Vous possédez la majorité des compétences requises{score_text}"
            else:
                return f"Couverture insuffisante des compétences requises{score_text}" if not for_job else \
                       f"Il vous manque plusieurs compétences requises{score_text}"
        
        if "skills_expertise" in feature_name:
            if is_positive:
                return f"Niveau d'expertise technique adapté{score_text}" if not for_job else \
                       f"Votre niveau d'expertise technique est adapté{score_text}"
            else:
                return f"Niveau d'expertise technique insuffisant{score_text}" if not for_job else \
                       f"Votre niveau d'expertise technique est insuffisant{score_text}"
        
        # Features culturelles
        if "cultural_values" in feature_name:
            if is_positive:
                return f"Bon alignement avec les valeurs de l'entreprise{score_text}" if not for_job else \
                       f"Vos valeurs s'alignent bien avec celles de l'entreprise{score_text}"
            else:
                return f"Faible alignement avec les valeurs de l'entreprise{score_text}" if not for_job else \
                       f"Vos valeurs diffèrent de celles de l'entreprise{score_text}"
        
        if "cultural_overall" in feature_name:
            if is_positive:
                return f"Bonne compatibilité culturelle globale{score_text}" if not for_job else \
                       f"L'environnement de travail correspond à vos attentes{score_text}"
            else:
                return f"Faible compatibilité culturelle globale{score_text}" if not for_job else \
                       f"L'environnement de travail pourrait ne pas vous convenir{score_text}"
        
        # Features textuelles
        if "text_job_title" in feature_name:
            if is_positive:
                return f"Titre du poste correspondant bien à l'expérience{score_text}" if not for_job else \
                       f"Le poste correspond bien à votre parcours professionnel{score_text}"
            else:
                return f"Titre du poste peu aligné avec l'expérience{score_text}" if not for_job else \
                       f"Le poste diffère de votre parcours professionnel habituel{score_text}"
        
        if "text_experience" in feature_name:
            if is_positive:
                return f"Expérience professionnelle pertinente pour le poste{score_text}" if not for_job else \
                       f"Votre expérience est très pertinente pour ce poste{score_text}"
            else:
                return f"Expérience professionnelle peu pertinente pour le poste{score_text}" if not for_job else \
                       f"Votre expérience est peu adaptée à ce poste{score_text}"
        
        # Features de préférence
        if "pref_location" in feature_name:
            if is_positive:
                return f"Localisation correspondant aux préférences{score_text}" if not for_job else \
                       f"Localisation idéale selon vos préférences{score_text}"
            else:
                return f"Localisation ne correspondant pas aux préférences{score_text}" if not for_job else \
                       f"Localisation éloignée de vos préférences{score_text}"
        
        if "pref_salary" in feature_name:
            if is_positive:
                return f"Rémunération correspondant aux attentes{score_text}" if not for_job else \
                       f"Rémunération conforme à vos attentes{score_text}"
            else:
                return f"Rémunération ne correspondant pas aux attentes{score_text}" if not for_job else \
                       f"Rémunération en dessous de vos attentes{score_text}"
        
        if "pref_work_mode" in feature_name:
            if is_positive:
                return f"Mode de travail adapté aux préférences{score_text}" if not for_job else \
                       f"Mode de travail correspondant à vos préférences{score_text}"
            else:
                return f"Mode de travail non adapté aux préférences{score_text}" if not for_job else \
                       f"Mode de travail différent de vos préférences{score_text}"
        
        # Description par défaut
        if is_positive:
            return f"Forte correspondance{score_text}"
        else:
            return f"Faible correspondance{score_text}"
    
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
        
        return category_scores
    
    def _extract_candidate_highlights(self, candidate, positive_factors):
        """
        Extrait les points forts du candidat basés sur les facteurs positifs.
        
        Args:
            candidate: Profil du candidat
            positive_factors: Facteurs positifs identifiés
            
        Returns:
            List: Points forts du candidat
        """
        highlights = []
        
        # Compétences techniques
        if any("skills" in factor["factor"].lower() for factor in positive_factors):
            if "competences" in candidate and isinstance(candidate["competences"], list):
                top_skills = candidate["competences"][:5] if len(candidate["competences"]) > 5 else candidate["competences"]
                if top_skills:
                    highlights.append({
                        "type": "skills",
                        "title": "Compétences clés",
                        "items": top_skills
                    })
        
        # Expérience pertinente
        if any("experience" in factor["factor"].lower() for factor in positive_factors):
            if "experience" in candidate and isinstance(candidate["experience"], list):
                relevant_exp = []
                for exp in candidate["experience"][:2]:  # Limiter aux 2 expériences les plus récentes
                    if isinstance(exp, dict):
                        exp_info = f"{exp.get('title', 'Poste')} chez {exp.get('company', 'Entreprise')}"
                        if "duration" in exp:
                            exp_info += f" ({exp['duration']})"
                        relevant_exp.append(exp_info)
                    elif isinstance(exp, str):
                        relevant_exp.append(exp)
                
                if relevant_exp:
                    highlights.append({
                        "type": "experience",
                        "title": "Expérience pertinente",
                        "items": relevant_exp
                    })
        
        # Formation
        if "education" in candidate:
            education_info = []
            if isinstance(candidate["education"], list):
                for edu in candidate["education"][:2]:  # Limiter aux 2 formations principales
                    if isinstance(edu, dict):
                        edu_info = f"{edu.get('degree', 'Diplôme')} en {edu.get('field', 'domaine')}"
                        if "institution" in edu:
                            edu_info += f" - {edu['institution']}"
                        education_info.append(edu_info)
                    elif isinstance(edu, str):
                        education_info.append(edu)
            elif isinstance(candidate["education"], str):
                education_info.append(candidate["education"])
                
            if education_info:
                highlights.append({
                    "type": "education",
                    "title": "Formation",
                    "items": education_info
                })
        
        return highlights
    
    def _extract_job_requirements(self, job, features):
        """
        Extrait les exigences clés du poste pertinentes pour le matching.
        
        Args:
            job: Profil de l'offre d'emploi
            features: Features générées pour la paire
            
        Returns:
            List: Exigences clés du poste
        """
        requirements = []
        
        # Compétences requises
        if "required_skills" in job and isinstance(job["required_skills"], list):
            skills = job["required_skills"][:5] if len(job["required_skills"]) > 5 else job["required_skills"]
            if skills:
                requirements.append({
                    "type": "skills",
                    "title": "Compétences requises",
                    "items": skills
                })
        
        # Expérience requise
        experience_info = []
        if "required_experience_years" in job:
            years = job["required_experience_years"]
            experience_info.append(f"{years} an(s) d'expérience requis")
        
        if "required_experience" in job:
            if isinstance(job["required_experience"], list):
                for exp in job["required_experience"][:2]:
                    experience_info.append(exp)
            elif isinstance(job["required_experience"], str):
                experience_info.append(job["required_experience"])
        
        if experience_info:
            requirements.append({
                "type": "experience",
                "title": "Expérience requise",
                "items": experience_info
            })
        
        # Formation requise
        education_info = []
        if "required_education_level" in job:
            education_info.append(f"Niveau: {job['required_education_level']}")
        
        if "preferred_education_field" in job:
            education_info.append(f"Domaine: {job['preferred_education_field']}")
        
        if education_info:
            requirements.append({
                "type": "education",
                "title": "Formation requise",
                "items": education_info
            })
        
        # Informations pratiques
        practical_info = []
        if "location" in job:
            practical_info.append(f"Lieu: {job['location']}")
        
        if "work_mode" in job:
            practical_info.append(f"Mode de travail: {job['work_mode']}")
        
        if "contract_type" in job:
            practical_info.append(f"Type de contrat: {job['contract_type']}")
        
        if practical_info:
            requirements.append({
                "type": "practical",
                "title": "Informations pratiques",
                "items": practical_info
            })
        
        return requirements
    
    def _generate_improvement_suggestions(self, candidate, job, negative_factors):
        """
        Génère des suggestions d'amélioration basées sur les facteurs négatifs.
        
        Args:
            candidate: Profil du candidat
            job: Profil de l'offre d'emploi
            negative_factors: Facteurs négatifs identifiés
            
        Returns:
            List: Suggestions d'amélioration
        """
        suggestions = []
        
        # Suggestions pour les compétences
        if any("skills" in factor["factor"].lower() for factor in negative_factors):
            if "required_skills" in job and isinstance(job["required_skills"], list):
                candidate_skills = candidate.get("competences", []) if isinstance(candidate.get("competences"), list) else []
                missing_skills = [skill for skill in job["required_skills"] 
                                 if not any(s.lower() == skill.lower() or skill.lower() in s.lower() 
                                          or s.lower() in skill.lower() for s in candidate_skills)]
                
                if missing_skills:
                    suggestions.append({
                        "area": "Compétences techniques",
                        "suggestion": f"Développer les compétences suivantes: {', '.join(missing_skills[:3])}" + 
                                     (f" et {len(missing_skills) - 3} autres" if len(missing_skills) > 3 else "")
                    })
        
        # Suggestions pour l'expérience
        if any("experience" in factor["factor"].lower() for factor in negative_factors):
            if "required_experience_years" in job:
                candidate_exp_years = candidate.get("experience_years", 0)
                required_years = job["required_experience_years"]
                
                if candidate_exp_years < required_years:
                    suggestions.append({
                        "area": "Expérience professionnelle",
                        "suggestion": f"Acquérir {required_years - candidate_exp_years} année(s) d'expérience supplémentaire dans le domaine"
                    })
        
        # Suggestions pour la formation
        if any("education" in factor["factor"].lower() for factor in negative_factors):
            if "required_education_level" in job:
                suggestions.append({
                    "area": "Formation",
                    "suggestion": f"Envisager de compléter votre formation pour atteindre le niveau {job['required_education_level']}"
                })
        
        # Suggestions génériques si aucune suggestion spécifique n'est générée
        if not suggestions:
            # Suggestion basée sur les facteurs négatifs les plus importants
            if negative_factors:
                top_factor = negative_factors[0]["factor"]
                if "skills" in top_factor.lower():
                    suggestions.append({
                        "area": "Compétences techniques",
                        "suggestion": "Renforcer vos compétences techniques pour mieux correspondre aux exigences du poste"
                    })
                elif "experience" in top_factor.lower():
                    suggestions.append({
                        "area": "Expérience professionnelle",
                        "suggestion": "Mettre en avant les aspects de votre expérience les plus pertinents pour ce poste"
                    })
                elif "cultural" in top_factor.lower() or "values" in top_factor.lower():
                    suggestions.append({
                        "area": "Fit culturel",
                        "suggestion": "Renseignez-vous davantage sur la culture d'entreprise pour évaluer votre compatibilité"
                    })
                elif "location" in top_factor.lower():
                    suggestions.append({
                        "area": "Localisation",
                        "suggestion": "Évaluez si la localisation du poste est compatible avec vos contraintes"
                    })
                else:
                    suggestions.append({
                        "area": "Compatibilité globale",
                        "suggestion": "Évaluez si ce type de poste correspond réellement à vos objectifs professionnels"
                    })
        
        return suggestions
