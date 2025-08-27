"""
Score Value Objects

Représente les différents types de scores dans le système de matching.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum


class ScoreLevel(Enum):
    """
    Niveaux de qualité pour les scores.
    """
    EXCELLENT = (0.9, 1.0, "Excellent")
    GOOD = (0.7, 0.9, "Good")
    FAIR = (0.5, 0.7, "Fair")
    POOR = (0.3, 0.5, "Poor")
    VERY_POOR = (0.0, 0.3, "Very Poor")
    
    def __init__(self, min_score: float, max_score: float, label: str):
        self.min_score = min_score
        self.max_score = max_score
        self.label = label
    
    @classmethod
    def from_score(cls, score: float) -> 'ScoreLevel':
        """
        Détermine le niveau à partir d'un score.
        
        Args:
            score: Score entre 0 et 1
            
        Returns:
            Niveau correspondant au score
        """
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        
        # Fallback pour valeurs extrêmes
        if score < 0:
            return cls.VERY_POOR
        else:
            return cls.EXCELLENT


@dataclass(frozen=True)
class OverallScore:
    """
    Représente le score global de matching.
    """
    
    value: float
    
    def __post_init__(self):
        if not 0 <= self.value <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {self.value}")
    
    @property
    def percentage(self) -> int:
        """
        Retourne le score en pourcentage.
        
        Returns:
            Score en pourcentage (0-100)
        """
        return round(self.value * 100)
    
    @property
    def level(self) -> ScoreLevel:
        """
        Retourne le niveau de qualité du score.
        
        Returns:
            Niveau de qualité
        """
        return ScoreLevel.from_score(self.value)
    
    def is_good_match(self, threshold: float = 0.7) -> bool:
        """
        Détermine si le score indique un bon matching.
        
        Args:
            threshold: Seuil pour déterminer un bon match
            
        Returns:
            True si le score est au-dessus du seuil
        """
        return self.value >= threshold
    
    def __str__(self) -> str:
        return f"{self.percentage}% ({self.level.label})"
    
    def __repr__(self) -> str:
        return f"OverallScore({self.value})"
    
    def __lt__(self, other):
        if isinstance(other, OverallScore):
            return self.value < other.value
        return self.value < other
    
    def __le__(self, other):
        if isinstance(other, OverallScore):
            return self.value <= other.value
        return self.value <= other
    
    def __gt__(self, other):
        if isinstance(other, OverallScore):
            return self.value > other.value
        return self.value > other
    
    def __ge__(self, other):
        if isinstance(other, OverallScore):
            return self.value >= other.value
        return self.value >= other


@dataclass(frozen=True)
class SkillScore:
    """
    Représente le score de correspondance des compétences.
    """
    
    raw_score: float
    matched_skills: Set[str]
    missing_skills: Set[str]
    additional_skills: Set[str] = None
    
    def __post_init__(self):
        if not 0 <= self.raw_score <= 1:
            raise ValueError(f"Raw score must be between 0 and 1, got {self.raw_score}")
        
        if self.additional_skills is None:
            object.__setattr__(self, 'additional_skills', set())
    
    @property
    def normalized_score(self) -> float:
        """
        Retourne le score normalisé (avec bonus pour compétences supplémentaires).
        
        Returns:
            Score normalisé entre 0 et 1
        """
        # Bonus pour compétences supplémentaires (max 10% de bonus)
        bonus = min(0.1, len(self.additional_skills) * 0.02)
        return min(1.0, self.raw_score + bonus)
    
    @property
    def match_ratio(self) -> float:
        """
        Ratio de compétences correspondantes.
        
        Returns:
            Ratio entre 0 et 1
        """
        total_required = len(self.matched_skills) + len(self.missing_skills)
        if total_required == 0:
            return 1.0
        return len(self.matched_skills) / total_required
    
    def get_gap_analysis(self) -> Dict[str, List[str]]:
        """
        Analyse des écarts de compétences.
        
        Returns:
            Dictionnaire avec les compétences par catégorie
        """
        return {
            'matched': list(self.matched_skills),
            'missing': list(self.missing_skills),
            'additional': list(self.additional_skills)
        }
    
    def __str__(self) -> str:
        return f"SkillScore({self.normalized_score:.2f}, {len(self.matched_skills)} matched, {len(self.missing_skills)} missing)"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass(frozen=True)
class LocationScore:
    """
    Représente le score de correspondance de localisation.
    """
    
    raw_score: float
    travel_time_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    transport_modes: Optional[List[str]] = None
    
    def __post_init__(self):
        if not 0 <= self.raw_score <= 1:
            raise ValueError(f"Raw score must be between 0 and 1, got {self.raw_score}")
    
    @property
    def normalized_score(self) -> float:
        """
        Score normalisé (identique au score brut pour la localisation).
        
        Returns:
            Score normalisé
        """
        return self.raw_score
    
    def is_reasonable_commute(self, max_minutes: int = 60) -> bool:
        """
        Vérifie si le temps de trajet est raisonnable.
        
        Args:
            max_minutes: Temps maximum acceptable en minutes
            
        Returns:
            True si le trajet est raisonnable
        """
        if self.travel_time_minutes is None:
            return True
        return self.travel_time_minutes <= max_minutes
    
    def get_commute_description(self) -> str:
        """
        Description du trajet.
        
        Returns:
            Description lisible du trajet
        """
        if self.travel_time_minutes is None:
            return "Travel time not calculated"
        
        if self.travel_time_minutes == 0:
            return "No commute (remote or same location)"
        
        hours = self.travel_time_minutes // 60
        minutes = self.travel_time_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}min commute"
        else:
            return f"{minutes}min commute"
        
        if self.distance_km:
            return f"{self.get_commute_description()} ({self.distance_km:.1f}km)"
    
    @classmethod
    def from_cached_data(cls, cached_data: Dict) -> 'LocationScore':
        """
        Crée un LocationScore à partir de données mises en cache.
        
        Args:
            cached_data: Données du cache
            
        Returns:
            Instance de LocationScore
        """
        return cls(
            raw_score=cached_data['raw_score'],
            travel_time_minutes=cached_data.get('travel_time_minutes'),
            distance_km=cached_data.get('distance_km'),
            transport_modes=cached_data.get('transport_modes')
        )
    
    def to_cache_data(self) -> Dict:
        """
        Convertit en données pour le cache.
        
        Returns:
            Dictionnaire pour la mise en cache
        """
        return {
            'raw_score': self.raw_score,
            'travel_time_minutes': self.travel_time_minutes,
            'distance_km': self.distance_km,
            'transport_modes': self.transport_modes
        }
    
    def __str__(self) -> str:
        return f"LocationScore({self.raw_score:.2f}, {self.get_commute_description()})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass(frozen=True)
class DetailedScores:
    """
    Représente l'ensemble des scores détaillés par critère.
    """
    
    skills: float
    location: float
    experience: float
    education: float
    preferences: float
    additional_scores: Dict[str, float] = None
    
    def __post_init__(self):
        scores = [self.skills, self.location, self.experience, self.education, self.preferences]
        
        for score in scores:
            if not 0 <= score <= 1:
                raise ValueError(f"All scores must be between 0 and 1, got {score}")
        
        if self.additional_scores is None:
            object.__setattr__(self, 'additional_scores', {})
    
    def get_all_scores(self) -> Dict[str, float]:
        """
        Retourne tous les scores sous forme de dictionnaire.
        
        Returns:
            Dictionnaire de tous les scores
        """
        scores = {
            'skills': self.skills,
            'location': self.location,
            'experience': self.experience,
            'education': self.education,
            'preferences': self.preferences
        }
        scores.update(self.additional_scores)
        return scores
    
    def get_highest_scoring_criterion(self) -> str:
        """
        Retourne le critère avec le score le plus élevé.
        
        Returns:
            Nom du critère
        """
        all_scores = self.get_all_scores()
        return max(all_scores.items(), key=lambda x: x[1])[0]
    
    def get_lowest_scoring_criterion(self) -> str:
        """
        Retourne le critère avec le score le plus bas.
        
        Returns:
            Nom du critère
        """
        all_scores = self.get_all_scores()
        return min(all_scores.items(), key=lambda x: x[1])[0]
    
    def get_scores_by_level(self, level: ScoreLevel) -> List[str]:
        """
        Retourne les critères ayant un niveau de score spécifique.
        
        Args:
            level: Niveau de score recherché
            
        Returns:
            Liste des critères
        """
        criteria = []
        for criterion, score in self.get_all_scores().items():
            if ScoreLevel.from_score(score) == level:
                criteria.append(criterion)
        return criteria
    
    def get_strengths(self) -> List[str]:
        """
        Retourne les points forts (scores ≥ 0.7).
        
        Returns:
            Liste des critères avec bons scores
        """
        strengths = []
        for criterion, score in self.get_all_scores().items():
            if score >= 0.7:
                strengths.append(criterion)
        return strengths
    
    def get_weaknesses(self) -> List[str]:
        """
        Retourne les points faibles (scores < 0.5).
        
        Returns:
            Liste des critères avec scores faibles
        """
        weaknesses = []
        for criterion, score in self.get_all_scores().items():
            if score < 0.5:
                weaknesses.append(criterion)
        return weaknesses
    
    def calculate_weighted_average(self, weights: Dict[str, float]) -> float:
        """
        Calcule la moyenne pondérée des scores.
        
        Args:
            weights: Dictionnaire des poids par critère
            
        Returns:
            Moyenne pondérée
        """
        all_scores = self.get_all_scores()
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, score in all_scores.items():
            weight = weights.get(criterion, 0.0)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def __str__(self) -> str:
        return f"DetailedScores(skills={self.skills:.2f}, location={self.location:.2f}, experience={self.experience:.2f})"
    
    def __repr__(self) -> str:
        return self.__str__()
