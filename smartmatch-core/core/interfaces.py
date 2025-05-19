"""
Core Interfaces for SmartMatcher
-------------------------------
Définit les interfaces abstraites et protocols utilisés dans l'architecture modulaire.
Suit le principe d'inversion de dépendance (SOLID).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator, Protocol
from .models import Candidate, Job, MatchResult, MatchInsight


class BaseMatchEngine(ABC):
    """Interface de base pour tous les moteurs de matching"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom du matcher"""
        pass
    
    @abstractmethod
    def get_weight(self) -> float:
        """Retourne le poids de ce critère dans le score final"""
        pass
    
    @abstractmethod
    async def calculate_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score de matching pour ce critère
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        pass
    
    @abstractmethod
    def generate_insights(self, candidate: Candidate, job: Job, score: float) -> List[MatchInsight]:
        """
        Génère des insights pour expliquer le score
        
        Args:
            candidate: Le candidat évalué
            job: L'offre d'emploi évaluée
            score: Le score calculé
            
        Returns:
            Liste d'insights
        """
        pass
    
    def is_enabled(self) -> bool:
        """Indique si ce matcher est activé"""
        return True
    
    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration du matcher"""
        return {}


class ScoringStrategy(ABC):
    """Interface pour les stratégies de calcul de score global"""
    
    @abstractmethod
    def calculate_overall_score(self, category_scores: Dict[str, float], 
                              matchers: List[BaseMatchEngine]) -> float:
        """
        Calcule le score global à partir des scores par catégorie
        
        Args:
            category_scores: Scores par catégorie
            matchers: Liste des matchers utilisés
            
        Returns:
            Score global entre 0 et 1
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        pass


class CacheService(ABC):
    """Interface pour les services de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Supprime une valeur du cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Vide le cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache"""
        pass


class NLPService(ABC):
    """Interface pour les services de traitement du langage naturel"""
    
    @abstractmethod
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes"""
        pass
    
    @abstractmethod
    def calculate_skills_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """Calcule la similarité entre deux listes de compétences"""
        pass
    
    @abstractmethod
    def expand_skills_with_synonyms(self, skills: List[str]) -> List[str]:
        """Étend une liste de compétences avec des synonymes"""
        pass
    
    @abstractmethod
    def normalize_text(self, text: str) -> str:
        """Normalise un texte (lowercase, suppression accents, etc.)"""
        pass
    
    @abstractmethod
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extrait des compétences d'un texte libre"""
        pass


class LocationService(ABC):
    """Interface pour les services de géolocalisation"""
    
    @abstractmethod
    async def calculate_travel_time(self, origin: str, destination: str, 
                                  mode: str = 'driving') -> Optional[int]:
        """
        Calcule le temps de trajet entre deux points
        
        Args:
            origin: Point de départ
            destination: Point d'arrivée
            mode: Mode de transport (driving, walking, transit, bicycling)
            
        Returns:
            Temps de trajet en minutes ou None si impossible à calculer
        """
        pass
    
    @abstractmethod
    async def get_coordinates(self, address: str) -> Optional[tuple]:
        """
        Obtient les coordonnées d'une adresse
        
        Args:
            address: Adresse à géocoder
            
        Returns:
            Tuple (latitude, longitude) ou None si non trouvé
        """
        pass
    
    @abstractmethod
    async def get_city_from_coordinates(self, lat: float, lng: float) -> Optional[str]:
        """Obtient le nom de la ville à partir de coordonnées"""
        pass


class MetricsCollector(ABC):
    """Interface pour la collecte de métriques"""
    
    @abstractmethod
    def record_match_calculated(self, result: MatchResult) -> None:
        """Enregistre les métriques d'un calcul de match"""
        pass
    
    @abstractmethod
    def record_batch_processed(self, batch_size: int, processing_time_ms: float) -> None:
        """Enregistre les métriques d'un traitement en lot"""
        pass
    
    @abstractmethod
    def record_error(self, error_type: str, error_message: str) -> None:
        """Enregistre une erreur"""
        pass
    
    @abstractmethod
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des métriques collectées"""
        pass


class ConfigurationProvider(ABC):
    """Interface pour les fournisseurs de configuration"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        pass
    
    @abstractmethod
    def get_weights(self) -> Dict[str, float]:
        """Récupère les poids des différents critères"""
        pass
    
    @abstractmethod
    def get_thresholds(self) -> Dict[str, float]:
        """Récupère les seuils de qualification"""
        pass
    
    @abstractmethod
    def reload_config(self) -> None:
        """Recharge la configuration"""
        pass


class DataRepository(Protocol):
    """Protocol pour les repositories de données (candidates, jobs)"""
    
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Récupère un candidat par son ID"""
        ...
    
    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Récupère une offre d'emploi par son ID"""
        ...
    
    async def get_candidates(self, filters: Dict[str, Any] = None, 
                           limit: int = 100) -> List[Candidate]:
        """Récupère une liste de candidats avec filtres optionnels"""
        ...
    
    async def get_jobs(self, filters: Dict[str, Any] = None, 
                      limit: int = 100) -> List[Job]:
        """Récupère une liste d'offres d'emploi avec filtres optionnels"""
        ...


