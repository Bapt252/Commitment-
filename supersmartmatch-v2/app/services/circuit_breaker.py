"""
Gestion des Circuit Breakers pour SuperSmartMatch V2

Implémente le pattern Circuit Breaker pour protéger les appels
vers les services externes et permettre une dégradation gracieuse.

États :
- CLOSED : Service fonctionnel
- OPEN : Service en panne, utilisation du fallback
- HALF_OPEN : Test de récupération
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum

from ..models.algorithm_models import AlgorithmType, CircuitBreakerState
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CircuitBreaker:
    """
    Circuit Breaker pour un service spécifique
    
    Protège les appels vers un service externe et gère automatiquement
    les états d'ouverture/fermeture selon les échecs.
    """
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = None,
        recovery_timeout: int = None,
        expected_exception: Exception = Exception
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold or settings.circuit_breaker_failure_threshold
        self.recovery_timeout = recovery_timeout or settings.circuit_breaker_recovery_timeout
        self.expected_exception = expected_exception
        
        # État du circuit breaker
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.next_retry_time: Optional[datetime] = None
        
        # Statistiques
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.state_transitions = {
            CircuitBreakerState.CLOSED: 0,
            CircuitBreakerState.OPEN: 0,
            CircuitBreakerState.HALF_OPEN: 0
        }
        
        # Historique des changements d'état
        self.state_history = []
        
        logger.info(
            f"🔒 Circuit Breaker créé pour {service_name} "
            f"(seuil: {self.failure_threshold}, timeout: {self.recovery_timeout}s)"
        )
    
    def can_execute(self) -> bool:
        """
        Vérifie si une requête peut être exécutée
        
        Returns:
            True si l'exécution est autorisée
        """
        now = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        elif self.state == CircuitBreakerState.OPEN:
            # Vérifier si on peut passer en HALF_OPEN
            if self.next_retry_time and now >= self.next_retry_time:
                self._transition_to_half_open()
                return True
            return False
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """
        Enregistre un succès
        """
        self.total_requests += 1
        self.successful_requests += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Récupération réussie, fermer le circuit
            self._transition_to_closed()
            logger.info(f"✅ Circuit Breaker {self.service_name} récupéré avec succès")
        
        # Réinitialiser le compteur d'échecs sur succès
        if self.failure_count > 0:
            logger.debug(f"Réinitialisation compteur échecs pour {self.service_name}")
            self.failure_count = 0
    
    def record_failure(self):
        """
        Enregistre un échec
        """
        self.total_requests += 1
        self.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        logger.warning(
            f"⚠️ Échec enregistré pour {self.service_name} "
            f"({self.failure_count}/{self.failure_threshold})"
        )
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Échec pendant la récupération, rouvrir le circuit
            self._transition_to_open()
        
        elif self.state == CircuitBreakerState.CLOSED:
            # Vérifier si on doit ouvrir le circuit
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition vers l'état OPEN"""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.next_retry_time = datetime.now() + timedelta(seconds=self.recovery_timeout)
        
        self._record_state_transition(old_state, CircuitBreakerState.OPEN)
        
        logger.error(
            f"🔴 Circuit Breaker {self.service_name} OUVERT "
            f"(prochaine tentative: {self.next_retry_time})"
        )
    
    def _transition_to_half_open(self):
        """Transition vers l'état HALF_OPEN"""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        
        self._record_state_transition(old_state, CircuitBreakerState.HALF_OPEN)
        
        logger.info(f"🟡 Circuit Breaker {self.service_name} en test de récupération")
    
    def _transition_to_closed(self):
        """Transition vers l'état CLOSED"""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.next_retry_time = None
        
        self._record_state_transition(old_state, CircuitBreakerState.CLOSED)
        
        logger.info(f"🟢 Circuit Breaker {self.service_name} FERMÉ")
    
    def _record_state_transition(self, from_state: CircuitBreakerState, to_state: CircuitBreakerState):
        """Enregistre un changement d'état"""
        self.state_transitions[to_state] += 1
        
        transition = {
            "timestamp": datetime.now(),
            "from_state": from_state,
            "to_state": to_state,
            "failure_count": self.failure_count
        }
        
        self.state_history.append(transition)
        
        # Garder seulement les 100 dernières transitions
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut détaillé du circuit breaker"""
        now = datetime.now()
        
        success_rate = 0.0
        if self.total_requests > 0:
            success_rate = self.successful_requests / self.total_requests
        
        status = {
            "service_name": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "next_retry_time": self.next_retry_time.isoformat() if self.next_retry_time else None,
            "state_transitions": {k.value: v for k, v in self.state_transitions.items()},
            "recent_transitions": len(self.state_history)
        }
        
        # Temps jusqu'à la prochaine tentative
        if self.next_retry_time and now < self.next_retry_time:
            status["seconds_until_retry"] = int((self.next_retry_time - now).total_seconds())
        
        return status
    
    def reset(self):
        """Remet à zéro le circuit breaker"""
        logger.info(f"🔄 Réinitialisation Circuit Breaker {self.service_name}")
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.next_retry_time = None


class CircuitBreakerManager:
    """
    Gestionnaire centralisé des Circuit Breakers
    
    Gère tous les circuit breakers pour les différents services
    et fournit une interface unifiée.
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        
        logger.info("🔧 CircuitBreakerManager initialisé")
    
    async def initialize(self):
        """Initialise le gestionnaire et crée les circuit breakers"""
        logger.info("🚀 Initialisation CircuitBreakerManager...")
        
        # Créer les circuit breakers pour chaque algorithme
        algorithms = [
            AlgorithmType.NEXTEN,
            AlgorithmType.SMART_MATCH,
            AlgorithmType.ENHANCED,
            AlgorithmType.SEMANTIC,
            AlgorithmType.HYBRID,
            AlgorithmType.BASIC
        ]
        
        for algorithm in algorithms:
            self.circuit_breakers[algorithm.value] = CircuitBreaker(
                service_name=f"algorithm_{algorithm.value}",
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout
            )
        
        # Démarrer la surveillance
        if settings.monitoring_enabled:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info(f"✅ {len(self.circuit_breakers)} Circuit Breakers créés")
    
    async def cleanup(self):
        """Nettoie les ressources"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🧹 CircuitBreakerManager nettoyé")
    
    def get_circuit_breaker(self, algorithm: AlgorithmType) -> CircuitBreaker:
        """
        Récupère le circuit breaker pour un algorithme
        
        Args:
            algorithm: Type d'algorithme
            
        Returns:
            CircuitBreaker correspondant
        """
        key = algorithm.value
        
        if key not in self.circuit_breakers:
            # Créer dynamiquement si nécessaire
            self.circuit_breakers[key] = CircuitBreaker(
                service_name=f"algorithm_{key}"
            )
            logger.info(f"🔧 Circuit Breaker créé dynamiquement pour {key}")
        
        return self.circuit_breakers[key]
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de tous les circuit breakers"""
        return {
            name: cb.get_status()
            for name, cb in self.circuit_breakers.items()
        }
    
    def reset_all(self):
        """Remet à zéro tous les circuit breakers"""
        logger.info("🔄 Réinitialisation de tous les Circuit Breakers")
        
        for cb in self.circuit_breakers.values():
            cb.reset()
    
    def reset_circuit_breaker(self, algorithm: AlgorithmType):
        """Remet à zéro un circuit breaker spécifique"""
        cb = self.get_circuit_breaker(algorithm)
        cb.reset()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de santé de tous les circuit breakers"""
        total_cb = len(self.circuit_breakers)
        closed_cb = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitBreakerState.CLOSED)
        open_cb = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitBreakerState.OPEN)
        half_open_cb = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitBreakerState.HALF_OPEN)
        
        # Services dégradés
        degraded_services = [
            name for name, cb in self.circuit_breakers.items()
            if cb.state != CircuitBreakerState.CLOSED
        ]
        
        return {
            "total_circuit_breakers": total_cb,
            "healthy_services": closed_cb,
            "failed_services": open_cb,
            "recovering_services": half_open_cb,
            "degraded_services": degraded_services,
            "overall_health": "healthy" if open_cb == 0 else "degraded"
        }
    
    async def _monitoring_loop(self):
        """Boucle de surveillance des circuit breakers"""
        logger.info("👁️ Démarrage surveillance Circuit Breakers")
        
        try:
            while True:
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
                health_summary = self.get_health_summary()
                
                if health_summary["failed_services"] > 0:
                    logger.warning(
                        f"⚠️ Services dégradés: {health_summary['degraded_services']}"
                    )
                
                # Log des métriques détaillées en mode debug
                if logger.isEnabledFor(logging.DEBUG):
                    for name, cb in self.circuit_breakers.items():
                        status = cb.get_status()
                        logger.debug(
                            f"CB {name}: {status['state']} "
                            f"(succès: {status['success_rate']:.2%}, "
                            f"échecs: {status['failure_count']})"
                        )
        
        except asyncio.CancelledError:
            logger.info("🛑 Arrêt surveillance Circuit Breakers")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur surveillance Circuit Breakers: {e}", exc_info=True)
