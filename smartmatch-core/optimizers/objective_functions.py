"""
Fonctions objectif multi-critères pour l'optimisation du matching.

Ce module implémente différentes fonctions objectif qui combinent
plusieurs métriques pour évaluer la qualité du système de matching.
"""

import logging
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np

from ..core.models import MatchResult

logger = logging.getLogger(__name__)


@dataclass
class ObjectiveMetrics:
    """Métriques calculées pour l'évaluation objective."""
    accuracy_score: float
    diversity_score: float
    performance_score: float
    bias_score: float
    user_satisfaction_score: float
    combined_score: float


class BaseObjectiveFunction(ABC):
    """Classe de base pour les fonctions objectif."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialise la fonction objectif.
        
        Args:
            weights: Poids pour chaque métrique
        """
        self.weights = weights or self._get_default_weights()
        self._normalize_weights()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Poids par défaut pour les métriques."""
        return {
            'accuracy': 0.4,
            'diversity': 0.2,
            'performance': 0.2,
            'bias': 0.1,
            'user_satisfaction': 0.1
        }
    
    def _normalize_weights(self) -> None:
        """Normalise les poids pour qu'ils somment à 1."""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    @abstractmethod
    async def evaluate(self, 
                      matching_results: List[MatchResult],
                      ground_truth: List[Dict[str, Any]],
                      execution_times: List[float],
                      user_feedback: Optional[List[Dict[str, Any]]] = None) -> float:
        """
        Évalue la performance du système de matching.
        
        Args:
            matching_results: Résultats de matching
            ground_truth: Vérité terrain attendue
            execution_times: Temps d'exécution de chaque matching
            user_feedback: Feedback utilisateur historique
            
        Returns:
            Score de qualité normalisé entre 0 et 1
        """
        pass


