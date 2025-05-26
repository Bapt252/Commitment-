#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moniteur de Performance pour SuperSmartMatch
Suit les métriques d'utilisation et de performance des algorithmes
"""

import time
import threading
import psutil
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class ExecutionMetrics:
    """Métriques d'exécution d'un algorithme"""
    algorithm_name: str
    execution_time: float
    results_count: int
    timestamp: float
    memory_used: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class AlgorithmStats:
    """Statistiques d'un algorithme"""
    name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    avg_results_count: float
    avg_memory_usage: float
    avg_cpu_usage: float
    last_execution: Optional[float]
    success_rate: float

class PerformanceMonitor:
    """
    Moniteur de performance pour SuperSmartMatch
    """
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialise le moniteur de performance
        
        Args:
            max_history_size: Taille maximale de l'historique
        """
        self.max_history_size = max_history_size
        self.start_time = time.time()
        
        # Stockage des métriques
        self.execution_history: deque = deque(maxlen=max_history_size)
        self.algorithm_metrics: Dict[str, List[ExecutionMetrics]] = defaultdict(list)
        
        # Statistiques en temps réel
        self.current_stats: Dict[str, AlgorithmStats] = {}
        
        # Lock pour la thread safety
        self._lock = threading.Lock()
        
        # Métriques système
        self.system_metrics = {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "start_time": self.start_time
        }
        
        logger.info("Performance Monitor initialisé")
    
    def track_execution(
        self, 
        algorithm_name: str, 
        execution_time: float, 
        results_count: int,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Enregistre une exécution d'algorithme
        
        Args:
            algorithm_name: Nom de l'algorithme
            execution_time: Temps d'exécution en secondes
            results_count: Nombre de résultats retournés
            success: Si l'exécution a réussi
            error_message: Message d'erreur si échec
        """
        with self._lock:
            # Obtenir les métriques système actuelles
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Créer les métriques d'exécution
            metrics = ExecutionMetrics(
                algorithm_name=algorithm_name,
                execution_time=execution_time,
                results_count=results_count,
                timestamp=time.time(),
                memory_used=memory_info.percent,
                cpu_percent=cpu_percent,
                success=success,
                error_message=error_message
            )
            
            # Ajouter à l'historique
            self.execution_history.append(metrics)
            self.algorithm_metrics[algorithm_name].append(metrics)
            
            # Limiter la taille de l'historique par algorithme
            if len(self.algorithm_metrics[algorithm_name]) > self.max_history_size:
                self.algorithm_metrics[algorithm_name].pop(0)
            
            # Mettre à jour les statistiques
            self._update_algorithm_stats(algorithm_name)
            
            logger.debug(f"Execution tracked: {algorithm_name} - {execution_time:.3f}s")
    
    def _update_algorithm_stats(self, algorithm_name: str):
        """
        Met à jour les statistiques pour un algorithme
        
        Args:
            algorithm_name: Nom de l'algorithme
        """
        metrics_list = self.algorithm_metrics[algorithm_name]
        
        if not metrics_list:
            return
        
        successful_metrics = [m for m in metrics_list if m.success]
        failed_metrics = [m for m in metrics_list if not m.success]
        
        # Calculs des statistiques
        execution_times = [m.execution_time for m in successful_metrics]
        results_counts = [m.results_count for m in successful_metrics]
        memory_usages = [m.memory_used for m in successful_metrics]
        cpu_usages = [m.cpu_percent for m in successful_metrics]
        
        stats = AlgorithmStats(
            name=algorithm_name,
            total_executions=len(metrics_list),
            successful_executions=len(successful_metrics),
            failed_executions=len(failed_metrics),
            avg_execution_time=statistics.mean(execution_times) if execution_times else 0.0,
            min_execution_time=min(execution_times) if execution_times else 0.0,
            max_execution_time=max(execution_times) if execution_times else 0.0,
            avg_results_count=statistics.mean(results_counts) if results_counts else 0.0,
            avg_memory_usage=statistics.mean(memory_usages) if memory_usages else 0.0,
            avg_cpu_usage=statistics.mean(cpu_usages) if cpu_usages else 0.0,
            last_execution=metrics_list[-1].timestamp if metrics_list else None,
            success_rate=(len(successful_metrics) / len(metrics_list)) * 100 if metrics_list else 0.0
        )
        
        self.current_stats[algorithm_name] = stats
    
    def get_algorithm_stats(self, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les statistiques d'un algorithme
        
        Args:
            algorithm_name: Nom de l'algorithme
            
        Returns:
            Statistiques de l'algorithme ou None
        """
        with self._lock:
            stats = self.current_stats.get(algorithm_name)
            return asdict(stats) if stats else None
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne les statistiques de tous les algorithmes
        
        Returns:
            Dictionnaire des statistiques par algorithme
        """
        with self._lock:
            return {
                name: asdict(stats) 
                for name, stats in self.current_stats.items()
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques système actuelles
        
        Returns:
            Statistiques système
        """
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "cpu_percent": cpu_percent,
            "cpu_count": self.system_metrics["cpu_count"],
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "memory_total": memory.total,
            "uptime_seconds": time.time() - self.start_time,
            "total_executions": len(self.execution_history),
            "algorithms_count": len(self.current_stats)
        }
    
    def get_uptime(self) -> float:
        """
        Retourne l'uptime du service en secondes
        
        Returns:
            Uptime en secondes
        """
        return time.time() - self.start_time
    
    def get_recent_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retourne les exécutions récentes
        
        Args:
            limit: Nombre maximum d'exécutions à retourner
            
        Returns:
            Liste des exécutions récentes
        """
        with self._lock:
            recent = list(self.execution_history)[-limit:]
            return [asdict(metrics) for metrics in reversed(recent)]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des performances
        
        Returns:
            Résumé des performances
        """
        with self._lock:
            all_stats = self.get_all_stats()
            system_stats = self.get_system_stats()
            
            if not all_stats:
                return {
                    "summary": "Aucune exécution enregistrée",
                    "system": system_stats
                }
            
            # Calculs globaux
            total_executions = sum(stats["total_executions"] for stats in all_stats.values())
            total_successful = sum(stats["successful_executions"] for stats in all_stats.values())
            
            # Algorithme le plus utilisé
            most_used = max(all_stats.items(), key=lambda x: x[1]["total_executions"])
            
            # Algorithme le plus rapide
            fastest = min(
                all_stats.items(), 
                key=lambda x: x[1]["avg_execution_time"]
            )
            
            # Algorithme le plus fiable
            most_reliable = max(
                all_stats.items(),
                key=lambda x: x[1]["success_rate"]
            )
            
            return {
                "summary": {
                    "total_executions": total_executions,
                    "success_rate": (total_successful / total_executions * 100) if total_executions > 0 else 0,
                    "algorithms_count": len(all_stats),
                    "most_used_algorithm": {
                        "name": most_used[0],
                        "executions": most_used[1]["total_executions"]
                    },
                    "fastest_algorithm": {
                        "name": fastest[0],
                        "avg_time": fastest[1]["avg_execution_time"]
                    },
                    "most_reliable_algorithm": {
                        "name": most_reliable[0],
                        "success_rate": most_reliable[1]["success_rate"]
                    }
                },
                "algorithms": all_stats,
                "system": system_stats
            }
    
    def get_algorithm_comparison(self) -> Dict[str, Any]:
        """
        Compare les performances des algorithmes
        
        Returns:
            Comparaison des algorithmes
        """
        with self._lock:
            all_stats = self.get_all_stats()
            
            if len(all_stats) < 2:
                return {"message": "Besoin d'au moins 2 algorithmes pour comparer"}
            
            comparison = {
                "algorithms": [],
                "rankings": {
                    "by_speed": [],
                    "by_reliability": [],
                    "by_usage": [],
                    "by_results_count": []
                }
            }
            
            # Préparer les données pour comparaison
            for name, stats in all_stats.items():
                comparison["algorithms"].append({
                    "name": name,
                    "avg_execution_time": stats["avg_execution_time"],
                    "success_rate": stats["success_rate"],
                    "total_executions": stats["total_executions"],
                    "avg_results_count": stats["avg_results_count"]
                })
            
            # Classements
            comparison["rankings"]["by_speed"] = sorted(
                comparison["algorithms"],
                key=lambda x: x["avg_execution_time"]
            )
            
            comparison["rankings"]["by_reliability"] = sorted(
                comparison["algorithms"],
                key=lambda x: x["success_rate"],
                reverse=True
            )
            
            comparison["rankings"]["by_usage"] = sorted(
                comparison["algorithms"],
                key=lambda x: x["total_executions"],
                reverse=True
            )
            
            comparison["rankings"]["by_results_count"] = sorted(
                comparison["algorithms"],
                key=lambda x: x["avg_results_count"],
                reverse=True
            )
            
            return comparison
    
    def get_time_series_data(self, algorithm_name: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Retourne les données temporelles pour les graphiques
        
        Args:
            algorithm_name: Nom de l'algorithme (optionnel)
            hours: Nombre d'heures à inclure
            
        Returns:
            Données temporelles
        """
        with self._lock:
            cutoff_time = time.time() - (hours * 3600)
            
            if algorithm_name:
                # Données pour un algorithme spécifique
                metrics = [
                    m for m in self.algorithm_metrics.get(algorithm_name, [])
                    if m.timestamp >= cutoff_time
                ]
            else:
                # Données pour tous les algorithmes
                metrics = [
                    m for m in self.execution_history
                    if m.timestamp >= cutoff_time
                ]
            
            # Grouper par heure
            hourly_data = defaultdict(lambda: {
                "executions": 0,
                "avg_time": 0,
                "total_time": 0,
                "success_count": 0,
                "error_count": 0
            })
            
            for metric in metrics:
                hour_key = int(metric.timestamp // 3600) * 3600  # Arrondir à l'heure
                
                hourly_data[hour_key]["executions"] += 1
                hourly_data[hour_key]["total_time"] += metric.execution_time
                
                if metric.success:
                    hourly_data[hour_key]["success_count"] += 1
                else:
                    hourly_data[hour_key]["error_count"] += 1
            
            # Calculer les moyennes
            for hour_data in hourly_data.values():
                if hour_data["executions"] > 0:
                    hour_data["avg_time"] = hour_data["total_time"] / hour_data["executions"]
                    hour_data["success_rate"] = (hour_data["success_count"] / hour_data["executions"]) * 100
            
            # Convertir en format adapté pour les graphiques
            time_series = []
            for timestamp, data in sorted(hourly_data.items()):
                time_series.append({
                    "timestamp": timestamp,
                    "datetime": time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp)),
                    **data
                })
            
            return {
                "algorithm_name": algorithm_name or "all",
                "hours_range": hours,
                "data_points": len(time_series),
                "time_series": time_series
            }
    
    def clear_stats(self, algorithm_name: Optional[str] = None):
        """
        Efface les statistiques
        
        Args:
            algorithm_name: Nom de l'algorithme (optionnel, sinon tout effacer)
        """
        with self._lock:
            if algorithm_name:
                # Effacer pour un algorithme spécifique
                if algorithm_name in self.algorithm_metrics:
                    del self.algorithm_metrics[algorithm_name]
                if algorithm_name in self.current_stats:
                    del self.current_stats[algorithm_name]
                
                # Supprimer de l'historique global
                self.execution_history = deque(
                    [m for m in self.execution_history if m.algorithm_name != algorithm_name],
                    maxlen=self.max_history_size
                )
            else:
                # Tout effacer
                self.execution_history.clear()
                self.algorithm_metrics.clear()
                self.current_stats.clear()
            
            logger.info(f"Stats cleared for: {algorithm_name or 'all algorithms'}")
    
    def export_stats(self, format: str = "json") -> str:
        """
        Exporte les statistiques
        
        Args:
            format: Format d'export ("json" ou "csv")
            
        Returns:
            Données exportées
        """
        with self._lock:
            if format.lower() == "json":
                import json
                export_data = {
                    "export_timestamp": time.time(),
                    "uptime_seconds": self.get_uptime(),
                    "system_stats": self.get_system_stats(),
                    "algorithm_stats": self.get_all_stats(),
                    "recent_executions": self.get_recent_executions(100)
                }
                return json.dumps(export_data, indent=2)
            
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                
                # En-têtes CSV
                fieldnames = [
                    "algorithm", "timestamp", "execution_time", 
                    "results_count", "memory_used", "cpu_percent", 
                    "success", "error_message"
                ]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                # Données
                for metrics in self.execution_history:
                    writer.writerow({
                        "algorithm": metrics.algorithm_name,
                        "timestamp": metrics.timestamp,
                        "execution_time": metrics.execution_time,
                        "results_count": metrics.results_count,
                        "memory_used": metrics.memory_used,
                        "cpu_percent": metrics.cpu_percent,
                        "success": metrics.success,
                        "error_message": metrics.error_message or ""
                    })
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Format non supporté: {format}")
    
    def set_alert_thresholds(self, thresholds: Dict[str, float]):
        """
        Configure les seuils d'alerte
        
        Args:
            thresholds: Seuils d'alerte
        """
        self.alert_thresholds = {
            "max_execution_time": thresholds.get("max_execution_time", 5.0),
            "min_success_rate": thresholds.get("min_success_rate", 90.0),
            "max_memory_usage": thresholds.get("max_memory_usage", 80.0),
            "max_cpu_usage": thresholds.get("max_cpu_usage", 90.0)
        }
        
        logger.info(f"Alert thresholds configured: {self.alert_thresholds}")
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Vérifie les seuils d'alerte
        
        Returns:
            Liste des alertes actives
        """
        alerts = []
        
        if not hasattr(self, 'alert_thresholds'):
            return alerts
        
        with self._lock:
            for algorithm_name, stats in self.current_stats.items():
                # Vérifier le temps d'exécution
                if stats.avg_execution_time > self.alert_thresholds["max_execution_time"]:
                    alerts.append({
                        "type": "execution_time",
                        "algorithm": algorithm_name,
                        "value": stats.avg_execution_time,
                        "threshold": self.alert_thresholds["max_execution_time"],
                        "message": f"Temps d'exécution élevé pour {algorithm_name}"
                    })
                
                # Vérifier le taux de succès
                if stats.success_rate < self.alert_thresholds["min_success_rate"]:
                    alerts.append({
                        "type": "success_rate",
                        "algorithm": algorithm_name,
                        "value": stats.success_rate,
                        "threshold": self.alert_thresholds["min_success_rate"],
                        "message": f"Taux de succès faible pour {algorithm_name}"
                    })
        
        return alerts
