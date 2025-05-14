"""
Service de Matching Bidirectionnel Nexten
-----------------------------------------
Implémente un algorithme de matching avancé et bidirectionnel
entre candidats et offres d'emploi, en tenant compte:
- des données du CV
- des questionnaires candidat et entreprise
- de l'analyse géographique (temps de trajet)

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import logging
import json
import math
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import aiohttp

from app.algorithms.nlp_utils import (
    normalize_text, extract_keywords, calculate_similarity,
    calculate_semantic_similarity, are_skills_similar,
    find_common_skills, find_missing_skills
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class NextenBidirectionalMatcher:
    """
    Algorithme de matching bidirectionnel pour Nexten
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise l'algorithme de matching bidirectionnel
        
        Args:
            config: Configuration personnalisée (facultatif)
        """
        # Configuration par défaut
        self.default_config = {
            'weights': {
                # Poids pour l'analyse du CV
                'cv_skills': 0.25,
                'cv_experience': 0.15,
                'cv_description': 0.10,
                'cv_title': 0.05,
                
                # Poids pour les questionnaires
                'information_personnelle': 0.05,
                'mobilite_preferences': 0.15,
                'motivations_secteurs': 0.15,
                'disponibilite_situation': 0.10,
            },
            'thresholds': {
                'minimum_score': 0.3,
                'excellent_match': 0.85,
                'good_match': 0.7,
                'moderate_match': 0.5,
            },
            'skills_config': {
                'essential_bonus': 1.5,
                'nice_to_have_factor': 0.7,
                'synonym_similarity_threshold': 0.85,
            },
            'experience_config': {
                'penalty_rate_under': 0.8,
                'penalty_rate_over': 0.9,
            },
            'travel_time_config': {
                'maps_api_key': settings.GOOGLE_MAPS_API_KEY,
                'default_transport_mode': 'driving',
            }
        }
        
        # Fusionner avec la configuration personnalisée
        self.config = self.default_config.copy()
        if config:
            self._deep_update(self.config, config)
        
        # Initialiser les API externes
        self.maps_api_key = self.config['travel_time_config']['maps_api_key']
        
        logger.info("Initialisation de l'algorithme de matching bidirectionnel Nexten")
    
    def _deep_update(self, d: Dict, u: Dict) -> Dict:
        """Mise à jour récursive d'un dictionnaire"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    async def calculate_match(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score de matching entre un candidat et une offre d'emploi
        
        Args:
            candidate_data: Données du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Résultat du matching avec score et insights
        """
        # Extraire les données
        cv_data = candidate_data.get('cv', {})
        candidate_questionnaire = candidate_data.get('questionnaire', {})
        job_description = job_data.get('description', {})
        company_questionnaire = job_data.get('questionnaire', {})
        
        # 1. Évaluation basée sur le CV
        cv_scores = await self._evaluate_cv_match(cv_data, job_description, company_questionnaire)
        
        # 2. Évaluation basée sur les questionnaires
        questionnaire_scores = await self._evaluate_questionnaire_match(
            candidate_questionnaire, company_questionnaire, job_description
        )
        
        # 3. Calcul du score global
        weights = self.config['weights']
        total_score = (
            cv_scores['total'] * (weights['cv_skills'] + weights['cv_experience'] + 
                                weights['cv_description'] + weights['cv_title']) +
            questionnaire_scores['total'] * (weights['information_personnelle'] + 
                                          weights['mobilite_preferences'] + 
                                          weights['motivations_secteurs'] + 
                                          weights['disponibilite_situation'])
        )
        
        # 4. Déterminer la catégorie
        thresholds = self.config['thresholds']
        if total_score >= thresholds['excellent_match']:
            category = 'excellent'
        elif total_score >= thresholds['good_match']:
            category = 'good'
        elif total_score >= thresholds['moderate_match']:
            category = 'moderate'
        elif total_score >= thresholds['minimum_score']:
            category = 'weak'
        else:
            category = 'insufficient'
        
        # 5. Générer des insights
        insights = self._generate_insights(cv_scores, questionnaire_scores, cv_data, job_description)
        
        # Résultat complet
        result = {
            'score': round(total_score, 2),
            'category': category,
            'details': {
                'cv': cv_scores,
                'questionnaire': questionnaire_scores
            },
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    async def _evaluate_cv_match(self, cv_data: Dict[str, Any], job_description: Dict[str, Any], 
                                company_questionnaire: Dict[str, Any]) -> Dict[str, float]:
        """
        Évalue la correspondance basée sur le CV
        
        Args:
            cv_data: Données du CV
            job_description: Description du poste
            company_questionnaire: Questionnaire entreprise
            
        Returns:
            Scores de correspondance par critère
        """
        # Extraction des données pertinentes
        candidate_skills = cv_data.get('skills', [])
        candidate_experience = cv_data.get('experience', '')
        candidate_summary = cv_data.get('summary', '')
        candidate_job_title = cv_data.get('job_title', '')
        
        job_title = job_description.get('title', '')
        job_skills = job_description.get('required_skills', [])
        job_experience = job_description.get('required_experience', '')
        job_summary = job_description.get('description', '')
        
        # Ajouter les technologies requises et préférées du questionnaire
        if company_questionnaire:
            job_required_tech = company_questionnaire.get('technologies_requises', [])
            job_preferred_tech = company_questionnaire.get('technologies', [])
            
            if job_required_tech:
                job_skills.extend([tech for tech in job_required_tech if tech not in job_skills])
        
        # 1. Évaluation des compétences
        skills_score = await self._evaluate_skills_match(candidate_skills, job_skills, job_required_tech)
        
        # 2. Évaluation de l'expérience
        experience_score = self._evaluate_experience_match(candidate_experience, job_experience)
        
        # 3. Évaluation des descriptions
        description_score = calculate_semantic_similarity(candidate_summary, job_summary)
        
        # 4. Évaluation des titres de poste
        title_score = calculate_similarity(
            [normalize_text(candidate_job_title)], [normalize_text(job_title)]
        )
        
        # Combinaison pondérée
        weights = self.config['weights']
        total_cv_score = (
            skills_score * weights['cv_skills'] / (weights['cv_skills'] + weights['cv_experience'] + 
                                                weights['cv_description'] + weights['cv_title']) +
            experience_score * weights['cv_experience'] / (weights['cv_skills'] + weights['cv_experience'] + 
                                                        weights['cv_description'] + weights['cv_title']) +
            description_score * weights['cv_description'] / (weights['cv_skills'] + weights['cv_experience'] + 
                                                          weights['cv_description'] + weights['cv_title']) +
            title_score * weights['cv_title'] / (weights['cv_skills'] + weights['cv_experience'] + 
                                              weights['cv_description'] + weights['cv_title'])
        )
        
        return {
            'total': round(total_cv_score, 2),
            'skills': round(skills_score, 2),
            'experience': round(experience_score, 2),
            'description': round(description_score, 2),
            'title': round(title_score, 2)
        }
    
    async def _evaluate_skills_match(self, candidate_skills: List[str], job_skills: List[str], 
                               required_skills: Optional[List[str]] = None) -> float:
        """
        Évalue la correspondance des compétences entre candidat et offre
        
        Args:
            candidate_skills: Compétences du candidat
            job_skills: Compétences requises pour le poste
            required_skills: Compétences essentielles (sous-ensemble des compétences requises)
            
        Returns:
            Score de correspondance des compétences entre 0 et 1
        """
        if not candidate_skills or not job_skills:
            return 0.5  # Score neutre si pas de données
        
        # Normaliser les compétences
        normalized_candidate_skills = [normalize_text(skill) for skill in candidate_skills]
        normalized_job_skills = [normalize_text(skill) for skill in job_skills]
        
        # Liste des compétences essentielles
        if required_skills:
            normalized_required_skills = [normalize_text(skill) for skill in required_skills]
        else:
            normalized_required_skills = []
        
        # Trouver les compétences communes en tenant compte des synonymes
        common_skills = []
        for c_skill in normalized_candidate_skills:
            for j_skill in normalized_job_skills:
                if are_skills_similar(c_skill, j_skill):
                    common_skills.append(j_skill)
                    break
        
        # Compter les compétences essentielles correspondantes
        essential_matches = 0
        for skill in common_skills:
            if skill in normalized_required_skills:
                essential_matches += 1
        
        # Calcul du score
        skill_config = self.config['skills_config']
        
        # Bonus pour les compétences essentielles
        essential_bonus = skill_config['essential_bonus']
        nice_to_have_factor = skill_config['nice_to_have_factor']
        
        # Fraction des compétences essentielles couvertes
        if normalized_required_skills:
            essential_coverage = essential_matches / len(normalized_required_skills)
        else:
            essential_coverage = 1.0  # Pas de compétences essentielles spécifiées
        
        # Fraction des compétences totales couvertes
        total_coverage = len(common_skills) / len(normalized_job_skills) if normalized_job_skills else 0
        
        # Score final: importance plus grande aux compétences essentielles
        if normalized_required_skills:
            skills_score = (essential_coverage * essential_bonus + 
                          (total_coverage - essential_coverage * len(normalized_required_skills) / len(normalized_job_skills)) 
                          * nice_to_have_factor) / (essential_bonus * len(normalized_required_skills) / len(normalized_job_skills) + 
                                                  nice_to_have_factor * (1 - len(normalized_required_skills) / len(normalized_job_skills)))
        else:
            skills_score = total_coverage
        
        return min(1.0, skills_score)  # Plafonner à 1.0
    
    def _evaluate_experience_match(self, candidate_experience: str, job_experience: str) -> float:
        """
        Évalue la correspondance d'expérience
        
        Args:
            candidate_experience: Expérience du candidat
            job_experience: Expérience requise pour le poste
            
        Returns:
            Score de correspondance d'expérience entre 0 et 1
        """
        if not candidate_experience or not job_experience:
            return 0.5  # Score neutre si pas de données
        
        # Extraire les années d'expérience
        candidate_years = self._extract_years_from_experience(candidate_experience)
        min_years, max_years = self._extract_min_max_years(job_experience)
        
        if candidate_years is None or min_years is None:
            return 0.5  # Score neutre si extraction impossible
        
        # Calcul du score
        exp_config = self.config['experience_config']
        
        if candidate_years < min_years:
            # Expérience insuffisante
            ratio = candidate_years / min_years if min_years > 0 else 0
            score = max(0, ratio * exp_config['penalty_rate_under'])
        elif max_years is not None and candidate_years > max_years * 1.5:
            # Surqualifié (légèrement pénalisé)
            score = exp_config['penalty_rate_over']
        elif max_years is not None and candidate_years > max_years:
            # Légèrement au-dessus de l'expérience maximale
            over_ratio = 1 - (candidate_years - max_years) / (max_years * 0.5)
            score = exp_config['penalty_rate_over'] + (1 - exp_config['penalty_rate_over']) * over_ratio
        else:
            # Expérience dans la fourchette requise
            score = 1.0
        
        return score
    
    def _extract_years_from_experience(self, experience_text: str) -> Optional[int]:
        """
        Extrait le nombre d'années d'expérience à partir d'un texte
        
        Args:
            experience_text: Texte décrivant l'expérience
            
        Returns:
            Nombre d'années d'expérience ou None si non détecté
        """
        import re
        
        if not experience_text or experience_text == "Non détecté":
            return None
        
        # Recherche de motifs comme "5 ans", "5+ ans", "cinq ans", etc.
        pattern = r'(\d+)(?:\+)?(?:\s|-|_|\.)(?:an|ans|années|year|years)'
        match = re.search(pattern, experience_text.lower())
        
        if match:
            return int(match.group(1))
        
        # Recherche de nombres seuls
        pattern = r'(\d+)(?:\+)?'
        match = re.search(pattern, experience_text.lower())
        
        if match:
            return int(match.group(1))
        
        # Conversion de texte en nombre pour les cas comme "cinq ans"
        number_words = {
            'un': 1, 'une': 1, 'one': 1,
            'deux': 2, 'two': 2,
            'trois': 3, 'three': 3,
            'quatre': 4, 'four': 4,
            'cinq': 5, 'five': 5,
            'six': 6, 'six': 6,
            'sept': 7, 'seven': 7,
            'huit': 8, 'eight': 8,
            'neuf': 9, 'nine': 9,
            'dix': 10, 'ten': 10
        }
        
        for word, value in number_words.items():
            if word in experience_text.lower():
                return value
        
        return None
    
    def _extract_min_max_years(self, required_experience: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Extrait l'expérience minimale et maximale requise
        
        Args:
            required_experience: Texte décrivant l'expérience requise
            
        Returns:
            Tuple (min_years, max_years)
        """
        import re
        
        if not required_experience:
            return None, None
        
        # Recherche de motifs comme "3-5 ans", "minimum 3 ans", "au moins 3 ans", etc.
        range_pattern = r'(\d+)\s*[-à]\s*(\d+)\s*(?:an|ans|années|year|years)'
        min_pattern = r'(?:minimum|min|au moins|at least)\s*(\d+)\s*(?:an|ans|années|year|years)'
        max_pattern = r'(?:maximum|max|au plus|at most)\s*(\d+)\s*(?:an|ans|années|year|years)'
        single_pattern = r'(\d+)(?:\+)?\s*(?:an|ans|années|year|years)'
        
        # Vérifier d'abord s'il y a une fourchette
        range_match = re.search(range_pattern, required_experience.lower())
        if range_match:
            return int(range_match.group(1)), int(range_match.group(2))
        
        # Vérifier s'il y a un minimum et un maximum explicites
        min_match = re.search(min_pattern, required_experience.lower())
        max_match = re.search(max_pattern, required_experience.lower())
        
        if min_match and max_match:
            return int(min_match.group(1)), int(max_match.group(1))
        elif min_match:
            return int(min_match.group(1)), None
        elif max_match:
            return 0, int(max_match.group(1))
        
        # Vérifier s'il y a juste un nombre avec "+"
        plus_pattern = r'(\d+)\+\s*(?:an|ans|années|year|years)'
        plus_match = re.search(plus_pattern, required_experience.lower())
        if plus_match:
            return int(plus_match.group(1)), None
        
        # Vérifier s'il y a juste un nombre
        single_match = re.search(single_pattern, required_experience.lower())
        if single_match:
            return int(single_match.group(1)), int(single_match.group(1))
        
        return None, None
    
    async def _evaluate_questionnaire_match(self, candidate_questionnaire: Dict[str, Any], 
                                      company_questionnaire: Dict[str, Any],
                                      job_description: Dict[str, Any]) -> Dict[str, float]:
        """
        Évalue la correspondance basée sur les questionnaires
        
        Args:
            candidate_questionnaire: Questionnaire candidat
            company_questionnaire: Questionnaire entreprise
            job_description: Description du poste
            
        Returns:
            Scores de correspondance par section du questionnaire
        """
        # 1. Informations personnelles
        information_score = self._evaluate_information_match(
            candidate_questionnaire.get('informations_personnelles', {}),
            company_questionnaire
        )
        
        # 2. Mobilité et préférences
        mobility_score = await self._evaluate_mobility_match(
            candidate_questionnaire.get('mobilite_preferences', {}),
            company_questionnaire
        )
        
        # 3. Motivations et secteurs
        motivation_score = self._evaluate_motivation_match(
            candidate_questionnaire.get('motivations_secteurs', {}),
            company_questionnaire
        )
        
        # 4. Disponibilité et situation
        availability_score = self._evaluate_availability_match(
            candidate_questionnaire.get('disponibilite_situation', {}),
            company_questionnaire
        )
        
        # Combinaison pondérée
        weights = self.config['weights']
        total_questionnaire_score = (
            information_score * weights['information_personnelle'] / (weights['information_personnelle'] + 
                                                                   weights['mobilite_preferences'] + 
                                                                   weights['motivations_secteurs'] + 
                                                                   weights['disponibilite_situation']) +
            mobility_score * weights['mobilite_preferences'] / (weights['information_personnelle'] + 
                                                             weights['mobilite_preferences'] + 
                                                             weights['motivations_secteurs'] + 
                                                             weights['disponibilite_situation']) +
            motivation_score * weights['motivations_secteurs'] / (weights['information_personnelle'] + 
                                                               weights['mobilite_preferences'] + 
                                                               weights['motivations_secteurs'] + 
                                                               weights['disponibilite_situation']) +
            availability_score * weights['disponibilite_situation'] / (weights['information_personnelle'] + 
                                                                    weights['mobilite_preferences'] + 
                                                                    weights['motivations_secteurs'] + 
                                                                    weights['disponibilite_situation'])
        )
        
        return {
            'total': round(total_questionnaire_score, 2),
            'informations_personnelles': round(information_score, 2),
            'mobilite_preferences': round(mobility_score, 2),
            'motivations_secteurs': round(motivation_score, 2),
            'disponibilite_situation': round(availability_score, 2)
        }
    
    def _evaluate_information_match(self, candidate_info: Dict[str, Any], 
                                   company_info: Dict[str, Any]) -> float:
        """
        Évalue la correspondance des informations personnelles
        
        Args:
            candidate_info: Informations personnelles du candidat
            company_info: Questionnaire entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_info or not company_info:
            return 0.5  # Score neutre si pas de données
        
        candidate_job = normalize_text(candidate_info.get('poste_souhaite', ''))
        company_job = normalize_text(company_info.get('poste_propose', ''))
        
        if not candidate_job or not company_job:
            return 0.5  # Score neutre si pas de données
        
        # Similarité des titres de poste
        title_similarity = calculate_similarity([candidate_job], [company_job])
        
        return title_similarity
    
    async def _evaluate_mobility_match(self, candidate_mobility: Dict[str, Any], 
                                 company_info: Dict[str, Any]) -> float:
        """
        Évalue la correspondance de mobilité et préférences
        
        Args:
            candidate_mobility: Mobilité et préférences du candidat
            company_info: Questionnaire entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_mobility or not company_info:
            return 0.5  # Score neutre si pas de données
        
        # Mode de travail
        candidate_work_mode = candidate_mobility.get('mode_travail', '')
        company_work_mode = company_info.get('mode_travail', '')
        
        work_mode_score = self._compare_work_modes(candidate_work_mode, company_work_mode)
        
        # Localisation et temps de trajet
        candidate_location = candidate_mobility.get('localisation', '')
        company_location = company_info.get('localisation', '')
        
        location_score = await self._evaluate_location_match(
            candidate_location, company_location,
            candidate_mobility.get('temps_trajet_max', 60),
            candidate_mobility.get('mode_transport', 'driving'),
            candidate_work_mode, company_work_mode
        )
        
        # Type de contrat
        candidate_contract = candidate_mobility.get('type_contrat', '')
        company_contract = company_info.get('type_contrat', '')
        
        contract_score = self._compare_contract_types(candidate_contract, company_contract)
        
        # Taille d'entreprise
        candidate_size = candidate_mobility.get('taille_entreprise', '')
        company_size = company_info.get('taille_entreprise', '')
        
        size_score = self._compare_company_sizes(candidate_size, company_size)
        
        # Calcul du score global de mobilité
        mobility_score = (
            work_mode_score * 0.4 +
            location_score * 0.3 +
            contract_score * 0.2 +
            size_score * 0.1
        )
        
        return mobility_score
    
    def _compare_work_modes(self, candidate_mode: str, company_mode: str) -> float:
        """
        Compare les modes de travail
        
        Args:
            candidate_mode: Mode de travail souhaité par le candidat
            company_mode: Mode de travail proposé par l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_mode or not company_mode:
            return 0.5  # Score neutre si pas de données
        
        # Normalisation
        candidate_mode = normalize_text(candidate_mode)
        company_mode = normalize_text(company_mode)
        
        # Matrice de compatibilité des modes de travail
        compatibility_matrix = {
            'sur site': {'sur site': 1.0, 'hybride': 0.7, 'full remote': 0.0},
            'hybride': {'sur site': 0.7, 'hybride': 1.0, 'full remote': 0.5},
            'full remote': {'sur site': 0.0, 'hybride': 0.5, 'full remote': 1.0}
        }
        
        # Correspondance exacte
        if candidate_mode in compatibility_matrix and company_mode in compatibility_matrix[candidate_mode]:
            return compatibility_matrix[candidate_mode][company_mode]
        
        # Correspondance approximative
        for c_mode in compatibility_matrix:
            if candidate_mode in c_mode or c_mode in candidate_mode:
                for co_mode in compatibility_matrix[c_mode]:
                    if company_mode in co_mode or co_mode in company_mode:
                        return compatibility_matrix[c_mode][co_mode]
        
        return 0.5  # Score neutre par défaut
    
    async def _evaluate_location_match(self, candidate_location: str, company_location: str,
                                 max_commute_time: int = 60, transport_mode: str = 'driving',
                                 candidate_work_mode: str = '', company_work_mode: str = '') -> float:
        """
        Évalue la correspondance de localisation en tenant compte du temps de trajet
        
        Args:
            candidate_location: Localisation du candidat
            company_location: Localisation de l'entreprise
            max_commute_time: Temps de trajet maximal accepté (en minutes)
            transport_mode: Mode de transport (driving, transit, walking, bicycling)
            candidate_work_mode: Mode de travail souhaité par le candidat
            company_work_mode: Mode de travail proposé par l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        # Si l'un des modes de travail est full remote, la localisation n'est pas pertinente
        if ('remote' in candidate_work_mode.lower() or 'remote' in company_work_mode.lower()) and \
           not ('hybride' in company_work_mode.lower() or 'sur site' in company_work_mode.lower()):
            return 1.0
        
        if not candidate_location or not company_location:
            return 0.5  # Score neutre si pas de données
        
        # Correspondance exacte des localisations
        if normalize_text(candidate_location) == normalize_text(company_location):
            return 1.0
        
        # Calcul du temps de trajet avec l'API Google Maps
        try:
            commute_time = await self._calculate_commute_time(
                candidate_location, company_location, transport_mode
            )
            
            if commute_time is None:
                return 0.5  # Score neutre si calcul impossible
            
            # Calcul du score en fonction du temps de trajet
            if commute_time <= max_commute_time:
                # Score dégressif en fonction du pourcentage du temps maximal
                score = 1.0 - (commute_time / max_commute_time) * 0.3
            else:
                # Au-delà du temps maximal, score faible mais non nul
                score = max(0.2, 0.5 - (commute_time - max_commute_time) / 60 * 0.1)
            
            return score
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}", exc_info=True)
            
            # En cas d'erreur, utiliser une heuristique simple basée sur les noms de lieux
            location_similarity = calculate_similarity(
                [normalize_text(candidate_location)], [normalize_text(company_location)]
            )
            
            return 0.3 + location_similarity * 0.4  # Score entre 0.3 et 0.7
    
    async def _calculate_commute_time(self, origin: str, destination: str, 
                               mode: str = 'driving') -> Optional[float]:
        """
        Calcule le temps de trajet entre deux adresses avec l'API Google Maps
        
        Args:
            origin: Adresse d'origine
            destination: Adresse de destination
            mode: Mode de transport (driving, transit, walking, bicycling)
            
        Returns:
            Temps de trajet en minutes ou None si impossible à calculer
        """
        if not self.maps_api_key:
            logger.warning("Clé API Google Maps non configurée, impossible de calculer le temps de trajet")
            return None
        
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": self.maps_api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "OK" and len(data.get("rows", [])) > 0:
                        elements = data["rows"][0].get("elements", [])
                        if elements and elements[0].get("status") == "OK":
                            # Temps de trajet en minutes
                            duration_seconds = elements[0]["duration"]["value"]
                            return duration_seconds / 60
                            
                    logger.warning(f"Réponse invalide de l'API Distance Matrix: {data}")
                    return None
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Google Maps: {str(e)}", exc_info=True)
            return None
    
    def _compare_contract_types(self, candidate_contract: str, company_contract: str) -> float:
        """
        Compare les types de contrat
        
        Args:
            candidate_contract: Type de contrat souhaité par le candidat
            company_contract: Type de contrat proposé par l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_contract or not company_contract:
            return 0.5  # Score neutre si pas de données
        
        # Normalisation
        candidate_contract = normalize_text(candidate_contract)
        company_contract = normalize_text(company_contract)
        
        # Matrice de compatibilité des types de contrat
        compatibility_matrix = {
            'cdi': {'cdi': 1.0, 'cdd': 0.6, 'freelance': 0.3, 'stage': 0.2, 'alternance': 0.4},
            'cdd': {'cdi': 0.8, 'cdd': 1.0, 'freelance': 0.4, 'stage': 0.3, 'alternance': 0.5},
            'freelance': {'cdi': 0.5, 'cdd': 0.5, 'freelance': 1.0, 'stage': 0.2, 'alternance': 0.2},
            'stage': {'cdi': 0.2, 'cdd': 0.3, 'freelance': 0.1, 'stage': 1.0, 'alternance': 0.6},
            'alternance': {'cdi': 0.3, 'cdd': 0.4, 'freelance': 0.1, 'stage': 0.5, 'alternance': 1.0}
        }
        
        # Correspondance exacte
        if candidate_contract in compatibility_matrix and company_contract in compatibility_matrix[candidate_contract]:
            return compatibility_matrix[candidate_contract][company_contract]
        
        # Correspondance approximative
        for c_contract in compatibility_matrix:
            if c_contract in candidate_contract:
                for co_contract in compatibility_matrix[c_contract]:
                    if co_contract in company_contract:
                        return compatibility_matrix[c_contract][co_contract]
        
        return 0.5  # Score neutre par défaut
    
    def _compare_company_sizes(self, candidate_size: str, company_size: str) -> float:
        """
        Compare les tailles d'entreprise
        
        Args:
            candidate_size: Taille d'entreprise souhaitée par le candidat
            company_size: Taille de l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_size or not company_size or candidate_size.lower() == 'peu importe':
            return 1.0  # Score maximum si pas de préférence
        
        # Normalisation
        candidate_size = normalize_text(candidate_size)
        company_size = normalize_text(company_size)
        
        # Matrice de compatibilité des tailles d'entreprise
        compatibility_matrix = {
            'startup': {'startup': 1.0, 'pme': 0.8, 'grande entreprise': 0.4, 'grand groupe': 0.3},
            'pme': {'startup': 0.7, 'pme': 1.0, 'grande entreprise': 0.7, 'grand groupe': 0.5},
            'grande entreprise': {'startup': 0.3, 'pme': 0.6, 'grande entreprise': 1.0, 'grand groupe': 0.9},
            'grand groupe': {'startup': 0.2, 'pme': 0.4, 'grande entreprise': 0.8, 'grand groupe': 1.0}
        }
        
        # Correspondance exacte
        if candidate_size in compatibility_matrix and company_size in compatibility_matrix[candidate_size]:
            return compatibility_matrix[candidate_size][company_size]
        
        # Correspondance approximative
        for c_size in compatibility_matrix:
            if c_size in candidate_size:
                for co_size in compatibility_matrix[c_size]:
                    if co_size in company_size:
                        return compatibility_matrix[c_size][co_size]
        
        return 0.7  # Score moyen par défaut
    
    def _evaluate_motivation_match(self, candidate_motivation: Dict[str, Any], 
                                  company_info: Dict[str, Any]) -> float:
        """
        Évalue la correspondance des motivations et secteurs
        
        Args:
            candidate_motivation: Motivations et secteurs du candidat
            company_info: Questionnaire entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_motivation or not company_info:
            return 0.5  # Score neutre si pas de données
        
        # Secteurs d'activité
        candidate_sectors = candidate_motivation.get('secteurs', [])
        company_sector = company_info.get('secteur', '')
        
        sector_score = self._compare_sectors(candidate_sectors, company_sector)
        
        # Valeurs
        candidate_values = candidate_motivation.get('valeurs', [])
        company_values = company_info.get('valeurs', [])
        
        values_score = self._compare_values(candidate_values, company_values)
        
        # Technologies
        candidate_techs = candidate_motivation.get('technologies', [])
        company_techs = company_info.get('technologies', [])
        company_required_techs = company_info.get('technologies_requises', [])
        
        tech_score = self._compare_technologies(candidate_techs, company_techs, company_required_techs)
        
        # Calcul du score global de motivation
        motivation_score = (
            sector_score * 0.3 +
            values_score * 0.3 +
            tech_score * 0.4
        )
        
        return motivation_score
    
    def _compare_sectors(self, candidate_sectors: List[str], company_sector: str) -> float:
        """
        Compare les secteurs d'activité
        
        Args:
            candidate_sectors: Secteurs d'intérêt du candidat
            company_sector: Secteur de l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_sectors or not company_sector:
            return 0.5  # Score neutre si pas de données
        
        # Normalisation
        normalized_candidate_sectors = [normalize_text(sector) for sector in candidate_sectors]
        normalized_company_sector = normalize_text(company_sector)
        
        # Vérifier si le secteur de l'entreprise est dans les secteurs d'intérêt du candidat
        for sector in normalized_candidate_sectors:
            if sector in normalized_company_sector or normalized_company_sector in sector:
                return 1.0
        
        # Similarité partielle
        max_similarity = 0
        for sector in normalized_candidate_sectors:
            similarity = calculate_similarity([sector], [normalized_company_sector])
            max_similarity = max(max_similarity, similarity)
        
        return max(0.5, max_similarity)  # Score minimum de 0.5
    
    def _compare_values(self, candidate_values: List[str], company_values: List[str]) -> float:
        """
        Compare les valeurs
        
        Args:
            candidate_values: Valeurs importantes pour le candidat
            company_values: Valeurs de l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_values or not company_values:
            return 0.5  # Score neutre si pas de données
        
        # Normalisation
        normalized_candidate_values = [normalize_text(value) for value in candidate_values]
        normalized_company_values = [normalize_text(value) for value in company_values]
        
        # Calculer la correspondance des valeurs
        common_values_count = 0
        for c_value in normalized_candidate_values:
            for co_value in normalized_company_values:
                if c_value in co_value or co_value in c_value or calculate_similarity([c_value], [co_value]) > 0.7:
                    common_values_count += 1
                    break
        
        # Calculer le score
        if len(normalized_candidate_values) > 0:
            match_ratio = common_values_count / len(normalized_candidate_values)
            return min(1.0, 0.5 + match_ratio * 0.5)  # Score minimum de 0.5
        else:
            return 0.5
    
    def _compare_technologies(self, candidate_techs: List[str], company_techs: List[str],
                            required_techs: List[str]) -> float:
        """
        Compare les technologies
        
        Args:
            candidate_techs: Technologies préférées du candidat
            company_techs: Technologies utilisées par l'entreprise
            required_techs: Technologies requises pour le poste
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_techs:
            return 0.5  # Score neutre si pas de préférences
        
        if not company_techs and not required_techs:
            return 0.5  # Score neutre si pas de données côté entreprise
        
        # Normalisation
        normalized_candidate_techs = [normalize_text(tech) for tech in candidate_techs]
        normalized_company_techs = [normalize_text(tech) for tech in company_techs]
        normalized_required_techs = [normalize_text(tech) for tech in required_techs]
        
        # Calcul pour les technologies requises
        required_match_count = 0
        for r_tech in normalized_required_techs:
            for c_tech in normalized_candidate_techs:
                if are_skills_similar(r_tech, c_tech):
                    required_match_count += 1
                    break
        
        required_score = 1.0 if not normalized_required_techs else required_match_count / len(normalized_required_techs)
        
        # Calcul pour les technologies préférées (non requises)
        preferred_techs = [tech for tech in normalized_company_techs if tech not in normalized_required_techs]
        preferred_match_count = 0
        
        for p_tech in preferred_techs:
            for c_tech in normalized_candidate_techs:
                if are_skills_similar(p_tech, c_tech):
                    preferred_match_count += 1
                    break
        
        preferred_score = 1.0 if not preferred_techs else preferred_match_count / len(preferred_techs)
        
        # Score combiné avec plus de poids pour les technologies requises
        if normalized_required_techs:
            tech_score = required_score * 0.7 + preferred_score * 0.3
        else:
            tech_score = preferred_score
        
        return tech_score
    
    def _evaluate_availability_match(self, candidate_availability: Dict[str, Any], 
                                    company_info: Dict[str, Any]) -> float:
        """
        Évalue la correspondance de disponibilité et situation
        
        Args:
            candidate_availability: Disponibilité et situation du candidat
            company_info: Questionnaire entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_availability or not company_info:
            return 0.5  # Score neutre si pas de données
        
        # Disponibilité
        candidate_availability_date = candidate_availability.get('disponibilite', '')
        company_start_date = company_info.get('date_debut', '')
        
        availability_score = self._compare_availability_dates(candidate_availability_date, company_start_date)
        
        # Salaire
        candidate_salary = candidate_availability.get('salaire', {})
        company_salary = company_info.get('salaire', {})
        
        salary_score = self._compare_salary_ranges(candidate_salary, company_salary)
        
        # Calcul du score global de disponibilité
        availability_match_score = (
            availability_score * 0.4 +
            salary_score * 0.6
        )
        
        return availability_match_score
    
    def _compare_availability_dates(self, candidate_date: str, company_date: str) -> float:
        """
        Compare les dates de disponibilité
        
        Args:
            candidate_date: Date de disponibilité du candidat
            company_date: Date de début souhaitée par l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_date or not company_date:
            return 0.5  # Score neutre si pas de données
        
        # Extraction des périodes (immédiat, X semaines, X mois)
        candidate_weeks = self._extract_weeks_from_availability(candidate_date)
        company_weeks = self._extract_weeks_from_availability(company_date)
        
        if candidate_weeks is None or company_weeks is None:
            return 0.5  # Score neutre si extraction impossible
        
        # Calcul du score
        if candidate_weeks <= company_weeks:
            # Disponible avant ou à la date souhaitée
            return 1.0
        else:
            # Disponible après la date souhaitée
            delay = candidate_weeks - company_weeks
            if delay <= 4:  # Disponible dans le mois qui suit
                return 0.8
            elif delay <= 8:  # Disponible dans les deux mois
                return 0.6
            elif delay <= 12:  # Disponible dans les trois mois
                return 0.4
            else:  # Disponible après plus de trois mois
                return 0.2
    
    def _extract_weeks_from_availability(self, availability_text: str) -> Optional[int]:
        """
        Extrait le nombre de semaines avant disponibilité
        
        Args:
            availability_text: Texte décrivant la disponibilité
            
        Returns:
            Nombre de semaines ou None si non détecté
        """
        import re
        
        if not availability_text:
            return None
        
        # Convertir le texte en minuscules
        text = availability_text.lower()
        
        # Cas "immédiat" ou "immédiatement"
        if "immédiat" in text:
            return 0
        
        # Cas "X semaines"
        weeks_pattern = r'(\d+)\s*semaines'
        weeks_match = re.search(weeks_pattern, text)
        if weeks_match:
            return int(weeks_match.group(1))
        
        # Cas "X mois"
        months_pattern = r'(\d+)\s*mois'
        months_match = re.search(months_pattern, text)
        if months_match:
            return int(months_match.group(1)) * 4  # Conversion approximative en semaines
        
        # Cas dates explicites au format JJ/MM/AAAA ou similaire
        from datetime import datetime
        
        date_patterns = [
            r'(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2,4})',  # JJ/MM/AAAA ou JJ-MM-AAAA
            r'(\d{4})[\/\.-](\d{1,2})[\/\.-](\d{1,2})'    # AAAA/MM/JJ ou AAAA-MM-JJ
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                try:
                    # Essayer de parser la date
                    if len(date_match.group(3)) == 4:  # Premier pattern JJ/MM/AAAA
                        day, month, year = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                    else:  # Second pattern AAAA/MM/JJ
                        year, month, day = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                    
                    # Calculer le nombre de semaines entre aujourd'hui et la date
                    availability_date = datetime(year, month, day)
                    today = datetime.now()
                    
                    if availability_date < today:
                        return 0  # Disponible immédiatement si la date est passée
                    
                    delta = availability_date - today
                    return max(0, delta.days // 7)
                except:
                    pass
        
        # Valeur par défaut si aucune information n'est détectée
        return 4  # Environ un mois
    
    def _compare_salary_ranges(self, candidate_salary: Dict[str, Any], 
                              company_salary: Dict[str, Any]) -> float:
        """
        Compare les fourchettes de salaire
        
        Args:
            candidate_salary: Attentes salariales du candidat
            company_salary: Fourchette salariale proposée par l'entreprise
            
        Returns:
            Score de correspondance entre 0 et 1
        """
        if not candidate_salary or not company_salary:
            return 0.5  # Score neutre si pas de données
        
        candidate_min = candidate_salary.get('min', 0)
        candidate_max = candidate_salary.get('max', 0)
        company_min = company_salary.get('min', 0)
        company_max = company_salary.get('max', 0)
        
        if candidate_min <= 0 or company_min <= 0:
            return 0.5  # Score neutre si données invalides
        
        # Cas où le candidat n'a pas spécifié de maximum
        if candidate_max <= 0 or candidate_max <= candidate_min:
            candidate_max = candidate_min * 1.5
        
        # Cas où l'entreprise n'a pas spécifié de maximum
        if company_max <= 0 or company_max <= company_min:
            company_max = company_min * 1.5
        
        # Vérifier s'il y a une intersection entre les fourchettes
        overlap_min = max(candidate_min, company_min)
        overlap_max = min(candidate_max, company_max)
        
        if overlap_max < overlap_min:
            # Pas d'intersection
            if candidate_min > company_max:
                # Attentes du candidat trop élevées
                ratio = company_max / candidate_min
                return max(0.2, ratio * 0.5)  # Score minimum de 0.2
            else:
                # Offre de l'entreprise supérieure aux attentes
                return 0.9  # Très bon score mais pas parfait
        else:
            # Intersection
            candidate_range = candidate_max - candidate_min
            company_range = company_max - company_min
            overlap_range = overlap_max - overlap_min
            
            # Calculer l'intersection relative
            if candidate_range > 0 and company_range > 0:
                candidate_overlap = overlap_range / candidate_range
                company_overlap = overlap_range / company_range
                average_overlap = (candidate_overlap + company_overlap) / 2
                
                return min(1.0, 0.5 + average_overlap * 0.5)  # Score entre 0.5 et 1.0
            else:
                return 0.5
    
    def _generate_insights(self, cv_scores: Dict[str, float], questionnaire_scores: Dict[str, float],
                         cv_data: Dict[str, Any], job_description: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Génère des insights pour expliquer le matching
        
        Args:
            cv_scores: Scores basés sur le CV
            questionnaire_scores: Scores basés sur les questionnaires
            cv_data: Données du CV
            job_description: Description du poste
            
        Returns:
            Insights avec forces, points d'amélioration et recommandations
        """
        insights = {
            'strengths': [],
            'areas_of_improvement': [],
            'recommendations': []
        }
        
        # Identifier les forces (scores > 0.8)
        if cv_scores.get('skills', 0) > 0.8:
            insights['strengths'].append("Excellente adéquation des compétences techniques")
        elif cv_scores.get('skills', 0) > 0.6:
            insights['strengths'].append("Bonne maîtrise des compétences techniques requises")
        
        if cv_scores.get('experience', 0) > 0.8:
            insights['strengths'].append("Niveau d'expérience idéal pour le poste")
        
        if questionnaire_scores.get('motivations_secteurs', 0) > 0.8:
            insights['strengths'].append("Fort intérêt pour le secteur d'activité et les technologies")
        
        if questionnaire_scores.get('mobilite_preferences', 0) > 0.8:
            insights['strengths'].append("Préférences de travail en parfaite adéquation (mode, localisation, contrat)")
        
        # Identifier les points d'amélioration (scores < 0.4)
        if cv_scores.get('skills', 0) < 0.4:
            insights['areas_of_improvement'].append("Compétences techniques insuffisantes pour le poste")
        
        if cv_scores.get('experience', 0) < 0.4:
            if cv_data.get('experience', ''):
                candidate_years = self._extract_years_from_experience(cv_data.get('experience', ''))
                min_years, _ = self._extract_min_max_years(job_description.get('required_experience', ''))
                
                if candidate_years is not None and min_years is not None and candidate_years < min_years:
                    insights['areas_of_improvement'].append(
                        f"Expérience insuffisante ({candidate_years} ans vs {min_years} ans requis)"
                    )
                else:
                    insights['areas_of_improvement'].append("Expérience inadéquate pour le poste")
        
        if questionnaire_scores.get('mobilite_preferences', 0) < 0.4:
            insights['areas_of_improvement'].append("Préférences de travail incompatibles (mode, localisation, contrat)")
        
        if questionnaire_scores.get('disponibilite_situation', 0) < 0.4:
            insights['areas_of_improvement'].append("Disponibilité ou attentes salariales incompatibles")
        
        # Générer des recommandations
        total_score = (cv_scores.get('total', 0) + questionnaire_scores.get('total', 0)) / 2
        
        if total_score >= self.config['thresholds']['excellent_match']:
            insights['recommendations'].append("Profil idéal, entretien fortement recommandé")
        elif total_score >= self.config['thresholds']['good_match']:
            insights['recommendations'].append("Bon profil, entretien recommandé")
        elif total_score >= self.config['thresholds']['moderate_match']:
            insights['recommendations'].append("Profil intéressant, à considérer si peu de candidats")
        else:
            insights['recommendations'].append("Profil peu adapté, à ne considérer qu'en dernier recours")
        
        # Ajouter des recommandations spécifiques
        if cv_scores.get('skills', 0) < 0.5 and cv_scores.get('experience', 0) > 0.7:
            insights['recommendations'].append("Formation possible: bonne expérience mais compétences à développer")
        
        if questionnaire_scores.get('disponibilite_situation', 0) < 0.5 and total_score > 0.7:
            insights['recommendations'].append("Négociation possible sur la rémunération ou la date de début")
        
        return insights
    
    async def find_jobs_for_candidate(self, candidate_data: Dict[str, Any], 
                                job_list: List[Dict[str, Any]], 
                                limit: int = 10, 
                                min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Trouve les meilleures offres d'emploi pour un candidat
        
        Args:
            candidate_data: Données du candidat
            job_list: Liste des offres d'emploi
            limit: Nombre maximum de résultats à retourner
            min_score: Score minimum pour inclure un match
            
        Returns:
            Liste des offres d'emploi correspondantes triées par score décroissant
        """
        matches = []
        
        for job_data in job_list:
            # Calculer le score de matching
            match_result = await self.calculate_match(candidate_data, job_data)
            
            # Filtrer selon le score minimum
            if match_result['score'] >= min_score:
                matches.append({
                    'job': job_data,
                    'score': match_result['score'],
                    'category': match_result['category'],
                    'details': match_result['details'],
                    'insights': match_result['insights']
                })
        
        # Trier par score décroissant et limiter le nombre de résultats
        sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        
        return sorted_matches[:limit] if limit > 0 else sorted_matches
    
    async def find_candidates_for_job(self, job_data: Dict[str, Any], 
                               candidate_list: List[Dict[str, Any]], 
                               limit: int = 10, 
                               min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Trouve les meilleurs candidats pour une offre d'emploi
        
        Args:
            job_data: Données de l'offre d'emploi
            candidate_list: Liste des candidats
            limit: Nombre maximum de résultats à retourner
            min_score: Score minimum pour inclure un match
            
        Returns:
            Liste des candidats correspondants triés par score décroissant
        """
        matches = []
        
        for candidate_data in candidate_list:
            # Calculer le score de matching
            match_result = await self.calculate_match(candidate_data, job_data)
            
            # Filtrer selon le score minimum
            if match_result['score'] >= min_score:
                matches.append({
                    'candidate': candidate_data,
                    'score': match_result['score'],
                    'category': match_result['category'],
                    'details': match_result['details'],
                    'insights': match_result['insights']
                })
        
        # Trier par score décroissant et limiter le nombre de résultats
        sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        
        return sorted_matches[:limit] if limit > 0 else sorted_matches
