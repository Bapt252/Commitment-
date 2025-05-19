"""
MatchResult Entity

Représente le résultat d'un matching entre un candidat et une offre d'emploi.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from ..value_objects import (
    OverallScore,
    DetailedScores,
    MatchInsight
)


@dataclass(frozen=True)
class MatchResult:
    """
    Entité représentant le résultat d'un matching.
    
    Contient le score global, les scores détaillés par critère
    et les insights générés pour expliquer le matching.
    """
    
    candidate_id: str
    job_id: str
    overall_score: OverallScore
    detailed_scores: DetailedScores
    insights: List[MatchInsight]
    calculated_at: datetime
    
    @classmethod
    def create(
        cls,
        candidate_id: str,
        job_id: str,
        overall_score: float,
        skill_score: float,
        location_score: float,
        experience_score: float,
        education_score: float,
        preference_score: float,
        insights: List[MatchInsight]
    ) -> 'MatchResult':
        """
        Factory method pour créer un MatchResult à partir de scores individuels.
        
        Args:
            candidate_id: ID du candidat
            job_id: ID de l'offre d'emploi
            overall_score: Score global (0-1)
            skill_score: Score de compétences (0-1)
            location_score: Score de localisation (0-1) 
            experience_score: Score d'expérience (0-1)
            education_score: Score d'éducation (0-1)
            preference_score: Score de préférences (0-1)
            insights: Liste des insights générés
            
        Returns:
            Instance de MatchResult
        """
        return cls(
            candidate_id=candidate_id,
            job_id=job_id,
            overall_score=OverallScore(overall_score),
            detailed_scores=DetailedScores(
                skills=skill_score,
                location=location_score,
                experience=experience_score,
                education=education_score,
                preferences=preference_score
            ),
            insights=insights,
            calculated_at=datetime.now()
        )
    
    def is_good_match(self, threshold: float = 0.7) -> bool:
        """
        Détermine si le matching est considéré comme bon.
        
        Args:
            threshold: Seuil au-delà duquel le match est considéré comme bon (par défaut 0.7)
            
        Returns:
            True si le score global dépasse le seuil, False sinon
        """
        return self.overall_score.value >= threshold
    
    def get_strongest_criteria(self) -> str:
        """
        Retourne le critère avec le score le plus élevé.
        
        Returns:
            Nom du critère avec le meilleur score
        """
        return self.detailed_scores.get_highest_scoring_criterion()
    
    def get_weakest_criteria(self) -> str:
        """
        Retourne le critère avec le score le plus bas.
        
        Returns:
            Nom du critère avec le score le plus bas
        """
        return self.detailed_scores.get_lowest_scoring_criterion()
    
    def get_insights_by_category(self, category: str) -> List[MatchInsight]:
        """
        Retourne les insights d'une catégorie spécifique.
        
        Args:
            category: Catégorie d'insights recherchée
            
        Returns:
            Liste des insights de la catégorie
        """
        return [insight for insight in self.insights if insight.category == category]
    
    def to_dict(self) -> Dict:
        """
        Convertit le résultat en dictionnaire pour la sérialisation.
        
        Returns:
            Dictionnaire représentant le MatchResult
        """
        return {
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score.value,
            'detailed_scores': {
                'skills': self.detailed_scores.skills,
                'location': self.detailed_scores.location,
                'experience': self.detailed_scores.experience,
                'education': self.detailed_scores.education,
                'preferences': self.detailed_scores.preferences
            },
            'insights': [insight.to_dict() for insight in self.insights],
            'calculated_at': self.calculated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"MatchResult(candidate={self.candidate_id}, job={self.job_id}, score={self.overall_score.value:.2f})"
    
    def __repr__(self) -> str:
        return self.__str__()
