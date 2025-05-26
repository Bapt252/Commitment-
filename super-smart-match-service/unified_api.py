#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Unifiée pour SuperSmartMatch

Interface simplifiée pour accéder à tous les algorithmes de matching :
- Sélection automatique d'algorithme
- Exécution unifiée
- Gestion des erreurs et fallbacks
- Comparaisons d'algorithmes
- Optimisations de performance

Auteur: Nexten Team
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class UnifiedMatchingAPI:
    """
    Interface unifiée pour tous les algorithmes de matching
    """
    
    def __init__(self, algorithm_manager, algorithm_selector):
        self.algorithm_manager = algorithm_manager
        self.algorithm_selector = algorithm_selector
        self.cache = {}  # Cache simple pour les résultats
        self.cache_ttl = 300  # 5 minutes
    
    async def match(self, candidate_data: Dict[str, Any], jobs_data: List[Dict[str, Any]], 
                   algorithm: str = "auto", options: Dict[str, Any] = None, 
                   limit: int = 10) -> Dict[str, Any]:
        """
        Point d'entrée principal pour le matching unifié
        
        Args:
            candidate_data: Données du candidat
            jobs_data: Liste des offres d'emploi
            algorithm: Algorithme à utiliser ('auto' pour sélection automatique)
            options: Options supplémentaires
            limit: Nombre maximum de résultats
        
        Returns:
            Résultats de matching avec métadonnées
        """
        if options is None:
            options = {}
        
        start_time = time.time()
        
        try:
            # Validation des données d'entrée
            self._validate_input(candidate_data, jobs_data, limit)
            
            # Sélection de l'algorithme
            if algorithm == "auto":
                recommendation = self.algorithm_selector.recommend_algorithm(
                    candidate_data, len(jobs_data), options
                )
                selected_algorithm = recommendation['algorithm']
                selection_reason = recommendation['reasoning']
            else:
                selected_algorithm = algorithm
                selection_reason = [f"Algorithme spécifié manuellement: {algorithm}"]
            
            logger.info(f"Algorithme sélectionné: {selected_algorithm} pour {len(jobs_data)} offres")
            
            # Vérification du cache
            cache_key = self._generate_cache_key(candidate_data, jobs_data, selected_algorithm, limit)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info("Résultat retourné depuis le cache")
                cached_result['from_cache'] = True
                return cached_result
            
            # Exécution de l'algorithme
            result = await self._execute_algorithm_safe(
                selected_algorithm, candidate_data, jobs_data, limit, options
            )
            
            # Enrichissement des résultats
            enriched_result = self._enrich_results(
                result, selected_algorithm, selection_reason, 
                candidate_data, jobs_data, start_time
            )
            
            # Mise en cache
            self._cache_result(cache_key, enriched_result)
            
            execution_time = time.time() - start_time
            logger.info(f"Matching terminé en {execution_time:.3f}s avec {selected_algorithm}")
            
            return enriched_result
            
        except Exception as e:
            logger.error(f"Erreur lors du matching unifié: {str(e)}")
            # Tentative de fallback
            return await self._fallback_matching(candidate_data, jobs_data, limit, str(e))
    
    async def compare_all_algorithms(self, candidate_data: Dict[str, Any], 
                                   jobs_data: List[Dict[str, Any]], 
                                   limit: int = 10) -> Dict[str, Any]:
        """
        Compare tous les algorithmes sur le même dataset
        """
        comparison_results = {
            'comparison_timestamp': datetime.now().isoformat(),
            'candidate_profile': {
                'experience': candidate_data.get('annees_experience', 0),
                'skills_count': len(candidate_data.get('competences', [])),
                'location': candidate_data.get('adresse', 'Non spécifié')
            },
            'dataset_info': {
                'total_jobs': len(jobs_data),
                'limit': limit
            },
            'algorithms_results': {},
            'performance_comparison': {},
            'recommendation': None
        }
        
        available_algorithms = self.algorithm_manager.get_available_algorithms()
        
        # Exécution de tous les algorithmes
        for algorithm in available_algorithms:
            try:
                start_time = time.time()
                
                result = await self._execute_algorithm_safe(
                    algorithm, candidate_data, jobs_data, limit, {}
                )
                
                execution_time = time.time() - start_time
                
                # Analyse des résultats
                matches = result.get('matches', [])
                if matches:
                    avg_score = sum(match.get('matching_score', 0) for match in matches) / len(matches)
                    top_score = matches[0].get('matching_score', 0) if matches else 0
                else:
                    avg_score = 0
                    top_score = 0
                
                comparison_results['algorithms_results'][algorithm] = {
                    'matches': matches,
                    'execution_time': round(execution_time, 4),
                    'avg_score': round(avg_score, 1),
                    'top_score': top_score,
                    'results_count': len(matches),
                    'algorithm_info': self.algorithm_manager.get_algorithm_info(algorithm)
                }
                
                comparison_results['performance_comparison'][algorithm] = {
                    'speed_rank': 0,  # À calculer après
                    'accuracy_rank': 0,  # À calculer après
                    'avg_score': round(avg_score, 1),
                    'execution_time': round(execution_time, 4)
                }
                
            except Exception as e:
                logger.error(f"Erreur avec l'algorithme {algorithm}: {str(e)}")
                comparison_results['algorithms_results'][algorithm] = {
                    'error': str(e),
                    'execution_time': None,
                    'avg_score': None,
                    'top_score': None,
                    'results_count': 0
                }
        
        # Calcul des rangs
        self._calculate_performance_ranks(comparison_results['performance_comparison'])
        
        # Recommandation basée sur les résultats
        comparison_results['recommendation'] = self._recommend_best_from_comparison(
            comparison_results['performance_comparison']
        )
        
        return comparison_results
    
    def _validate_input(self, candidate_data: Dict[str, Any], jobs_data: List[Dict[str, Any]], 
                       limit: int) -> None:
        """
        Valide les données d'entrée
        """
        if not candidate_data:
            raise ValueError("Données candidat manquantes")
        
        if not jobs_data:
            raise ValueError("Aucune offre d'emploi fournie")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limite doit être entre 1 et 100")
        
        # Validation des champs requis du candidat
        required_fields = ['competences']
        for field in required_fields:
            if field not in candidate_data:
                logger.warning(f"Champ candidat manquant: {field}")
        
        # Validation des offres
        for i, job in enumerate(jobs_data):
            if 'id' not in job:
                job['id'] = i + 1  # Ajouter un ID si manquant
            if 'titre' not in job:
                logger.warning(f"Titre manquant pour l'offre {job.get('id', i)}")
    
    async def _execute_algorithm_safe(self, algorithm: str, candidate_data: Dict[str, Any], 
                                    jobs_data: List[Dict[str, Any]], limit: int, 
                                    options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute un algorithme avec gestion d'erreur sécurisée
        """
        try:
            # Conversion du format pour compatibilité avec les algorithmes existants
            cv_data = {
                'competences': candidate_data.get('competences', []),
                'annees_experience': candidate_data.get('annees_experience', 0),
                'formation': candidate_data.get('formation', '')
            }
            
            questionnaire_data = {
                'contrats_recherches': candidate_data.get('contrats_recherches', ['CDI']),
                'adresse': candidate_data.get('adresse', ''),
                'salaire_min': candidate_data.get('salaire_souhaite', 0),
                'date_disponibilite': candidate_data.get('date_disponibilite'),
                'temps_trajet_max': candidate_data.get('temps_trajet_max', 60)
            }
            
            # Exécution de l'algorithme
            result = self.algorithm_manager.execute_algorithm(
                algorithm, cv_data, questionnaire_data, jobs_data, limit
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de {algorithm}: {str(e)}")
            raise
    
    async def _fallback_matching(self, candidate_data: Dict[str, Any], 
                               jobs_data: List[Dict[str, Any]], limit: int, 
                               error_message: str) -> Dict[str, Any]:
        """
        Matching de fallback en cas d'erreur
        """
        logger.warning("Activation du mode fallback")
        
        try:
            # Tentative avec l'algorithme original (plus stable)
            if 'original' in self.algorithm_manager.get_available_algorithms():
                result = await self._execute_algorithm_safe(
                    'original', candidate_data, jobs_data, limit, {}
                )
                
                result['fallback_used'] = True
                result['original_error'] = error_message
                result['algorithm_used'] = 'original (fallback)'
                
                return result
            else:
                # Matching très basique en dernier recours
                return self._basic_fallback_matching(candidate_data, jobs_data, limit, error_message)
                
        except Exception as fallback_error:
            logger.error(f"Erreur même en mode fallback: {str(fallback_error)}")
            return self._basic_fallback_matching(candidate_data, jobs_data, limit, str(fallback_error))
    
    def _basic_fallback_matching(self, candidate_data: Dict[str, Any], 
                               jobs_data: List[Dict[str, Any]], limit: int, 
                               error_message: str) -> Dict[str, Any]:
        """
        Matching de base en cas d'échec total
        """
        logger.warning("Utilisation du matching de base (fallback final)")
        
        candidate_skills = set(skill.lower() for skill in candidate_data.get('competences', []))
        
        results = []
        for job in jobs_data:
            job_skills = set(skill.lower() for skill in job.get('competences', []))
            
            # Score basique basé sur les compétences
            if job_skills:
                score = len(candidate_skills.intersection(job_skills)) / len(job_skills)
            else:
                score = 0.5
            
            job_result = job.copy()
            job_result['matching_score'] = round(score * 100)
            job_result['algorithm_version'] = 'basic-fallback-v1.0.0'
            
            results.append(job_result)
        
        # Tri par score
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return {
            'matches': results[:limit],
            'algorithm_used': 'basic-fallback',
            'success': True,
            'fallback_used': True,
            'error_message': error_message,
            'warning': 'Résultats générés par l\'algorithme de fallback basique'
        }
    
    def _enrich_results(self, result: Dict[str, Any], algorithm: str, 
                       selection_reason: List[str], candidate_data: Dict[str, Any], 
                       jobs_data: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
        """
        Enrichit les résultats avec des métadonnées supplémentaires
        """
        enriched = result.copy()
        
        # Métadonnées de l'exécution
        enriched.update({
            'algorithm_used': algorithm,
            'selection_reason': selection_reason,
            'processing_metadata': {
                'total_execution_time': round(time.time() - start_time, 4),
                'algorithm_execution_time': result.get('execution_time', 0),
                'jobs_analyzed': len(jobs_data),
                'results_returned': len(result.get('matches', [])),
                'timestamp': datetime.now().isoformat()
            },
            'candidate_summary': {
                'experience_years': candidate_data.get('annees_experience', 0),
                'skills_count': len(candidate_data.get('competences', [])),
                'location': candidate_data.get('adresse', 'Non spécifié'),
                'contracts_sought': candidate_data.get('contrats_recherches', [])
            },
            'quality_metrics': self._calculate_quality_metrics(result.get('matches', []))
        })
        
        return enriched
    
    def _calculate_quality_metrics(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule des métriques de qualité des résultats
        """
        if not matches:
            return {
                'avg_score': 0,
                'score_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0},
                'score_variance': 0
            }
        
        scores = [match.get('matching_score', 0) for match in matches]
        avg_score = sum(scores) / len(scores)
        
        # Distribution des scores
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        for score in scores:
            if score >= 80:
                distribution['excellent'] += 1
            elif score >= 60:
                distribution['good'] += 1
            elif score >= 40:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        # Variance
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores) if len(scores) > 1 else 0
        
        return {
            'avg_score': round(avg_score, 1),
            'score_distribution': distribution,
            'score_variance': round(variance, 1),
            'top_score': max(scores),
            'min_score': min(scores)
        }
    
    def _generate_cache_key(self, candidate_data: Dict[str, Any], 
                          jobs_data: List[Dict[str, Any]], algorithm: str, limit: int) -> str:
        """
        Génère une clé de cache pour les résultats
        """
        # Simplification pour éviter les clés trop longues
        candidate_hash = hash((
            tuple(sorted(candidate_data.get('competences', []))),
            candidate_data.get('annees_experience', 0),
            candidate_data.get('adresse', '')
        ))
        
        jobs_hash = hash(tuple(
            (job.get('id', i), tuple(sorted(job.get('competences', [])))) 
            for i, job in enumerate(jobs_data)
        ))
        
        return f"{algorithm}_{candidate_hash}_{jobs_hash}_{limit}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un résultat du cache s'il est valide
        """
        if cache_key in self.cache:
            cached_entry = self.cache[cache_key]
            if time.time() - cached_entry['timestamp'] < self.cache_ttl:
                return cached_entry['result']
            else:
                # Suppression du cache expiré
                del self.cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        Met en cache un résultat
        """
        # Nettoyage du cache si trop volumineux
        if len(self.cache) > 100:
            # Supprimer les 20 entrées les plus anciennes
            oldest_keys = sorted(self.cache.keys(), 
                               key=lambda k: self.cache[k]['timestamp'])[:20]
            for key in oldest_keys:
                del self.cache[key]
        
        self.cache[cache_key] = {
            'timestamp': time.time(),
            'result': result
        }
    
    def _calculate_performance_ranks(self, performance_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Calcule les rangs de performance
        """
        algorithms = list(performance_data.keys())
        
        # Rang par vitesse (temps d'exécution croissant)
        speed_sorted = sorted(algorithms, 
                            key=lambda a: performance_data[a].get('execution_time', float('inf')))
        for i, algo in enumerate(speed_sorted):
            if algo in performance_data:
                performance_data[algo]['speed_rank'] = i + 1
        
        # Rang par précision (score moyen décroissant)
        accuracy_sorted = sorted(algorithms, 
                               key=lambda a: performance_data[a].get('avg_score', 0), 
                               reverse=True)
        for i, algo in enumerate(accuracy_sorted):
            if algo in performance_data:
                performance_data[algo]['accuracy_rank'] = i + 1
    
    def _recommend_best_from_comparison(self, performance_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommande le meilleur algorithme basé sur la comparaison
        """
        if not performance_data:
            return {'algorithm': 'enhanced', 'reason': 'Algorithme par défaut'}
        
        # Score composite : vitesse + précision
        best_algorithm = None
        best_score = -1
        
        for algo, data in performance_data.items():
            if data.get('avg_score') is not None and data.get('execution_time') is not None:
                # Score composite (privilégie la précision)
                composite_score = (
                    data['avg_score'] * 0.7 +  # 70% précision
                    (10 - data['speed_rank']) * 3  # 30% vitesse (rang inversé)
                )
                
                if composite_score > best_score:
                    best_score = composite_score
                    best_algorithm = algo
        
        if best_algorithm:
            return {
                'algorithm': best_algorithm,
                'reason': f"Meilleur score composite ({round(best_score, 1)})",
                'avg_score': performance_data[best_algorithm]['avg_score'],
                'speed_rank': performance_data[best_algorithm]['speed_rank'],
                'accuracy_rank': performance_data[best_algorithm]['accuracy_rank']
            }
        else:
            return {'algorithm': 'enhanced', 'reason': 'Aucun algorithme valide trouvé, utilisation par défaut'}
