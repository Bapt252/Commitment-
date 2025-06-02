# SuperSmartMatch V2 - Orchestrateur Principal
# Architecture unifiée avec intégration intelligente de Nexten Matcher
# Suite à l'audit technique révélant la déconnexion critique

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .models import (
    AlgorithmType, MatchingContext, MatchingConfig, 
    DataCompleteness, ProfileType, GeoConstraints
)
from .context_analyzer import ContextAnalyzer
from .smart_algorithm_selector import SmartAlgorithmSelector
from .data_adapter import DataFormatAdapter
from .nexten_adapter import NextenMatcherAdapter
from .performance_monitor import PerformanceMonitor
from .fallback_manager import FallbackManager
from .circuit_breaker import AlgorithmCircuitBreaker, CircuitBreakerOpenException

# Import des algorithmes existants
from ..algorithms.nexten_matcher import NextenMatcher
from ..smartmatch import SmartMatchingEngine
from ..smartmatch_enhanced import EnhancedMatchingEngine
from ..smartmatch_semantic_enhanced import SemanticMatchingEngine

logger = logging.getLogger(__name__)

class SuperSmartMatchV2Orchestrator:
    """
    🚀 ORCHESTRATEUR PRINCIPAL SUPERSMARTMATCH V2
    
    Architecture unifiée qui transforme la déconnexion identifiée dans l'audit
    en avantage concurrentiel en intégrant intelligemment :
    
    - Nexten Matcher (40K lignes) comme algorithme prioritaire
    - Smart, Enhanced, Semantic, Hybrid en fallback intelligent
    - Sélection automatique selon contexte
    - Port 5062 préservé avec backward compatibility
    
    Objectifs selon l'audit :
    - +13% précision grâce à Nexten Matcher prioritaire
    - Réduction 66% services (3→1 unifié)
    - Sélection automatique intelligente
    - <100ms temps de réponse maintenu
    """
    
    def __init__(self):
        # Analyseur de contexte pour sélection intelligente
        self.context_analyzer = ContextAnalyzer()
        
        # Sélecteur d'algorithmes basé sur règles d'audit
        self.algorithm_selector = SmartAlgorithmSelector()
        
        # Adaptateur de formats bidirectionnel
        self.data_adapter = DataFormatAdapter()
        
        # Adaptateur Nexten Matcher (intégration 40K lignes)
        self.nexten_adapter = NextenMatcherAdapter()
        
        # Monitoring des performances par algorithme
        self.performance_monitor = PerformanceMonitor()
        
        # Gestionnaire de fallback hiérarchique
        self.fallback_manager = FallbackManager()
        
        # Circuit breakers pour chaque algorithme
        self.circuit_breakers = {
            AlgorithmType.NEXTEN_MATCHER: AlgorithmCircuitBreaker(),
            AlgorithmType.SMART_MATCH: AlgorithmCircuitBreaker(),
            AlgorithmType.ENHANCED_MATCH: AlgorithmCircuitBreaker(),
            AlgorithmType.SEMANTIC_MATCH: AlgorithmCircuitBreaker(),
            AlgorithmType.HYBRID_MATCH: AlgorithmCircuitBreaker()
        }
        
        # Algorithmes unifiés sous orchestrateur
        self.algorithms = {
            AlgorithmType.NEXTEN_MATCHER: self.nexten_adapter,
            AlgorithmType.SMART_MATCH: SmartMatchingEngine(),
            AlgorithmType.ENHANCED_MATCH: EnhancedMatchingEngine(), 
            AlgorithmType.SEMANTIC_MATCH: SemanticMatchingEngine(),
            AlgorithmType.HYBRID_MATCH: self._create_hybrid_engine()
        }
        
        logger.info("🚀 SuperSmartMatch V2 Orchestrator initialized")
        logger.info("✅ Nexten Matcher integration: ACTIVE (40K lignes)")
        logger.info("✅ Algorithms unified: Nexten, Smart, Enhanced, Semantic, Hybrid")
        logger.info("✅ Port 5062 preserved with backward compatibility")

    async def match_v2(self, 
                      candidate_data: Dict[str, Any],
                      offers_data: List[Dict[str, Any]], 
                      config: MatchingConfig) -> Dict[str, Any]:
        """
        🎯 POINT D'ENTRÉE PRINCIPAL SUPERSMARTMATCH V2
        
        Sélection automatique intelligente d'algorithme selon contexte
        avec priorité Nexten Matcher quand données complètes disponibles
        
        Args:
            candidate_data: Données candidat (format V1 compatible + extensions V2)
            offers_data: Liste des offres à matcher
            config: Configuration matching (algorithm='auto' par défaut)
            
        Returns:
            Réponse unifiée avec métadonnées enrichies
        """
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        try:
            logger.info(f"🔍 [{request_id}] Starting V2 matching - {len(offers_data)} offers")
            
            # 1. ANALYSE DU CONTEXTE pour sélection optimale
            context = self.context_analyzer.analyze(
                candidate_data, offers_data, config
            )
            
            logger.info(f"📊 [{request_id}] Context analyzed - "
                       f"completeness: {context.data_completeness.overall_score:.2f}, "
                       f"complexity: {context.complexity_score:.2f}")
            
            # 2. SÉLECTION AUTOMATIQUE INTELLIGENTE selon règles d'audit
            selected_algorithm = self.algorithm_selector.select(context, config)
            
            logger.info(f"🎯 [{request_id}] Algorithm selected: {selected_algorithm.value}")
            
            # 3. ADAPTATION DES DONNÉES pour algorithme sélectionné
            adapted_candidate, adapted_offers = self.data_adapter.adapt_for_algorithm(
                candidate_data, offers_data, selected_algorithm
            )
            
            # 4. EXÉCUTION AVEC CIRCUIT BREAKER et fallback
            results = await self._execute_matching_with_protection(
                selected_algorithm, adapted_candidate, adapted_offers, 
                config, context, request_id
            )
            
            # 5. POST-PROCESSING et enrichissement
            response = self._build_enriched_response(
                results, context, selected_algorithm, start_time, request_id
            )
            
            # 6. MONITORING des performances
            execution_time = time.time() - start_time
            await self.performance_monitor.track_algorithm_performance(
                selected_algorithm, execution_time, 
                response.get('metadata', {}).get('avg_score', 0), context
            )
            
            logger.info(f"✅ [{request_id}] V2 matching completed - "
                       f"{execution_time*1000:.1f}ms, "
                       f"best_score: {response.get('metadata', {}).get('max_score', 0):.3f}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Error in V2 matching: {str(e)}")
            return await self.fallback_manager.handle_error(
                e, candidate_data, offers_data, config, request_id
            )

    async def _execute_matching_with_protection(self, 
                                              algorithm_type: AlgorithmType,
                                              candidate: Dict[str, Any],
                                              offers: List[Dict[str, Any]], 
                                              config: MatchingConfig,
                                              context: MatchingContext,
                                              request_id: str) -> List[Dict[str, Any]]:
        """
        Exécution protégée avec circuit breaker et fallback automatique
        """
        circuit_breaker = self.circuit_breakers[algorithm_type]
        algorithm = self.algorithms[algorithm_type]
        
        try:
            # Tentative avec circuit breaker
            if algorithm_type == AlgorithmType.NEXTEN_MATCHER:
                # Appel spécial pour Nexten Matcher (40K lignes)
                return await circuit_breaker.call_algorithm(
                    self.nexten_adapter.match, candidate, offers, config
                )
            else:
                # Appel standard pour autres algorithmes
                return await circuit_breaker.call_algorithm(
                    algorithm.match, candidate, offers, config
                )
                
        except CircuitBreakerOpenException:
            logger.warning(f"⚠️  [{request_id}] Circuit breaker OPEN for {algorithm_type.value}")
            return await self.fallback_manager.execute_fallback(
                algorithm_type, candidate, offers, config, context, request_id
            )
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Algorithm {algorithm_type.value} failed: {str(e)}")
            if config.fallback_enabled:
                return await self.fallback_manager.execute_fallback(
                    algorithm_type, candidate, offers, config, context, request_id
                )
            raise e

    def _build_enriched_response(self, 
                               results: List[Dict[str, Any]], 
                               context: MatchingContext,
                               algorithm_used: AlgorithmType,
                               start_time: float,
                               request_id: str) -> Dict[str, Any]:
        """
        Construction de la réponse enrichie avec métadonnées V2
        """
        execution_time = time.time() - start_time
        
        # Calcul des statistiques enrichies
        scores = [result.get('score', 0) for result in results if result.get('score') is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        # Tri intelligent des résultats
        sorted_results = sorted(
            results, 
            key=lambda x: (x.get('score', 0), x.get('confidence', 0)), 
            reverse=True
        )
        
        # Métadonnées enrichies V2
        response = {
            'matches': sorted_results,
            'metadata': {
                # Informations algorithme
                'algorithm_used': algorithm_used.value,
                'algorithm_priority': self._get_algorithm_priority(algorithm_used),
                'nexten_matcher_available': context.data_completeness.overall_score > 0.7,
                
                # Performance
                'execution_time_ms': round(execution_time * 1000, 2),
                'performance_target_met': execution_time < 0.1,  # <100ms
                
                # Statistiques matching
                'total_offers_analyzed': len(results),
                'valid_matches_count': len([r for r in results if r.get('score', 0) > 0.5]),
                'avg_score': round(avg_score, 3),
                'max_score': round(max_score, 3),
                'min_score': round(min_score, 3),
                'score_distribution': self._calculate_score_distribution(scores),
                
                # Analyse contextuelle
                'context_analysis': {
                    'data_completeness_score': context.data_completeness.overall_score,
                    'candidate_questionnaire': context.data_completeness.candidate_questionnaire,
                    'company_questionnaires': context.data_completeness.company_questionnaires,
                    'complexity_score': context.complexity_score,
                    'geo_critical': context.geo_constraints.is_critical,
                    'senior_profile': context.profile_type.experience_years >= 7,
                    'skills_count': context.profile_type.skills_count
                },
                
                # Informations sélection
                'selection_rationale': self._get_selection_rationale(context, algorithm_used),
                'alternative_algorithms': self._get_alternative_algorithms(context),
                
                # Audit compliance
                'audit_objectives': {
                    'precision_improvement_target': '+13%',
                    'service_unification': '3→1 services',
                    'nexten_integration': 'ACTIVE',
                    'backward_compatibility': 'PRESERVED'
                }
            },
            'version': 'v2',
            'request_id': request_id,
            'timestamp': time.time()
        }
        
        return response

    def _get_algorithm_priority(self, algorithm: AlgorithmType) -> str:
        """Retourne la priorité de l'algorithme selon l'audit"""
        priorities = {
            AlgorithmType.NEXTEN_MATCHER: "HIGHEST - Primary algorithm per audit",
            AlgorithmType.ENHANCED_MATCH: "HIGH - Senior profiles",
            AlgorithmType.SMART_MATCH: "HIGH - Geolocation critical",
            AlgorithmType.SEMANTIC_MATCH: "MEDIUM - Semantic analysis",
            AlgorithmType.HYBRID_MATCH: "MEDIUM - Cross validation"
        }
        return priorities.get(algorithm, "STANDARD")

    def _get_selection_rationale(self, context: MatchingContext, algorithm: AlgorithmType) -> str:
        """Explication de la sélection d'algorithme"""
        if algorithm == AlgorithmType.NEXTEN_MATCHER:
            if context.data_completeness.overall_score > 0.7:
                return "Nexten Matcher selected: Complete questionnaire data available (optimal precision)"
            else:
                return "Nexten Matcher selected: Default high-performance algorithm"
        elif algorithm == AlgorithmType.SMART_MATCH:
            return "Smart Match selected: Critical geographical constraints detected"
        elif algorithm == AlgorithmType.ENHANCED_MATCH:
            return "Enhanced Match selected: Senior profile without complete questionnaires"
        elif algorithm == AlgorithmType.SEMANTIC_MATCH:
            return "Semantic Match selected: High skills count requiring semantic analysis"
        elif algorithm == AlgorithmType.HYBRID_MATCH:
            return "Hybrid Match selected: High complexity requiring cross-validation"
        
        return "Standard selection"

    def _get_alternative_algorithms(self, context: MatchingContext) -> List[str]:
        """Algorithmes alternatifs possibles selon le contexte"""
        alternatives = []
        
        if context.data_completeness.overall_score > 0.5:
            alternatives.append("nexten_matcher")
        if context.geo_constraints.is_critical:
            alternatives.append("smart_match")
        if context.profile_type.experience_years >= 7:
            alternatives.append("enhanced_match")
        if context.profile_type.skills_count > 15:
            alternatives.append("semantic_match")
        if context.complexity_score > 0.8:
            alternatives.append("hybrid_match")
            
        return alternatives

    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calcul de la distribution des scores"""
        if not scores:
            return {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for score in scores:
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
                
        return distribution

    def _create_hybrid_engine(self):
        """Création de l'engine hybride combinant plusieurs algorithmes"""
        from .hybrid_engine import HybridMatchingEngine
        return HybridMatchingEngine()

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Status de santé de l'orchestrateur V2
        """
        circuit_breaker_status = {}
        for algo_type, breaker in self.circuit_breakers.items():
            circuit_breaker_status[algo_type.value] = {
                'state': breaker.state,
                'failure_count': breaker.failure_count,
                'last_failure': breaker.last_failure_time
            }
        
        performance_stats = await self.performance_monitor.get_performance_summary()
        
        return {
            'orchestrator': 'SuperSmartMatch V2',
            'status': 'healthy',
            'algorithms_available': list(self.algorithms.keys()),
            'nexten_integration': 'active',
            'circuit_breakers': circuit_breaker_status,
            'performance_stats': performance_stats,
            'version': 'v2.0',
            'audit_compliance': True
        }

    async def force_algorithm(self, 
                            algorithm: AlgorithmType,
                            candidate_data: Dict[str, Any],
                            offers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Force l'utilisation d'un algorithme spécifique (pour tests/debug)
        """
        config = MatchingConfig(algorithm=algorithm.value, fallback_enabled=False)
        return await self.match_v2(candidate_data, offers_data, config)


# Factory pour créer l'orchestrateur
def create_supersmartmatch_v2_orchestrator() -> SuperSmartMatchV2Orchestrator:
    """
    Factory pour créer une instance configurée de l'orchestrateur V2
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = SuperSmartMatchV2Orchestrator()
    
    logger.info("🚀 SuperSmartMatch V2 Orchestrator ready")
    logger.info("📋 Architecture: Unified 5 algorithms under intelligent selector")
    logger.info("🎯 Primary: Nexten Matcher (40K lignes) for maximum precision")
    logger.info("⚡ Performance target: <100ms response time maintained")
    logger.info("🔄 Port 5062 preserved with full backward compatibility")
    
    return orchestrator
