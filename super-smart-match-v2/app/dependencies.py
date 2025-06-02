"""
Dépendances FastAPI pour SuperSmartMatch V2

Gestion de l'injection de dépendances pour :
- Service orchestrateur
- Analyseur de contexte
- Services d'administration
"""

from functools import lru_cache
from typing import Optional

from .services.orchestrator import ServiceOrchestrator
from .services.context_analyzer import ContextAnalyzer
from .services.admin_service import AdminService
from .adapters.nexten_adapter import NextenAdapter
from .adapters.v1_adapter import V1Adapter
from .adapters.cache_adapter import CacheAdapter
from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)
config = get_config()

# Instances globales (singletons)
_orchestrator: Optional[ServiceOrchestrator] = None
_context_analyzer: Optional[ContextAnalyzer] = None
_admin_service: Optional[AdminService] = None
_nexten_adapter: Optional[NextenAdapter] = None
_v1_adapter: Optional[V1Adapter] = None
_cache_adapter: Optional[CacheAdapter] = None

# Factory functions avec cache
@lru_cache(maxsize=1)
def get_cache_adapter() -> CacheAdapter:
    """Factory pour l'adaptateur de cache"""
    global _cache_adapter
    if _cache_adapter is None:
        _cache_adapter = CacheAdapter()
        logger.info("Cache adapter initialized")
    return _cache_adapter

@lru_cache(maxsize=1)
def get_nexten_adapter() -> NextenAdapter:
    """Factory pour l'adaptateur Nexten"""
    global _nexten_adapter
    if _nexten_adapter is None:
        cache_adapter = get_cache_adapter()
        _nexten_adapter = NextenAdapter(cache_adapter=cache_adapter)
        logger.info("Nexten adapter initialized", service_url=config.nexten_matcher_url)
    return _nexten_adapter

@lru_cache(maxsize=1)
def get_v1_adapter() -> V1Adapter:
    """Factory pour l'adaptateur V1"""
    global _v1_adapter
    if _v1_adapter is None:
        cache_adapter = get_cache_adapter()
        _v1_adapter = V1Adapter(cache_adapter=cache_adapter)
        logger.info("V1 adapter initialized", service_url=config.supersmartmatch_v1_url)
    return _v1_adapter

@lru_cache(maxsize=1)
def get_context_analyzer() -> ContextAnalyzer:
    """Factory pour l'analyseur de contexte"""
    global _context_analyzer
    if _context_analyzer is None:
        _context_analyzer = ContextAnalyzer()
        logger.info("Context analyzer initialized")
    return _context_analyzer

@lru_cache(maxsize=1)
def get_service_orchestrator() -> ServiceOrchestrator:
    """Factory pour l'orchestrateur de services"""
    global _orchestrator
    if _orchestrator is None:
        nexten_adapter = get_nexten_adapter()
        v1_adapter = get_v1_adapter()
        context_analyzer = get_context_analyzer()
        cache_adapter = get_cache_adapter()
        
        _orchestrator = ServiceOrchestrator(
            nexten_adapter=nexten_adapter,
            v1_adapter=v1_adapter,
            context_analyzer=context_analyzer,
            cache_adapter=cache_adapter
        )
        logger.info("Service orchestrator initialized")
    return _orchestrator

@lru_cache(maxsize=1)
def get_admin_service() -> AdminService:
    """Factory pour le service d'administration"""
    global _admin_service
    if _admin_service is None:
        cache_adapter = get_cache_adapter()
        orchestrator = get_service_orchestrator()
        
        _admin_service = AdminService(
            cache_adapter=cache_adapter,
            orchestrator=orchestrator
        )
        logger.info("Admin service initialized")
    return _admin_service

# Fonctions utilitaires pour les tests
def reset_dependencies():
    """Réinitialiser toutes les dépendances (pour les tests)"""
    global _orchestrator, _context_analyzer, _admin_service
    global _nexten_adapter, _v1_adapter, _cache_adapter
    
    _orchestrator = None
    _context_analyzer = None
    _admin_service = None
    _nexten_adapter = None
    _v1_adapter = None
    _cache_adapter = None
    
    # Vider les caches
    get_cache_adapter.cache_clear()
    get_nexten_adapter.cache_clear()
    get_v1_adapter.cache_clear()
    get_context_analyzer.cache_clear()
    get_service_orchestrator.cache_clear()
    get_admin_service.cache_clear()
    
    logger.info("All dependencies reset (test mode)")

def create_test_dependencies(**overrides):
    """Créer des dépendances pour les tests avec overrides"""
    # TODO: Implémenter la création de mocks pour les tests
    pass