# Fallback Manager - Gestionnaire de Fallback Hiérarchique
# Système de fallback intelligent pour robustesse maximale

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from .models import (
    AlgorithmType, MatchingContext, MatchingConfig
)

logger = logging.getLogger(__name__)

class FallbackManager:
    """
    🛡️ GESTIONNAIRE DE FALLBACK HIÉRARCHIQUE SUPERSMARTMATCH V2
    
    Système de fallback intelligent pour assurer la robustesse maximale
    du service même en cas de défaillance d'algorithmes.
    
    HIÉRARCHIE DE FALLBACK (selon audit) :
    1. NEXTEN MATCHER → ENHANCED MATCH → SMART MATCH → MINIMAL
    2. ENHANCED MATCH → SMART MATCH → SEMANTIC MATCH → MINIMAL  
    3. SMART MATCH → SEMANTIC MATCH → NEXTEN MATCH → MINIMAL
    4. SEMANTIC MATCH → ENHANCED MATCH → SMART MATCH → MINIMAL
    5. HYBRID MATCH → NEXTEN MATCHER → ENHANCED MATCH → MINIMAL
    
    Objectifs :
    - Disponibilité 99.9% même avec défaillances
    - Dégradation gracieuse des performances
    - Réponse toujours fournie (fallback minimal)
    - Monitoring et alerting automatique
    """
    
    def __init__(self):
        # Hiérarchie de fallback optimisée selon l'audit
        self.fallback_hierarchy = {
            AlgorithmType.NEXTEN_MATCHER: [
                AlgorithmType.ENHANCED_MATCH,  # Meilleure alternative
                AlgorithmType.SMART_MATCH,     # Si geo contraintes
                AlgorithmType.SEMANTIC_MATCH   # Analyse compétences
            ],
            AlgorithmType.ENHANCED_MATCH: [
                AlgorithmType.SMART_MATCH,     # Compatible profils seniors
                AlgorithmType.SEMANTIC_MATCH,  # Analyse compétences
                AlgorithmType.NEXTEN_MATCHER   # Si récupération
            ],
            AlgorithmType.SMART_MATCH: [
                AlgorithmType.SEMANTIC_MATCH,  # Analyse alternative
                AlgorithmType.ENHANCED_MATCH,  # Si profil senior
                AlgorithmType.NEXTEN_MATCHER   # Si questionnaires
            ],
            AlgorithmType.SEMANTIC_MATCH: [
                AlgorithmType.ENHANCED_MATCH,  # Pondération adaptative
                AlgorithmType.SMART_MATCH,     # Géolocalisation
                AlgorithmType.NEXTEN_MATCHER   # Si données complètes
            ],
            AlgorithmType.HYBRID_MATCH: [
                AlgorithmType.NEXTEN_MATCHER,  # Retour au principal
                AlgorithmType.ENHANCED_MATCH,  # Pondération senior
                AlgorithmType.SMART_MATCH      # Géo backup
            ]
        }
        
        # Statistiques de fallback
        self.fallback_stats = {
            'total_fallbacks': 0,
            'successful_fallbacks': 0,
            'minimal_responses': 0,
            'algorithm_failures': {algo: 0 for algo in AlgorithmType}
        }
        
        # Configuration fallback
        self.fallback_config = {
            'max_fallback_attempts': 3,
            'fallback_timeout': 5.0,  # secondes
            'minimal_score_base': 0.3,
            'degraded_confidence': 0.6
        }
        
        logger.info("🛡️ Fallback Manager initialized with hierarchical strategy")

    async def execute_fallback(self,
                             failed_algorithm: AlgorithmType,
                             candidate: Dict[str, Any],
                             offers: List[Dict[str, Any]],
                             config: MatchingConfig,
                             context: MatchingContext,
                             request_id: str) -> List[Dict[str, Any]]:
        """
        🚀 EXÉCUTION DU FALLBACK HIÉRARCHIQUE
        
        Essaie les algorithmes de fallback dans l'ordre hiérarchique
        jusqu'à obtenir une réponse ou fallback minimal.
        
        Args:
            failed_algorithm: Algorithme qui a échoué
            candidate: Données candidat
            offers: Liste des offres
            config: Configuration matching
            context: Contexte analysé
            request_id: ID de la requête pour tracking
            
        Returns:
            Liste des résultats de matching (garantie non-vide)
        """
        
        self.fallback_stats['total_fallbacks'] += 1
        self.fallback_stats['algorithm_failures'][failed_algorithm] += 1
        
        logger.warning(f"🔄 [{request_id}] Starting fallback for {failed_algorithm.value}")
        
        fallback_options = self.fallback_hierarchy.get(failed_algorithm, [])
        
        # Tentative de fallback hiérarchique
        for attempt, fallback_algorithm in enumerate(fallback_options):
            if attempt >= self.fallback_config['max_fallback_attempts']:
                logger.warning(f"⚠️ [{request_id}] Max fallback attempts reached")
                break
                
            try:
                logger.info(f"🔄 [{request_id}] Attempting fallback: "
                           f"{failed_algorithm.value} → {fallback_algorithm.value}")
                
                # Exécution avec timeout
                results = await asyncio.wait_for(
                    self._execute_fallback_algorithm(
                        fallback_algorithm, candidate, offers, config, context, request_id
                    ),
                    timeout=self.fallback_config['fallback_timeout']
                )
                
                if results and len(results) > 0:
                    logger.info(f"✅ [{request_id}] Fallback successful: {fallback_algorithm.value}")
                    self.fallback_stats['successful_fallbacks'] += 1
                    
                    # Marquer les résultats comme fallback
                    return self._mark_as_fallback(results, failed_algorithm, fallback_algorithm)
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ [{request_id}] Fallback timeout: {fallback_algorithm.value}")
                continue
                
            except Exception as e:
                logger.warning(f"❌ [{request_id}] Fallback failed {fallback_algorithm.value}: {str(e)}")
                continue
        
        # Si tous les fallbacks échouent → réponse minimale garantie
        logger.warning(f"🆘 [{request_id}] All fallbacks failed, generating minimal response")
        self.fallback_stats['minimal_responses'] += 1
        
        return self._create_minimal_response(offers, failed_algorithm, request_id)

    async def _execute_fallback_algorithm(self,
                                        algorithm: AlgorithmType,
                                        candidate: Dict[str, Any],
                                        offers: List[Dict[str, Any]],
                                        config: MatchingConfig,
                                        context: MatchingContext,
                                        request_id: str) -> List[Dict[str, Any]]:
        """
        Exécution d'un algorithme de fallback spécifique
        """
        
        # Import dynamique pour éviter les dépendances circulaires
        if algorithm == AlgorithmType.NEXTEN_MATCHER:
            from .nexten_adapter import NextenMatcherAdapter
            adapter = NextenMatcherAdapter()
            return await adapter.match(candidate, offers, config)
            
        elif algorithm == AlgorithmType.SMART_MATCH:
            return await self._execute_smart_match_fallback(candidate, offers, config)
            
        elif algorithm == AlgorithmType.ENHANCED_MATCH:
            return await self._execute_enhanced_match_fallback(candidate, offers, config, context)
            
        elif algorithm == AlgorithmType.SEMANTIC_MATCH:
            return await self._execute_semantic_match_fallback(candidate, offers, config)
            
        elif algorithm == AlgorithmType.HYBRID_MATCH:
            return await self._execute_hybrid_match_fallback(candidate, offers, config, context)
        
        else:
            raise ValueError(f"Unknown fallback algorithm: {algorithm}")

    async def _execute_smart_match_fallback(self,
                                          candidate: Dict[str, Any],
                                          offers: List[Dict[str, Any]],
                                          config: MatchingConfig) -> List[Dict[str, Any]]:
        """Fallback Smart Match simplifié"""
        results = []
        
        candidate_location = candidate.get('profile', {}).get('location', {})
        candidate_skills = candidate.get('profile', {}).get('skills', [])
        
        for i, offer in enumerate(offers):
            offer_location = offer.get('job_data', {}).get('location', {})
            offer_skills = offer.get('job_data', {}).get('skills_required', [])
            
            # Score géographique simplifié
            geo_score = 0.8 if offer_location.get('remote_work', False) else 0.6
            
            # Score compétences basique
            if candidate_skills and offer_skills:
                skill_matches = len(set(candidate_skills) & set(offer_skills))
                skills_score = min(skill_matches / max(len(offer_skills), 1), 1.0)
            else:
                skills_score = 0.5
            
            # Score composite
            final_score = (geo_score * 0.4) + (skills_score * 0.6)
            
            results.append({
                'offer_id': offer.get('job_data', {}).get('id', f'offer_{i}'),
                'company_id': offer.get('company_id', f'company_{i}'),
                'score': round(final_score, 3),
                'confidence': 0.7,  # Confiance réduite pour fallback
                'algorithm_used': 'smart_match_fallback',
                'match_details': {
                    'geo_score': geo_score,
                    'skills_score': skills_score,
                    'fallback_mode': True
                }
            })
        
        return results

    async def _execute_enhanced_match_fallback(self,
                                             candidate: Dict[str, Any],
                                             offers: List[Dict[str, Any]],
                                             config: MatchingConfig,
                                             context: MatchingContext) -> List[Dict[str, Any]]:
        """Fallback Enhanced Match avec pondération expérience"""
        results = []
        
        experience_years = context.profile_type.experience_years
        seniority_level = context.profile_type.seniority_level
        
        # Bonus séniorité
        seniority_bonus = {
            'junior': 0.0,
            'mid': 0.1,
            'senior': 0.2,
            'expert': 0.3
        }.get(seniority_level, 0.0)
        
        for i, offer in enumerate(offers):
            job_data = offer.get('job_data', {})
            required_experience = job_data.get('experience_required', 0)
            
            # Score expérience pondéré
            if experience_years >= required_experience:
                experience_score = 0.9 + seniority_bonus
            else:
                experience_score = max(0.3, experience_years / max(required_experience, 1))
            
            # Score de base
            base_score = 0.6 + (experience_score * 0.4)
            
            results.append({
                'offer_id': job_data.get('id', f'offer_{i}'),
                'company_id': offer.get('company_id', f'company_{i}'),
                'score': round(min(base_score, 1.0), 3),
                'confidence': 0.75,
                'algorithm_used': 'enhanced_match_fallback',
                'match_details': {
                    'experience_score': experience_score,
                    'seniority_bonus': seniority_bonus,
                    'fallback_mode': True
                }
            })
        
        return results

    async def _execute_semantic_match_fallback(self,
                                             candidate: Dict[str, Any],
                                             offers: List[Dict[str, Any]],
                                             config: MatchingConfig) -> List[Dict[str, Any]]:
        """Fallback Semantic Match simplifié"""
        results = []
        
        candidate_skills = candidate.get('profile', {}).get('skills', [])
        candidate_text = ' '.join([
            candidate.get('profile', {}).get('cv_data', {}).get('summary', ''),
            ' '.join(candidate_skills)
        ]).lower()
        
        for i, offer in enumerate(offers):
            job_data = offer.get('job_data', {})
            offer_text = ' '.join([
                job_data.get('title', ''),
                job_data.get('description', ''),
                ' '.join(job_data.get('skills_required', []))
            ]).lower()
            
            # Analyse sémantique très basique (mots-clés)
            candidate_words = set(candidate_text.split())
            offer_words = set(offer_text.split())
            
            if candidate_words and offer_words:
                overlap = len(candidate_words & offer_words)
                semantic_score = min(overlap / max(len(offer_words), 10), 1.0)
            else:
                semantic_score = 0.4
            
            results.append({
                'offer_id': job_data.get('id', f'offer_{i}'),
                'company_id': offer.get('company_id', f'company_{i}'),
                'score': round(semantic_score, 3),
                'confidence': 0.65,
                'algorithm_used': 'semantic_match_fallback',
                'match_details': {
                    'semantic_score': semantic_score,
                    'word_overlap': len(candidate_words & offer_words) if candidate_words and offer_words else 0,
                    'fallback_mode': True
                }
            })
        
        return results

    async def _execute_hybrid_match_fallback(self,
                                           candidate: Dict[str, Any],
                                           offers: List[Dict[str, Any]],
                                           config: MatchingConfig,
                                           context: MatchingContext) -> List[Dict[str, Any]]:
        """Fallback Hybrid Match - consensus simplifié"""
        
        # Exécution de 2-3 algorithmes simples
        smart_results = await self._execute_smart_match_fallback(candidate, offers, config)
        enhanced_results = await self._execute_enhanced_match_fallback(candidate, offers, config, context)
        
        # Consensus des scores
        results = []
        for i in range(len(offers)):
            smart_score = smart_results[i]['score'] if i < len(smart_results) else 0.3
            enhanced_score = enhanced_results[i]['score'] if i < len(enhanced_results) else 0.3
            
            # Score consensus pondéré
            consensus_score = (smart_score * 0.5) + (enhanced_score * 0.5)
            consensus_confidence = 0.8  # Hybride augmente confiance
            
            results.append({
                'offer_id': offers[i].get('job_data', {}).get('id', f'offer_{i}'),
                'company_id': offers[i].get('company_id', f'company_{i}'),
                'score': round(consensus_score, 3),
                'confidence': consensus_confidence,
                'algorithm_used': 'hybrid_match_fallback',
                'match_details': {
                    'smart_score': smart_score,
                    'enhanced_score': enhanced_score,
                    'consensus_score': consensus_score,
                    'fallback_mode': True
                }
            })
        
        return results

    def _create_minimal_response(self,
                               offers: List[Dict[str, Any]],
                               failed_algorithm: AlgorithmType,
                               request_id: str) -> List[Dict[str, Any]]:
        """
        🆘 RÉPONSE MINIMALE GARANTIE
        
        Génère une réponse minimale mais cohérente quand tous les algorithmes échouent.
        Assure qu'une réponse est toujours fournie pour éviter les erreurs côté client.
        """
        
        logger.warning(f"🆘 [{request_id}] Creating minimal response for {len(offers)} offers")
        
        results = []
        base_score = self.fallback_config['minimal_score_base']
        
        for i, offer in enumerate(offers):
            # Score minimal dégradé mais cohérent
            # Légère variation pour éviter ex-aequo total
            minimal_score = base_score + (i * 0.001)
            
            results.append({
                'offer_id': offer.get('job_data', {}).get('id', f'minimal_offer_{i}'),
                'company_id': offer.get('company_id', f'minimal_company_{i}'),
                'score': round(minimal_score, 3),
                'confidence': self.fallback_config['degraded_confidence'],
                'algorithm_used': 'minimal_fallback',
                'match_details': {
                    'minimal_response': True,
                    'original_algorithm_failed': failed_algorithm.value,
                    'all_fallbacks_failed': True,
                    'score_type': 'degraded_minimal'
                },
                'warning': 'This is a degraded response due to system issues'
            })
        
        return results

    def _mark_as_fallback(self,
                         results: List[Dict[str, Any]],
                         original_algorithm: AlgorithmType,
                         fallback_algorithm: AlgorithmType) -> List[Dict[str, Any]]:
        """
        Marque les résultats comme provenant d'un fallback
        """
        for result in results:
            result['fallback_info'] = {
                'is_fallback': True,
                'original_algorithm': original_algorithm.value,
                'fallback_algorithm': fallback_algorithm.value,
                'degraded_service': True
            }
            
            # Réduction légère de la confiance pour fallback
            if 'confidence' in result:
                result['confidence'] = max(0.1, result['confidence'] * 0.9)
        
        return results

    async def handle_error(self,
                          error: Exception,
                          candidate_data: Dict[str, Any],
                          offers_data: List[Dict[str, Any]],
                          config: MatchingConfig,
                          request_id: str = None) -> Dict[str, Any]:
        """
        🚨 GESTION D'ERREUR GLOBALE
        
        Gère les erreurs non récupérables et fournit une réponse d'urgence.
        """
        
        if not request_id:
            request_id = f"error_{int(time.time() * 1000)}"
        
        logger.error(f"🚨 [{request_id}] Global error handler: {str(error)}")
        
        # Tentative de réponse minimale d'urgence
        try:
            minimal_results = self._create_emergency_response(offers_data, error, request_id)
            
            return {
                'matches': minimal_results,
                'metadata': {
                    'algorithm_used': 'emergency_fallback',
                    'execution_time_ms': 0,
                    'total_offers_analyzed': len(offers_data),
                    'error_mode': True,
                    'error_type': type(error).__name__,
                    'fallback_level': 'emergency'
                },
                'version': 'v2',
                'request_id': request_id,
                'timestamp': time.time(),
                'status': 'degraded',
                'warning': 'Service temporarily degraded due to system error'
            }
            
        except Exception as emergency_error:
            logger.critical(f"💥 [{request_id}] Emergency fallback failed: {str(emergency_error)}")
            
            # Réponse absolue d'urgence
            return {
                'matches': [],
                'metadata': {
                    'algorithm_used': 'critical_fallback',
                    'error_mode': True,
                    'critical_failure': True
                },
                'version': 'v2',
                'request_id': request_id,
                'timestamp': time.time(),
                'status': 'critical_error',
                'error': 'Critical system failure - no results available'
            }

    def _create_emergency_response(self,
                                 offers: List[Dict[str, Any]],
                                 error: Exception,
                                 request_id: str) -> List[Dict[str, Any]]:
        """Réponse d'urgence absolue"""
        
        return [
            {
                'offer_id': offer.get('job_data', {}).get('id', f'emergency_{i}'),
                'company_id': offer.get('company_id', f'emergency_company_{i}'),
                'score': 0.2,  # Score très bas pour signaler le problème
                'confidence': 0.1,
                'algorithm_used': 'emergency_response',
                'match_details': {
                    'emergency_mode': True,
                    'error_type': type(error).__name__,
                    'warning': 'Emergency response due to system failure'
                }
            }
            for i, offer in enumerate(offers[:10])  # Limite à 10 pour sécurité
        ]

    def get_fallback_analytics(self) -> Dict[str, Any]:
        """
        📊 ANALYTICS DU SYSTÈME DE FALLBACK
        
        Statistiques pour monitoring et amélioration continue.
        """
        total_fallbacks = self.fallback_stats['total_fallbacks']
        
        if total_fallbacks == 0:
            return {"message": "No fallbacks recorded yet"}
        
        success_rate = (self.fallback_stats['successful_fallbacks'] / total_fallbacks) * 100
        minimal_rate = (self.fallback_stats['minimal_responses'] / total_fallbacks) * 100
        
        return {
            'fallback_overview': {
                'total_fallback_attempts': total_fallbacks,
                'successful_fallbacks': self.fallback_stats['successful_fallbacks'],
                'minimal_responses': self.fallback_stats['minimal_responses'],
                'success_rate': f"{success_rate:.1f}%",
                'minimal_response_rate': f"{minimal_rate:.1f}%"
            },
            'algorithm_reliability': {
                algo.value: {
                    'failures': self.fallback_stats['algorithm_failures'][algo],
                    'reliability_score': max(0, 100 - (self.fallback_stats['algorithm_failures'][algo] * 10))
                }
                for algo in AlgorithmType
            },
            'fallback_hierarchy': {
                algo.value: [fallback.value for fallback in fallbacks]
                for algo, fallbacks in self.fallback_hierarchy.items()
            },
            'recommendations': self._get_fallback_recommendations()
        }

    def _get_fallback_recommendations(self) -> List[str]:
        """Recommandations d'amélioration du système de fallback"""
        recommendations = []
        
        total_failures = sum(self.fallback_stats['algorithm_failures'].values())
        if total_failures == 0:
            return ["✅ No reliability issues detected"]
        
        # Analyse des patterns de défaillance
        for algo, failures in self.fallback_stats['algorithm_failures'].items():
            if failures > 5:
                recommendations.append(f"🔧 {algo.value}: {failures} failures - needs investigation")
        
        if self.fallback_stats['minimal_responses'] > self.fallback_stats['total_fallbacks'] * 0.3:
            recommendations.append("⚠️ High minimal response rate - consider improving fallback algorithms")
        
        if self.fallback_stats['successful_fallbacks'] < self.fallback_stats['total_fallbacks'] * 0.7:
            recommendations.append("📈 Low fallback success rate - review fallback hierarchy")
        
        return recommendations if recommendations else ["✅ Fallback system operating normally"]

    def reset_stats(self):
        """Reset des statistiques pour nouveau cycle de monitoring"""
        self.fallback_stats = {
            'total_fallbacks': 0,
            'successful_fallbacks': 0,
            'minimal_responses': 0,
            'algorithm_failures': {algo: 0 for algo in AlgorithmType}
        }
        logger.info("📊 Fallback statistics reset")