class MultiObjectiveFunction(BaseObjectiveFunction):
    """
    Fonction objectif multi-critères principale.
    
    Combine plusieurs métriques pour évaluer la qualité globale
    du système de matching en tenant compte de:
    - La précision des matchings
    - La diversité des résultats (éviter les biais)
    - Les performances (temps de réponse)
    - L'équité (absence de biais démographiques)
    - La satisfaction utilisateur
    """
    
    def __init__(self, 
                 weights: Optional[Dict[str, float]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise la fonction objectif multi-critères.
        
        Args:
            weights: Poids pour chaque métrique
            config: Configuration spécifique
        """
        super().__init__(weights)
        self.config = config or {}
        
        # Seuils de performance
        self.excellent_score_threshold = self.config.get('excellent_score_threshold', 0.85)
        self.good_score_threshold = self.config.get('good_score_threshold', 0.70)
        self.max_response_time = self.config.get('max_response_time_ms', 1000)
        self.diversity_window_size = self.config.get('diversity_window_size', 10)
        
        logger.info(f"MultiObjectiveFunction initialized with weights: {self.weights}")
    
    async def evaluate(self, 
                      matching_results: List[MatchResult],
                      ground_truth: List[Dict[str, Any]],
                      execution_times: List[float],
                      user_feedback: Optional[List[Dict[str, Any]]] = None) -> float:
        """
        Évalue la performance multi-critères du système.
        
        Args:
            matching_results: Résultats de matching à évaluer
            ground_truth: Vérité terrain pour validation
            execution_times: Temps d'exécution en secondes
            user_feedback: Feedback utilisateur optionnel
            
        Returns:
            Score combiné entre 0 et 1
        """
        if not matching_results:
            return 0.0
        
        try:
            # Calculer chaque métrique
            accuracy_score = await self.calculate_accuracy_score(matching_results, ground_truth)
            diversity_score = await self.calculate_diversity_score(matching_results)
            performance_score = await self.calculate_performance_score(execution_times)
            bias_score = await self.calculate_bias_score(matching_results)
            satisfaction_score = await self.calculate_user_satisfaction_score(user_feedback)
            
            # Combiner avec les poids
            combined_score = (
                self.weights.get('accuracy', 0) * accuracy_score +
                self.weights.get('diversity', 0) * diversity_score +
                self.weights.get('performance', 0) * performance_score +
                self.weights.get('bias', 0) * bias_score +
                self.weights.get('user_satisfaction', 0) * satisfaction_score
            )
            
            # Log des métriques détaillées
            logger.debug(f"Objective metrics: accuracy={accuracy_score:.3f}, "
                        f"diversity={diversity_score:.3f}, performance={performance_score:.3f}, "
                        f"bias={bias_score:.3f}, satisfaction={satisfaction_score:.3f}, "
                        f"combined={combined_score:.3f}")
            
            return combined_score
            
        except Exception as e:
            logger.error(f"Error in objective evaluation: {e}")
            return 0.0
    
    async def calculate_accuracy_score(self, 
                                     matching_results: List[MatchResult],
                                     ground_truth: List[Dict[str, Any]]) -> float:
        """
        Calcule le score de précision du matching.
        
        Compare les résultats obtenus avec la vérité terrain attendue.
        
        Args:
            matching_results: Résultats de matching
            ground_truth: Vérité terrain attendue
            
        Returns:
            Score de précision entre 0 et 1
        """
        if not matching_results or not ground_truth:
            return 0.5  # Score neutre si pas de données
        
        try:
            total_error = 0.0
            valid_comparisons = 0
            
            for i, result in enumerate(matching_results):
                if i >= len(ground_truth):
                    break
                
                expected = ground_truth[i]
                
                # Comparaison du score global
                if 'expected_score' in expected:
                    expected_score = expected['expected_score']
                    actual_score = result.overall_score
                    
                    # Erreur absolue normalisée
                    error = abs(expected_score - actual_score)
                    total_error += error
                    valid_comparisons += 1
                
                # Comparaison des top matches si disponible
                if 'expected_match' in expected:
                    expected_match = expected['expected_match']
                    # Vérifier si le candidat attendu est dans les top résultats
                    if hasattr(result, 'candidate_id'):
                        if result.candidate_id == expected_match:
                            total_error += 0.0  # Perfect match
                        else:
                            total_error += 0.5  # Partial penalty
                        valid_comparisons += 1
            
            if valid_comparisons == 0:
                # Fallback : évaluer la distribution des scores
                scores = [r.overall_score for r in matching_results]
                if scores:
                    # Favoriser les distributions avec des scores élevés et variés
                    mean_score = statistics.mean(scores)
                    std_score = statistics.stdev(scores) if len(scores) > 1 else 0
                    
                    # Score basé sur la moyenne avec bonus pour la variance
                    accuracy_score = mean_score + (std_score * 0.1)
                    return min(1.0, accuracy_score)
                else:
                    return 0.5
            
            # Conversion de l'erreur en score (moins d'erreur = meilleur score)
            avg_error = total_error / valid_comparisons
            accuracy_score = max(0.0, 1.0 - avg_error)
            
            return accuracy_score
            
        except Exception as e:
            logger.warning(f"Error calculating accuracy score: {e}")
            return 0.5
    
    async def calculate_diversity_score(self, matching_results: List[MatchResult]) -> float:
        """
        Calcule le score de diversité des résultats.
        
        Évalue la variété des résultats pour éviter les biais
        et favoriser la découverte de profils variés.
        
        Args:
            matching_results: Résultats de matching
            
        Returns:
            Score de diversité entre 0 et 1
        """
        if len(matching_results) < 2:
            return 0.5  # Score neutre si pas assez de données
        
        try:
            # 1. Diversité des scores
            scores = [r.overall_score for r in matching_results]
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            # Normaliser la variance (favoriser une distribution étalée)
            max_variance = 0.25  # Variance maximale théorique pour scores [0,1]
            score_diversity = min(1.0, score_variance / max_variance)
            
            # 2. Diversité des insights (si disponible)
            insight_types = set()
            for result in matching_results:
                if hasattr(result, 'insights'):
                    for insight in result.insights:
                        insight_types.add(f"{insight.category}_{insight.type}")
            
            # Plus d'insights variés = plus de diversité
            max_insight_types = 10  # Nombre maximum d'insights différents attendus
            insight_diversity = min(1.0, len(insight_types) / max_insight_types)
            
            # 3. Éviter les scores trop concentrés (anti-bias)
            # Vérifier qu'on n'a pas trop de scores dans la même gamme
            score_bins = [0, 0.3, 0.7, 1.0]
            score_distribution = [0] * (len(score_bins) - 1)
            
            for score in scores:
                for i in range(len(score_bins) - 1):
                    if score_bins[i] <= score < score_bins[i + 1]:
                        score_distribution[i] += 1
                        break
            
            # Calculer l'entropie de la distribution
            total = len(scores)
            entropy = 0
            for count in score_distribution:
                if count > 0:
                    p = count / total
                    entropy -= p * np.log2(p)
            
            # Normaliser l'entropie
            max_entropy = np.log2(len(score_distribution))
            entropy_diversity = entropy / max_entropy if max_entropy > 0 else 0
            
            # 4. Diversité temporelle (éviter des patterns répétitifs)
            temporal_diversity = 1.0  # Score par défaut
            
            if len(matching_results) >= self.diversity_window_size:
                # Vérifier les patterns dans une fenêtre glissante
                recent_scores = scores[-self.diversity_window_size:]
                
                # Calculer l'autocorrélation pour détecter des patterns
                autocorr = self._calculate_autocorrelation(recent_scores)
                temporal_diversity = max(0.0, 1.0 - abs(autocorr))
            
            # Combiner toutes les métriques de diversité
            diversity_score = (
                score_diversity * 0.4 +
                insight_diversity * 0.2 +
                entropy_diversity * 0.3 +
                temporal_diversity * 0.1
            )
            
            return min(1.0, diversity_score)
            
        except Exception as e:
            logger.warning(f"Error calculating diversity score: {e}")
            return 0.5
    
    def _calculate_autocorrelation(self, values: List[float], lag: int = 1) -> float:
        """Calcule l'autocorrélation pour détecter des patterns."""
        if len(values) <= lag:
            return 0.0
        
        try:
            n = len(values)
            mean = statistics.mean(values)
            
            # Calcul de l'autocorrélation à lag 1
            numerator = sum((values[i] - mean) * (values[i - lag] - mean) 
                          for i in range(lag, n))
            denominator = sum((values[i] - mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception:
            return 0.0
    
    async def calculate_performance_score(self, execution_times: List[float]) -> float:
        """
        Calcule le score de performance basé sur les temps de réponse.
        
        Args:
            execution_times: Temps d'exécution en secondes
            
        Returns:
            Score de performance entre 0 et 1
        """
        if not execution_times:
            return 1.0  # Score parfait si pas de données
        
        try:
            # Convertir en millisecondes pour l'évaluation
            times_ms = [t * 1000 for t in execution_times]
            
            # Métriques de temps
            avg_time = statistics.mean(times_ms)
            max_time = max(times_ms)
            p95_time = self._calculate_percentile(times_ms, 95)
            
            # Score basé sur le temps moyen
            if avg_time <= 100:  # Très rapide (<100ms)
                avg_score = 1.0
            elif avg_time <= 500:  # Rapide (<500ms)
                avg_score = 1.0 - (avg_time - 100) / 400 * 0.2
            elif avg_time <= self.max_response_time:  # Acceptable
                avg_score = 0.8 - (avg_time - 500) / (self.max_response_time - 500) * 0.6
            else:  # Trop lent
                avg_score = max(0.0, 0.2 - (avg_time - self.max_response_time) / 5000)
            
            # Score basé sur la consistance (pénaliser les pics)
            if p95_time <= self.max_response_time:
                consistency_score = 1.0
            else:
                consistency_score = max(0.0, 1.0 - (p95_time - self.max_response_time) / 5000)
            
            # Score basé sur la stabilité (faible variance)
            if len(times_ms) > 1:
                cv = statistics.stdev(times_ms) / statistics.mean(times_ms)  # Coefficient de variation
                stability_score = max(0.0, 1.0 - cv)
            else:
                stability_score = 1.0
            
            # Combiner les métriques
            performance_score = (
                avg_score * 0.5 +
                consistency_score * 0.3 +
                stability_score * 0.2
            )
            
            return performance_score
            
        except Exception as e:
            logger.warning(f"Error calculating performance score: {e}")
            return 0.5
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calcule un percentile des valeurs."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        floor_k = int(k)
        ceil_k = floor_k + 1
        
        if ceil_k >= len(sorted_values):
            return sorted_values[-1]
        
        d0 = sorted_values[floor_k] * (ceil_k - k)
        d1 = sorted_values[ceil_k] * (k - floor_k)
        
        return d0 + d1
    
    async def calculate_bias_score(self, matching_results: List[MatchResult]) -> float:
        """
        Calcule le score d'équité (absence de biais).
        
        Évalue si le système présente des biais systématiques
        dans ses recommandations.
        
        Args:
            matching_results: Résultats de matching
            
        Returns:
            Score d'équité entre 0 et 1 (1 = pas de biais)
        """
        if not matching_results:
            return 1.0  # Score parfait si pas de données
        
        try:
            bias_score = 1.0
            
            # 1. Biais de score (éviter des scores trop uniformes ou trop extrêmes)
            scores = [r.overall_score for r in matching_results]
            
            # Vérifier concentration excessive sur certaines valeurs
            score_range = max(scores) - min(scores)
            if score_range < 0.1:  # Scores trop concentrés
                bias_score -= 0.3
            
            # Vérifier distribution déséquilibrée
            mean_score = statistics.mean(scores)
            if mean_score > 0.9:  # Tous les scores très élevés (suspect)
                bias_score -= 0.2
            elif mean_score < 0.3:  # Tous les scores très bas (suspect)
                bias_score -= 0.2
            
            # 2. Biais d'insights (si disponible)
            insight_categories = {}
            total_insights = 0
            
            for result in matching_results:
                if hasattr(result, 'insights'):
                    for insight in result.insights:
                        category = insight.category
                        insight_categories[category] = insight_categories.get(category, 0) + 1
                        total_insights += 1
            
            if total_insights > 0:
                # Vérifier la distribution des insights
                category_proportions = [count / total_insights 
                                      for count in insight_categories.values()]
                
                # Pénaliser si une catégorie domine trop (>80%)
                max_proportion = max(category_proportions)
                if max_proportion > 0.8:
                    bias_score -= 0.2
            
            # 3. Pattern matching bias (éviter des patterns trop répétitifs)
            if len(matching_results) >= 5:
                # Vérifier si les scores suivent un pattern trop régulier
                score_diffs = [scores[i+1] - scores[i] for i in range(len(scores)-1)]
                
                # Si les différences sont très similaires, c'est suspect
                if len(score_diffs) > 1:
                    diff_std = statistics.stdev(score_diffs)
                    if diff_std < 0.01:  # Différences trop uniformes
                        bias_score -= 0.1
            
            # 4. Diversité démographique (si des métadonnées sont disponibles)
            # Cette partie nécessiterait des métadonnées sur les candidats
            # Pour l'instant, on assume une distribution équitable
            
            return max(0.0, min(1.0, bias_score))
            
        except Exception as e:
            logger.warning(f"Error calculating bias score: {e}")
            return 1.0  # Par défaut, assumer pas de biais
    
    async def calculate_user_satisfaction_score(self, 
                                              user_feedback: Optional[List[Dict[str, Any]]]) -> float:
        """
        Calcule le score de satisfaction utilisateur.
        
        Args:
            user_feedback: Feedback utilisateur historique
            
        Returns:
            Score de satisfaction entre 0 et 1
        """
        if not user_feedback:
            return 0.75  # Score neutre si pas de feedback
        
        try:
            satisfaction_scores = []
            
            for feedback in user_feedback:
                # Parser différents types de feedback
                if 'rating' in feedback:
                    # Rating direct (ex: 1-5 étoiles)
                    rating = feedback['rating']
                    max_rating = feedback.get('max_rating', 5)
                    normalized_rating = rating / max_rating
                    satisfaction_scores.append(normalized_rating)
                
                elif 'clicked' in feedback:
                    # Feedback implicite basé sur les clics
                    if feedback['clicked']:
                        satisfaction_scores.append(0.8)  # Clic = satisfaction modérée
                    else:
                        satisfaction_scores.append(0.3)  # Pas de clic = insatisfaction
                
                elif 'applied' in feedback:
                    # Application à une offre = forte satisfaction
                    if feedback['applied']:
                        satisfaction_scores.append(0.9)
                    else:
                        satisfaction_scores.append(0.5)
                
                elif 'interview' in feedback:
                    # Entretien obtenu = très forte satisfaction
                    if feedback['interview']:
                        satisfaction_scores.append(0.95)
                    else:
                        satisfaction_scores.append(0.6)
                
                elif 'hired' in feedback:
                    # Embauche = satisfaction maximale
                    if feedback['hired']:
                        satisfaction_scores.append(1.0)
                    else:
                        satisfaction_scores.append(0.7)
            
            if satisfaction_scores:
                # Calculer la satisfaction moyenne avec pondération récente
                if len(satisfaction_scores) > 10:
                    # Donner plus de poids aux feedbacks récents
                    weights = [1.0 + i * 0.1 for i in range(len(satisfaction_scores))]
                    weighted_avg = sum(s * w for s, w in zip(satisfaction_scores, weights)) / sum(weights)
                else:
                    weighted_avg = statistics.mean(satisfaction_scores)
                
                return min(1.0, weighted_avg)
            else:
                return 0.75
                
        except Exception as e:
            logger.warning(f"Error calculating user satisfaction score: {e}")
            return 0.75
    
    def get_detailed_metrics(self, 
                           matching_results: List[MatchResult],
                           ground_truth: List[Dict[str, Any]],
                           execution_times: List[float],
                           user_feedback: Optional[List[Dict[str, Any]]] = None) -> ObjectiveMetrics:
        """
        Retourne toutes les métriques détaillées.
        
        Args:
            matching_results: Résultats de matching
            ground_truth: Vérité terrain
            execution_times: Temps d'exécution
            user_feedback: Feedback utilisateur
            
        Returns:
            ObjectiveMetrics avec toutes les métriques calculées
        """
        import asyncio
        
        # Calculer toutes les métriques de façon asynchrone
        async def calculate_all():
            accuracy = await self.calculate_accuracy_score(matching_results, ground_truth)
            diversity = await self.calculate_diversity_score(matching_results)
            performance = await self.calculate_performance_score(execution_times)
            bias = await self.calculate_bias_score(matching_results)
            satisfaction = await self.calculate_user_satisfaction_score(user_feedback)
            
            combined = (
                self.weights.get('accuracy', 0) * accuracy +
                self.weights.get('diversity', 0) * diversity +
                self.weights.get('performance', 0) * performance +
                self.weights.get('bias', 0) * bias +
                self.weights.get('user_satisfaction', 0) * satisfaction
            )
            
            return ObjectiveMetrics(
                accuracy_score=accuracy,
                diversity_score=diversity,
                performance_score=performance,
                bias_score=bias,
                user_satisfaction_score=satisfaction,
                combined_score=combined
            )
        
        return asyncio.run(calculate_all())


class SimpleAccuracyObjective(BaseObjectiveFunction):
    """
    Fonction objectif simple basée uniquement sur la précision.
    
    Utile pour des optimisations rapides ou des comparaisons de base.
    """
    
    def __init__(self):
        super().__init__({'accuracy': 1.0})
    
    async def evaluate(self, 
                      matching_results: List[MatchResult],
                      ground_truth: List[Dict[str, Any]],
                      execution_times: List[float],
                      user_feedback: Optional[List[Dict[str, Any]]] = None) -> float:
        """Évalue uniquement la précision."""
        multi_objective = MultiObjectiveFunction()
        return await multi_objective.calculate_accuracy_score(matching_results, ground_truth)


class PerformanceOptimizedObjective(BaseObjectiveFunction):
    """
    Fonction objectif optimisée pour la performance.
    
    Favorise les temps de réponse rapides tout en maintenant
    une précision acceptable.
    """
    
    def __init__(self):
        super().__init__({
            'accuracy': 0.6,
            'performance': 0.4
        })
    
    async def evaluate(self, 
                      matching_results: List[MatchResult],
                      ground_truth: List[Dict[str, Any]],
                      execution_times: List[float],
                      user_feedback: Optional[List[Dict[str, Any]]] = None) -> float:
        """Évalue avec focus sur performance."""
        multi_objective = MultiObjectiveFunction(weights=self.weights)
        return await multi_objective.evaluate(
            matching_results, ground_truth, execution_times, user_feedback
        )


class UserSatisfactionObjective(BaseObjectiveFunction):
    """
    Fonction objectif axée sur la satisfaction utilisateur.
    
    Privilégie les résultats qui maximisent l'engagement
    et la satisfaction des utilisateurs.
    """
    
    def __init__(self):
        super().__init__({
            'accuracy': 0.3,
            'diversity': 0.2,
            'user_satisfaction': 0.5
        })
    
    async def evaluate(self, 
                      matching_results: List[MatchResult],
                      ground_truth: List[Dict[str, Any]],
                      execution_times: List[float],
                      user_feedback: Optional[List[Dict[str, Any]]] = None) -> float:
        """Évalue avec focus sur satisfaction utilisateur."""
        multi_objective = MultiObjectiveFunction(weights=self.weights)
        return await multi_objective.evaluate(
            matching_results, ground_truth, execution_times, user_feedback
        )
