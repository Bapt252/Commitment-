"""
Insight Value Objects

Représente les insights générés lors du matching.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class InsightType(Enum):
    """
    Types d'insights possibles.
    """
    # Insights positifs
    SKILL_MATCH = "skill_match"
    EXPERIENCE_MATCH = "experience_match"
    EDUCATION_MATCH = "education_match"
    LOCATION_MATCH = "location_match"
    SALARY_MATCH = "salary_match"
    REMOTE_MATCH = "remote_match"
    CULTURE_MATCH = "culture_match"
    
    # Insights négatifs/gaps
    SKILL_GAP = "skill_gap"
    EXPERIENCE_GAP = "experience_gap"
    EDUCATION_GAP = "education_gap"
    LOCATION_ISSUE = "location_issue"
    SALARY_MISMATCH = "salary_mismatch"
    REMOTE_MISMATCH = "remote_mismatch"
    
    # Insights neutres/informatifs
    OVERQUALIFIED = "overqualified"
    ALTERNATIVE_PATH = "alternative_path"
    DEVELOPMENT_OPPORTUNITY = "development_opportunity"
    CAREER_ADVANCEMENT = "career_advancement"


class InsightCategory(Enum):
    """
    Catégories d'insights.
    """
    STRENGTH = "strength"          # Points forts du match
    WEAKNESS = "weakness"          # Points faibles du match
    OPPORTUNITY = "opportunity"    # Opportunités de développement
    RISK = "risk"                  # Risques potentiels
    NEUTRAL = "neutral"            # Informations neutres


class InsightSeverity(Enum):
    """
    Niveaux de sévérité des insights.
    """
    INFO = (0, "Info")
    LOW = (1, "Low")
    MEDIUM = (2, "Medium")
    HIGH = (3, "High")
    CRITICAL = (4, "Critical")
    
    def __init__(self, level: int, label: str):
        self.level = level
        self.label = label
    
    def __lt__(self, other):
        if isinstance(other, InsightSeverity):
            return self.level < other.level
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, InsightSeverity):
            return self.level <= other.level
        return NotImplemented


@dataclass(frozen=True)
class MatchInsight:
    """
    Représente un insight généré lors du matching.
    """
    
    type: InsightType
    category: InsightCategory
    severity: InsightSeverity
    message: str
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    generated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.score is not None and not 0 <= self.score <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")
        
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        
        if self.generated_at is None:
            object.__setattr__(self, 'generated_at', datetime.now())
    
    @classmethod
    def create_strength(
        cls,
        insight_type: InsightType,
        message: str,
        score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'MatchInsight':
        """
        Crée un insight de type force.
        
        Args:
            insight_type: Type d'insight
            message: Message descriptif
            score: Score associé
            metadata: Métadonnées supplémentaires
            
        Returns:
            Nouvel insight
        """
        severity = InsightSeverity.HIGH if score >= 0.9 else InsightSeverity.MEDIUM
        
        return cls(
            type=insight_type,
            category=InsightCategory.STRENGTH,
            severity=severity,
            message=message,
            score=score,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_weakness(
        cls,
        insight_type: InsightType,
        message: str,
        score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'MatchInsight':
        """
        Crée un insight de type faiblesse.
        
        Args:
            insight_type: Type d'insight
            message: Message descriptif
            score: Score associé
            metadata: Métadonnées supplémentaires
            
        Returns:
            Nouvel insight
        """
        severity = InsightSeverity.HIGH if score <= 0.3 else InsightSeverity.MEDIUM
        
        return cls(
            type=insight_type,
            category=InsightCategory.WEAKNESS,
            severity=severity,
            message=message,
            score=score,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_opportunity(
        cls,
        insight_type: InsightType,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'MatchInsight':
        """
        Crée un insight d'opportunité.
        
        Args:
            insight_type: Type d'insight
            message: Message descriptif
            metadata: Métadonnées supplémentaires
            
        Returns:
            Nouvel insight
        """
        return cls(
            type=insight_type,
            category=InsightCategory.OPPORTUNITY,
            severity=InsightSeverity.LOW,
            message=message,
            metadata=metadata or {}
        )
    
    def is_positive(self) -> bool:
        """
        Vérifie si l'insight est positif.
        
        Returns:
            True si l'insight est une force ou une opportunité
        """
        return self.category in [InsightCategory.STRENGTH, InsightCategory.OPPORTUNITY]
    
    def is_negative(self) -> bool:
        """
        Vérifie si l'insight est négatif.
        
        Returns:
            True si l'insight est une faiblesse ou un risque
        """
        return self.category in [InsightCategory.WEAKNESS, InsightCategory.RISK]
    
    def get_display_icon(self) -> str:
        """
        Retourne une icône pour l'affichage de l'insight.
        
        Returns:
            Caractère Unicode représentant l'insight
        """
        category_icons = {
            InsightCategory.STRENGTH: "✅",      # ✓️
            InsightCategory.WEAKNESS: "⚠️",      # ⚠
            InsightCategory.OPPORTUNITY: "💡",   # 💡
            InsightCategory.RISK: "⛔",          # ⛔
            InsightCategory.NEUTRAL: "ℹ️"       # ℹ
        }
        return category_icons.get(self.category, "ℹ️")
    
    def get_color_code(self) -> str:
        """
        Retourne un code couleur pour l'affichage.
        
        Returns:
            Code couleur hexa
        """
        severity_colors = {
            InsightSeverity.INFO: "#6c757d",      # Gris
            InsightSeverity.LOW: "#17a2b8",       # Bleu clair
            InsightSeverity.MEDIUM: "#ffc107",    # Jaune
            InsightSeverity.HIGH: "#fd7e14",      # Orange
            InsightSeverity.CRITICAL: "#dc3545"   # Rouge
        }
        return severity_colors.get(self.severity, "#6c757d")
    
    def format_for_display(self) -> str:
        """
        Formate l'insight pour l'affichage.
        
        Returns:
            Chaîne formatée pour l'affichage
        """
        icon = self.get_display_icon()
        score_str = f" (Score: {self.score:.0%})" if self.score is not None else ""
        return f"{icon} {self.message}{score_str}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'insight en dictionnaire.
        
        Returns:
            Représentation dictionnaire de l'insight
        """
        return {
            'type': self.type.value,
            'category': self.category.value,
            'severity': self.severity.label,
            'message': self.message,
            'score': self.score,
            'metadata': self.metadata,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'display': {
                'icon': self.get_display_icon(),
                'color': self.get_color_code(),
                'formatted': self.format_for_display()
            }
        }
    
    def __str__(self) -> str:
        return f"Insight({self.category.value}: {self.message})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass(frozen=True)
