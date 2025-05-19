"""
Matching Domain Service

Service de domaine pour les règles métier complexes de matching.
"""

from typing import Dict, List, Tuple

from ..entities import Candidate, JobOffer, MatchResult
from ..value_objects import (
    SkillScore, LocationScore, OverallScore, DetailedScores,
    MatchInsight, InsightCollection
)
from .score_calculator import ScoreCalculator
from .insight_generator import InsightGenerator


class MatchingDomainService:
    """
    Service de domaine pour la logique métier de matching.
    
    Coordonne les calculs de scores et la génération d'insights
    selon les règles métier du domaine.
    """
    
    def __init__(self, 
                 score_calculator: ScoreCalculator,
                 insight_generator: InsightGenerator):
        self._score_calculator = score_calculator
        self._insight_generator = insight_generator
    
    def calculate_compatibility(
        self, 
        candidate: Candidate, 
        job: JobOffer,
        weights: Dict[str, float] = None
    ) -> MatchResult:
        """
        Calcule la compatibilité entre un candidat et une offre d'emploi.
        
        Args:
            candidate: Candidat à évaluer
            job: Offre d'emploi à évaluer
            weights: Pondzération des critères (optionnel)
            
        Returns:
            Résultat complet du matching
        """
        # Poids par défaut si non spécifiés
        if weights is None:
            weights = self._get_default_weights()
        
        # Calcul des scores individuels
        skill_score = self._score_calculator.calculate_skill_score(
            candidate.skills, job.get_all_desired_skills()
        )
        
        location_score = self._score_calculator.calculate_location_score(
            candidate.location, job.location
        )
        
        experience_score = self._score_calculator.calculate_experience_score(
            candidate.experience, job.experience_range
        )
        
        education_score = self._score_calculator.calculate_education_score(
            candidate.education, job.required_education
        )
        
        preference_score = self._score_calculator.calculate_preference_score(
            candidate.preferences, job
        )
        
        # Création des scores détaillés
        detailed_scores = DetailedScores(
            skills=skill_score.normalized_score,
            location=location_score.normalized_score,
            experience=experience_score,
            education=education_score,
            preferences=preference_score
        )
        
        # Calcul du score global pondéré
        overall_score = self._calculate_weighted_score(detailed_scores, weights)
        
        # Génération des insights
        insights = self._insight_generator.generate_insights(
            candidate, job, detailed_scores
        )
        
        # Création du résultat final
        return MatchResult.create(
            candidate_id=candidate.id,
            job_id=job.id,
            overall_score=overall_score,
            skill_score=detailed_scores.skills,
            location_score=detailed_scores.location,
            experience_score=detailed_scores.experience,
            education_score=detailed_scores.education,
            preference_score=detailed_scores.preferences,
            insights=insights.insights
        )
    
    def batch_calculate_compatibility(
        self,
        candidates: List[Candidate],
        jobs: List[JobOffer],
        weights: Dict[str, float] = None
    ) -> List[MatchResult]:
        """
        Calcule la compatibilité pour plusieurs paires candidat-job.
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des offres d'emploi
            weights: Pondération des critères
            
        Returns:
            Liste des résultats de matching
        """
        results = []
        
        for candidate in candidates:
            for job in jobs:
                result = self.calculate_compatibility(candidate, job, weights)
                results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda r: r.overall_score.value, reverse=True)
        
        return results
    
    def find_best_matches(
        self,
        candidate: Candidate,
        jobs: List[JobOffer],
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[MatchResult]:
        """
        Trouve les meilleures offres pour un candidat.
        
        Args:
            candidate: Candidat à matcher
            jobs: Liste des offres disponibles
            limit: Nombre maximum de résultats
            min_score: Score minimum requis
            
        Returns:
            Liste des meilleurs matches
        """
        all_results = []
        
        for job in jobs:
            result = self.calculate_compatibility(candidate, job)
            if result.overall_score.value >= min_score:
                all_results.append(result)
        
        # Trier et limiter
        all_results.sort(key=lambda r: r.overall_score.value, reverse=True)
        return all_results[:limit]
    
    def find_best_candidates(
        self,
        job: JobOffer,
        candidates: List[Candidate],
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[MatchResult]:
        """
        Trouve les meilleurs candidats pour une offre.
        
        Args:
            job: Offre d'emploi à pourvoir
            candidates: Liste des candidats disponibles
            limit: Nombre maximum de résultats
            min_score: Score minimum requis
            
        Returns:
            Liste des meilleurs candidats
        """
        all_results = []
        
        for candidate in candidates:
            result = self.calculate_compatibility(candidate, job)
            if result.overall_score.value >= min_score:
                all_results.append(result)
        
        # Trier et limiter
        all_results.sort(key=lambda r: r.overall_score.value, reverse=True)
        return all_results[:limit]
    
    def analyze_match_quality(
        self,
        result: MatchResult
    ) -> Dict[str, any]:
        """
        Analyse la qualité d'un match et fournit des recommandations.
        
        Args:
            result: Résultat de matching à analyser
            
        Returns:
            Dictionnaire avec analyse et recommandations
        """
        analysis = {
            'quality_level': result.overall_score.level.label,
            'is_recommended': result.is_good_match(),
            'strengths': result.detailed_scores.get_strengths(),
            'weaknesses': result.detailed_scores.get_weaknesses(),
            'strongest_criterion': result.get_strongest_criteria(),
            'weakest_criterion': result.get_weakest_criteria(),
            'critical_issues': result.get_insights_by_category('weakness'),
            'opportunities': result.get_insights_by_category('opportunity')
        }
        
        # Recommandations basées sur l'analyse
        recommendations = self._generate_recommendations(result)
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def _calculate_weighted_score(
        self,
        detailed_scores: DetailedScores,
        weights: Dict[str, float]
    ) -> float:
        """
        Calcule le score global pondéré.
        
        Args:
            detailed_scores: Scores détaillés par critère
            weights: Poids pour chaque critère
            
        Returns:
            Score global pondéré
        """
        return detailed_scores.calculate_weighted_average(weights)
    
    def _get_default_weights(self) -> Dict[str, float]:
        """
        Retourne les poids par défaut pour les critères.
        
        Returns:
            Dictionnaire des poids par défaut
        """
        return {
            'skills': 0.40,
            'location': 0.25,
            'experience': 0.15,
            'education': 0.10,
            'preferences': 0.10
        }
    
    def _generate_recommendations(
        self,
        result: MatchResult
    ) -> List[str]:
        """
        Génère des recommandations basées sur le résultat.
        
        Args:
            result: Résultat de matching
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Recommandations basées sur le score global
        if result.overall_score.value >= 0.9:
            recommendations.append("Excellent match - Procéder rapidement au contact")
        elif result.overall_score.value >= 0.7:
            recommendations.append("Bon match - Organiser un entretien")
        elif result.overall_score.value >= 0.5:
            recommendations.append("Match acceptable - Évaluer plus en détail")
        else:
            recommendations.append("Match faible - Considérer d'autres options")
        
        # Recommandations spécifiques par critère
        weaknesses = result.detailed_scores.get_weaknesses()
        
        if 'skills' in weaknesses:
            recommendations.append("Envisager formation ou mentorat pour combler l'écart de compétences")
        
        if 'location' in weaknesses:
            recommendations.append("Discuter des options de télétravail ou d'aide à la relocalisation")
        
        if 'experience' in weaknesses:
            recommendations.append("Considérer un poste junior ou un plan de développement")
        
        if 'education' in weaknesses:
            recommendations.append("Évaluer l'expérience pratique comme alternative")
        
        return recommendations
