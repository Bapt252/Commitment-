"""
Modèles Pydantic pour SuperSmartMatch V2

Définit tous les modèles de données utilisés pour :
- Requêtes de matching (V1 et V2)
- Réponses et résultats
- Configuration et options
- Monitoring et métriques
"""

from .matching_models import (
    MatchingRequestV1,
    MatchingRequestV2,
    MatchingResponse,
    MatchingOptions,
    CVData,
    JobData,
    MatchResult,
    HealthResponse,
    MetricsResponse
)

from .algorithm_models import (
    AlgorithmType,
    AlgorithmSelection,
    AlgorithmStatus,
    CircuitBreakerState
)

__all__ = [
    "MatchingRequestV1",
    "MatchingRequestV2", 
    "MatchingResponse",
    "MatchingOptions",
    "CVData",
    "JobData",
    "MatchResult",
    "HealthResponse",
    "MetricsResponse",
    "AlgorithmType",
    "AlgorithmSelection",
    "AlgorithmStatus",
    "CircuitBreakerState"
]
