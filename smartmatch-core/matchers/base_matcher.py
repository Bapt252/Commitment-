"""
Base Matcher Implementation
--------------------------
Classe de base abstraite pour tous les matchers du SmartMatcher.
Implémente les fonctionnalités communes et définit l'interface standard.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.interfaces import BaseMatchEngine
from ..core.models import Candidate, Job, MatchInsight
from ..core.exceptions import MatcherError, ConfigurationError

logger = logging.getLogger(__name__)


class AbstractBaseMatcher(BaseMatchEngine):
    """
    Classe de base abstraite pour tous les matchers.
    Fournit les fonctionnalités communes et la structure de base.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le matcher de base
        
        Args:
            config: Configuration spécifique du matcher
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace('Matcher', '').lower()
        self.weight = self.config.get('weight', self._get_default_weight())
        self.enabled = self.config.get('enabled', True)
        
        # Configuration des seuils de performance
        self.performance_thresholds = {
            'excellent': self.config.get('thresholds', {}).get('excellent', 0.8),
            'good': self.config.get('thresholds', {}).get('good', 0.6),
            'moderate': self.config.get('thresholds', {}).get('moderate', 0.4),
            'weak': self.config.get('thresholds', {}).get('weak', 0.2)
        }
        
        # Validation de la configuration
        self._validate_config()
        
        logger.debug(f"Initialized {self.get_name()} matcher with weight {self.weight}")
    
    def get_name(self) -> str:
        """Retourne le nom du matcher"""
        return self.name
    
    def get_weight(self) -> float:
        """Retourne le poids du matcher dans le score final"""
        return self.weight
    
    def is_enabled(self) -> bool:
        """Indique si le matcher est activé"""
        return self.enabled
    
    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration du matcher"""
        return {
            'name': self.get_name(),
            'weight': self.get_weight(),
            'enabled': self.is_enabled(),
            'thresholds': self.performance_thresholds,
            'config': self.config
        }
    
    async def calculate_score(self, candidate: Candidate, job: Job) -> float:
        """
        Point d'entrée principal pour le calcul de score.
        Gère la validation, les erreurs et les métriques.
        """
        start_time = time.time()
        
        try:
            # Validation des entrées
            self._validate_inputs(candidate, job)
            
            # Si le matcher est désactivé, retourner un score neutre
            if not self.is_enabled():
                logger.debug(f"{self.get_name()} matcher is disabled, returning neutral score")
                return 0.5
            
            # Calcul du score spécifique au matcher
            score = await self._calculate_specific_score(candidate, job)
            
            # Validation du score
            score = self._validate_score(score)
            
            # Log performance si nécessaire
            duration = (time.time() - start_time) * 1000
            if duration > 100:  # Log si plus de 100ms
                logger.warning(
                    f"{self.get_name()} matcher took {duration:.2f}ms for "
                    f"candidate {candidate.id} and job {job.id}"
                )
            
            logger.debug(
                f"{self.get_name()} score for candidate {candidate.id} "
                f"and job {job.id}: {score:.3f}"
            )
            
            return score
            
        except Exception as e:
            logger.error(
                f"Error in {self.get_name()} matcher for candidate {candidate.id} "
                f"and job {job.id}: {str(e)}", exc_info=True
            )
            raise MatcherError(
                message=f"Error calculating score in {self.get_name()} matcher: {str(e)}",
                matcher_name=self.get_name()
            )
    
    def generate_insights(self, candidate: Candidate, job: Job, score: float) -> List[MatchInsight]:
        """
        Génère des insights explicatifs pour le score.
        Peut être surchargée par les matchers spécifiques.
        """
        try:
            insights = self._generate_specific_insights(candidate, job, score)
            
            # Ajouter un insight général basé sur le score
            category = self._categorize_score(score)
            general_insight = self._create_general_insight(score, category)
            if general_insight:
                insights.append(general_insight)
            
            return insights
            
        except Exception as e:
            logger.error(
                f"Error generating insights in {self.get_name()} matcher: {str(e)}",
                exc_info=True
            )
            # Retourner un insight d'erreur plutôt que de lever une exception
            return [MatchInsight(
                type='error',
                category=self.get_name(),
                message=f"Erreur lors de la génération d'insights: {str(e)}",
                priority=1
            )]
    
    @abstractmethod
    async def _calculate_specific_score(self, candidate: Candidate, job: Job) -> float:
        """
        Méthode abstraite pour le calcul de score spécifique.
        Doit être implémentée par chaque matcher.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        pass
    
    @abstractmethod
    def _get_default_weight(self) -> float:
        """
        Retourne le poids par défaut pour ce type de matcher.
        Doit être implémentée par chaque matcher.
        """
        pass
    
    def _generate_specific_insights(self, candidate: Candidate, job: Job, 
                                  score: float) -> List[MatchInsight]:
        """
        Génère des insights spécifiques au matcher.
        Peut être surchargée par les matchers spécifiques.
        
        Returns:
            Liste d'insights spécifiques
        """
        return []
    
    def _validate_config(self) -> None:
        """Valide la configuration du matcher"""
        if not (0 <= self.weight <= 1):
            raise ConfigurationError(
                f"Weight for {self.get_name()} matcher must be between 0 and 1, "
                f"got {self.weight}"
            )
        
        # Valider les seuils
        thresholds = ['excellent', 'good', 'moderate', 'weak']
        for threshold in thresholds:
            value = self.performance_thresholds[threshold]
            if not (0 <= value <= 1):
                raise ConfigurationError(
                    f"Threshold '{threshold}' for {self.get_name()} matcher "
                    f"must be between 0 and 1, got {value}"
                )
    
    def _validate_inputs(self, candidate: Candidate, job: Job) -> None:
        """Valide les entrées"""
        if not candidate:
            raise MatcherError(f"Candidate is required for {self.get_name()} matcher")
        
        if not job:
            raise MatcherError(f"Job is required for {self.get_name()} matcher")
        
        if not candidate.id:
            raise MatcherError(f"Candidate ID is required for {self.get_name()} matcher")
        
        if not job.id:
            raise MatcherError(f"Job ID is required for {self.get_name()} matcher")
    
    def _validate_score(self, score: float) -> float:
        """Valide et normalise le score"""
        if score is None:
            logger.warning(f"{self.get_name()} matcher returned None, using neutral score")
            return 0.5
        
        # Assurer que le score est dans la plage [0, 1]
        score = max(0.0, min(1.0, float(score)))
        
        return score
    
    def _categorize_score(self, score: float) -> str:
        """Catégorise le score selon les seuils définis"""
        if score >= self.performance_thresholds['excellent']:
            return 'excellent'
        elif score >= self.performance_thresholds['good']:
            return 'good'
        elif score >= self.performance_thresholds['moderate']:
            return 'moderate'
        elif score >= self.performance_thresholds['weak']:
            return 'weak'
        else:
            return 'insufficient'
    
    def _create_general_insight(self, score: float, category: str) -> Optional[MatchInsight]:
        """Crée un insight général basé sur le score et la catégorie"""
        messages = {
            'excellent': f"Excellente adéquation pour {self.get_name()}",
            'good': f"Bonne correspondance pour {self.get_name()}",
            'moderate': f"Correspondance modérée pour {self.get_name()}",
            'weak': f"Faible correspondance pour {self.get_name()}",
            'insufficient': f"Correspondance insuffisante pour {self.get_name()}"
        }
        
        insight_types = {
            'excellent': 'strength',
            'good': 'strength', 
            'moderate': 'neutral',
            'weak': 'weakness',
            'insufficient': 'weakness'
        }
        
        priorities = {
            'excellent': 3,
            'good': 2,
            'moderate': 1,
            'weak': 2,
            'insufficient': 3
        }
        
        if category in messages:
            return MatchInsight(
                type=insight_types[category],
                category=self.get_name(),
                message=messages[category],
                score=score,
                priority=priorities[category]
            )
        
        return None
    
    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """
        Extrait un nombre d'un texte.
        Utilitaire commun pour l'extraction d'années d'expérience, etc.
        """
        import re
        
        if not text or text.lower() == "non détecté":
            return None
        
        # Recherche de motifs numériques
        patterns = [
            r'(\d+)(?:\+)?\s*(?:an|ans|années|year|years)',  # "5 ans", "5+ ans"
            r'(\d+)(?:\+)?',  # Nombres seuls
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # Conversion de texte en nombre
        word_to_number = {
            'un': 1, 'une': 1, 'one': 1,
            'deux': 2, 'two': 2,
            'trois': 3, 'three': 3,
            'quatre': 4, 'four': 4,
            'cinq': 5, 'five': 5,
            'six': 6, 'six': 6,
            'sept': 7, 'seven': 7,
            'huit': 8, 'eight': 8,
            'neuf': 9, 'nine': 9,
            'dix': 10, 'ten': 10
        }
        
        for word, number in word_to_number.items():
            if word in text.lower():
                return number
        
        return None
    
    def _calculate_overlap_ratio(self, list1: List[str], list2: List[str]) -> float:
        """
        Calcule le ratio de chevauchement entre deux listes.
        Utilitaire commun pour comparer compétences, valeurs, etc.
        """
        if not list1 or not list2:
            return 0.0
        
        # Normaliser les listes (lowercase, strip)
        normalized_list1 = {item.lower().strip() for item in list1 if item.strip()}
        normalized_list2 = {item.lower().strip() for item in list2 if item.strip()}
        
        if not normalized_list1 or not normalized_list2:
            return 0.0
        
        # Calculer l'intersection
        intersection = normalized_list1.intersection(normalized_list2)
        
        # Ratio basé sur la liste la plus petite (Jaccard index)
        union = normalized_list1.union(normalized_list2)
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_similarity_with_threshold(self, value1: Any, value2: Any, 
                                           threshold: float = 0.8) -> float:
        """
        Calcule la similarité entre deux valeurs avec un seuil.
        Retourne 1.0 si la similarité dépasse le seuil, 0.0 sinon.
        """
        if value1 == value2:
            return 1.0
        
        # Pour les strings, calculer la similarité de caractères
        if isinstance(value1, str) and isinstance(value2, str):
            if not value1 or not value2:
                return 0.0
            
            # Simple similarité basée sur les caractères communs
            set1 = set(value1.lower())
            set2 = set(value2.lower())
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            
            if not union:
                return 0.0
            
            similarity = len(intersection) / len(union)
            return 1.0 if similarity >= threshold else 0.0
        
        return 0.0
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(weight={self.weight}, enabled={self.enabled})"
    
    def __repr__(self) -> str:
        return self.__str__()
