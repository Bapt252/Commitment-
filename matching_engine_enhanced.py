#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import math
import datetime
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de l'API Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")

class EnhancedMatchingEngine:
    """
    Moteur de matching amélioré entre candidats et offres d'emploi
    """
    
    def __init__(self):
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        self.preferences = {}
        
    def load_candidate_data(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> None:
        """
        Charge les données du candidat dans le moteur
        
        Args:
            cv_data: Données extraites du CV
            questionnaire_data: Données extraites du questionnaire
        """
        self.cv_data = cv_data
        self.questionnaire_data = questionnaire_data
        
        # Extraire les préférences du candidat pour la pondération dynamique
        self.preferences = self._extract_candidate_preferences()
        
        logger.info(f"Données candidat chargées: {len(self.cv_data)} éléments CV, {len(self.questionnaire_data)} éléments questionnaire")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """
        Charge les données des offres d'emploi dans le moteur
        
        Args:
            job_data: Liste des offres d'emploi à analyser
        """
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def _extract_candidate_preferences(self) -> Dict[str, float]:
        """
        Extrait les préférences du candidat pour ajuster la pondération des critères
        
        Returns:
            Dictionnaire des préférences de pondération
        """
        # Pondération par défaut
        default_weights = {
            'skills': 0.30,        # 30% pour les compétences
            'contract': 0.15,      # 15% pour le type de contrat
            'location': 0.20,      # 20% pour la localisation
            'date': 0.10,          # 10% pour la disponibilité
            'salary': 0.15,        # 15% pour le salaire
            'experience': 0.10,    # 10% pour l'expérience
            'soft_skills': 0.0,    # 0% pour les soft skills (nouveau)
            'culture': 0.0         # 0% pour la culture d'entreprise (nouveau)
        }
        
        # Si le questionnaire contient des préférences explicites
        if 'criteres_importants' in self.questionnaire_data:
            criteres = self.questionnaire_data['criteres_importants']
            
            # Mise à jour des poids selon les préférences
            weights_adjustment = {}
            
            # Exemples de mappings pour les préférences
            preference_mappings = {
                'salaire': 'salary',
                'salaire_important': 'salary',
                'localisation': 'location',
                'proximite': 'location',
                'competences': 'skills',
                'competences_techniques': 'skills',
                'type_contrat': 'contract',
                'contrat': 'contract',
                'date_debut': 'date',
                'disponibilite': 'date',
                'experience': 'experience',
                'niveau_experience': 'experience',
                'soft_skills': 'soft_skills',
                'competences_comportementales': 'soft_skills',
                'culture': 'culture',
                'culture_entreprise': 'culture',
                'ambiance': 'culture'
            }
            
            # Calculer les ajustements en fonction des préférences
            total_importance = 0
            for critere, importance in criteres.items():
                critere_key = preference_mappings.get(critere.lower(), None)
                if critere_key:
                    weights_adjustment[critere_key] = float(importance)
                    total_importance += float(importance)
            
            # Normaliser les ajustements pour que la somme soit égale à 1
            if total_importance > 0:
                weights = {}
                remaining_weight = 1.0
                
                # Appliquer les ajustements proportionnellement
                for key, value in weights_adjustment.items():
                    weights[key] = (value / total_importance) * 0.7  # 70% du poids basé sur les préférences
                    remaining_weight -= weights[key]
                
                # Répartir le poids restant proportionnellement sur les critères non spécifiés
                unspecified_criteria = [k for k in default_weights.keys() if k not in weights]
                if unspecified_criteria:
                    for key in unspecified_criteria:
                        weights[key] = remaining_weight / len(unspecified_criteria)
                
                return weights
        
        # Si le candidat a mentionné des soft skills spécifiques dans son CV
        if 'soft_skills' in self.cv_data and self.cv_data['soft_skills']:
            # Augmenter légèrement le poids des soft skills
            default_weights['soft_skills'] = 0.05
            # Réduire proportionnellement les autres poids
            remaining_sum = 0.95
            original_sum = sum(v for k, v in default_weights.items() if k != 'soft_skills')
            for k in default_weights:
                if k != 'soft_skills':
                    default_weights[k] = default_weights[k] * (remaining_sum / original_sum)
        
        return default_weights
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """
        Calcule les scores de matching pour toutes les offres chargées
        
        Returns:
            Liste des offres avec leurs scores de matching
        """
        if not self.cv_data or not self.questionnaire_data or not self.job_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        
        for job in self.job_data:
            # Calcul des différents critères de matching
            skills_score = self._calculate_skills_score(job)
            contract_score = self._calculate_contract_score(job)
            location_score = self._calculate_location_score(job)
            date_score = self._calculate_availability_score(job)
            salary_score = self._calculate_salary_score(job)
            experience_score = self._calculate_experience_score(job)
            
            # Nouveaux critères
            soft_skills_score = self._calculate_soft_skills_score(job)
            culture_score = self._calculate_culture_score(job)
            
            # Utiliser les poids dynamiques basés sur les préférences du candidat
            weights = self.preferences
            
            # Calcul du score global (pondéré)
            total_score = (
                skills_score * weights.get('skills', 0.30) +
                contract_score * weights.get('contract', 0.15) +
                location_score * weights.get('location', 0.20) +
                date_score * weights.get('date', 0.10) +
                salary_score * weights.get('salary', 0.15) +
                experience_score * weights.get('experience', 0.10) +
                soft_skills_score * weights.get('soft_skills', 0.0) +
                culture_score * weights.get('culture', 0.0)
            )
            
            # Formatage du score final en pourcentage
            job_result = job.copy()  # Copie pour ne pas modifier l'original
            job_result['matching_score'] = round(total_score * 100)
            
            # Détails des scores par critère pour affichage détaillé
            job_result['matching_details'] = {
                'skills': round(skills_score * 100),
                'contract': round(contract_score * 100),
                'location': round(location_score * 100),
                'date': round(date_score * 100),
                'salary': round(salary_score * 100),
                'experience': round(experience_score * 100),
                'soft_skills': round(soft_skills_score * 100),
                'culture': round(culture_score * 100)
            }
            
            # Ajouter des explications textuelles sur le matching
            job_result['matching_explanations'] = self._generate_matching_explanations(job_result['matching_details'])
            
            results.append(job_result)
        
        # Tri des résultats par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return results
    
    def _generate_matching_explanations(self, scores: Dict[str, int]) -> Dict[str, str]:
        """
        Génère des explications textuelles pour chaque critère de matching
        
        Args:
            scores: Dictionnaire des scores par critère
            
        Returns:
            Dictionnaire d'explications par critère
        """
        explanations = {}
        
        # Explications pour les compétences
        if scores['skills'] >= 90:
            explanations['skills'] = "Vos compétences correspondent parfaitement au profil recherché."
        elif scores['skills'] >= 70:
            explanations['skills'] = "La plupart de vos compétences correspondent aux besoins du poste."
        elif scores['skills'] >= 50:
            explanations['skills'] = "Certaines de vos compétences correspondent au profil, mais il y a des écarts importants."
        else:
            explanations['skills'] = "Peu de correspondance entre vos compétences et celles recherchées pour ce poste."
        
        # Explications pour le contrat
        if scores['contract'] >= 90:
            explanations['contract'] = "Le type de contrat correspond exactement à vos attentes."
        elif scores['contract'] >= 50:
            explanations['contract'] = "Le type de contrat est similaire à ce que vous recherchez."
        else:
            explanations['contract'] = "Le type de contrat ne correspond pas à vos préférences."
        
        # Explications pour la localisation
        if scores['location'] >= 90:
            explanations['location'] = "Localisation idéale par rapport à votre domicile."
        elif scores['location'] >= 70:
            explanations['location'] = "Temps de trajet raisonnable par rapport à vos attentes."
        elif scores['location'] >= 50:
            explanations['location'] = "Temps de trajet légèrement supérieur à vos préférences."
        else:
            explanations['location'] = "Localisation éloignée de votre domicile."
        
        # Explications pour la date de disponibilité
        if scores['date'] >= 90:
            explanations['date'] = "La date de prise de poste correspond parfaitement à votre disponibilité."
        elif scores['date'] >= 70:
            explanations['date'] = "Date de début proche de votre disponibilité."
        else:
            explanations['date'] = "Décalage important entre votre disponibilité et la date de début souhaitée."
        
        # Explications pour le salaire
        if scores['salary'] >= 90:
            explanations['salary'] = "Rémunération proposée supérieure à vos attentes."
        elif scores['salary'] >= 70:
            explanations['salary'] = "Rémunération en ligne avec vos attentes."
        elif scores['salary'] >= 50:
            explanations['salary'] = "Rémunération légèrement inférieure à vos attentes."
        else:
            explanations['salary'] = "Rémunération proposée nettement inférieure à vos attentes."
        
        # Explications pour l'expérience
        if scores['experience'] >= 90:
            explanations['experience'] = "Votre niveau d'expérience correspond parfaitement au poste."
        elif scores['experience'] >= 70:
            explanations['experience'] = "Votre expérience est appropriée pour ce poste."
        elif scores['experience'] >= 50:
            explanations['experience'] = "Vous avez un peu moins d'expérience que demandé, mais cela reste accessible."
        else:
            explanations['experience'] = "Écart important entre votre expérience et celle recherchée."
        
        # Explications pour les soft skills (si applicables)
        if 'soft_skills' in scores:
            if scores['soft_skills'] >= 80:
                explanations['soft_skills'] = "Vos compétences comportementales correspondent bien à la culture de l'entreprise."
            elif scores['soft_skills'] >= 50:
                explanations['soft_skills'] = "Certaines de vos compétences comportementales sont recherchées pour ce poste."
            else:
                explanations['soft_skills'] = "Vos compétences comportementales déclarées diffèrent de celles recherchées."
        
        # Explications pour la culture d'entreprise (si applicable)
        if 'culture' in scores:
            if scores['culture'] >= 80:
                explanations['culture'] = "La culture d'entreprise semble parfaitement alignée avec vos valeurs."
            elif scores['culture'] >= 50:
                explanations['culture'] = "La culture d'entreprise présente certaines similitudes avec vos préférences."
            else:
                explanations['culture'] = "La culture d'entreprise pourrait ne pas correspondre à vos préférences."
        
        return explanations
    
    def _calculate_soft_skills_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des soft skills
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire les soft skills du CV et du job
        cv_soft_skills = set(skill.lower() for skill in self.cv_data.get('soft_skills', []))
        
        # Vérifier si le job a des soft skills spécifiés
        if 'soft_skills' not in job:
            return 0.5  # Score neutre si pas d'information
        
        job_soft_skills = set(skill.lower() for skill in job.get('soft_skills', []))
        
        # Si pas de soft skills listés dans l'offre, retourner un score par défaut
        if not job_soft_skills:
            return 0.5
        
        # Calculer l'intersection des soft skills
        matching_skills = cv_soft_skills.intersection(job_soft_skills)
        
        # Calculer le score basé sur le pourcentage de soft skills requis que le candidat possède
        if len(job_soft_skills) == 0:
            return 0.5
        
        # Si le candidat n'a pas déclaré de soft skills mais que l'offre en demande
        if not cv_soft_skills:
            return 0.3  # Score par défaut plutôt bas mais pas nul
        
        # Calculer un score basé sur la correspondance
        match_ratio = len(matching_skills) / len(job_soft_skills)
        
        # Ajouter un bonus si le candidat a des soft skills supplémentaires valorisables
        additional_skills = cv_soft_skills - job_soft_skills
        if additional_skills:
            bonus = min(0.2, len(additional_skills) * 0.05)  # Max 20% de bonus
            match_ratio = min(1.0, match_ratio + bonus)
        
        return match_ratio
    
    def _calculate_culture_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la culture d'entreprise
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Vérifier si le job et le candidat ont des informations sur la culture
        if 'culture_entreprise' not in job or 'preferences_culture' not in self.questionnaire_data:
            return 0.5  # Score neutre si pas d'information
        
        # Extraire les préférences culturelles
        job_culture = job.get('culture_entreprise', {})
        candidate_preferences = self.questionnaire_data.get('preferences_culture', {})
        
        # Si les structures ne correspondent pas, score par défaut
        if not isinstance(job_culture, dict) or not isinstance(candidate_preferences, dict):
            return 0.5
        
        # Calculer le score sur plusieurs dimensions culturelles
        scores = []
        
        # Valeurs d'entreprise
        if 'valeurs' in job_culture and 'valeurs_importantes' in candidate_preferences:
            job_values = set(v.lower() for v in job_culture['valeurs'])
            candidate_values = set(v.lower() for v in candidate_preferences['valeurs_importantes'])
            
            if job_values and candidate_values:
                matching_values = job_values.intersection(candidate_values)
                values_score = len(matching_values) / max(len(job_values), len(candidate_values))
                scores.append(values_score)
        
        # Taille de l'équipe
        if 'taille_equipe' in job_culture and 'taille_equipe_preferee' in candidate_preferences:
            job_size = job_culture['taille_equipe']
            preferred_size = candidate_preferences['taille_equipe_preferee']
            
            # Conversion en catégories pour comparaison
            size_categories = {
                'petite': range(1, 10),
                'moyenne': range(10, 30),
                'grande': range(30, 100),
                'très grande': range(100, 1000)
            }
            
            # Convertir les tailles numériques en catégories
            job_size_category = None
            for category, size_range in size_categories.items():
                if job_size in size_range:
                    job_size_category = category
                    break
            
            if job_size_category and preferred_size:
                if job_size_category == preferred_size:
                    scores.append(1.0)
                elif (job_size_category == 'moyenne' and preferred_size == 'petite') or \
                     (job_size_category == 'petite' and preferred_size == 'moyenne') or \
                     (job_size_category == 'grande' and preferred_size == 'moyenne') or \
                     (job_size_category == 'moyenne' and preferred_size == 'grande'):
                    scores.append(0.7)  # Catégories adjacentes
                else:
                    scores.append(0.3)  # Catégories éloignées
        
        # Méthodologie de travail
        if 'methodologie' in job_culture and 'methodologie_preferee' in candidate_preferences:
            job_methodology = job_culture['methodologie'].lower()
            preferred_methodology = candidate_preferences['methodologie_preferee'].lower()
            
            if job_methodology and preferred_methodology:
                # Correspondance exacte
                if job_methodology == preferred_methodology:
                    scores.append(1.0)
                # Correspondances partielles (ex: Agile et Scrum)
                elif ('agile' in job_methodology and 'agile' in preferred_methodology) or \
                     ('scrum' in job_methodology and 'scrum' in preferred_methodology) or \
                     ('kanban' in job_methodology and 'kanban' in preferred_methodology):
                    scores.append(0.8)
                # Autres cas
                else:
                    scores.append(0.4)
        
        # Environnement de travail
        if 'environnement' in job_culture and 'environnement_prefere' in candidate_preferences:
            job_env = job_culture['environnement'].lower()
            preferred_env = candidate_preferences['environnement_prefere'].lower()
            
            if job_env and preferred_env:
                # Correspondance par mots-clés
                keywords_job = set(job_env.split())
                keywords_pref = set(preferred_env.split())
                
                matching_keywords = keywords_job.intersection(keywords_pref)
                if matching_keywords:
                    keyword_score = len(matching_keywords) / max(len(keywords_job), len(keywords_pref))
                    scores.append(keyword_score)
                else:
                    scores.append(0.3)
        
        # Si aucun critère n'a pu être comparé, retourner un score neutre
        if not scores:
            return 0.5
        
        # Moyenne des scores calculés
        return sum(scores) / len(scores)
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retourne les N meilleures offres correspondant au profil
        
        Args:
            limit: Nombre d'offres à retourner
            
        Returns:
            Liste des meilleures offres avec leurs scores
        """
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]
    
    # Les autres méthodes de calcul restent similaires à l'implémentation originale
    # Je ne les reproduis pas toutes ici pour concision, mais elles seraient à conserver
    # _calculate_skills_score, _calculate_contract_score, etc.
    
# Fonction d'entrée principale améliorée
def enhanced_match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                           job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction principale améliorée qui calcule les matchings entre un candidat et des offres d'emploi
    
    Args:
        cv_data: Données extraites du CV
        questionnaire_data: Données du questionnaire
        job_data: Liste des offres d'emploi
        limit: Nombre maximum d'offres à retourner
        
    Returns:
        Liste des meilleures offres avec leurs scores
    """
    engine = EnhancedMatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)