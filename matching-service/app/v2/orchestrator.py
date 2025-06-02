"""
SuperSmartMatch V2 - Orchestrateur Principal Unifié
===================================================

Orchestrateur qui unifie intelligemment tous les algorithmes de matching
pour maximiser la précision selon le contexte des données disponibles.

Fonctionnalités:
- Sélection automatique d'algorithme (SmartAlgorithmSelector)
- Intégration Nexten Matcher comme algorithme principal
- Fallback hiérarchique avec circuit breakers
- Monitoring et métriques en temps réel
- Compatibilité backward complète V1
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# MODELS DE DONNÉES V2
# ================================

@dataclass
class MatchingRequestV2:
    """Requête V2 étendue avec support questionnaires"""
    candidate_data: Dict[str, Any]
    candidate_questionnaire: Optional[Dict[str, Any]] = None
    offers_data: List[Dict[str, Any]] = None
    company_questionnaires: Optional[List[Dict[str, Any]]] = None
    algorithm: str = "auto"
    version: str = "v2"
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.offers_data is None:
            self.offers_data = []
        if self.options is None:
            self.options = {}

@dataclass
class MatchingResult:
    """Résultat unifié de matching avec métadonnées enrichies"""
    offer_id: str
    score: float
    confidence: float
    algorithm_used: str
    match_details: Dict[str, Any]
    explanation: str
    processing_time_ms: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MatchingResponse:
    """Réponse complète avec contexte et métriques"""
    results: List[MatchingResult]
    total_processing_time_ms: float
    algorithm_selection_reason: str
    context_analysis: Dict[str, Any]
    version: str = "v2"
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}

@dataclass
class MatchingContext:
    """Contexte d'analyse pour la sélection d'algorithme"""
    has_candidate_questionnaire: bool
    has_company_questionnaires: bool
    skills_count: int
    experience_years: int
    mobility_type: str
    has_geo_constraints: bool
    requires_semantic_analysis: bool = False
    requires_validation: bool = False
    has_partial_questionnaires: bool = False
    data_quality_score: float = 0.0

# ================================
# CIRCUIT BREAKER POUR RÉSILIENCE
# ================================

class AlgorithmCircuitBreaker:
    """Protection contre les défaillances d'algorithmes"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_counts = defaultdict(int)
        self.last_failure = defaultdict(float)
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_counts = defaultdict(int)
    
    def is_available(self, algorithm_name: str) -> bool:
        """Vérifie si l'algorithme est disponible"""
        now = time.time()
        if self.failure_counts[algorithm_name] >= self.failure_threshold:
            if now - self.last_failure[algorithm_name] > self.timeout:
                # Reset après timeout
                self.failure_counts[algorithm_name] = 0
                logger.info(f"Circuit breaker reset pour {algorithm_name}")
                return True
            logger.warning(f"Circuit breaker ouvert pour {algorithm_name}")
            return False
        return True
    
    def record_failure(self, algorithm_name: str):
        """Enregistre un échec d'algorithme"""
        self.failure_counts[algorithm_name] += 1
        self.last_failure[algorithm_name] = time.time()
        logger.warning(f"Échec algorithme {algorithm_name} (total: {self.failure_counts[algorithm_name]})")
    
    def record_success(self, algorithm_name: str):
        """Enregistre un succès (reset partiel)"""
        self.success_counts[algorithm_name] += 1
        if self.failure_counts[algorithm_name] > 0:
            self.failure_counts[algorithm_name] = max(0, self.failure_counts[algorithm_name] - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du circuit breaker"""
        return {
            'failure_counts': dict(self.failure_counts),
            'success_counts': dict(self.success_counts),
            'availability': {
                algo: self.is_available(algo) 
                for algo in set(list(self.failure_counts.keys()) + list(self.success_counts.keys()))
            }
        }

# ================================
# COLLECTEUR DE MÉTRIQUES
# ================================

class MetricsCollector:
    """Collecteur de métriques pour monitoring et optimisation"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.success_rates = defaultdict(list)
        self.algorithm_selections = defaultdict(int)
        self.precision_scores = defaultdict(list)
        
        # Limite de rétention des métriques
        self.max_metrics_history = 1000
    
    def record_request(self, algorithm: str, response_time_ms: float, 
                      result_count: int, success: bool = True, precision: float = None):
        """Enregistre une requête pour monitoring"""
        self.request_counts[algorithm] += 1
        self.response_times[algorithm].append(response_time_ms)
        self.success_rates[algorithm].append(1.0 if success else 0.0)
        self.algorithm_selections[algorithm] += 1
        
        if precision is not None:
            self.precision_scores[algorithm].append(precision)
        
        # Nettoyage automatique pour éviter la surcharge mémoire
        self._cleanup_old_metrics(algorithm)
    
    def _cleanup_old_metrics(self, algorithm: str):
        """Nettoie les anciennes métriques pour optimiser la mémoire"""
        if len(self.response_times[algorithm]) > self.max_metrics_history:
            self.response_times[algorithm] = self.response_times[algorithm][-self.max_metrics_history:]
            self.success_rates[algorithm] = self.success_rates[algorithm][-self.max_metrics_history:]
            self.precision_scores[algorithm] = self.precision_scores[algorithm][-self.max_metrics_history:]
    
    def get_algorithm_stats(self, algorithm: str) -> Dict[str, Any]:
        """Statistiques détaillées pour un algorithme"""
        times = self.response_times[algorithm]
        successes = self.success_rates[algorithm]
        precisions = self.precision_scores[algorithm]
        
        if not times:
            return {'error': 'Aucune donnée disponible'}
        
        return {
            'request_count': self.request_counts[algorithm],
            'avg_response_time_ms': sum(times) / len(times),
            'p95_response_time_ms': sorted(times)[int(len(times) * 0.95)] if times else 0,
            'p99_response_time_ms': sorted(times)[int(len(times) * 0.99)] if times else 0,
            'success_rate': sum(successes) / len(successes) if successes else 0,
            'avg_precision': sum(precisions) / len(precisions) if precisions else None,
            'selection_count': self.algorithm_selections[algorithm]
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Statistiques globales du système"""
        all_algorithms = set(self.request_counts.keys())
        total_requests = sum(self.request_counts.values())
        
        stats = {
            'total_requests': total_requests,
            'algorithms_active': len(all_algorithms),
            'algorithm_distribution': {
                algo: {
                    'percentage': (self.algorithm_selections[algo] / total_requests * 100) if total_requests > 0 else 0,
                    'count': self.algorithm_selections[algo]
                }
                for algo in all_algorithms
            },
            'performance_summary': {}
        }
        
        # Résumé de performance par algorithme
        for algo in all_algorithms:
            stats['performance_summary'][algo] = self.get_algorithm_stats(algo)
        
        return stats

# ================================
# ORCHESTRATEUR PRINCIPAL V2
# ================================

class MatchingOrchestrator:
    """
    Orchestrateur principal SuperSmartMatch V2
    
    Unifie intelligemment tous les algorithmes de matching:
    - Nexten Matcher (principal avec 40K lignes ML)
    - SmartMatch (géolocalisation avancée) 
    - Enhanced (pondération adaptative)
    - Semantic (analyse NLP pure)
    - Hybrid (consensus multi-algorithmes)
    """
    
    def __init__(self):
        # Composants principaux
        self.algorithm_selector = None  # Sera initialisé après import
        self.data_adapter = None        # Sera initialisé après import
        self.circuit_breaker = AlgorithmCircuitBreaker()
        self.metrics_collector = MetricsCollector()
        
        # Pool de threads pour parallélisation
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Configuration
        self.config = {
            'default_algorithm': 'nexten',
            'max_response_time_ms': 100,
            'enable_fallback': True,
            'enable_parallel_execution': False,  # Pour mode validation
            'cache_enabled': True
        }
        
        # Cache simple en mémoire
        self.result_cache = {}
        self.cache_max_size = 1000
        
        # Initialisation des algorithmes (lazy loading)
        self.algorithms = {}
        self._algorithms_initialized = False
        
        logger.info("🚀 SuperSmartMatch V2 Orchestrator initialisé")
    
    def _initialize_algorithms(self):
        """Initialisation paresseuse des algorithmes"""
        if self._algorithms_initialized:
            return
        
        try:
            # Import des composants V2
            from .selector import SmartAlgorithmSelector
            from .data_adapter import DataFormatAdapter
            from .nexten_adapter import NextenMatcherAdapter
            
            # Import des algorithmes legacy (avec fallback gracieux)
            try:
                from ..smartmatch import SmartMatchAlgorithm
                from ..smartmatch_enhanced import EnhancedMatchAlgorithm  
                from ..smartmatch_semantic_enhanced import SemanticMatchAlgorithm
                from .hybrid_algorithm import HybridMatchAlgorithm
            except ImportError as e:
                logger.warning(f"Import legacy algorithms failed: {e}")
                # On utilisera des mocks pour l'instant
            
            # Initialisation des composants
            self.algorithm_selector = SmartAlgorithmSelector()
            self.data_adapter = DataFormatAdapter()
            
            # Initialisation des algorithmes disponibles
            self.algorithms = {
                'nexten': NextenMatcherAdapter(),
                # Les autres seront ajoutés au fur et à mesure
            }
            
            self._algorithms_initialized = True
            logger.info("✅ Algorithmes SuperSmartMatch V2 initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation algorithmes: {e}")
            # Fallback minimal
            self.algorithms = {'nexten': None}
            self._algorithms_initialized = True
    
    async def match_v2(self, request: MatchingRequestV2) -> MatchingResponse:
        """
        Point d'entrée principal SuperSmartMatch V2
        
        Orchestration intelligente avec sélection automatique d'algorithme,
        fallback hiérarchique et monitoring complet.
        """
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000000)}"
        
        logger.info(f"🎯 SuperSmartMatch V2 - Début matching {request_id}")
        
        try:
            # 1. Initialisation paresseuse
            self._initialize_algorithms()
            
            # 2. Validation de la requête
            self._validate_request(request)
            
            # 3. Analyse du contexte
            context = self._analyze_request_context(request)
            logger.info(f"📊 Contexte analysé: questionnaires={context.has_candidate_questionnaire}, "
                       f"compétences={context.skills_count}, expérience={context.experience_years}")
            
            # 4. Sélection d'algorithme
            selected_algorithm = self._select_algorithm(request, context)
            logger.info(f"🧠 Algorithme sélectionné: {selected_algorithm}")
            
            # 5. Vérification circuit breaker
            if not self.circuit_breaker.is_available(selected_algorithm):
                fallback_algorithm = self._get_fallback_algorithm(selected_algorithm)
                logger.warning(f"⚠️ Circuit breaker: {selected_algorithm} → {fallback_algorithm}")
                selected_algorithm = fallback_algorithm
            
            # 6. Vérification cache
            cache_key = self._generate_cache_key(request, selected_algorithm)
            if self.config['cache_enabled'] and cache_key in self.result_cache:
                logger.info("💾 Cache hit - résultat retourné du cache")
                cached_result = self.result_cache[cache_key]
                cached_result.metadata['cache_hit'] = True
                return cached_result
            
            # 7. Exécution du matching
            results = await self._execute_matching(selected_algorithm, request, context)
            
            # 8. Post-traitement et métriques
            total_time = (time.time() - start_time) * 1000
            response = self._build_response(results, total_time, selected_algorithm, context)
            
            # 9. Mise en cache
            if self.config['cache_enabled']:
                self._cache_result(cache_key, response)
            
            # 10. Enregistrement métriques
            self.metrics_collector.record_request(
                selected_algorithm, total_time, len(results), success=True
            )
            self.circuit_breaker.record_success(selected_algorithm)
            
            logger.info(f"✅ SuperSmartMatch V2 - Matching {request_id} terminé: "
                       f"{len(results)} résultats en {total_time:.1f}ms")
            
            return response
            
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Erreur SuperSmartMatch V2 {request_id}: {e}")
            
            # Fallback d'urgence
            return await self._emergency_fallback(request, str(e), total_time)
    
    def _validate_request(self, request: MatchingRequestV2):
        """Validation de la requête avec messages d'erreur détaillés"""
        if not request.candidate_data:
            raise ValueError("candidate_data est requis")
        
        if not request.offers_data:
            raise ValueError("offers_data ne peut pas être vide")
        
        # Validation des champs essentiels candidat
        required_fields = ['skills']
        missing_fields = [field for field in required_fields 
                         if field not in request.candidate_data]
        
        if missing_fields:
            logger.warning(f"⚠️ Champs manquants candidat: {missing_fields}")
        
        # Validation des offres
        for i, offer in enumerate(request.offers_data):
            if 'id' not in offer:
                raise ValueError(f"Offre {i}: 'id' manquant")
    
    def _analyze_request_context(self, request: MatchingRequestV2) -> MatchingContext:
        """Analyse contextuelle approfondie pour la sélection d'algorithme"""
        candidate = request.candidate_data
        offers = request.offers_data
        
        # Analyse questionnaires
        has_candidate_questionnaire = bool(request.candidate_questionnaire)
        has_company_questionnaires = bool(request.company_questionnaires and 
                                        any(q for q in request.company_questionnaires))
        
        # Analyse compétences et expérience
        skills = candidate.get('skills', [])
        skills_count = len(skills) if isinstance(skills, list) else 0
        experience_years = candidate.get('experience_years', 0)
        
        # Analyse mobilité et contraintes géographiques
        mobility = candidate.get('mobility', 'standard')
        has_geo_constraints = self._detect_geo_constraints(candidate, offers)
        
        # Score de qualité des données
        data_quality_score = self._calculate_data_quality_score(
            candidate, request.candidate_questionnaire, offers
        )
        
        return MatchingContext(
            has_candidate_questionnaire=has_candidate_questionnaire,
            has_company_questionnaires=has_company_questionnaires,
            skills_count=skills_count,
            experience_years=experience_years,
            mobility_type=mobility,
            has_geo_constraints=has_geo_constraints,
            data_quality_score=data_quality_score
        )
    
    def _detect_geo_constraints(self, candidate: Dict[str, Any], 
                              offers: List[Dict[str, Any]]) -> bool:
        """Détection des contraintes géographiques complexes"""
        candidate_location = candidate.get('location', {})
        if not candidate_location:
            return False
        
        # Vérification de la diversité géographique des offres
        offer_locations = [offer.get('location', {}) for offer in offers]
        unique_cities = set(loc.get('city', '') for loc in offer_locations if loc.get('city'))
        
        # Si plus de 3 villes différentes, considéré comme contraintes complexes
        return len(unique_cities) > 3
    
    def _calculate_data_quality_score(self, candidate: Dict[str, Any], 
                                    questionnaire: Optional[Dict[str, Any]], 
                                    offers: List[Dict[str, Any]]) -> float:
        """Calcul du score de qualité des données (0.0 à 1.0)"""
        score = 0.0
        max_score = 5.0
        
        # Score candidat (0-3 points)
        if candidate.get('skills'):
            score += 1.0
        if candidate.get('experience_years', 0) > 0:
            score += 1.0
        if questionnaire:
            score += 1.0
        
        # Score offres (0-2 points)
        if offers:
            score += 1.0
        
        offer_quality = sum(1 for offer in offers if offer.get('requirements'))
        if offer_quality > len(offers) * 0.7:  # 70% des offres ont des requirements
            score += 1.0
        
        return min(score / max_score, 1.0)
    
    def _select_algorithm(self, request: MatchingRequestV2, context: MatchingContext) -> str:
        """Sélection intelligente d'algorithme selon le contexte"""
        
        # Algorithme forcé par l'utilisateur
        if request.algorithm != "auto":
            if request.algorithm in self.algorithms:
                return request.algorithm
            else:
                logger.warning(f"⚠️ Algorithme {request.algorithm} non disponible, sélection auto")
        
        # Application des règles de sélection SuperSmartMatch V2
        
        # RÈGLE 1: Nexten prioritaire si données complètes (précision +13%)
        if (context.has_candidate_questionnaire and 
            context.has_company_questionnaires and 
            context.skills_count >= 5):
            return 'nexten'
        
        # RÈGLE 2: SmartMatch pour géolocalisation complexe
        if (context.mobility_type in ['remote', 'hybrid'] or 
            context.has_geo_constraints):
            return 'smart'
        
        # RÈGLE 3: Enhanced pour profils seniors
        if (context.experience_years >= 7 and 
            context.has_partial_questionnaires):
            return 'enhanced'
        
        # RÈGLE 4: Semantic pour analyse NLP pure
        if context.requires_semantic_analysis:
            return 'semantic'
        
        # RÈGLE 5: Hybrid pour validation critique
        if context.requires_validation:
            return 'hybrid'
        
        # RÈGLE 6: Défaut intelligent - Nexten comme meilleur algorithme
        return 'nexten'
    
    def _get_fallback_algorithm(self, failed_algorithm: str) -> str:
        """Stratégie de fallback hiérarchique"""
        fallback_hierarchy = {
            'nexten': 'enhanced',
            'enhanced': 'smart', 
            'smart': 'semantic',
            'semantic': 'hybrid',
            'hybrid': 'nexten'
        }
        
        fallback = fallback_hierarchy.get(failed_algorithm, 'nexten')
        
        # Vérification récursive si le fallback est aussi indisponible
        if not self.circuit_breaker.is_available(fallback) and fallback != failed_algorithm:
            return self._get_fallback_algorithm(fallback)
        
        return fallback
    
    async def _execute_matching(self, algorithm_name: str, 
                              request: MatchingRequestV2, 
                              context: MatchingContext) -> List[MatchingResult]:
        """Exécution sécurisée du matching avec l'algorithme sélectionné"""
        
        algorithm = self.algorithms.get(algorithm_name)
        if not algorithm:
            raise ValueError(f"Algorithme {algorithm_name} non disponible")
        
        try:
            # Timeout pour maintenir performance <100ms
            results = await asyncio.wait_for(
                self._call_algorithm(algorithm, request, context),
                timeout=self.config['max_response_time_ms'] / 1000
            )
            
            # Enrichissement des résultats avec métadonnées
            for result in results:
                result.algorithm_used = algorithm_name
                result.metadata.update({
                    'context_score': context.data_quality_score,
                    'selection_reason': f"Sélectionné pour: {algorithm_name}"
                })
            
            return results
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout algorithme {algorithm_name}")
            self.circuit_breaker.record_failure(algorithm_name)
            raise
        except Exception as e:
            logger.error(f"❌ Erreur algorithme {algorithm_name}: {e}")
            self.circuit_breaker.record_failure(algorithm_name)
            raise
    
    async def _call_algorithm(self, algorithm, request: MatchingRequestV2, 
                            context: MatchingContext) -> List[MatchingResult]:
        """Appel unifié d'algorithme avec adaptation des données"""
        
        # Pour l'instant, simulation avec Nexten
        # TODO: Implémenter l'appel réel selon l'interface de chaque algorithme
        
        results = []
        for i, offer in enumerate(request.offers_data):
            # Simulation d'un résultat de matching
            score = 0.8 + (i % 3) * 0.1  # Score simulé
            
            result = MatchingResult(
                offer_id=offer.get('id', f'offer_{i}'),
                score=score,
                confidence=0.85,
                algorithm_used='simulation',
                match_details={
                    'skills_match': score * 0.9,
                    'experience_match': score * 0.8,
                    'location_match': score * 0.7
                },
                explanation=f"Match simulé avec score {score:.2f}",
                processing_time_ms=10.0,
                metadata={'simulation': True}
            )
            results.append(result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _build_response(self, results: List[MatchingResult], 
                       total_time: float, algorithm: str, 
                       context: MatchingContext) -> MatchingResponse:
        """Construction de la réponse complète avec métadonnées"""
        
        return MatchingResponse(
            results=results,
            total_processing_time_ms=total_time,
            algorithm_selection_reason=f"Algorithme {algorithm} sélectionné automatiquement",
            context_analysis={
                'data_quality_score': context.data_quality_score,
                'questionnaires_available': context.has_candidate_questionnaire,
                'skills_count': context.skills_count,
                'experience_years': context.experience_years,
                'geo_constraints': context.has_geo_constraints
            },
            performance_metrics={
                'algorithm_used': algorithm,
                'results_count': len(results),
                'avg_score': sum(r.score for r in results) / len(results) if results else 0,
                'processing_time_per_offer': total_time / len(results) if results else 0
            }
        )
    
    def _generate_cache_key(self, request: MatchingRequestV2, algorithm: str) -> str:
        """Génération de clé de cache basée sur le contenu de la requête"""
        import hashlib
        
        # Simplification pour le cache
        key_data = {
            'candidate_id': request.candidate_data.get('id', 'unknown'),
            'offer_ids': [offer.get('id', 'unknown') for offer in request.offers_data],
            'algorithm': algorithm,
            'has_questionnaire': bool(request.candidate_questionnaire)
        }
        
        key_str = str(sorted(key_data.items()))
        return hashlib.md5(key_str.encode()).hexdigest()[:16]
    
    def _cache_result(self, cache_key: str, response: MatchingResponse):
        """Mise en cache avec nettoyage automatique"""
        # Nettoyage si cache plein
        if len(self.result_cache) >= self.cache_max_size:
            # Suppression des 20% plus anciens
            to_remove = list(self.result_cache.keys())[:self.cache_max_size // 5]
            for key in to_remove:
                del self.result_cache[key]
        
        # Ajout du timestamp pour expiration future
        response.metadata = getattr(response, 'metadata', {})
        response.metadata['cached_at'] = time.time()
        
        self.result_cache[cache_key] = response
    
    async def _emergency_fallback(self, request: MatchingRequestV2, 
                                error: str, total_time: float) -> MatchingResponse:
        """Fallback d'urgence avec résultats par défaut"""
        logger.error(f"🚨 Fallback d'urgence activé: {error}")
        
        # Création de résultats par défaut
        fallback_results = []
        for i, offer in enumerate(request.offers_data):
            result = MatchingResult(
                offer_id=offer.get('id', f'offer_{i}'),
                score=0.5,  # Score neutre
                confidence=0.1,  # Très faible confiance
                algorithm_used='emergency_fallback',
                match_details={'error': error, 'status': 'fallback'},
                explanation='Service en mode dégradé - score par défaut',
                processing_time_ms=0.0,
                metadata={'emergency': True, 'error': error}
            )
            fallback_results.append(result)
        
        return MatchingResponse(
            results=fallback_results,
            total_processing_time_ms=total_time,
            algorithm_selection_reason=f"Fallback d'urgence: {error}",
            context_analysis={'error': error, 'status': 'degraded'},
            performance_metrics={'emergency_mode': True}
        )
    
    # ================================
    # MÉTHODES UTILITAIRES ET MONITORING
    # ================================
    
    def get_system_health(self) -> Dict[str, Any]:
        """État de santé du système SuperSmartMatch V2"""
        return {
            'status': 'healthy',
            'version': 'v2.0.0',
            'algorithms_available': list(self.algorithms.keys()),
            'circuit_breaker_stats': self.circuit_breaker.get_stats(),
            'metrics_summary': self.metrics_collector.get_global_stats(),
            'cache_stats': {
                'size': len(self.result_cache),
                'max_size': self.cache_max_size,
                'hit_rate': 'TODO: implémenter calcul hit rate'
            },
            'config': self.config
        }
    
    def get_algorithm_performance(self, algorithm: str) -> Dict[str, Any]:
        """Performance détaillée d'un algorithme spécifique"""
        return self.metrics_collector.get_algorithm_stats(algorithm)
    
    def update_config(self, new_config: Dict[str, Any]):
        """Mise à jour de la configuration en temps réel"""
        self.config.update(new_config)
        logger.info(f"🔧 Configuration mise à jour: {new_config}")
    
    def clear_cache(self):
        """Vidage manuel du cache"""
        self.result_cache.clear()
        logger.info("🗑️ Cache vidé manuellement")

# ================================
# INSTANCE GLOBALE (SINGLETON)
# ================================

# Instance globale pour utilisation dans l'API
_orchestrator_instance = None

def get_orchestrator() -> MatchingOrchestrator:
    """Factory singleton pour l'orchestrateur"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MatchingOrchestrator()
    return _orchestrator_instance

# ================================
# EXEMPLE D'UTILISATION
# ================================

async def example_usage():
    """Exemple d'utilisation de l'orchestrateur SuperSmartMatch V2"""
    
    orchestrator = get_orchestrator()
    
    # Requête V2 avec questionnaires
    request = MatchingRequestV2(
        candidate_data={
            'id': 'candidate_123',
            'name': 'Jean Dupont',
            'skills': ['Python', 'Machine Learning', 'AWS'],
            'experience_years': 8,
            'location': {'city': 'Paris', 'country': 'France'},
            'mobility': 'hybrid'
        },
        candidate_questionnaire={
            'work_style': 'collaborative',
            'career_goals': 'leadership',
            'technology_preferences': ['cloud', 'ai']
        },
        offers_data=[
            {
                'id': 'offer_001',
                'title': 'Senior ML Engineer',
                'company': 'TechCorp',
                'location': {'city': 'Paris', 'country': 'France'},
                'requirements': ['Python', 'ML', 'Cloud']
            }
        ],
        company_questionnaires=[{
            'company_culture': 'innovative',
            'work_environment': 'collaborative'
        }]
    )
    
    # Exécution du matching
    response = await orchestrator.match_v2(request)
    
    print(f"✅ SuperSmartMatch V2 - Résultats:")
    print(f"   Algorithme: {response.algorithm_selection_reason}")
    print(f"   Temps: {response.total_processing_time_ms:.1f}ms")
    print(f"   Matches: {len(response.results)}")
    
    for match in response.results:
        print(f"   📊 {match.offer_id}: {match.score:.2f} ({match.algorithm_used})")

if __name__ == "__main__":
    # Test rapide
    asyncio.run(example_usage())
