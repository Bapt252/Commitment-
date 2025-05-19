"""
Auto-tuning des poids basé sur le feedback utilisateur.

Ce module implémente un système d'auto-ajustement des poids
du système de matching basé sur l'analyse du feedback utilisateur
et des métriques de performance en temps réel.
"""

import logging
import time
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque

import numpy as np

from ..core.models import MatchResult

logger = logging.getLogger(__name__)


@dataclass
class FeedbackTrend:
    """Tendance du feedback utilisateur."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend_direction: str  # 'improving', 'stable', 'declining'
    confidence: float  # 0-1, confidence in the trend


@dataclass
class WeightAdjustment:
    """Ajustement suggéré pour un poids."""
    parameter_name: str
    current_weight: float
    suggested_weight: float
    adjustment_magnitude: float
    reasoning: str
    confidence: float


@dataclass
class TuningResult:
    """Résultat d'une session d'auto-tuning."""
    adjustments: List[WeightAdjustment]
    total_adjustments: int
    avg_confidence: float
    expected_improvement: float
    tuning_time: float
    feedback_score_before: float
    feedback_score_after: Optional[float] = None


class WeightTuner:
    """
    Auto-tuning des poids basé sur le feedback utilisateur.
    
    Analyse le feedback utilisateur en temps réel et ajuste
    automatiquement les poids du système de matching pour
    optimiser la satisfaction utilisateur.
    
    Fonctionnalités:
    - Collecte et analyse du feedback utilisateur
    - Détection des tendances de satisfaction
    - Ajustement automatique des poids
    - Historique et rollback des ajustements
    - Validation des améliorations
    """
    
    def __init__(self, 
                 enhanced_matcher=None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise le weight tuner.
        
        Args:
            enhanced_matcher: Matcher à optimiser
            config: Configuration spécifique
        """
        self.enhanced_matcher = enhanced_matcher
        self.config = config or self._get_default_config()
        
        # Configuration du tuning
        self.feedback_window_hours = self.config.get('feedback_window_hours', 24)
        self.min_feedback_count = self.config.get('min_feedback_count', 10)
        self.adjustment_sensitivity = self.config.get('adjustment_sensitivity', 0.1)
        self.max_weight_change = self.config.get('max_weight_change', 0.2)
        self.learning_rate = self.config.get('learning_rate', 0.01)
        
        # Seuils de détection de tendances
        self.trend_detection_threshold = self.config.get('trend_detection_threshold', 0.05)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        # État interne
        self.feedback_history = deque(maxlen=1000)
        self.weight_history = []
        self.tuning_history = []
        self.performance_baselines = {}
        
        # Cache pour optimisation
        self.cached_trends = {}
        self.last_trend_calculation = None
        self.trend_cache_duration = timedelta(minutes=15)
        
        logger.info(f"WeightTuner initialized with config: {self.config}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut du tuner."""
        return {
            'feedback_window_hours': 24,
            'min_feedback_count': 10,
            'adjustment_sensitivity': 0.1,
            'max_weight_change': 0.2,
            'learning_rate': 0.01,
            'trend_detection_threshold': 0.05,
            'confidence_threshold': 0.7,
            'enable_auto_tuning': True,
            'tuning_frequency_hours': 6,
            'validation_samples': 50,
            'rollback_threshold': -0.1,  # Rollback si dégradation > 10%
            'feedback_types': {
                'click': 0.3,
                'apply': 0.6,
                'interview': 0.8,
                'hire': 1.0,
                'rating': 1.0
            }
        }
    
    async def collect_user_feedback(self, 
                                   candidate_id: str,
                                   job_id: str,
                                   feedback_type: str,
                                   feedback_value: Any,
                                   matcher_config: Optional[Dict[str, Any]] = None,
                                   timestamp: Optional[datetime] = None) -> None:
        """
        Collecte le feedback utilisateur pour le matching.
        
        Args:
            candidate_id: ID du candidat
            job_id: ID du job
            feedback_type: Type de feedback ('click', 'apply', 'rating', etc.)
            feedback_value: Valeur du feedback (bool, int, float)
            matcher_config: Configuration du matcher au moment du matching
            timestamp: Timestamp du feedback (now si None)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Normaliser le feedback en score 0-1
        normalized_score = self._normalize_feedback(feedback_type, feedback_value)
        
        feedback_entry = {
            'candidate_id': candidate_id,
            'job_id': job_id,
            'feedback_type': feedback_type,
            'feedback_value': feedback_value,
            'normalized_score': normalized_score,
            'matcher_config': matcher_config or {},
            'timestamp': timestamp
        }
        
        self.feedback_history.append(feedback_entry)
        
        logger.debug(f"Collected feedback: {feedback_type}={feedback_value} "
                    f"(normalized={normalized_score:.3f}) for {candidate_id}/{job_id}")
        
        # Déclencher un auto-tuning si configuré
        if (self.config.get('enable_auto_tuning', True) and 
            len(self.feedback_history) % self.config.get('auto_tuning_interval', 50) == 0):
            await self._trigger_auto_tuning()
    
    def _normalize_feedback(self, feedback_type: str, feedback_value: Any) -> float:
        """Normalise le feedback en score entre 0 et 1."""
        feedback_weights = self.config.get('feedback_types', {})
        
        if feedback_type == 'rating':
            # Assumer que les ratings sont sur une échelle (ex: 1-5)
            if isinstance(feedback_value, (int, float)):
                # Détecter l'échelle automatiquement
                if feedback_value <= 1:
                    return feedback_value  # Déjà normalisé
                elif feedback_value <= 5:
                    return (feedback_value - 1) / 4  # Échelle 1-5
                elif feedback_value <= 10:
                    return feedback_value / 10  # Échelle 0-10
                else:
                    return min(1.0, feedback_value / 100)  # Échelle 0-100
            else:
                return 0.5
        
        elif feedback_type in ['click', 'apply', 'interview', 'hire']:
            # Feedback binaire
            base_score = feedback_weights.get(feedback_type, 0.5)
            if isinstance(feedback_value, bool):
                return base_score if feedback_value else 0.0
            else:
                return base_score if feedback_value else 0.0
        
        elif feedback_type == 'time_spent':
            # Temps passé sur une offre (en secondes)
            if isinstance(feedback_value, (int, float)):
                # Plus de temps = plus d'intérêt
                return min(1.0, feedback_value / 300)  # Max à 5 minutes
            else:
                return 0.5
        
        else:
            # Feedback inconnu, essayer de le normaliser
            if isinstance(feedback_value, bool):
                return 1.0 if feedback_value else 0.0
            elif isinstance(feedback_value, (int, float)):
                if 0 <= feedback_value <= 1:
                    return feedback_value
                else:
                    return min(1.0, max(0.0, feedback_value / 5))
            else:
                return 0.5
    
    async def analyze_feedback_trends(self, 
                                    window_hours: Optional[int] = None) -> List[FeedbackTrend]:
        """
        Analyse les tendances du feedback utilisateur.
        
        Args:
            window_hours: Fenêtre d'analyse en heures
            
        Returns:
            Liste des tendances détectées
        """
        window_hours = window_hours or self.feedback_window_hours
        
        # Vérifier le cache
        now = datetime.now()
        if (self.last_trend_calculation and 
            self.cached_trends and 
            now - self.last_trend_calculation < self.trend_cache_duration):
            return self.cached_trends.get('trends', [])
        
        # Filtrer le feedback récent
        cutoff_time = now - timedelta(hours=window_hours)
        recent_feedback = [
            fb for fb in self.feedback_history 
            if fb['timestamp'] >= cutoff_time
        ]
        
        if len(recent_feedback) < self.min_feedback_count:
            logger.warning(f"Not enough recent feedback ({len(recent_feedback)}) for trend analysis")
            return []
        
        trends = []
        
        try:
            # 1. Tendance de satisfaction globale
            satisfaction_trend = await self._analyze_satisfaction_trend(recent_feedback)
            if satisfaction_trend:
                trends.append(satisfaction_trend)
            
            # 2. Tendances par type de feedback
            feedback_type_trends = await self._analyze_feedback_type_trends(recent_feedback)
            trends.extend(feedback_type_trends)
            
            # 3. Tendances par configuration de matcher
            config_trends = await self._analyze_config_trends(recent_feedback)
            trends.extend(config_trends)
            
            # 4. Tendances temporelles
            temporal_trends = await self._analyze_temporal_trends(recent_feedback)
            trends.extend(temporal_trends)
            
            # Cache les résultats
            self.cached_trends = {'trends': trends}
            self.last_trend_calculation = now
            
            logger.info(f"Analyzed {len(recent_feedback)} feedback entries, found {len(trends)} trends")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing feedback trends: {e}")
            return []
    
    async def _analyze_satisfaction_trend(self, 
                                        feedback_data: List[Dict[str, Any]]) -> Optional[FeedbackTrend]:
        """Analyse la tendance de satisfaction globale."""
        if len(feedback_data) < 6:  # Besoin d'au moins 6 points
            return None
        
        # Diviser en deux périodes
        mid_point = len(feedback_data) // 2
        first_half = feedback_data[:mid_point]
        second_half = feedback_data[mid_point:]
        
        # Calculer les scores moyens
        first_score = statistics.mean(fb['normalized_score'] for fb in first_half)
        second_score = statistics.mean(fb['normalized_score'] for fb in second_half)
        
        # Calculer le changement
        change = (second_score - first_score) / first_score * 100 if first_score > 0 else 0
        
        # Déterminer la direction de la tendance
        if abs(change) < self.trend_detection_threshold * 100:
            direction = 'stable'
        elif change > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        # Calculer la confiance basée sur la cohérence
        confidence = self._calculate_trend_confidence(feedback_data, 'satisfaction')
        
        return FeedbackTrend(
            metric_name='overall_satisfaction',
            current_value=second_score,
            previous_value=first_score,
            change_percentage=change,
            trend_direction=direction,
            confidence=confidence
        )
    
    async def _analyze_feedback_type_trends(self, 
                                          feedback_data: List[Dict[str, Any]]) -> List[FeedbackTrend]:
        """Analyse les tendances par type de feedback."""
        trends = []
        
        # Grouper par type de feedback
        by_type = defaultdict(list)
        for fb in feedback_data:
            by_type[fb['feedback_type']].append(fb)
        
        for feedback_type, type_feedback in by_type.items():
            if len(type_feedback) < 4:  # Pas assez de données
                continue
            
            # Diviser en deux périodes
            mid = len(type_feedback) // 2
            first_half = type_feedback[:mid]
            second_half = type_feedback[mid:]
            
            first_score = statistics.mean(fb['normalized_score'] for fb in first_half)
            second_score = statistics.mean(fb['normalized_score'] for fb in second_half)
            
            change = (second_score - first_score) / first_score * 100 if first_score > 0 else 0
            
            if abs(change) < self.trend_detection_threshold * 100:
                direction = 'stable'
            elif change > 0:
                direction = 'improving'
            else:
                direction = 'declining'
            
            confidence = self._calculate_trend_confidence(type_feedback, feedback_type)
            
            trends.append(FeedbackTrend(
                metric_name=f'{feedback_type}_satisfaction',
                current_value=second_score,
                previous_value=first_score,
                change_percentage=change,
                trend_direction=direction,
                confidence=confidence
            ))
        
        return trends
    
    async def _analyze_config_trends(self, 
                                   feedback_data: List[Dict[str, Any]]) -> List[FeedbackTrend]:
        """Analyse les tendances par configuration de matcher."""
        trends = []
        
        # Grouper par configuration majeure (ex: matching_mode)
        config_groups = defaultdict(list)
        
        for fb in feedback_data:
            matcher_config = fb.get('matcher_config', {})
            
            # Grouper par mode de matching
            mode = matcher_config.get('matching_mode', 'unknown')
            config_groups[f'mode_{mode}'].append(fb)
            
            # Grouper par seuils (buckets)
            semantic_threshold = matcher_config.get('semantic_threshold', 0.75)
            threshold_bucket = f"threshold_{int(semantic_threshold * 10) / 10}"
            config_groups[threshold_bucket].append(fb)
        
        for config_key, config_feedback in config_groups.items():
            if len(config_feedback) < 4:
                continue
            
            # Calculer la satisfaction moyenne pour cette configuration
            avg_score = statistics.mean(fb['normalized_score'] for fb in config_feedback)
            
            # Comparer avec la satisfaction globale
            overall_score = statistics.mean(fb['normalized_score'] for fb in feedback_data)
            
            change = (avg_score - overall_score) / overall_score * 100 if overall_score > 0 else 0
            
            direction = 'above_average' if change > 5 else 'below_average' if change < -5 else 'average'
            
            confidence = min(1.0, len(config_feedback) / 20)  # Plus de données = plus de confiance
            
            trends.append(FeedbackTrend(
                metric_name=f'config_{config_key}',
                current_value=avg_score,
                previous_value=overall_score,
                change_percentage=change,
                trend_direction=direction,
                confidence=confidence
            ))
        
        return trends
    
    async def _analyze_temporal_trends(self, 
                                     feedback_data: List[Dict[str, Any]]) -> List[FeedbackTrend]:
        """Analyse les tendances temporelles (par heure de la journée, jour de la semaine)."""
        trends = []
        
        # Grouper par heure de la journée
        by_hour = defaultdict(list)
        for fb in feedback_data:
            hour = fb['timestamp'].hour
            by_hour[hour].append(fb)
        
        # Trouver les heures avec le plus/moins de satisfaction
        hour_scores = {}
        for hour, hour_feedback in by_hour.items():
            if len(hour_feedback) >= 3:
                hour_scores[hour] = statistics.mean(fb['normalized_score'] for fb in hour_feedback)
        
        if hour_scores:
            best_hour = max(hour_scores, key=hour_scores.get)
            worst_hour = min(hour_scores, key=hour_scores.get)
            
            if hour_scores[best_hour] - hour_scores[worst_hour] > 0.1:  # Différence significative
                trends.append(FeedbackTrend(
                    metric_name='temporal_satisfaction',
                    current_value=hour_scores[best_hour],
                    previous_value=hour_scores[worst_hour],
                    change_percentage=(hour_scores[best_hour] - hour_scores[worst_hour]) * 100,
                    trend_direction=f'peak_at_hour_{best_hour}',
                    confidence=0.6
                ))
        
        return trends
    
    def _calculate_trend_confidence(self, 
                                  feedback_data: List[Dict[str, Any]], 
                                  metric_type: str) -> float:
        """Calcule la confiance dans une tendance détectée."""
        if len(feedback_data) < 4:
            return 0.0
        
        # Facteurs qui influencent la confiance:
        # 1. Nombre de points de données
        data_confidence = min(1.0, len(feedback_data) / 50)
        
        # 2. Consistance de la tendance
        scores = [fb['normalized_score'] for fb in feedback_data]
        if len(scores) > 1:
            # Calculer la variation
            std_dev = statistics.stdev(scores)
            consistency_confidence = max(0.0, 1.0 - std_dev * 2)
        else:
            consistency_confidence = 0.5
        
        # 3. Récence des données
        now = datetime.now()
        recency_scores = []
        for fb in feedback_data:
            hours_ago = (now - fb['timestamp']).total_seconds() / 3600
            recency_score = max(0.0, 1.0 - hours_ago / (self.feedback_window_hours * 2))
            recency_scores.append(recency_score)
        
        recency_confidence = statistics.mean(recency_scores) if recency_scores else 0.5
        
        # Combiner les facteurs
        overall_confidence = (
            data_confidence * 0.4 +
            consistency_confidence * 0.4 +
            recency_confidence * 0.2
        )
        
        return overall_confidence
    
    async def suggest_weight_adjustments(self, 
                                       trends: Optional[List[FeedbackTrend]] = None) -> List[WeightAdjustment]:
        """
        Suggère des ajustements de poids basés sur les tendances.
        
        Args:
            trends: Tendances à analyser (calcule si None)
            
        Returns:
            Liste d'ajustements suggérés
        """
        if trends is None:
            trends = await self.analyze_feedback_trends()
        
        if not trends:
            logger.info("No trends available for weight adjustment suggestions")
            return []
        
        adjustments = []
        
        try:
            # Obtenir la configuration actuelle
            if self.enhanced_matcher:
                current_config = self.enhanced_matcher.get_configuration()
            else:
                current_config = {}
            
            # Analyser chaque tendance pour suggérer des ajustements
            for trend in trends:
                if trend.confidence < self.confidence_threshold:
                    continue
                
                suggested_adjustments = self._analyze_trend_for_adjustments(trend, current_config)
                adjustments.extend(suggested_adjustments)
            
            # Consolider les ajustements multiples pour le même paramètre
            consolidated_adjustments = self._consolidate_adjustments(adjustments)
            
            # Valider et limiter les ajustements
            validated_adjustments = self._validate_adjustments(consolidated_adjustments, current_config)
            
            logger.info(f"Generated {len(validated_adjustments)} weight adjustment suggestions")
            return validated_adjustments
            
        except Exception as e:
            logger.error(f"Error suggesting weight adjustments: {e}")
            return []
    
    def _analyze_trend_for_adjustments(self, 
                                     trend: FeedbackTrend,
                                     current_config: Dict[str, Any]) -> List[WeightAdjustment]:
        """Analyse une tendance pour suggérer des ajustements spécifiques."""
        adjustments = []
        
        metric = trend.metric_name
        direction = trend.trend_direction
        change = trend.change_percentage
        confidence = trend.confidence
        
        # Règles d'ajustement basées sur les tendances
        
        # 1. Satisfaction globale en déclin
        if metric == 'overall_satisfaction' and direction == 'declining':
            # Si satisfaction globale décline, ajuster les poids principaux
            
            if 'embeddings_weight' in current_config:
                # Augmenter le poids des embeddings si disponible
                current_weight = current_config.get('embeddings_weight', 0.7)
                suggested_weight = min(0.9, current_weight + abs(change) * 0.01)
                
                adjustments.append(WeightAdjustment(
                    parameter_name='embeddings_weight',
                    current_weight=current_weight,
                    suggested_weight=suggested_weight,
                    adjustment_magnitude=suggested_weight - current_weight,
                    reasoning=f"Increasing embeddings weight due to declining satisfaction ({change:.1f}%)",
                    confidence=confidence
                ))
            
            if 'semantic_threshold' in current_config:
                # Réduire le seuil sémantique pour plus de matches
                current_threshold = current_config.get('semantic_threshold', 0.75)
                suggested_threshold = max(0.6, current_threshold - abs(change) * 0.002)
                
                adjustments.append(WeightAdjustment(
                    parameter_name='semantic_threshold',
                    current_weight=current_threshold,
                    suggested_weight=suggested_threshold,
                    adjustment_magnitude=suggested_threshold - current_threshold,
                    reasoning=f"Lowering semantic threshold to increase match flexibility",
                    confidence=confidence
                ))
        
        # 2. Satisfaction en amélioration avec un mode spécifique
        elif 'mode_' in metric and direction == 'above_average':
            mode = metric.split('mode_')[1]
            
            if mode in ['embeddings_only', 'hybrid']:
                # Favoriser les embeddings
                current_weight = current_config.get('embeddings_weight', 0.7)
                suggested_weight = min(0.9, current_weight + 0.05)
                
                adjustments.append(WeightAdjustment(
                    parameter_name='embeddings_weight',
                    current_weight=current_weight,
                    suggested_weight=suggested_weight,
                    adjustment_magnitude=suggested_weight - current_weight,
                    reasoning=f"Mode {mode} showing good results, increasing embeddings weight",
                    confidence=confidence
                ))
        
        # 3. Tendances de performance par seuil
        elif 'threshold_' in metric:
            threshold_value = float(metric.split('threshold_')[1])
            
            if direction == 'above_average':
                # Ce seuil donne de bons résultats
                current_threshold = current_config.get('semantic_threshold', 0.75)
                # Ajuster doucement vers ce seuil
                target_threshold = threshold_value
                suggested_threshold = current_threshold + (target_threshold - current_threshold) * 0.3
                
                adjustments.append(WeightAdjustment(
                    parameter_name='semantic_threshold',
                    current_weight=current_threshold,
                    suggested_weight=suggested_threshold,
                    adjustment_magnitude=suggested_threshold - current_threshold,
                    reasoning=f"Threshold {threshold_value} shows better satisfaction",
                    confidence=confidence
                ))
        
        # 4. Types de feedback spécifiques
        elif '_satisfaction' in metric and metric != 'overall_satisfaction':
            feedback_type = metric.split('_satisfaction')[0]
            
            if direction == 'declining':
                # Ajuster en fonction du type de feedback qui décline
                if feedback_type == 'click':
                    # Améliorer la diversité des résultats
                    if 'max_expanded_skills' in current_config:
                        current_expanded = current_config.get('max_expanded_skills', 5)
                        suggested_expanded = min(10, current_expanded + 1)
                        
                        adjustments.append(WeightAdjustment(
                            parameter_name='max_expanded_skills',
                            current_weight=float(current_expanded),
                            suggested_weight=float(suggested_expanded),
                            adjustment_magnitude=float(suggested_expanded - current_expanded),
                            reasoning=f"Increasing skills expansion due to declining click-through",
                            confidence=confidence
                        ))
                
                elif feedback_type == 'apply':
                    # Améliorer la précision des matches
                    current_bonus = current_config.get('essential_skill_bonus', 1.5)
                    suggested_bonus = min(2.0, current_bonus + 0.1)
                    
                    adjustments.append(WeightAdjustment(
                        parameter_name='essential_skill_bonus',
                        current_weight=current_bonus,
                        suggested_weight=suggested_bonus,
                        adjustment_magnitude=suggested_bonus - current_bonus,
                        reasoning=f"Increasing skill bonus due to declining application rate",
                        confidence=confidence
                    ))
        
        return adjustments
    
    def _consolidate_adjustments(self, 
                               adjustments: List[WeightAdjustment]) -> List[WeightAdjustment]:
        """Consolide les ajustements multiples pour le même paramètre."""
        consolidated = {}
        
        for adj in adjustments:
            param = adj.parameter_name
            
            if param not in consolidated:
                consolidated[param] = adj
            else:
                # Moyenner les ajustements, pondérés par la confiance
                existing = consolidated[param]
                
                # Poids basés sur la confiance
                total_confidence = existing.confidence + adj.confidence
                w1 = existing.confidence / total_confidence
                w2 = adj.confidence / total_confidence
                
                # Nouvelle suggestion pondérée
                new_suggested = (existing.suggested_weight * w1 + adj.suggested_weight * w2)
                
                # Nouveau reasoning combiné
                new_reasoning = f"{existing.reasoning}; {adj.reasoning}"
                
                consolidated[param] = WeightAdjustment(
                    parameter_name=param,
                    current_weight=existing.current_weight,
                    suggested_weight=new_suggested,
                    adjustment_magnitude=new_suggested - existing.current_weight,
                    reasoning=new_reasoning,
                    confidence=(existing.confidence + adj.confidence) / 2
                )
        
        return list(consolidated.values())
    
    def _validate_adjustments(self, 
                            adjustments: List[WeightAdjustment],
                            current_config: Dict[str, Any]) -> List[WeightAdjustment]:
        """Valide et limite les ajustements proposés."""
        validated = []
        
        for adj in adjustments:
            # Limiter l'amplitude du changement
            max_change = self.max_weight_change
            if abs(adj.adjustment_magnitude) > max_change:
                # Réduire l'ajustement
                sign = 1 if adj.adjustment_magnitude > 0 else -1
                limited_magnitude = sign * max_change
                limited_suggested = adj.current_weight + limited_magnitude
                
                adj = WeightAdjustment(
                    parameter_name=adj.parameter_name,
                    current_weight=adj.current_weight,
                    suggested_weight=limited_suggested,
                    adjustment_magnitude=limited_magnitude,
                    reasoning=f"{adj.reasoning} (magnitude limited to {max_change})",
                    confidence=adj.confidence
                )
            
            # Vérifier les contraintes spécifiques par paramètre
            if adj.parameter_name in ['embeddings_weight', 'tfidf_weight']:
                # Poids entre 0.1 et 0.9
                adj.suggested_weight = max(0.1, min(0.9, adj.suggested_weight))
            elif adj.parameter_name in ['semantic_threshold', 'synonym_threshold']:
                # Seuils entre 0.5 et 0.95
                adj.suggested_weight = max(0.5, min(0.95, adj.suggested_weight))
            elif adj.parameter_name == 'max_expanded_skills':
                # Entier entre 1 et 15
                adj.suggested_weight = max(1.0, min(15.0, round(adj.suggested_weight)))
            elif adj.parameter_name == 'essential_skill_bonus':
                # Bonus entre 1.0 et 3.0
                adj.suggested_weight = max(1.0, min(3.0, adj.suggested_weight))
            
            # Recalculer l'amplitude après validation
            adj.adjustment_magnitude = adj.suggested_weight - adj.current_weight
            
            # Garder seulement les ajustements significatifs
            if abs(adj.adjustment_magnitude) > 0.001:  # Seuil minimal
                validated.append(adj)
        
        return validated
    
    async def apply_adjustments(self, 
                              adjustments: List[WeightAdjustment],
                              validate_improvement: bool = True) -> TuningResult:
        """
        Applique les ajustements suggérés au matcher.
        
        Args:
            adjustments: Ajustements à appliquer
            validate_improvement: Valider l'amélioration après application
            
        Returns:
            Résultat du tuning avec métriques
        """
        if not adjustments:
            logger.info("No adjustments to apply")
            return TuningResult(
                adjustments=[],
                total_adjustments=0,
                avg_confidence=0.0,
                expected_improvement=0.0,
                tuning_time=0.0,
                feedback_score_before=0.0
            )
        
        start_time = time.time()
        
        try:
            # Mesurer les performances avant
            feedback_score_before = await self._measure_current_feedback_score()
            
            # Sauvegarder la configuration actuelle
            if self.enhanced_matcher:
                original_config = self.enhanced_matcher.get_configuration()
                self._save_config_to_history(original_config)
            else:
                original_config = {}
            
            # Appliquer les ajustements
            applied_adjustments = []
            for adj in adjustments:
                try:
                    if self.enhanced_matcher:
                        setattr(self.enhanced_matcher, adj.parameter_name, adj.suggested_weight)
                        # Mettre à jour la config interne aussi
                        self.enhanced_matcher.config[adj.parameter_name] = adj.suggested_weight
                    
                    applied_adjustments.append(adj)
                    logger.info(f"Applied adjustment: {adj.parameter_name} "
                              f"{adj.current_weight:.3f} -> {adj.suggested_weight:.3f}")
                    
                except Exception as e:
                    logger.error(f"Failed to apply adjustment for {adj.parameter_name}: {e}")
            
            # Calculer les métriques de résultat
            total_adjustments = len(applied_adjustments)
            avg_confidence = statistics.mean(adj.confidence for adj in applied_adjustments) if applied_adjustments else 0.0
            
            # Estimer l'amélioration attendue
            expected_improvement = sum(
                abs(adj.adjustment_magnitude) * adj.confidence
                for adj in applied_adjustments
            ) / total_adjustments if total_adjustments > 0 else 0.0
            
            tuning_time = time.time() - start_time
            
            # Validation de l'amélioration si demandée
            feedback_score_after = None
            if validate_improvement and self.enhanced_matcher:
                # Attendre un peu pour collecter de nouveaux feedbacks
                import asyncio
                await asyncio.sleep(1)  # Simulation
                feedback_score_after = await self._measure_current_feedback_score()
            
            result = TuningResult(
                adjustments=applied_adjustments,
                total_adjustments=total_adjustments,
                avg_confidence=avg_confidence,
                expected_improvement=expected_improvement,
                tuning_time=tuning_time,
                feedback_score_before=feedback_score_before,
                feedback_score_after=feedback_score_after
            )
            
            self.tuning_history.append(result)
            
            logger.info(f"Applied {total_adjustments} adjustments in {tuning_time:.2f}s, "
                       f"avg_confidence={avg_confidence:.3f}, "
                       f"expected_improvement={expected_improvement:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying adjustments: {e}")
            # En cas d'erreur, essayer de restaurer la config originale
            if self.enhanced_matcher and original_config:
                try:
                    for key, value in original_config.items():
                        if hasattr(self.enhanced_matcher, key):
                            setattr(self.enhanced_matcher, key, value)
                except Exception as restore_error:
                    logger.error(f"Failed to restore configuration: {restore_error}")
            
            raise
    
    async def _trigger_auto_tuning(self) -> None:
        """Déclenche un auto-tuning automatique."""
        logger.info("Triggering automatic weight tuning...")
        
        try:
            # Analyser les tendances
            trends = await self.analyze_feedback_trends()
            
            if not trends:
                logger.info("No trends detected, skipping auto-tuning")
                return
            
            # Suggérer des ajustements
            adjustments = await self.suggest_weight_adjustments(trends)
            
            if not adjustments:
                logger.info("No adjustments suggested, skipping auto-tuning")
                return
            
            # Filtrer les ajustements les plus confiants
            confident_adjustments = [
                adj for adj in adjustments 
                if adj.confidence >= self.confidence_threshold
            ]
            
            if confident_adjustments:
                # Appliquer les ajustements
                result = await self.apply_adjustments(confident_adjustments)
                logger.info(f"Auto-tuning completed: {result.total_adjustments} adjustments applied")
            else:
                logger.info("No confident adjustments found, skipping auto-tuning")
                
        except Exception as e:
            logger.error(f"Error in auto-tuning: {e}")
    
    async def _measure_current_feedback_score(self) -> float:
        """Mesure le score de feedback actuel."""
        if not self.feedback_history:
            return 0.5
        
        # Calculer le score des feedbacks récents
        recent_feedbacks = list(self.feedback_history)[-50:]  # Derniers 50 feedbacks
        
        if recent_feedbacks:
            return statistics.mean(fb['normalized_score'] for fb in recent_feedbacks)
        else:
            return 0.5
    
    def _save_config_to_history(self, config: Dict[str, Any]) -> None:
        """Sauvegarde une configuration dans l'historique."""
        config_entry = {
            'timestamp': datetime.now(),
            'config': config.copy()
        }
        self.weight_history.append(config_entry)
        
        # Limiter la taille de l'historique
        if len(self.weight_history) > 100:
            self.weight_history = self.weight_history[-100:]
    
    def rollback_to_previous_config(self, steps_back: int = 1) -> bool:
        """
        Rollback vers une configuration précédente.
        
        Args:
            steps_back: Nombre d'étapes à remonter
            
        Returns:
            True si le rollback a réussi
        """
        if len(self.weight_history) < steps_back + 1:
            logger.warning(f"Not enough history for rollback (need {steps_back + 1}, have {len(self.weight_history)})")
            return False
        
        try:
            # Obtenir la configuration à restaurer
            target_config = self.weight_history[-(steps_back + 1)]['config']
            
            # Appliquer la configuration
            if self.enhanced_matcher:
                for key, value in target_config.items():
                    if hasattr(self.enhanced_matcher, key):
                        setattr(self.enhanced_matcher, key, value)
                        self.enhanced_matcher.config[key] = value
            
            logger.info(f"Rolled back {steps_back} configuration steps")
            return True
            
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
    
    def get_tuning_insights(self) -> Dict[str, Any]:
        """Génère des insights sur l'historique de tuning."""
        if not self.tuning_history:
            return {}
        
        recent_tunings = self.tuning_history[-10:]  # Derniers 10 tunings
        
        # Statistiques générales
        total_adjustments = sum(t.total_adjustments for t in recent_tunings)
        avg_confidence = statistics.mean(t.avg_confidence for t in recent_tunings)
        avg_improvement = statistics.mean(t.expected_improvement for t in recent_tunings)
        
        # Paramètres les plus ajustés
        parameter_counts = defaultdict(int)
        for tuning in recent_tunings:
            for adj in tuning.adjustments:
                parameter_counts[adj.parameter_name] += 1
        
        most_adjusted = sorted(parameter_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Tendance de performance
        performance_trend = []
        for tuning in recent_tunings:
            if tuning.feedback_score_after is not None:
                improvement = tuning.feedback_score_after - tuning.feedback_score_before
                performance_trend.append(improvement)
        
        avg_actual_improvement = statistics.mean(performance_trend) if performance_trend else None
        
        insights = {
            'total_tuning_sessions': len(self.tuning_history),
            'recent_sessions': len(recent_tunings),
            'total_adjustments': total_adjustments,
            'avg_confidence': avg_confidence,
            'avg_expected_improvement': avg_improvement,
            'avg_actual_improvement': avg_actual_improvement,
            'most_adjusted_parameters': most_adjusted[:5],
            'feedback_volume': len(self.feedback_history),
            'recent_feedback_score': await self._measure_current_feedback_score() if self.feedback_history else None
        }
        
        return insights
    
    def export_feedback_data(self, 
                           hours_back: int = 24) -> List[Dict[str, Any]]:
        """Exporte les données de feedback pour analyse externe."""
        cutoff = datetime.now() - timedelta(hours=hours_back)
        
        export_data = []
        for fb in self.feedback_history:
            if fb['timestamp'] >= cutoff:
                export_data.append({
                    'timestamp': fb['timestamp'].isoformat(),
                    'feedback_type': fb['feedback_type'],
                    'normalized_score': fb['normalized_score'],
                    'matcher_config': fb['matcher_config']
                })
        
        return export_data
