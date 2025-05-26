#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire d'Algorithmes pour SuperSmartMatch

Gère l'accès unifié à tous les algorithmes de matching :
- Chargement dynamique des algorithmes
- Interface standardisée
- Métriques de performance
- Gestion des erreurs

Auteur: Nexten Team
"""

import os
import sys
import time
import logging
import importlib
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import traceback

# Ajout du chemin parent pour importer les algorithmes existants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class AlgorithmManager:
    """
    Gestionnaire unifié pour tous les algorithmes de matching
    """
    
    def __init__(self):
        self.algorithms = {}
        self.usage_stats = {}
        self.performance_cache = {}
        self._load_algorithms()
    
    def _load_algorithms(self):
        """Charge tous les algorithmes disponibles"""
        try:
            # 1. Algorithme Original
            try:
                from matching_engine import match_candidate_with_jobs as original_algorithm
                self.algorithms["original"] = {
                    "function": original_algorithm,
                    "name": "Algorithme Original",
                    "version": "1.0.0",
                    "description": "Algorithme de base avec critères standards",
                    "strengths": ["Rapide", "Stable", "Éprouvé"],
                    "best_for": ["Volume important", "Critères simples", "Performance"]
                }
                logger.info("✅ Algorithme Original chargé")
            except ImportError as e:
                logger.warning(f"❌ Impossible de charger l'algorithme Original: {e}")
            
            # 2. Smart Match (bidirectionnel)
            try:
                # Implémentation basée sur README-SMARTMATCH.md
                self.algorithms["smart-match"] = {
                    "function": self._smart_match_wrapper,
                    "name": "SmartMatch Bidirectionnel",
                    "version": "1.2.0",
                    "description": "Matching bidirectionnel avec géolocalisation Google Maps",
                    "strengths": ["Géolocalisation avancée", "Bidirectionnel", "Temps de trajet réels"],
                    "best_for": ["Mobilité géographique", "Critères de localisation", "Matching précis"]
                }
                logger.info("✅ SmartMatch chargé")
            except Exception as e:
                logger.warning(f"❌ Impossible de charger SmartMatch: {e}")
            
            # 3. Enhanced Matching Engine
            try:
                from enhanced_matching_engine import match_candidate_with_jobs as enhanced_algorithm
                self.algorithms["enhanced"] = {
                    "function": enhanced_algorithm,
                    "name": "Enhanced Matching Engine",
                    "version": "1.0.0",
                    "description": "Moteur avancé avec matching sémantique et pondération adaptative",
                    "strengths": ["Matching sémantique", "Pondération adaptative", "Scoring graduel"],
                    "best_for": ["Compétences techniques", "Candidats expérimentés", "Précision maximale"]
                }
                logger.info("✅ Enhanced Matching Engine chargé")
            except ImportError as e:
                logger.warning(f"❌ Impossible de charger Enhanced: {e}")
            
            # 4. Analyseur Sémantique
            try:
                self.algorithms["semantic"] = {
                    "function": self._semantic_wrapper,
                    "name": "Analyseur Sémantique",
                    "version": "1.1.0",
                    "description": "Analyse sémantique des compétences avec reconnaissance des technologies liées",
                    "strengths": ["Compétences liées", "Synonymes", "Similarité textuelle"],
                    "best_for": ["Compétences techniques", "Technologies émergentes", "Polyvalence"]
                }
                logger.info("✅ Analyseur Sémantique chargé")
            except Exception as e:
                logger.warning(f"❌ Impossible de charger Sémantique: {e}")
            
            # 5. Algorithme Personnalisé
            try:
                from my_matching_engine import match_candidate_with_jobs as custom_algorithm
                self.algorithms["custom"] = {
                    "function": custom_algorithm,
                    "name": "Algorithme Personnalisé",
                    "version": "1.0.0",
                    "description": "Algorithme optimisé spécifique au projet",
                    "strengths": ["Optimisé projet", "Critères spécifiques", "Performance ajustée"],
                    "best_for": ["Besoins spécifiques", "Optimisation locale", "Cas particuliers"]
                }
                logger.info("✅ Algorithme Personnalisé chargé")
            except ImportError as e:
                logger.warning(f"❌ Impossible de charger Personnalisé: {e}")
            
            # 6. Algorithme Hybride (combine plusieurs approches)
            self.algorithms["hybrid"] = {
                "function": self._hybrid_wrapper,
                "name": "Algorithme Hybride",
                "version": "1.0.0",
                "description": "Combine les forces de plusieurs algorithmes",
                "strengths": ["Robuste", "Adaptable", "Meilleurs résultats"],
                "best_for": ["Cas complexes", "Maximiser la précision", "Candidats divers"]
            }
            
            logger.info(f"🎯 {len(self.algorithms)} algorithmes chargés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des algorithmes: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _smart_match_wrapper(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Wrapper pour SmartMatch basé sur les spécifications README-SMARTMATCH.md
        """
        try:
            # Simulation de l'algorithme SmartMatch bidirectionnel
            # En production, ceci ferait appel au vrai SmartMatch
            
            results = []
            for job in job_data:
                # Calcul simplifié pour la démo
                score = self._calculate_smart_match_score(cv_data, questionnaire_data, job)
                
                job_result = job.copy()
                job_result['matching_score'] = round(score * 100)
                job_result['algorithm_version'] = "smart-match-v1.2.0"
                job_result['bidirectional_score'] = True
                job_result['geolocation_bonus'] = self._calculate_geolocation_bonus(questionnaire_data, job)
                
                results.append(job_result)
            
            # Tri par score décroissant
            results.sort(key=lambda x: x['matching_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Erreur SmartMatch: {e}")
            # Fallback vers algorithme de base
            return self._basic_fallback(cv_data, questionnaire_data, job_data, limit)
    
    def _semantic_wrapper(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Wrapper pour l'analyseur sémantique
        """
        try:
            # Simulation de l'analyseur sémantique
            # Basé sur README-SEMANTIC-INTEGRATION.md
            
            results = []
            for job in job_data:
                score = self._calculate_semantic_score(cv_data, job)
                
                job_result = job.copy()
                job_result['matching_score'] = round(score * 100)
                job_result['algorithm_version'] = "semantic-v1.1.0"
                job_result['semantic_analysis'] = True
                job_result['skills_similarity'] = self._get_skills_similarity(cv_data, job)
                
                results.append(job_result)
            
            results.sort(key=lambda x: x['matching_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Erreur Sémantique: {e}")
            return self._basic_fallback(cv_data, questionnaire_data, job_data, limit)
    
    def _hybrid_wrapper(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Algorithme hybride qui combine plusieurs approches
        """
        try:
            results = []
            available_algorithms = ["enhanced", "semantic", "original"]
            
            # Utiliser tous les algorithmes disponibles et faire une moyenne pondérée
            for job in job_data:
                scores = []
                weights = []
                
                for algo_name in available_algorithms:
                    if algo_name in self.algorithms:
                        try:
                            algo_result = self.algorithms[algo_name]["function"](cv_data, questionnaire_data, [job], 1)
                            if algo_result:
                                score = algo_result[0].get('matching_score', 0) / 100.0
                                scores.append(score)
                                
                                # Pondération selon la force de l'algorithme
                                if algo_name == "enhanced":
                                    weights.append(0.4)  # Plus de poids sur enhanced
                                elif algo_name == "semantic":
                                    weights.append(0.35)
                                else:
                                    weights.append(0.25)
                        except Exception as e:
                            logger.warning(f"Erreur avec {algo_name}: {e}")
                
                # Calcul de la moyenne pondérée
                if scores and weights:
                    final_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
                else:
                    final_score = 0.5  # Score par défaut
                
                job_result = job.copy()
                job_result['matching_score'] = round(final_score * 100)
                job_result['algorithm_version'] = "hybrid-v1.0.0"
                job_result['algorithms_used'] = available_algorithms[:len(scores)]
                job_result['score_components'] = dict(zip(available_algorithms[:len(scores)], [round(s*100) for s in scores]))
                
                results.append(job_result)
            
            results.sort(key=lambda x: x['matching_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Erreur Hybride: {e}")
            return self._basic_fallback(cv_data, questionnaire_data, job_data, limit)
    
    def _calculate_smart_match_score(self, cv_data: Dict, questionnaire_data: Dict, job: Dict) -> float:
        """
        Calcul simplifié pour SmartMatch (version démo)
        """
        score = 0.0
        
        # Compétences (40%)
        cv_skills = set(skill.lower() for skill in cv_data.get('competences', []))
        job_skills = set(skill.lower() for skill in job.get('competences', []))
        if job_skills:
            skills_match = len(cv_skills.intersection(job_skills)) / len(job_skills)
            score += skills_match * 0.4
        
        # Localisation avec bonus géographique (30%)
        location_score = self._calculate_geolocation_bonus(questionnaire_data, job)
        score += location_score * 0.3
        
        # Contrat (20%)
        preferred_contracts = questionnaire_data.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '')
        if job_contract.upper() in [c.upper() for c in preferred_contracts]:
            score += 0.2
        
        # Bonus bidirectionnel (10%)
        score += 0.1  # Bonus pour la nature bidirectionnelle
        
        return min(1.0, score)
    
    def _calculate_geolocation_bonus(self, questionnaire_data: Dict, job: Dict) -> float:
        """
        Calcul du bonus de géolocalisation
        """
        candidate_location = questionnaire_data.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if 'remote' in job_location or 'télétravail' in job_location:
            return 1.0  # Remote = parfait
        
        if candidate_location and job_location:
            # Détection simple des villes principales
            if any(city in candidate_location and city in job_location 
                   for city in ['paris', 'lyon', 'marseille', 'toulouse', 'nice']):
                return 1.0  # Même ville
            elif any(city in candidate_location or city in job_location 
                     for city in ['paris', 'lyon', 'marseille']):
                return 0.7  # Grandes villes
        
        return 0.5  # Défaut
    
    def _calculate_semantic_score(self, cv_data: Dict, job: Dict) -> float:
        """
        Calcul sémantique simplifié
        """
        cv_skills = [skill.lower() for skill in cv_data.get('competences', [])]
        job_skills = [skill.lower() for skill in job.get('competences', [])]
        
        if not job_skills:
            return 0.5
        
        # Groupes de compétences sémantiques
        skill_groups = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'node'],
            'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes']
        }
        
        total_score = 0
        for job_skill in job_skills:
            best_match = 0
            
            # Correspondance exacte
            if job_skill in cv_skills:
                best_match = 1.0
            else:
                # Correspondance sémantique
                for group_skills in skill_groups.values():
                    if job_skill in group_skills:
                        for cv_skill in cv_skills:
                            if cv_skill in group_skills:
                                best_match = max(best_match, 0.8)
            
            total_score += best_match
        
        return total_score / len(job_skills)
    
    def _get_skills_similarity(self, cv_data: Dict, job: Dict) -> Dict[str, float]:
        """
        Détail de la similarité des compétences
        """
        cv_skills = set(skill.lower() for skill in cv_data.get('competences', []))
        job_skills = set(skill.lower() for skill in job.get('competences', []))
        
        return {
            'exact_matches': len(cv_skills.intersection(job_skills)),
            'total_required': len(job_skills),
            'match_ratio': len(cv_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0,
            'candidate_total': len(cv_skills)
        }
    
    def _basic_fallback(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], limit: int) -> List[Dict]:
        """
        Algorithme de fallback basique
        """
        results = []
        for job in job_data:
            # Score très basique
            cv_skills = set(skill.lower() for skill in cv_data.get('competences', []))
            job_skills = set(skill.lower() for skill in job.get('competences', []))
            
            if job_skills:
                score = len(cv_skills.intersection(job_skills)) / len(job_skills)
            else:
                score = 0.5
            
            job_result = job.copy()
            job_result['matching_score'] = round(score * 100)
            job_result['algorithm_version'] = "fallback-v1.0.0"
            
            results.append(job_result)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results[:limit]
    
    def execute_algorithm(self, algorithm_name: str, cv_data: Dict, questionnaire_data: Dict, 
                         job_data: List[Dict], limit: int = 10) -> Dict[str, Any]:
        """
        Exécute un algorithme spécifique
        """
        if algorithm_name not in self.algorithms:
            available = ", ".join(self.algorithms.keys())
            raise ValueError(f"Algorithme '{algorithm_name}' non disponible. Disponibles: {available}")
        
        start_time = time.time()
        
        try:
            # Statistiques d'usage
            if algorithm_name not in self.usage_stats:
                self.usage_stats[algorithm_name] = {'calls': 0, 'total_time': 0, 'errors': 0}
            
            self.usage_stats[algorithm_name]['calls'] += 1
            
            # Exécution de l'algorithme
            algorithm_info = self.algorithms[algorithm_name]
            result = algorithm_info["function"](cv_data, questionnaire_data, job_data, limit)
            
            execution_time = time.time() - start_time
            self.usage_stats[algorithm_name]['total_time'] += execution_time
            
            return {
                "matches": result,
                "algorithm_used": algorithm_name,
                "algorithm_info": algorithm_info,
                "execution_time": execution_time,
                "success": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.usage_stats[algorithm_name]['errors'] += 1
            
            logger.error(f"Erreur lors de l'exécution de {algorithm_name}: {str(e)}")
            raise
    
    def get_available_algorithms(self) -> List[str]:
        """Retourne la liste des algorithmes disponibles"""
        return list(self.algorithms.keys())
    
    def get_algorithms_info(self) -> List[Dict[str, Any]]:
        """Retourne les informations de tous les algorithmes"""
        result = []
        for name, info in self.algorithms.items():
            algo_info = info.copy()
            algo_info['id'] = name
            
            # Ajout des statistiques d'usage
            if name in self.usage_stats:
                stats = self.usage_stats[name]
                algo_info['performance'] = {
                    'total_calls': stats['calls'],
                    'total_errors': stats['errors'],
                    'avg_execution_time': stats['total_time'] / max(stats['calls'], 1),
                    'error_rate': stats['errors'] / max(stats['calls'], 1)
                }
            else:
                algo_info['performance'] = {
                    'total_calls': 0,
                    'total_errors': 0,
                    'avg_execution_time': 0,
                    'error_rate': 0
                }
            
            result.append(algo_info)
        
        return result
    
    def get_algorithm_info(self, algorithm_name: str) -> Dict[str, Any]:
        """Retourne les informations d'un algorithme spécifique"""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithme '{algorithm_name}' non trouvé")
        
        return self.get_algorithms_info()[self.get_available_algorithms().index(algorithm_name)]
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de tous les algorithmes"""
        health_status = {}
        
        # Données de test simple
        test_cv = {'competences': ['Python'], 'annees_experience': 2}
        test_questionnaire = {'contrats_recherches': ['CDI'], 'adresse': 'Paris'}
        test_jobs = [{'id': 1, 'titre': 'Test', 'competences': ['Python'], 'type_contrat': 'CDI'}]
        
        for name in self.algorithms.keys():
            try:
                result = self.execute_algorithm(name, test_cv, test_questionnaire, test_jobs, 1)
                health_status[name] = {
                    'status': 'healthy',
                    'execution_time': result['execution_time'],
                    'last_check': datetime.now().isoformat()
                }
            except Exception as e:
                health_status[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        return health_status
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'usage globales"""
        total_calls = sum(stats['calls'] for stats in self.usage_stats.values())
        total_errors = sum(stats['errors'] for stats in self.usage_stats.values())
        
        return {
            'total_algorithms': len(self.algorithms),
            'total_calls': total_calls,
            'total_errors': total_errors,
            'global_error_rate': total_errors / max(total_calls, 1),
            'algorithms_stats': self.usage_stats,
            'last_updated': datetime.now().isoformat()
        }
