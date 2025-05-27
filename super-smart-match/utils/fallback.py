#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de Fallback pour SuperSmartMatch
Gère les cas d'erreur et fournit des algorithmes de secours
"""

import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

class FallbackManager:
    """
    Gestionnaire de fallback pour assurer la continuité de service
    même en cas d'erreur des algorithmes principaux
    """
    
    def __init__(self):
        """Initialise le gestionnaire de fallback"""
        self.fallback_algorithms = self._initialize_fallback_algorithms()
        self.error_patterns = self._initialize_error_patterns()
        
        logger.info("Fallback Manager initialisé")
    
    def _initialize_fallback_algorithms(self) -> Dict[str, Any]:
        """Initialise les algorithmes de fallback"""
        return {
            "simple": {
                "name": "Simple Matching",
                "description": "Algorithme de matching simple basé sur les compétences",
                "complexity": 1,
                "reliability": 0.95
            },
            "keyword": {
                "name": "Keyword Matching", 
                "description": "Matching par mots-clés avec scores pondérés",
                "complexity": 2,
                "reliability": 0.90
            },
            "statistical": {
                "name": "Statistical Matching",
                "description": "Matching statistique basé sur les fréquences",
                "complexity": 3,
                "reliability": 0.85
            }
        }
    
    def _initialize_error_patterns(self) -> Dict[str, str]:
        """Initialise les patterns d'erreur et leurs fallbacks recommandés"""
        return {
            "import_error": "simple",
            "api_error": "keyword", 
            "timeout_error": "simple",
            "memory_error": "simple",
            "connection_error": "keyword",
            "data_error": "statistical",
            "unknown_error": "simple"
        }
    
    def execute_simple_matching(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute l'algorithme de matching simple (fallback principal)
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des résultats de matching
        """
        try:
            logger.info("Exécution du fallback simple matching")
            
            results = []
            
            # Extraire les compétences du candidat
            candidate_skills = self._extract_skills(candidat)
            
            for i, offre in enumerate(offres[:limit]):
                # Calculer le score simple
                score = self._calculate_simple_score(candidat, offre, candidate_skills)
                
                result = {
                    'id': offre.get('id', f'fallback_job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'score_global': int(score * 100),
                    'scores_details': {
                        'skills': self._calculate_skills_match(candidate_skills, offre) * 100,
                        'contract': self._calculate_contract_match(candidat, offre) * 100,
                        'location': self._calculate_location_match(candidat, offre) * 100,
                        'experience': self._calculate_experience_match(candidat, offre) * 100
                    },
                    'explications': {
                        'skills': self._explain_skills_match(candidate_skills, offre),
                        'general': 'Score calculé avec algorithme de fallback simple'
                    },
                    'confiance': score * 0.8,  # Confiance légèrement réduite pour le fallback
                    'donnees_originales': offre,
                    'fallback_used': True
                }
                
                results.append(result)
            
            # Trier par score décroissant
            results.sort(key=lambda x: x['score_global'], reverse=True)
            
            logger.info(f"Fallback simple matching: {len(results)} résultats générés")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans le fallback simple: {e}")
            return self._execute_emergency_fallback(candidat, offres, limit)
    
    def execute_keyword_matching(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute l'algorithme de matching par mots-clés
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des résultats de matching
        """
        try:
            logger.info("Exécution du fallback keyword matching")
            
            results = []
            
            # Extraire tous les mots-clés du candidat
            candidate_keywords = self._extract_all_keywords(candidat)
            
            for i, offre in enumerate(offres[:limit]):
                # Calculer le score basé sur les mots-clés
                score = self._calculate_keyword_score(candidate_keywords, offre)
                
                result = {
                    'id': offre.get('id', f'keyword_job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'score_global': int(score * 100),
                    'scores_details': {
                        'keywords': score * 100,
                        'relevance': self._calculate_relevance_score(candidate_keywords, offre) * 100
                    },
                    'explications': {
                        'keywords': self._explain_keyword_match(candidate_keywords, offre),
                        'general': 'Score calculé avec algorithme de fallback par mots-clés'
                    },
                    'confiance': score * 0.75,  # Confiance réduite pour le fallback
                    'donnees_originales': offre,
                    'fallback_used': True
                }
                
                results.append(result)
            
            # Trier par score décroissant
            results.sort(key=lambda x: x['score_global'], reverse=True)
            
            logger.info(f"Fallback keyword matching: {len(results)} résultats générés")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans le fallback keyword: {e}")
            return self._execute_emergency_fallback(candidat, offres, limit)
    
    def execute_statistical_matching(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute l'algorithme de matching statistique
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des résultats de matching
        """
        try:
            logger.info("Exécution du fallback statistical matching")
            
            results = []
            
            # Analyser les fréquences dans les données
            candidate_freq = self._calculate_frequency_profile(candidat)
            
            for i, offre in enumerate(offres[:limit]):
                # Calculer le score statistique
                score = self._calculate_statistical_score(candidate_freq, offre)
                
                result = {
                    'id': offre.get('id', f'stat_job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'score_global': int(score * 100),
                    'scores_details': {
                        'statistical': score * 100,
                        'frequency': self._calculate_frequency_match(candidate_freq, offre) * 100
                    },
                    'explications': {
                        'statistical': self._explain_statistical_match(candidate_freq, offre),
                        'general': 'Score calculé avec algorithme de fallback statistique'
                    },
                    'confiance': score * 0.7,  # Confiance réduite pour le fallback
                    'donnees_originales': offre,
                    'fallback_used': True
                }
                
                results.append(result)
            
            # Trier par score décroissant
            results.sort(key=lambda x: x['score_global'], reverse=True)
            
            logger.info(f"Fallback statistical matching: {len(results)} résultats générés")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans le fallback statistical: {e}")
            return self._execute_emergency_fallback(candidat, offres, limit)
    
    def _execute_emergency_fallback(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fallback d'urgence en cas d'échec de tous les autres
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des résultats basiques
        """
        logger.warning("Exécution du fallback d'urgence")
        
        results = []
        
        try:
            for i, offre in enumerate(offres[:limit]):
                # Score basique (50% par défaut)
                score = 50
                
                # Bonus si titre contient des mots communs
                titre = offre.get('titre', '').lower()
                candidate_name = candidat.get('nom', '').lower()
                
                if any(word in titre for word in ['développeur', 'developer', 'ingénieur', 'engineer']):
                    score += 10
                
                result = {
                    'id': offre.get('id', f'emergency_job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'score_global': score,
                    'scores_details': {
                        'emergency': score
                    },
                    'explications': {
                        'general': 'Score généré par le fallback d\'urgence - données limitées disponibles'
                    },
                    'confiance': 0.3,  # Confiance très faible
                    'donnees_originales': offre,
                    'fallback_used': True,
                    'emergency_fallback': True
                }
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.critical(f"Échec du fallback d'urgence: {e}")
            # Retourner au moins une structure vide
            return [{
                'id': 'error',
                'titre': 'Erreur de matching',
                'score_global': 0,
                'scores_details': {},
                'explications': {
                    'error': 'Tous les algorithmes de fallback ont échoué'
                },
                'confiance': 0.0,
                'donnees_originales': {},
                'fallback_used': True,
                'emergency_fallback': True,
                'error': str(e)
            }]
    
    def determine_fallback_algorithm(self, error_type: str, error_message: str = "") -> str:
        """
        Détermine quel algorithme de fallback utiliser selon l'erreur
        
        Args:
            error_type: Type d'erreur
            error_message: Message d'erreur
            
        Returns:
            Nom de l'algorithme de fallback recommandé
        """
        # Analyser le type d'erreur
        error_lower = error_type.lower()
        message_lower = error_message.lower()
        
        # Patterns spécifiques
        if "import" in error_lower or "module" in message_lower:
            return "simple"
        elif "timeout" in error_lower or "time" in message_lower:
            return "simple"
        elif "memory" in error_lower or "ram" in message_lower:
            return "simple"
        elif "connection" in error_lower or "network" in message_lower:
            return "keyword"
        elif "api" in error_lower or "request" in message_lower:
            return "keyword"
        elif "data" in error_lower or "format" in message_lower:
            return "statistical"
        else:
            return "simple"  # Fallback par défaut
    
    def get_fallback_by_name(self, fallback_name: str) -> callable:
        """
        Retourne la fonction de fallback par nom
        
        Args:
            fallback_name: Nom du fallback
            
        Returns:
            Fonction de fallback
        """
        fallback_functions = {
            "simple": self.execute_simple_matching,
            "keyword": self.execute_keyword_matching,
            "statistical": self.execute_statistical_matching
        }
        
        return fallback_functions.get(fallback_name, self.execute_simple_matching)
    
    # Méthodes utilitaires pour les calculs
    
    def _extract_skills(self, candidat: Dict[str, Any]) -> List[str]:
        """Extrait et normalise les compétences du candidat"""
        skills = candidat.get('competences', []) or candidat.get('skills', [])
        
        if isinstance(skills, str):
            skills = [skills]
        
        return [skill.lower().strip() for skill in skills if skill]
    
    def _extract_all_keywords(self, candidat: Dict[str, Any]) -> List[str]:
        """Extrait tous les mots-clés du candidat"""
        keywords = []
        
        # Compétences
        skills = self._extract_skills(candidat)
        keywords.extend(skills)
        
        # Formation
        formation = candidat.get('formation', '') or candidat.get('education', '')
        if formation:
            keywords.extend(formation.lower().split())
        
        # Autres champs texte
        for field in ['experience', 'description', 'secteur_activite']:
            value = candidat.get(field, '')
            if isinstance(value, str) and value:
                keywords.extend(value.lower().split())
        
        # Nettoyer et dédupliquer
        cleaned_keywords = []
        for keyword in keywords:
            # Supprimer la ponctuation
            cleaned = re.sub(r'[^\w]', '', keyword)
            if len(cleaned) > 2:  # Garder seulement les mots de plus de 2 caractères
                cleaned_keywords.append(cleaned)
        
        return list(set(cleaned_keywords))  # Dédupliquer
    
    def _calculate_simple_score(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any], 
        candidate_skills: List[str]
    ) -> float:
        """Calcule un score simple de matching"""
        scores = []
        
        # Score compétences (poids 40%)
        skills_score = self._calculate_skills_match(candidate_skills, offre)
        scores.append(skills_score * 0.4)
        
        # Score contrat (poids 20%)
        contract_score = self._calculate_contract_match(candidat, offre)
        scores.append(contract_score * 0.2)
        
        # Score localisation (poids 20%)
        location_score = self._calculate_location_match(candidat, offre)
        scores.append(location_score * 0.2)
        
        # Score expérience (poids 20%)
        experience_score = self._calculate_experience_match(candidat, offre)
        scores.append(experience_score * 0.2)
        
        return sum(scores)
    
    def _calculate_skills_match(self, candidate_skills: List[str], offre: Dict[str, Any]) -> float:
        """Calcule la correspondance des compétences"""
        required_skills = offre.get('competences', []) or offre.get('required_skills', [])
        
        if not required_skills:
            return 0.6  # Score neutre
        
        if not candidate_skills:
            return 0.2  # Score bas
        
        # Normaliser les compétences requises
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        
        # Calculer l'intersection
        matching_skills = set(candidate_skills).intersection(set(required_skills_lower))
        
        if not required_skills_lower:
            return 0.6
        
        # Score basé sur le pourcentage de correspondance
        match_ratio = len(matching_skills) / len(required_skills_lower)
        
        # Bonus si candidat a plus de compétences
        if len(candidate_skills) > len(required_skills_lower):
            bonus = min(0.2, (len(candidate_skills) - len(required_skills_lower)) * 0.05)
            match_ratio += bonus
        
        return min(1.0, match_ratio)
    
    def _calculate_contract_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule la correspondance du type de contrat"""
        candidate_contracts = candidat.get('contrats_recherches', []) or candidat.get('contract_types', [])
        job_contract = offre.get('type_contrat', '') or offre.get('contract_type', '')
        
        if not candidate_contracts or not job_contract:
            return 0.7  # Score neutre
        
        # Normaliser
        if isinstance(candidate_contracts, str):
            candidate_contracts = [candidate_contracts]
        
        candidate_contracts_lower = [c.lower() for c in candidate_contracts]
        job_contract_lower = job_contract.lower()
        
        # Correspondance directe
        if job_contract_lower in candidate_contracts_lower:
            return 1.0
        
        # Correspondances partielles
        if 'cdi' in candidate_contracts_lower and 'cdi' in job_contract_lower:
            return 1.0
        if 'cdd' in candidate_contracts_lower and 'cdd' in job_contract_lower:
            return 1.0
        
        return 0.3  # Pas de correspondance
    
    def _calculate_location_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule la correspondance de localisation"""
        candidate_location = candidat.get('adresse', '') or candidat.get('location', '')
        job_location = offre.get('localisation', '') or offre.get('location', '')
        
        if not candidate_location or not job_location:
            return 0.6  # Score neutre
        
        candidate_lower = candidate_location.lower()
        job_lower = job_location.lower()
        
        # Correspondance exacte
        if candidate_lower == job_lower:
            return 1.0
        
        # Correspondance partielle
        if candidate_lower in job_lower or job_lower in candidate_lower:
            return 0.8
        
        # Même ville (vérification basique)
        candidate_words = set(candidate_lower.split())
        job_words = set(job_lower.split())
        
        if candidate_words.intersection(job_words):
            return 0.7
        
        return 0.4  # Différent
    
    def _calculate_experience_match(self, candidat: Dict[str, Any], offre: Dict[str, Any]) -> float:
        """Calcule la correspondance d'expérience"""
        candidate_exp = candidat.get('annees_experience', 0) or candidat.get('years_experience', 0)
        required_exp = offre.get('experience_requise', 0) or offre.get('required_experience', 0)
        
        if required_exp == 0:
            return 0.8  # Pas d'exigence
        
        if candidate_exp == 0:
            return 0.3  # Candidat sans expérience
        
        if candidate_exp >= required_exp:
            return 1.0  # Assez d'expérience
        else:
            # Score proportionnel
            return min(1.0, candidate_exp / required_exp)
    
    def _calculate_keyword_score(self, candidate_keywords: List[str], offre: Dict[str, Any]) -> float:
        """Calcule un score basé sur les mots-clés"""
        # Extraire les mots-clés de l'offre
        job_text = ""
        for field in ['titre', 'title', 'description', 'competences', 'required_skills']:
            value = offre.get(field, '')
            if isinstance(value, list):
                job_text += " " + " ".join(str(v) for v in value)
            elif isinstance(value, str):
                job_text += " " + value
        
        job_keywords = set(re.findall(r'\w+', job_text.lower()))
        candidate_keywords_set = set(candidate_keywords)
        
        # Calculer l'intersection
        matching_keywords = candidate_keywords_set.intersection(job_keywords)
        
        if not job_keywords:
            return 0.5
        
        # Score basé sur la proportion de mots-clés correspondants
        score = len(matching_keywords) / len(job_keywords)
        
        return min(1.0, score)
    
    def _calculate_frequency_profile(self, candidat: Dict[str, Any]) -> Dict[str, int]:
        """Calcule un profil de fréquence des termes du candidat"""
        text = ""
        for field, value in candidat.items():
            if isinstance(value, str):
                text += " " + value
            elif isinstance(value, list):
                text += " " + " ".join(str(v) for v in value)
        
        # Compter les fréquences
        words = re.findall(r'\w+', text.lower())
        frequency = {}
        for word in words:
            if len(word) > 2:  # Ignorer les mots trop courts
                frequency[word] = frequency.get(word, 0) + 1
        
        return frequency
    
    def _calculate_statistical_score(self, candidate_freq: Dict[str, int], offre: Dict[str, Any]) -> float:
        """Calcule un score statistique basé sur les fréquences"""
        # Extraire le texte de l'offre
        job_text = ""
        for field, value in offre.items():
            if isinstance(value, str):
                job_text += " " + value
            elif isinstance(value, list):
                job_text += " " + " ".join(str(v) for v in value)
        
        job_words = re.findall(r'\w+', job_text.lower())
        
        if not job_words or not candidate_freq:
            return 0.5
        
        # Calculer le score basé sur les fréquences communes
        score = 0
        total_job_words = len(job_words)
        
        for word in set(job_words):
            if word in candidate_freq:
                # Score pondéré par la fréquence
                word_score = candidate_freq[word] / sum(candidate_freq.values())
                score += word_score
        
        return min(1.0, score)
    
    # Méthodes d'explication
    
    def _explain_skills_match(self, candidate_skills: List[str], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching des compétences"""
        required_skills = offre.get('competences', []) or offre.get('required_skills', [])
        
        if not required_skills:
            return "Aucune compétence spécifiée dans l'offre"
        
        required_skills_lower = [skill.lower() for skill in required_skills]
        matching_skills = set(candidate_skills).intersection(set(required_skills_lower))
        
        if len(matching_skills) == len(required_skills_lower):
            return "Toutes les compétences requises correspondent"
        elif len(matching_skills) > 0:
            return f"{len(matching_skills)}/{len(required_skills_lower)} compétences correspondent"
        else:
            return "Aucune compétence en correspondance directe"
    
    def _explain_keyword_match(self, candidate_keywords: List[str], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching par mots-clés"""
        job_text = str(offre.get('titre', '')) + " " + str(offre.get('description', ''))
        job_keywords = set(re.findall(r'\w+', job_text.lower()))
        
        matching_keywords = set(candidate_keywords).intersection(job_keywords)
        
        if len(matching_keywords) > 5:
            return f"Nombreux mots-clés en commun ({len(matching_keywords)})"
        elif len(matching_keywords) > 0:
            return f"{len(matching_keywords)} mots-clés en commun"
        else:
            return "Peu de mots-clés en commun"
    
    def _explain_statistical_match(self, candidate_freq: Dict[str, int], offre: Dict[str, Any]) -> str:
        """Génère une explication pour le matching statistique"""
        if not candidate_freq:
            return "Profil statistique candidat limité"
        
        most_frequent = max(candidate_freq.items(), key=lambda x: x[1])
        return f"Analyse basée sur les termes fréquents (ex: '{most_frequent[0]}')"
    
    def _calculate_relevance_score(self, candidate_keywords: List[str], offre: Dict[str, Any]) -> float:
        """Calcule un score de pertinence"""
        return self._calculate_keyword_score(candidate_keywords, offre) * 0.8
    
    def _calculate_frequency_match(self, candidate_freq: Dict[str, int], offre: Dict[str, Any]) -> float:
        """Calcule la correspondance de fréquence"""
        return self._calculate_statistical_score(candidate_freq, offre) * 0.9