class EventListener(ABC):
    """Interface pour les écouteurs d'événements"""
    
    @abstractmethod
    async def on_match_calculated(self, result: MatchResult) -> None:
        """Appelé lorsqu'un match est calculé"""
        pass
    
    @abstractmethod
    async def on_batch_started(self, batch_size: int) -> None:
        """Appelé au début d'un traitement en lot"""
        pass
    
    @abstractmethod
    async def on_batch_completed(self, results: List[MatchResult]) -> None:
        """Appelé à la fin d'un traitement en lot"""
        pass
    
    @abstractmethod
    async def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Appelé lorsqu'une erreur survient"""
        pass


class PerformanceMonitor(ABC):
    """Interface pour le monitoring des performances"""
    
    @abstractmethod
    def start_timing(self, operation: str) -> str:
        """Démarre le chronométrage d'une opération, retourne un ID de timer"""
        pass
    
    @abstractmethod
    def end_timing(self, timer_id: str) -> float:
        """Termine le chronométrage et retourne la durée en millisecondes"""
        pass
    
    @abstractmethod
    def record_memory_usage(self, operation: str) -> None:
        """Enregistre l'utilisation mémoire pour une opération"""
        pass
    
    @abstractmethod
    def get_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport de performance"""
        pass


class MatchingEventEmitter(ABC):
    """Interface pour l'émission d'événements de matching"""
    
    @abstractmethod
    def add_listener(self, event_type: str, listener: EventListener) -> None:
        """Ajoute un écouteur pour un type d'événement"""
        pass
    
    @abstractmethod
    def remove_listener(self, event_type: str, listener: EventListener) -> None:
        """Supprime un écouteur"""
        pass
    
    @abstractmethod
    async def emit(self, event_type: str, data: Any) -> None:
        """Émet un événement"""
        pass


class StreamingMatchEngine(ABC):
    """Interface pour le matching en streaming"""
    
    @abstractmethod
    async def stream_matches_for_candidate(
        self, 
        candidate: Candidate,
        job_stream: AsyncGenerator[Job, None]
    ) -> AsyncGenerator[MatchResult, None]:
        """Stream de matching pour un candidat contre un flux d'offres"""
        pass
    
    @abstractmethod
    async def stream_matches_for_job(
        self,
        job: Job,
        candidate_stream: AsyncGenerator[Candidate, None]
    ) -> AsyncGenerator[MatchResult, None]:
        """Stream de matching pour une offre contre un flux de candidats"""
        pass


class MatchingAPIClient(Protocol):
    """Protocol pour les clients API de matching"""
    
    async def calculate_single_match(self, candidate_id: str, job_id: str) -> MatchResult:
        """Calcule un match unique"""
        ...
    
    async def find_jobs_for_candidate(self, candidate_id: str, 
                                    limit: int = 10) -> List[MatchResult]:
        """Trouve les meilleures offres pour un candidat"""
        ...
    
    async def find_candidates_for_job(self, job_id: str, 
                                    limit: int = 50) -> List[MatchResult]:
        """Trouve les meilleurs candidats pour une offre"""
        ...
    
    async def batch_match(self, candidate_ids: List[str], 
                         job_ids: List[str]) -> List[MatchResult]:
        """Effectue un matching en lot"""
        ...


class MatchingEngine(ABC):
    """Interface principale pour le moteur de matching"""
    
    @abstractmethod
    async def calculate_match(self, candidate: Candidate, job: Job) -> MatchResult:
        """Calcule un match entre un candidat et une offre"""
        pass
    
    @abstractmethod
    async def batch_match(self, candidates: List[Candidate], 
                         jobs: List[Job]) -> List[MatchResult]:
        """Effectue un matching en lot"""
        pass
    
    @abstractmethod
    async def find_best_jobs_for_candidate(self, candidate: Candidate,
                                         available_jobs: List[Job],
                                         limit: int = 10) -> List[MatchResult]:
        """Trouve les meilleures offres pour un candidat"""
        pass
    
    @abstractmethod
    async def find_best_candidates_for_job(self, job: Job,
                                         available_candidates: List[Candidate],
                                         limit: int = 50) -> List[MatchResult]:
        """Trouve les meilleurs candidats pour une offre"""
        pass
    
    @abstractmethod
    def add_matcher(self, matcher: BaseMatchEngine) -> None:
        """Ajoute un matcher au moteur"""
        pass
    
    @abstractmethod
    def remove_matcher(self, matcher_name: str) -> None:
        """Supprime un matcher du moteur"""
        pass
    
    @abstractmethod
    def set_scoring_strategy(self, strategy: ScoringStrategy) -> None:
        """Définit la stratégie de calcul de score"""
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration courante du moteur"""
        pass
