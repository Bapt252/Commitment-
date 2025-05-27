#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptateur pour l'algorithme SmartMatch dans SuperSmartMatch
"""

import sys
import os
import logging
from typing import Dict, List, Any

# Ajouter le répertoire racine au path pour importer les modules existants
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from .base import BaseAlgorithm

logger = logging.getLogger(__name__)

class SmartMatchAlgorithm(BaseAlgorithm):
    """
    Adaptateur pour l'algorithme SmartMatch bidirectionnel
    """
    
    def __init__(self):
        super().__init__()
        self.name = "smart-match"
        self.description = "Algorithme bidirectionnel avec géolocalisation Google Maps"
        self.version = "1.0"
        
        # Initialiser le moteur SmartMatch
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialise le moteur SmartMatch original"""
        try:
            # Import conditionnel pour éviter les erreurs si le module n'existe pas
            from app.smartmatch import SmartMatchEngine
            from app.data_loader import DataLoader
            
            self.engine = SmartMatchEngine()
            self.data_loader = DataLoader()
            self.initialized = True
            
            logger.info("SmartMatch engine initialisé avec succès")
            
        except ImportError as e:
            logger.warning(f"Impossible d'importer SmartMatch: {e}")
            self.engine = None
            self.initialized = False
            
            # Fallback vers l'implémentation simplifiée
            self._setup_fallback()
    
    def _setup_fallback(self):
        """Configure un fallback si l'algorithme original n'est pas disponible"""
        logger.info("Configuration du fallback SmartMatch")
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
        # SmartMatch fonctionne mieux avec des données de géolocalisation
        has_location = bool(
            candidat.get('adresse') or 
            candidat.get('localisation') or
            candidat.get('location')
        )
        
        has_remote_prefs = bool(
            candidat.get('mobilite') or
            candidat.get('remote_preference') or
            candidat.get('politique_remote')
        )
        
        # Vérifier que les offres ont des informations de localisation
        offers_have_location = any(
            offre.get('localisation') or 
            offre.get('lieu') or 
            offre.get('location')
            for offre in offres
        )
        
        return has_location and offers_have_location
    
    def match_candidate_with_jobs(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute le matching SmartMatch
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des offres avec scores de matching
        """
        if not self.initialized:
            raise RuntimeError("SmartMatch algorithm non initialisé")
        
        try:
            if self.engine:
                # Utiliser l'algorithme original
                return self._execute_original(candidat, offres, limit)
            else:
                # Utiliser le fallback
                return self._execute_fallback(candidat, offres, limit)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution SmartMatch: {e}")
            # Fallback en cas d'erreur
            return self._execute_fallback(candidat, offres, limit)
    
    def _execute_original(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Exécute l'algorithme SmartMatch original
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            limit: Limite de résultats
            
        Returns:
            Résultats de matching
        """
        # Adapter les données au format attendu par SmartMatch
        candidates = [self._adapt_candidate_to_smartmatch(candidat)]
        companies = [self._adapt_offer_to_smartmatch(offre) for offre in offres]
        
        # Exécuter le matching
        matching_results = self.engine.match(candidates, companies)
        
        # Adapter les résultats au format SuperSmartMatch
        adapted_results = []
        for result in matching_results[:limit]:
            adapted_result = self._adapt_result_from_smartmatch(result, offres)
            adapted_results.append(adapted_result)
        
        return adapted_results
    
    def _execute_fallback(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Exécute une version simplifiée de SmartMatch
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            limit: Limite de résultats
            
        Returns:
            Résultats de matching
        """
        results = []
        
        for i, offre in enumerate(offres[:limit]):
            # Calcul simple de score basé sur les critères SmartMatch
            score = self._calculate_simple_score(candidat, offre)
            
            result = {
                'id': offre.get('id', f'job_{i}'),
                'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                'matching_score': int(score * 100),
                'matching_details': {
                    'skills': self._calculate_skills_score(candidat, offre) * 100,
                    'location': self._calculate_location_score(candidat, offre) * 100,
                    'remote_policy': self._calculate_remote_score(candidat, offre) * 100,
                    'contract': self._calculate_contract_score(candidat, offre) * 100
                },
                'matching_explanations': {
                    'skills': self._explain_skills_match(candidat, offre),
                    'location': self._explain_location_match(candidat, offre),
                    'remote_policy': self._explain_remote_match(candidat, offre),
                    'contract': self._explain_contract_match(candidat, offre)
                },
                **offre  # Inclure toutes les données de l'offre originale
            }
            
            results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return results
    
    def _calculate_simple_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> float:
        """
        Calcule un score simple de matching
        
        Args:
            candidat: Données candidat
            offre: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Poids pour les différents critères (style SmartMatch)
        weights = {
            'skills': 0.4,
            'location': 0.25,
            'remote_policy': 0.15,
            'contract': 0.2
        }
        
        scores = {
            'skills': self._calculate_skills_score(candidat, offre),
            'location': self._calculate_location_score(candidat, offre),
            'remote_policy': self._calculate_remote_score(candidat, offre),
            'contract': self._calculate_contract_score(candidat, offre)
        }
        
        # Score pondéré
        total_score = sum(scores[criterion] * weights[criterion] for criterion in weights)
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_skills_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> float:
        """Calcule le score de correspondance des compétences"""
        candidate_skills = set(skill.lower() for skill in candidat.get('competences', []))
        required_skills = set(skill.lower() for skill in offre.get('competences', []))
        
        if not required_skills:
            return 0.5  # Score neutre si pas de compétences spécifiées
        
        matching_skills = candidate_skills.intersection(required_skills)
        
        if not candidate_skills:
            return 0.2  # Score bas si candidat n'a pas de compétences listées
        
        # Score basé sur le pourcentage de compétences requises couvertes
        coverage_score = len(matching_skills) / len(required_skills)
        
        # Bonus si le candidat a des compétences supplémentaires
        additional_skills = candidate_skills - required_skills
        bonus = min(0.2, len(additional_skills) * 0.05)
        
        return min(1.0, coverage_score + bonus)
    
    def _calculate_location_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> float:
        """Calcule le score de correspondance de localisation"""
        candidate_location = candidat.get('adresse', '').lower()
        job_location = offre.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.5  # Score neutre si pas d'info de localisation
        
        # Correspondance exacte de ville
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Correspondance partielle (même région, etc.)
        candidate_words = set(candidate_location.split())
        job_words = set(job_location.split())
        
        common_words = candidate_words.intersection(job_words)
        if common_words:
            return 0.8
        
        # Vérifications spécifiques pour les grandes villes
        major_cities = ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'bordeaux']
        
        candidate_city = None
        job_city = None
        
        for city in major_cities:
            if city in candidate_location:
                candidate_city = city
            if city in job_location:
                job_city = city
        
        if candidate_city and job_city:
            if candidate_city == job_city:
                return 1.0
            else:
                return 0.3  # Différentes grandes villes
        
        return 0.4  # Score par défaut pour localisation différente
    
    def _calculate_remote_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> float:
        """Calcule le score de correspondance pour le télétravail"""
        candidate_remote = candidat.get('mobilite', '').lower()
        job_remote = offre.get('politique_remote', '').lower()
        
        if not candidate_remote and not job_remote:
            return 0.7  # Score neutre
        
        # Mapping des préférences
        remote_mapping = {
            'remote': ['remote', 'télétravail', 'full remote', 'totalement'],
            'hybrid': ['hybrid', 'hybride', 'mixte', 'partiel'],
            'onsite': ['onsite', 'présentiel', 'bureau', 'sur site']
        }
        
        candidate_type = None
        job_type = None
        
        for remote_type, keywords in remote_mapping.items():
            if any(keyword in candidate_remote for keyword in keywords):
                candidate_type = remote_type
            if any(keyword in job_remote for keyword in keywords):
                job_type = remote_type
        
        if candidate_type and job_type:
            if candidate_type == job_type:
                return 1.0
            elif (candidate_type == 'hybrid' and job_type in ['remote', 'onsite']) or \
                 (job_type == 'hybrid' and candidate_type in ['remote', 'onsite']):
                return 0.7
            else:
                return 0.3
        
        return 0.5  # Score par défaut
    
    def _calculate_contract_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> float:
        """Calcule le score de correspondance du type de contrat"""
        candidate_contracts = [c.lower() for c in candidat.get('contrats_recherches', [])]
        job_contract = offre.get('type_contrat', '').lower()
        
        if not candidate_contracts or not job_contract:
            return 0.7  # Score neutre
        
        # Correspondance directe
        if job_contract in candidate_contracts:
            return 1.0
        
        # Correspondances partielles
        if 'cdi' in candidate_contracts and 'cdi' in job_contract:
            return 1.0
        if 'cdd' in candidate_contracts and 'cdd' in job_contract:
            return 1.0
        if 'freelance' in candidate_contracts and ('freelance' in job_contract or 'consultant' in job_contract):
            return 1.0
        
        return 0.2  # Pas de correspondance
    
    def _explain_skills_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching des compétences"""
        candidate_skills = set(skill.lower() for skill in candidat.get('competences', []))
        required_skills = set(skill.lower() for skill in offre.get('competences', []))
        
        matching_skills = candidate_skills.intersection(required_skills)
        
        if len(matching_skills) == len(required_skills):
            return "Toutes les compétences requises correspondent parfaitement"
        elif len(matching_skills) >= len(required_skills) * 0.7:
            return f"{len(matching_skills)}/{len(required_skills)} compétences correspondent"
        else:
            return f"Correspondance partielle ({len(matching_skills)}/{len(required_skills)} compétences)"
    
    def _explain_location_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching de localisation"""
        candidate_location = candidat.get('adresse', '')
        job_location = offre.get('localisation', '')
        
        if candidate_location.lower() == job_location.lower():
            return "Localisation parfaitement correspondante"
        elif candidate_location.lower() in job_location.lower() or job_location.lower() in candidate_location.lower():
            return "Localisation dans la même zone géographique"
        else:
            return f"Localisation différente ({candidate_location} vs {job_location})"
    
    def _explain_remote_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching télétravail"""
        candidate_remote = candidat.get('mobilite', '')
        job_remote = offre.get('politique_remote', '')
        
        if candidate_remote.lower() == job_remote.lower():
            return "Politique de télétravail parfaitement alignée"
        else:
            return f"Préférences télétravail: {candidate_remote} vs {job_remote}"
    
    def _explain_contract_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching de contrat"""
        candidate_contracts = candidat.get('contrats_recherches', [])
        job_contract = offre.get('type_contrat', '')
        
        if job_contract.lower() in [c.lower() for c in candidate_contracts]:
            return f"Type de contrat souhaité ({job_contract})"
        else:
            return f"Type de contrat différent (recherché: {', '.join(candidate_contracts)}, proposé: {job_contract})"
    
    def _adapt_candidate_to_smartmatch(self, candidat: Dict[str, Any]) -> Dict[str, Any]:
        """Adapte les données candidat au format SmartMatch"""
        return {
            "id": candidat.get('id', 'candidate_1'),
            "name": candidat.get('nom', 'Candidat'),
            "skills": candidat.get('competences', []),
            "experience": candidat.get('annees_experience', 0),
            "location": candidat.get('adresse', ''),
            "remote_preference": candidat.get('mobilite', ''),
            "salary_expectation": candidat.get('salaire_souhaite', 0)
        }
    
    def _adapt_offer_to_smartmatch(self, offre: Dict[str, Any]) -> Dict[str, Any]:
        """Adapte les données d'offre au format SmartMatch"""
        return {
            "id": offre.get('id', 'company_1'),
            "name": offre.get('entreprise', offre.get('titre', 'Entreprise')),
            "required_skills": offre.get('competences', []),
            "location": offre.get('localisation', ''),
            "remote_policy": offre.get('politique_remote', ''),
            "salary_range": {
                "min": 0,
                "max": 100000
            },
            "required_experience": offre.get('experience_requise', 0)
        }
    
    def _adapt_result_from_smartmatch(
        self, 
        result: Dict[str, Any], 
        original_offers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Adapte les résultats SmartMatch au format SuperSmartMatch"""
        # Trouver l'offre originale correspondante
        original_offer = None
        for offer in original_offers:
            if offer.get('id') == result.get('company_id'):
                original_offer = offer
                break
        
        if not original_offer:
            original_offer = original_offers[0] if original_offers else {}
        
        return {
            'id': result.get('company_id', 'unknown'),
            'titre': original_offer.get('titre', result.get('company_name', 'Poste sans titre')),
            'matching_score': int(result.get('score', 0) * 100),
            'matching_details': result.get('details', {}),
            'matching_explanations': result.get('explanations', {}),
            **original_offer
        }
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'algorithme"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": {
                "geolocation": True,
                "remote_preferences": True,
                "bidirectional_matching": True,
                "google_maps_integration": True
            },
            "optimal_for": [
                "Candidats avec adresse précise",
                "Offres avec localisation",
                "Préférences de télétravail",
                "Matching bidirectionnel"
            ],
            "initialized": self.initialized
        }
