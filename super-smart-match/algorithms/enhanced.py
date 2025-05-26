#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptateur pour l'algorithme Enhanced Matching Engine dans SuperSmartMatch
"""

import sys
import os
import logging
from typing import Dict, List, Any

# Ajouter le répertoire racine au path pour importer les modules existants
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from .base import BaseAlgorithm

logger = logging.getLogger(__name__)

class EnhancedAlgorithm(BaseAlgorithm):
    """
    Adaptateur pour l'Enhanced Matching Engine
    """
    
    def __init__(self):
        super().__init__()
        self.name = "enhanced"
        self.description = "Moteur de matching avancé avec pondération dynamique et soft skills"
        self.version = "1.0"
        
        # Initialiser le moteur Enhanced
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialise l'Enhanced Matching Engine original"""
        try:
            # Import conditionnel pour éviter les erreurs si le module n'existe pas
            from matching_engine_enhanced import EnhancedMatchingEngine, enhanced_match_candidate_with_jobs
            
            self.engine_class = EnhancedMatchingEngine
            self.match_function = enhanced_match_candidate_with_jobs
            self.initialized = True
            
            logger.info("Enhanced Matching Engine initialisé avec succès")
            
        except ImportError as e:
            logger.warning(f"Impossible d'importer Enhanced Matching Engine: {e}")
            self.engine_class = None
            self.match_function = None
            self.initialized = False
            
            # Fallback vers l'implémentation simplifiée
            self._setup_fallback()
    
    def _setup_fallback(self):
        """Configure un fallback si l'algorithme original n'est pas disponible"""
        logger.info("Configuration du fallback Enhanced")
        self.initialized = True  # Marquer comme initialisé pour le fallback
    
    def supports(self, candidat: Dict[str, Any], offres: List[Dict[str, Any]]) -> bool:
        """
        Vérifie si l'algorithme peut traiter ces données
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            
        Returns:
            True si l'algorithme peut traiter les données
        """
        # Enhanced fonctionne mieux avec des données riches
        has_soft_skills = bool(
            candidat.get('soft_skills') or 
            candidat.get('competences_comportementales') or
            candidat.get('personnalite')
        )
        
        has_preferences = bool(
            candidat.get('preferences_culture') or
            candidat.get('criteres_importants') or
            candidat.get('valeurs_importantes')
        )
        
        has_detailed_experience = bool(
            candidat.get('annees_experience') is not None or
            candidat.get('experience_detaillee')
        )
        
        # Vérifier que les offres ont des données compatibles
        offers_have_details = any(
            offre.get('soft_skills') or 
            offre.get('culture_entreprise') or
            offre.get('description_detaillee')
            for offre in offres
        )
        
        # Enhanced peut traiter la plupart des cas, mais est optimal avec des données riches
        return True  # Toujours capable de traiter
    
    def match_candidate_with_jobs(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute le matching Enhanced
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des offres avec scores de matching
        """
        if not self.initialized:
            raise RuntimeError("Enhanced algorithm non initialisé")
        
        try:
            if self.match_function:
                # Utiliser l'algorithme original
                return self._execute_original(candidat, offres, limit)
            else:
                # Utiliser le fallback
                return self._execute_fallback(candidat, offres, limit)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution Enhanced: {e}")
            # Fallback en cas d'erreur
            return self._execute_fallback(candidat, offres, limit)
    
    def _execute_original(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Exécute l'Enhanced Matching Engine original
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            limit: Limite de résultats
            
        Returns:
            Résultats de matching
        """
        # Séparer les données CV et questionnaire
        cv_data = self._extract_cv_data(candidat)
        questionnaire_data = self._extract_questionnaire_data(candidat)
        
        # Adapter les offres au format Enhanced
        adapted_offers = [self._adapt_offer_to_enhanced(offre) for offre in offres]
        
        # Exécuter le matching
        results = self.match_function(cv_data, questionnaire_data, adapted_offers, limit)
        
        # Adapter les résultats au format SuperSmartMatch
        adapted_results = []
        for result in results:
            adapted_result = self._adapt_result_from_enhanced(result)
            adapted_results.append(adapted_result)
        
        return adapted_results
    
    def _execute_fallback(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Exécute une version simplifiée d'Enhanced
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            limit: Limite de résultats
            
        Returns:
            Résultats de matching
        """
        results = []
        
        # Extraire les préférences pour la pondération dynamique
        preferences = self._extract_candidate_preferences(candidat)
        
        for i, offre in enumerate(offres[:limit]):
            # Calcul du score avec pondération dynamique
            score = self._calculate_enhanced_score(candidat, offre, preferences)
            
            result = {
                'id': offre.get('id', f'job_{i}'),
                'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                'matching_score': int(score * 100),
                'matching_details': {
                    'skills': self._calculate_skills_score(candidat, offre) * 100,
                    'contract': self._calculate_contract_score(candidat, offre) * 100,
                    'location': self._calculate_location_score(candidat, offre) * 100,
                    'salary': self._calculate_salary_score(candidat, offre) * 100,
                    'experience': self._calculate_experience_score(candidat, offre) * 100,
                    'soft_skills': self._calculate_soft_skills_score(candidat, offre) * 100,
                    'culture': self._calculate_culture_score(candidat, offre) * 100
                },
                'matching_explanations': self._generate_explanations(candidat, offre),
                **offre  # Inclure toutes les données de l'offre originale
            }
            
            results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return results
    
    def _extract_candidate_preferences(self, candidat: Dict[str, Any]) -> Dict[str, float]:
        """
        Extrait les préférences du candidat pour la pondération dynamique
        
        Args:
            candidat: Données candidat
            
        Returns:
            Dictionnaire des poids
        """
        # Poids par défaut style Enhanced
        default_weights = {
            'skills': 0.30,
            'contract': 0.15,
            'location': 0.20,
            'salary': 0.15,
            'experience': 0.10,
            'soft_skills': 0.05,
            'culture': 0.05
        }
        
        # Ajuster selon les critères importants du candidat
        criteres = candidat.get('criteres_importants', {})
        
        if criteres:
            # Réajuster les poids selon les préférences
            if criteres.get('salaire_important'):
                default_weights['salary'] = 0.25
                default_weights['skills'] = 0.25
            
            if criteres.get('localisation_importante'):
                default_weights['location'] = 0.30
                default_weights['skills'] = 0.25
            
            if criteres.get('culture_importante'):
                default_weights['culture'] = 0.15
                default_weights['soft_skills'] = 0.10
                default_weights['skills'] = 0.25
        
        # Si le candidat a des soft skills, augmenter leur poids
        if candidat.get('soft_skills'):
            default_weights['soft_skills'] = 0.10
            default_weights['skills'] = 0.25
        
        return default_weights
    
    def _calculate_enhanced_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any], 
        weights: Dict[str, float]
    ) -> float:
        """
        Calcule le score Enhanced avec pondération dynamique
        
        Args:
            candidat: Données candidat
            offre: Offre d'emploi
            weights: Poids pour chaque critère
            
        Returns:
            Score entre 0 et 1
        """
        scores = {
            'skills': self._calculate_skills_score(candidat, offre),
            'contract': self._calculate_contract_score(candidat, offre),
            'location': self._calculate_location_score(candidat, offre),
            'salary': self._calculate_salary_score(candidat, offre),
            'experience': self._calculate_experience_score(candidat, offre),
            'soft_skills': self._calculate_soft_skills_score(candidat, offre),
            'culture': self._calculate_culture_score(candidat, offre)
        }
        
        # Score pondéré
        total_score = sum(scores[criterion] * weights.get(criterion, 0) for criterion in scores)
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_skills_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score de correspondance des compétences"""
        candidate_skills = set(skill.lower() for skill in candidat.get('competences', []))
        required_skills = set(skill.lower() for skill in offre.get('competences', []))
        
        if not required_skills:
            return 0.7  # Score neutre
        
        if not candidate_skills:
            return 0.3  # Score bas
        
        matching_skills = candidate_skills.intersection(required_skills)
        coverage_score = len(matching_skills) / len(required_skills)
        
        # Bonus pour compétences supplémentaires
        additional_skills = candidate_skills - required_skills
        bonus = min(0.2, len(additional_skills) * 0.05)
        
        return min(1.0, coverage_score + bonus)
    
    def _calculate_contract_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du contrat"""
        candidate_contracts = [c.lower() for c in candidat.get('contrats_recherches', [])]
        job_contract = offre.get('type_contrat', '').lower()
        
        if not candidate_contracts or not job_contract:
            return 0.7
        
        if job_contract in candidate_contracts:
            return 1.0
        
        # Correspondances partielles
        if 'cdi' in candidate_contracts and 'cdi' in job_contract:
            return 1.0
        
        return 0.3
    
    def _calculate_location_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score de localisation"""
        candidate_location = candidat.get('adresse', '').lower()
        job_location = offre.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.6
        
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Correspondance partielle
        candidate_words = set(candidate_location.split())
        job_words = set(job_location.split())
        
        if candidate_words.intersection(job_words):
            return 0.8
        
        return 0.4
    
    def _calculate_salary_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score de correspondance salariale"""
        candidate_salary = candidat.get('salaire_souhaite', 0)
        job_salary_str = offre.get('salaire', '')
        
        if not candidate_salary or not job_salary_str:
            return 0.7  # Score neutre
        
        # Parser le salaire de l'offre (format "XX-YYK€")
        try:
            if 'k' in job_salary_str.lower():
                # Extraire les nombres
                import re
                numbers = re.findall(r'\d+', job_salary_str)
                if len(numbers) >= 2:
                    min_salary = int(numbers[0]) * 1000
                    max_salary = int(numbers[1]) * 1000
                elif len(numbers) == 1:
                    min_salary = max_salary = int(numbers[0]) * 1000
                else:
                    return 0.7
            else:
                return 0.7
        except:
            return 0.7
        
        # Vérifier si le salaire candidat est dans la fourchette
        if min_salary <= candidate_salary <= max_salary:
            return 1.0
        elif candidate_salary < min_salary:
            # Le candidat demande moins (bon pour l'employeur)
            ratio = candidate_salary / min_salary
            return min(1.0, ratio + 0.2)  # Bonus
        else:
            # Le candidat demande plus
            ratio = max_salary / candidate_salary
            return max(0.1, ratio)
    
    def _calculate_experience_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score d'expérience"""
        candidate_exp = candidat.get('annees_experience', 0)
        required_exp = offre.get('experience_requise', 0)
        
        if required_exp == 0:
            return 0.8  # Pas d'exigence d'expérience
        
        if candidate_exp >= required_exp:
            # Candidat a assez d'expérience
            if candidate_exp <= required_exp * 1.5:
                return 1.0  # Expérience appropriée
            else:
                return 0.9  # Surqualifié
        else:
            # Candidat n'a pas assez d'expérience
            ratio = candidate_exp / required_exp
            return max(0.2, ratio)
    
    def _calculate_soft_skills_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score des soft skills"""
        candidate_soft_skills = set(skill.lower() for skill in candidat.get('soft_skills', []))
        job_soft_skills = set(skill.lower() for skill in offre.get('soft_skills', []))
        
        if not job_soft_skills:
            return 0.7  # Score neutre
        
        if not candidate_soft_skills:
            return 0.4  # Score par défaut
        
        matching_skills = candidate_soft_skills.intersection(job_soft_skills)
        if matching_skills:
            return len(matching_skills) / len(job_soft_skills)
        
        return 0.3
    
    def _calculate_culture_score(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule le score de culture d'entreprise"""
        candidate_values = candidat.get('valeurs_importantes', [])
        job_culture = offre.get('culture_entreprise', {})
        
        if not candidate_values or not job_culture:
            return 0.6  # Score neutre
        
        job_values = job_culture.get('valeurs', [])
        
        if not job_values:
            return 0.6
        
        # Correspondance des valeurs
        candidate_values_set = set(v.lower() for v in candidate_values)
        job_values_set = set(v.lower() for v in job_values)
        
        matching_values = candidate_values_set.intersection(job_values_set)
        
        if matching_values:
            return len(matching_values) / max(len(candidate_values_set), len(job_values_set))
        
        return 0.4
    
    def _generate_explanations(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> Dict[str, str]:
        """Génère des explications détaillées style Enhanced"""
        explanations = {}
        
        # Explication compétences
        candidate_skills = candidat.get('competences', [])
        required_skills = offre.get('competences', [])
        matching_skills = set(s.lower() for s in candidate_skills).intersection(
            set(s.lower() for s in required_skills)
        )
        
        if len(matching_skills) >= len(required_skills) * 0.8:
            explanations['skills'] = "Excellente correspondance des compétences techniques"
        elif len(matching_skills) >= len(required_skills) * 0.6:
            explanations['skills'] = "Bonne correspondance des compétences principales"
        else:
            explanations['skills'] = "Correspondance partielle des compétences"
        
        # Explication localisation
        candidate_location = candidat.get('adresse', '')
        job_location = offre.get('localisation', '')
        
        if candidate_location.lower() in job_location.lower():
            explanations['location'] = "Localisation parfaitement compatible"
        else:
            explanations['location'] = f"Localisation différente ({candidate_location} vs {job_location})"
        
        # Explication salaire
        candidate_salary = candidat.get('salaire_souhaite', 0)
        job_salary = offre.get('salaire', '')
        
        if candidate_salary and job_salary:
            explanations['salary'] = f"Attentes salariales: {candidate_salary}€ vs offre: {job_salary}"
        else:
            explanations['salary'] = "Informations salariales à préciser"
        
        return explanations
    
    def _extract_cv_data(self, candidat: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les données CV du candidat"""
        return {
            'competences': candidat.get('competences', []),
            'annees_experience': candidat.get('annees_experience', 0),
            'formation': candidat.get('formation', ''),
            'soft_skills': candidat.get('soft_skills', [])
        }
    
    def _extract_questionnaire_data(self, candidat: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les données questionnaire du candidat"""
        return {
            'contrats_recherches': candidat.get('contrats_recherches', []),
            'adresse': candidat.get('adresse', ''),
            'salaire_min': candidat.get('salaire_souhaite', 0),
            'mobilite': candidat.get('mobilite', ''),
            'disponibilite': candidat.get('disponibilite', ''),
            'criteres_importants': candidat.get('criteres_importants', {}),
            'preferences_culture': candidat.get('preferences_culture', {})
        }
    
    def _adapt_offer_to_enhanced(self, offre: Dict[str, Any]) -> Dict[str, Any]:
        """Adapte une offre au format Enhanced"""
        return {
            'id': offre.get('id', 'job_1'),
            'titre': offre.get('titre', offre.get('title', 'Poste')),
            'competences': offre.get('competences', []),
            'type_contrat': offre.get('type_contrat', ''),
            'localisation': offre.get('localisation', ''),
            'salaire': offre.get('salaire', ''),
            'experience_requise': offre.get('experience_requise', 0),
            'soft_skills': offre.get('soft_skills', []),
            'culture_entreprise': offre.get('culture_entreprise', {}),
            'politique_remote': offre.get('politique_remote', '')
        }
    
    def _adapt_result_from_enhanced(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Adapte les résultats Enhanced au format SuperSmartMatch"""
        return {
            'id': result.get('id', 'unknown'),
            'titre': result.get('titre', 'Poste sans titre'),
            'matching_score': result.get('matching_score', 0),
            'matching_details': result.get('matching_details', {}),
            'matching_explanations': result.get('matching_explanations', {}),
            **result  # Inclure toutes les données originales
        }
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'algorithme Enhanced"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": {
                "soft_skills": True,
                "culture_matching": True,
                "dynamic_weighting": True,
                "detailed_explanations": True,
                "preference_based": True
            },
            "optimal_for": [
                "Candidats avec soft skills",
                "Données de préférences culturelles",
                "Matching détaillé et personnalisé",
                "Critères d'importance spécifiés"
            ],
            "initialized": self.initialized
        }