class InsightCollection:
    """
    Collection d'insights avec méthodes de filtrage et d'analyse.
    """
    
    insights: List[MatchInsight]
    
    def __post_init__(self):
        if self.insights is None:
            object.__setattr__(self, 'insights', [])
    
    def filter_by_category(self, category: InsightCategory) -> 'InsightCollection':
        """
        Filtre les insights par catégorie.
        
        Args:
            category: Catégorie à filtrer
            
        Returns:
            Nouvelle collection filtrée
        """
        filtered = [insight for insight in self.insights if insight.category == category]
        return InsightCollection(filtered)
    
    def filter_by_severity(self, min_severity: InsightSeverity) -> 'InsightCollection':
        """
        Filtre les insights par niveau de sévérité minimum.
        
        Args:
            min_severity: Sévérité minimum
            
        Returns:
            Nouvelle collection filtrée
        """
        filtered = [insight for insight in self.insights if insight.severity >= min_severity]
        return InsightCollection(filtered)
    
    def get_strengths(self) -> List[MatchInsight]:
        """
        Retourne tous les points forts.
        
        Returns:
            Liste des insights de force
        """
        return self.filter_by_category(InsightCategory.STRENGTH).insights
    
    def get_weaknesses(self) -> List[MatchInsight]:
        """
        Retourne tous les points faibles.
        
        Returns:
            Liste des insights de faiblesse
        """
        return self.filter_by_category(InsightCategory.WEAKNESS).insights
    
    def get_opportunities(self) -> List[MatchInsight]:
        """
        Retourne toutes les opportunités.
        
        Returns:
            Liste des insights d'opportunité
        """
        return self.filter_by_category(InsightCategory.OPPORTUNITY).insights
    
    def get_critical_issues(self) -> List[MatchInsight]:
        """
        Retourne les problèmes critiques.
        
        Returns:
            Liste des insights critiques
        """
        return self.filter_by_severity(InsightSeverity.CRITICAL).insights
    
    def get_summary_stats(self) -> Dict[str, int]:
        """
        Statistiques récapitulatives des insights.
        
        Returns:
            Dictionnaire avec les comptages par catégorie
        """
        stats = {
            'total': len(self.insights),
            'strengths': len(self.get_strengths()),
            'weaknesses': len(self.get_weaknesses()),
            'opportunities': len(self.get_opportunities()),
            'critical': len(self.get_critical_issues())
        }
        return stats
    
    def sort_by_severity(self, descending: bool = True) -> 'InsightCollection':
        """
        Trie les insights par sévérité.
        
        Args:
            descending: True pour tri décroissant
            
        Returns:
            Nouvelle collection triée
        """
        sorted_insights = sorted(self.insights, 
                               key=lambda x: x.severity.level, 
                               reverse=descending)
        return InsightCollection(sorted_insights)
    
    def __len__(self) -> int:
        return len(self.insights)
    
    def __iter__(self):
        return iter(self.insights)
    
    def __getitem__(self, index):
        return self.insights[index]
    
    def __str__(self) -> str:
        stats = self.get_summary_stats()
        return f"InsightCollection({stats['total']} insights: {stats['strengths']} strengths, {stats['weaknesses']} weaknesses)"
    
    def __repr__(self) -> str:
        return self.__str__()
