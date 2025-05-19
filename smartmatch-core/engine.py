"""
SmartMatchEngine - Moteur de matching refactorisé
----------------------------------------------------------------
Nouvelle implémentation du système de matching utilisant l'architecture
modulaire et respectant les principes SOLID.

Architecture:
- Moteur principal orchestrant les matchers spécialisés  
- Support asynchrone pour les opérations coûteuses
- Injection de dépendances pour une meilleure testabilité
- Configuration centralisée et flexible
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Type
from dataclasses import asdict

from .core.models import Candidate, Job, MatchResult, MatchInsight
from .core.interfaces import BaseMatchEngine, ScoringStrategy, NLPService, LocationService, CacheService
from .core.config import SmartMatchConfig
from .core.exceptions import SmartMatchError, PerformanceError, ValidationError

from .matchers.skills_matcher import SkillsMatcher
# Imports pour matchers futurs :
# from .matchers.location_matcher import LocationMatcher
# from .matchers.experience_matcher import ExperienceMatcher
# from .matchers.education_matcher import EducationMatcher
# from .matchers.preference_matcher import PreferenceMatcher

logger = logging.getLogger(__name__)


class DefaultScoringStrategy:
    """Stratégie de scoring par défaut utilisant une moyenne pondérée."""
    
    def calculate_overall_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calcule le score global à partir des scores de catégorie et des poids.
        
        Args:
            scores: Dictionnaire des scores par catégorie
            weights: Dictionnaire des poids par catégorie
            
        Returns:
            Score global entre 0 et 1
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in scores.items():
            if category in weights:
                weight = weights[category]
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0


class SmartMatchEngine:
    """
    Moteur principal de matching modernisé utilisant l'architecture modulaire.
    
    Features:
    - Architecture modulaire avec matchers spécialisés
    - Calculs asynchrones pour de meilleures performances
    - Injection de dépendances pour tests et flexibilité
    - Configuration centralisée et validée
    - Insights détaillés et explicables
    """
    
    def __init__(
        self,
        config: Optional[SmartMatchConfig] = None,
        nlp_service: Optional[NLPService] = None,
        location_service: Optional[LocationService] = None,
        cache_service: Optional[CacheService] = None,
        scoring_strategy: Optional[ScoringStrategy] = None,
        custom_matchers: Optional[Dict[str, BaseMatchEngine]] = None
    ):
        """
        Initialise le moteur de matching.
        
        Args:
            config: Configuration du système (utilise défaut si None)
            nlp_service: Service NLP pour analyse sémantique
            location_service: Service de géolocalisation
            cache_service: Service de cache pour optimisation
            scoring_strategy: Stratégie de calcul du score global
            custom_matchers: Matchers personnalisés à ajouter
        """
        # Configuration
        self.config = config or SmartMatchConfig()
        
        # Services (injection de dépendances)
        self.nlp_service = nlp_service
        self.location_service = location_service  
        self.cache_service = cache_service
        
        # Stratégie de scoring
        self.scoring_strategy = scoring_strategy or DefaultScoringStrategy()
        
        # Initialisation des matchers
        self.matchers: Dict[str, BaseMatchEngine] = {}
        self._initialize_matchers(custom_matchers)
        
        # Métriques de performance
        self.performance_metrics = {
            "total_matches": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info(f"SmartMatchEngine initialisé avec {len(self.matchers)} matchers")
    
    def _initialize_matchers(self, custom_matchers: Optional[Dict[str, BaseMatchEngine]] = None):
        """
        Initialise les matchers par défaut et personnalisés.
        
        Args:
            custom_matchers: Matchers personnalisés à ajouter
        """
        # Matchers par défaut
        default_matchers = {
            "skills": SkillsMatcher(
                nlp_service=self.nlp_service,
                config=self.config.matchers.skills
            )
            # À ajouter dans les sessions futures :
            # "location": LocationMatcher(location_service=self.location_service),
            # "experience": ExperienceMatcher(),
            # "education": EducationMatcher(),
            # "preferences": PreferenceMatcher()
        }
        
        # Ajouter les matchers par défaut
        self.matchers.update(default_matchers)
        
        # Ajouter les matchers personnalisés
        if custom_matchers:
            self.matchers.update(custom_matchers)
        
        logger.info(f"Matchers initialisés: {list(self.matchers.keys())}")
    
    async def calculate_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> MatchResult:
        """
        Calcule le matching entre un candidat et une offre d'emploi.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            MatchResult: Résultat détaillé du matching
            
        Raises:
            ValidationError: Si les données d'entrée sont invalides
            PerformanceError: Si le calcul dépasse les limites de temps
        """
        start_time = time.time()
        
        try:
            # Validation des entrées
            candidate_obj = Candidate.from_dict(candidate)
            job_obj = Job.from_dict(job)
            
            # Vérifier les limits de performance
            if self.config.performance.max_execution_time > 0:
                timeout = self.config.performance.max_execution_time
            else:
                timeout = None
            
            # Calculer les scores avec timeout
            scores = await asyncio.wait_for(
                self._calculate_category_scores(candidate_obj, job_obj),
                timeout=timeout
            )
            
            # Calculer le score global
            overall_score = self.scoring_strategy.calculate_overall_score(
                scores, 
                self.config.scoring.weights
            )
            
            # Générer les insights
            insights = await self._generate_insights(candidate_obj, job_obj, scores)
            
            # Créer le résultat
            result = MatchResult(
                candidate_id=candidate_obj.id,
                job_id=job_obj.id,
                overall_score=overall_score,
                category_scores=scores,
                insights=insights,
                metadata={
                    "engine_version": "2.0",
                    "calculation_time": time.time() - start_time,
                    "matchers_used": list(self.matchers.keys())
                }
            )
            
            # Mise à jour des métriques
            self._update_performance_metrics(start_time)
            
            return result
            
        except asyncio.TimeoutError:
            raise PerformanceError(f"Calcul de matching dépassé le timeout de {timeout}s")
        except Exception as e:
            logger.error(f"Erreur lors du calcul de matching: {str(e)}")
            raise SmartMatchError(f"Erreur de matching: {str(e)}") from e
    
    async def _calculate_category_scores(self, candidate: Candidate, job: Job) -> Dict[str, float]:
        """
        Calcule les scores par catégorie en parallèle.
        
        Args:
            candidate: Profil candidat validé
            job: Offre d'emploi validée
            
        Returns:
            Dict des scores par catégorie
        """
        # Préparer les tâches de calcul en parallèle
        tasks = {}
        
        for category, matcher in self.matchers.items():
            # Vérifier si le matcher est activé dans la configuration
            if getattr(self.config.matchers, category, {}).get('enabled', True):
                tasks[category] = matcher.calculate_match(candidate, job)
        
        # Exécuter tous les matchers en parallèle
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Traiter les résultats
        scores = {}
        for category, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Erreur dans le matcher {category}: {str(result)}")
                scores[category] = 0.5  # Score neutre en cas d'erreur
            else:
                scores[category] = result
        
        return scores
    
    async def _generate_insights(
        self, 
        candidate: Candidate, 
        job: Job, 
        scores: Dict[str, float]
    ) -> List[MatchInsight]:
        """
        Génère des insights détaillés sur le matching.
        
        Args:
            candidate: Profil candidat
            job: Offre d'emploi  
            scores: Scores par catégorie
            
        Returns:
            Liste d'insights
        """
        insights = []
        
        # Insights basés sur les scores
        for category, score in scores.items():
            if score >= 0.8:
                insights.append(MatchInsight(
                    category=category,
                    type="strength",
                    title=f"Excellente correspondance {category}",
                    message=f"Score élevé de {score:.1%} en {category}",
                    score=score,
                    details={"threshold": "high", "category": category}
                ))
            elif score <= 0.3:
                insights.append(MatchInsight(
                    category=category,
                    type="weakness", 
                    title=f"Faible correspondance {category}",
                    message=f"Score faible de {score:.1%} en {category}",
                    score=score,
                    details={"threshold": "low", "category": category}
                ))
        
        # Insights spécialisés des matchers
        for category, matcher in self.matchers.items():
            if hasattr(matcher, 'generate_insights'):
                try:
                    matcher_insights = await matcher.generate_insights(candidate, job, scores[category])
                    insights.extend(matcher_insights)
                except Exception as e:
                    logger.error(f"Erreur génération insights {category}: {str(e)}")
        
        # Trier les insights par importance
        insights.sort(key=lambda x: (-x.score if x.type == "strength" else x.score))
        
        return insights
    
    def _update_performance_metrics(self, start_time: float):
        """Met à jour les métriques de performance."""
        execution_time = time.time() - start_time
        self.performance_metrics["total_matches"] += 1
        self.performance_metrics["total_time"] += execution_time
        self.performance_metrics["average_time"] = (
            self.performance_metrics["total_time"] / 
            self.performance_metrics["total_matches"]
        )
    
    async def batch_match(
        self, 
        candidates: List[Dict[str, Any]], 
        jobs: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> List[MatchResult]:
        """
        Effectue un matching en lot avec contrôle de concurrence.
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des offres d'emploi
            max_concurrent: Nombre maximum de matchings simultanés
            
        Returns:
            Liste des résultats de matching
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_match(candidate: Dict[str, Any], job: Dict[str, Any]) -> MatchResult:
            """Calcul de matching avec limitation de concurrence."""
            async with semaphore:
                return await self.calculate_match(candidate, job)
        
        # Créer toutes les tâches
        tasks = []
        for candidate in candidates:
            for job in jobs:
                tasks.append(bounded_match(candidate, job))
        
        # Exécuter avec logging de progression
        total_tasks = len(tasks)
        logger.info(f"Démarrage du batch matching: {total_tasks} paires")
        
        # Traiter les résultats au fur et à mesure
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            
            # Log de progression tous les 10%
            if (i + 1) % max(1, total_tasks // 10) == 0:
                progress = (i + 1) / total_tasks * 100
                logger.info(f"Batch matching: {progress:.1f}% completé")
        
        logger.info(f"Batch matching terminé: {total_tasks} paires en {self.performance_metrics['average_time']:.2f}s en moyenne")
        return results
    
    def add_matcher(self, name: str, matcher: BaseMatchEngine, weight: float = 0.1):
        """
        Ajoute un nouveau matcher au moteur.
        
        Args:
            name: Nom du matcher
            matcher: Instance du matcher
            weight: Poids dans le calcul global
        """
        self.matchers[name] = matcher
        
        # Mettre à jour les poids de configuration
        if hasattr(self.config.scoring, 'weights'):
            self.config.scoring.weights[name] = weight
        
        logger.info(f"Matcher '{name}' ajouté avec un poids de {weight}")
    
    def remove_matcher(self, name: str):
        """
        Supprime un matcher du moteur.
        
        Args:
            name: Nom du matcher à supprimer
        """
        if name in self.matchers:
            del self.matchers[name]
            
            # Supprimer des poids de configuration 
            if hasattr(self.config.scoring, 'weights') and name in self.config.scoring.weights:
                del self.config.scoring.weights[name]
            
            logger.info(f"Matcher '{name}' supprimé")
        else:
            logger.warning(f"Matcher '{name}' non trouvé")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance actuelles.
        
        Returns:
            Dict des métriques de performance
        """
        return self.performance_metrics.copy()
    
    def reset_performance_metrics(self):
        """Remet à zéro les métriques de performance."""
        self.performance_metrics = {
            "total_matches": 0,
            "total_time": 0.0, 
            "average_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        logger.info("Métriques de performance remises à zéro")


# Wrapper pour compatibilité avec l'ancienne interface
class LegacySmartMatcher:
    """
    Wrapper pour maintenir la compatibilité avec l'ancienne interface SmartMatcher.
    Délègue les appels vers le nouveau SmartMatchEngine.
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000):
        """Initialise avec les mêmes paramètres que l'ancien SmartMatcher."""
        # Créer une configuration compatible
        config = SmartMatchConfig()
        if api_key:
            config.external_apis.google_maps_api_key = api_key
        
        # Initialiser le nouveau moteur
        self.engine = SmartMatchEngine(config=config)
        
        # Garder la compatibilité avec les attributs anciens
        self.weights = {
            "skills": 0.40,
            "location": 0.25, 
            "experience": 0.15,
            "education": 0.10,
            "preferences": 0.10
        }
    
    def calculate_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Interface synchrone compatible avec l'ancien SmartMatcher."""
        # Exécuter le calcul asynchrone de manière synchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.engine.calculate_match(candidate, job))
            # Convertir en format dictionnaire pour compatibilité
            return asdict(result)
        finally:
            loop.close()
    
    def batch_match(self, candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Interface synchrone compatible pour le batch matching."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.engine.batch_match(candidates, jobs))
            # Convertir en format dictionnaires pour compatibilité
            return [asdict(result) for result in results]
        finally:
            loop.close()
    
    def load_test_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Charge les données de test (identique à l'ancienne version)."""
        # Réutiliser les données de test de l'ancien SmartMatcher
        from .smartmatch import SmartMatcher
        old_matcher = SmartMatcher()
        return old_matcher.load_test_data()


# Export pour rétrocompatibilité
SmartMatcher = LegacySmartMatcher
