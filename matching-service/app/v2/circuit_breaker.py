# Circuit Breaker - Protection et Monitoring des Algorithmes
# Système de protection contre les défaillances en cascade

import asyncio
import time
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Fonctionnement normal
    OPEN = "open"          # Circuit ouvert (bloque les appels)
    HALF_OPEN = "half_open"  # Test de récupération

@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    failure_threshold: int = 5        # Seuil d'échecs pour ouverture
    recovery_timeout: int = 60        # Timeout avant test récupération (secondes)
    success_threshold: int = 3        # Succès requis pour fermer en half-open
    timeout: float = 10.0             # Timeout par appel (secondes)
    slow_call_threshold: float = 5.0  # Seuil appel lent (secondes)

class CircuitBreakerOpenException(Exception):
    """Exception levée quand le circuit breaker est ouvert"""
    pass

class AlgorithmCircuitBreaker:
    """
    ⚡ CIRCUIT BREAKER POUR ALGORITHMES SUPERSMARTMATCH V2
    
    Protection intelligente contre les défaillances en cascade.
    Implémente le pattern Circuit Breaker pour chaque algorithme
    avec monitoring et récupération automatique.
    
    FONCTIONNEMENT :
    🟢 CLOSED: Fonctionnement normal, surveillance des échecs
    🔴 OPEN: Bloque tous les appels, protection active  
    🟡 HALF-OPEN: Test récupération avec appels limités
    
    Objectifs :
    - Protection cascade failures (Nexten Matcher, etc.)
    - Récupération automatique intelligente
    - Monitoring détaillé performances par algorithme
    - Fallback déclenché automatiquement
    """
    
    def __init__(self, 
                 algorithm_name: str,
                 config: Optional[CircuitBreakerConfig] = None):
        self.algorithm_name = algorithm_name
        self.config = config or CircuitBreakerConfig()
        
        # État du circuit
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
        
        # Statistiques détaillées
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'slow_calls': 0,
            'timeouts': 0,
            'avg_response_time': 0.0,
            'response_times': []  # Garde les 100 derniers temps de réponse
        }
        
        # Monitoring continu
        self.monitoring_enabled = True
        self.state_changes = []  # Historique des changements d'état
        
        logger.info(f"⚡ Circuit Breaker initialized for {algorithm_name}")

    async def call_algorithm(self, 
                           algorithm_func: Callable,
                           *args, **kwargs) -> Any:
        """
        🚀 APPEL PROTÉGÉ D'ALGORITHME
        
        Exécute l'algorithme avec protection circuit breaker.
        
        Args:
            algorithm_func: Fonction algorithme à appeler
            *args, **kwargs: Arguments pour l'algorithme
            
        Returns:
            Résultat de l'algorithme
            
        Raises:
            CircuitBreakerOpenException: Si circuit ouvert
            Exception: Erreurs algorithme si circuit fermé
        """
        
        self.stats['total_calls'] += 1
        
        # Vérification état du circuit
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                logger.warning(f"⚡ [{self.algorithm_name}] Circuit OPEN - blocking call")
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN for {self.algorithm_name}"
                )
        
        # Exécution avec monitoring
        start_time = time.time()
        
        try:
            # Appel avec timeout
            result = await asyncio.wait_for(
                algorithm_func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Succès
            execution_time = time.time() - start_time
            self._on_success(execution_time)
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"⏰ [{self.algorithm_name}] Timeout after {execution_time:.2f}s")
            self.stats['timeouts'] += 1
            self._on_failure("timeout")
            raise
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.warning(f"❌ [{self.algorithm_name}] Error after {execution_time:.2f}s: {str(e)}")
            self._on_failure(str(e))
            raise

    def _on_success(self, execution_time: float):
        """
        ✅ GESTION DU SUCCÈS
        
        Met à jour les métriques et l'état après un appel réussi.
        """
        self.stats['successful_calls'] += 1
        self.success_count += 1
        self.last_success_time = time.time()
        
        # Tracking temps de réponse
        self._update_response_time(execution_time)
        
        # Détection appel lent
        if execution_time > self.config.slow_call_threshold:
            self.stats['slow_calls'] += 1
            logger.warning(f"🐌 [{self.algorithm_name}] Slow call: {execution_time:.2f}s")
        
        # Transition d'état selon contexte
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count après succès
            self.failure_count = max(0, self.failure_count - 1)
        
        logger.debug(f"✅ [{self.algorithm_name}] Success in {execution_time:.3f}s "
                    f"(state: {self.state.value}, failures: {self.failure_count})")

    def _on_failure(self, error_type: str):
        """
        ❌ GESTION DE L'ÉCHEC
        
        Met à jour les métriques et l'état après un échec.
        """
        self.stats['failed_calls'] += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Transition vers OPEN si seuil atteint
        if (self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN] and 
            self.failure_count >= self.config.failure_threshold):
            self._transition_to_open()
        
        logger.debug(f"❌ [{self.algorithm_name}] Failure #{self.failure_count} "
                    f"(state: {self.state.value}, type: {error_type})")

    def _should_attempt_reset(self) -> bool:
        """
        🔄 VÉRIFICATION TENTATIVE DE RESET
        
        Détermine si on peut tenter de fermer le circuit.
        """
        if not self.last_failure_time:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout

    def _transition_to_closed(self):
        """🟢 Transition vers état CLOSED (normal)"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        
        self._record_state_change(old_state, self.state, "Recovery successful")
        logger.info(f"🟢 [{self.algorithm_name}] Circuit CLOSED - normal operation restored")

    def _transition_to_open(self):
        """🔴 Transition vers état OPEN (bloqué)"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.success_count = 0
        
        self._record_state_change(old_state, self.state, f"Failure threshold reached: {self.failure_count}")
        logger.warning(f"🔴 [{self.algorithm_name}] Circuit OPEN - blocking calls for {self.config.recovery_timeout}s")

    def _transition_to_half_open(self):
        """🟡 Transition vers état HALF-OPEN (test)"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        
        self._record_state_change(old_state, self.state, "Testing recovery")
        logger.info(f"🟡 [{self.algorithm_name}] Circuit HALF-OPEN - testing recovery")

    def _record_state_change(self, old_state: CircuitState, new_state: CircuitState, reason: str):
        """Enregistre les changements d'état pour analytics"""
        change_record = {
            'timestamp': time.time(),
            'from_state': old_state.value,
            'to_state': new_state.value,
            'reason': reason,
            'failure_count': self.failure_count,
            'success_count': self.success_count
        }
        
        self.state_changes.append(change_record)
        
        # Limite l'historique à 50 changements
        if len(self.state_changes) > 50:
            self.state_changes.pop(0)

    def _update_response_time(self, execution_time: float):
        """Met à jour les statistiques de temps de réponse"""
        self.stats['response_times'].append(execution_time)
        
        # Garde seulement les 100 derniers temps
        if len(self.stats['response_times']) > 100:
            self.stats['response_times'].pop(0)
        
        # Recalcul moyenne
        if self.stats['response_times']:
            self.stats['avg_response_time'] = sum(self.stats['response_times']) / len(self.stats['response_times'])

    def get_health_status(self) -> Dict[str, Any]:
        """
        📊 STATUS DE SANTÉ DU CIRCUIT BREAKER
        
        Retourne un état détaillé pour monitoring.
        """
        
        # Calcul métriques avancées
        total_calls = self.stats['total_calls']
        if total_calls > 0:
            success_rate = (self.stats['successful_calls'] / total_calls) * 100
            failure_rate = (self.stats['failed_calls'] / total_calls) * 100
            timeout_rate = (self.stats['timeouts'] / total_calls) * 100
            slow_call_rate = (self.stats['slow_calls'] / total_calls) * 100
        else:
            success_rate = failure_rate = timeout_rate = slow_call_rate = 0
        
        # Temps depuis dernier changement d'état
        time_in_current_state = None
        if self.state_changes:
            last_change = self.state_changes[-1]['timestamp']
            time_in_current_state = time.time() - last_change
        
        return {
            'algorithm': self.algorithm_name,
            'circuit_state': self.state.value,
            'is_healthy': self.state != CircuitState.OPEN,
            'current_failures': self.failure_count,
            'failure_threshold': self.config.failure_threshold,
            'time_in_current_state': time_in_current_state,
            'next_recovery_attempt': self._get_next_recovery_time(),
            
            'performance_metrics': {
                'total_calls': total_calls,
                'success_rate': f"{success_rate:.1f}%",
                'failure_rate': f"{failure_rate:.1f}%",
                'timeout_rate': f"{timeout_rate:.1f}%",
                'slow_call_rate': f"{slow_call_rate:.1f}%",
                'avg_response_time': f"{self.stats['avg_response_time']:.3f}s",
                'last_success': self._format_timestamp(self.last_success_time),
                'last_failure': self._format_timestamp(self.last_failure_time)
            },
            
            'configuration': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'call_timeout': self.config.timeout,
                'slow_call_threshold': self.config.slow_call_threshold
            },
            
            'recent_state_changes': self.state_changes[-5:] if self.state_changes else []
        }

    def get_performance_analytics(self) -> Dict[str, Any]:
        """
        📈 ANALYTICS DE PERFORMANCE DÉTAILLÉES
        
        Analyse approfondie pour optimisation continue.
        """
        
        if not self.stats['response_times']:
            return {"message": "No performance data available yet"}
        
        response_times = self.stats['response_times']
        
        # Calculs statistiques
        response_times_sorted = sorted(response_times)
        count = len(response_times_sorted)
        
        percentiles = {
            'p50': response_times_sorted[int(0.5 * count)] if count > 0 else 0,
            'p90': response_times_sorted[int(0.9 * count)] if count > 0 else 0,
            'p95': response_times_sorted[int(0.95 * count)] if count > 0 else 0,
            'p99': response_times_sorted[int(0.99 * count)] if count > 0 else 0
        }
        
        # Tendances récentes (10 derniers appels)
        recent_times = response_times[-10:] if len(response_times) >= 10 else response_times
        recent_avg = sum(recent_times) / len(recent_times) if recent_times else 0
        
        # Détection tendances
        trend = "stable"
        if len(response_times) > 20:
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg * 1.2:
                trend = "degrading"
            elif second_avg < first_avg * 0.8:
                trend = "improving"
        
        return {
            'algorithm': self.algorithm_name,
            'performance_summary': {
                'total_samples': len(response_times),
                'avg_response_time': f"{self.stats['avg_response_time']:.3f}s",
                'recent_avg_response_time': f"{recent_avg:.3f}s",
                'performance_trend': trend
            },
            'response_time_percentiles': {
                f'{k}': f"{v:.3f}s" for k, v in percentiles.items()
            },
            'quality_indicators': {
                'fast_calls': len([t for t in response_times if t < 1.0]),
                'normal_calls': len([t for t in response_times if 1.0 <= t < 3.0]),
                'slow_calls': len([t for t in response_times if t >= 3.0]),
                'timeout_calls': self.stats['timeouts']
            },
            'stability_analysis': {
                'circuit_state_changes': len(self.state_changes),
                'time_in_open_state': self._calculate_time_in_open_state(),
                'recovery_success_rate': self._calculate_recovery_success_rate()
            },
            'recommendations': self._get_performance_recommendations(percentiles, trend)
        }

    def _get_next_recovery_time(self) -> Optional[str]:
        """Calcule le prochain temps de tentative de récupération"""
        if self.state != CircuitState.OPEN or not self.last_failure_time:
            return None
        
        next_attempt = self.last_failure_time + self.config.recovery_timeout
        if time.time() >= next_attempt:
            return "Now (ready for recovery attempt)"
        else:
            seconds_left = next_attempt - time.time()
            return f"In {seconds_left:.0f} seconds"

    def _format_timestamp(self, timestamp: Optional[float]) -> str:
        """Formate un timestamp pour affichage"""
        if not timestamp:
            return "Never"
        
        seconds_ago = time.time() - timestamp
        if seconds_ago < 60:
            return f"{seconds_ago:.0f}s ago"
        elif seconds_ago < 3600:
            return f"{seconds_ago/60:.0f}m ago"
        else:
            return f"{seconds_ago/3600:.1f}h ago"

    def _calculate_time_in_open_state(self) -> float:
        """Calcule le temps total passé en état OPEN"""
        total_open_time = 0.0
        
        for i, change in enumerate(self.state_changes):
            if change['to_state'] == 'open':
                # Trouve la fin de cette période OPEN
                end_time = time.time()  # Par défaut maintenant
                
                # Cherche le prochain changement qui sort de OPEN
                for j in range(i + 1, len(self.state_changes)):
                    if self.state_changes[j]['from_state'] == 'open':
                        end_time = self.state_changes[j]['timestamp']
                        break
                
                open_duration = end_time - change['timestamp']
                total_open_time += open_duration
        
        return total_open_time

    def _calculate_recovery_success_rate(self) -> float:
        """Calcule le taux de succès des récupérations"""
        recovery_attempts = 0
        successful_recoveries = 0
        
        for change in self.state_changes:
            if change['to_state'] == 'half_open':
                recovery_attempts += 1
            elif change['from_state'] == 'half_open' and change['to_state'] == 'closed':
                successful_recoveries += 1
        
        if recovery_attempts == 0:
            return 100.0  # Pas de récupération nécessaire
        
        return (successful_recoveries / recovery_attempts) * 100

    def _get_performance_recommendations(self, percentiles: Dict, trend: str) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        if percentiles['p95'] > 5.0:
            recommendations.append("⚡ P95 response time > 5s - consider algorithm optimization")
        
        if trend == "degrading":
            recommendations.append("📉 Performance degrading - investigate resource constraints")
        
        if self.stats['slow_calls'] / max(self.stats['total_calls'], 1) > 0.1:
            recommendations.append("🐌 >10% slow calls - review timeout configuration")
        
        if len(self.state_changes) > 10:
            recommendations.append("🔄 Frequent state changes - review failure thresholds")
        
        if not recommendations:
            recommendations.append("✅ Performance within acceptable parameters")
        
        return recommendations

    def reset_stats(self):
        """Reset des statistiques pour nouveau cycle"""
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'slow_calls': 0,
            'timeouts': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }
        self.state_changes.clear()
        logger.info(f"📊 [{self.algorithm_name}] Circuit breaker stats reset")

    def force_open(self, reason: str = "Manual intervention"):
        """Force l'ouverture du circuit (pour maintenance)"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self._record_state_change(old_state, self.state, f"Forced open: {reason}")
        logger.warning(f"🔴 [{self.algorithm_name}] Circuit FORCED OPEN: {reason}")

    def force_close(self, reason: str = "Manual intervention"):
        """Force la fermeture du circuit (pour récupération)"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self._record_state_change(old_state, self.state, f"Forced closed: {reason}")
        logger.info(f"🟢 [{self.algorithm_name}] Circuit FORCED CLOSED: {reason}")
