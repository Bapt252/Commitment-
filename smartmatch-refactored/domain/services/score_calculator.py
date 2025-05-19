"""
Score Calculator Service

Service de domaine pour le calcul des différents scores de matching.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, Any

from ..value_objects import (
    SkillSet, Location, ExperienceLevel, ExperienceRange, 
    EducationLevel, CandidatePreferences, SkillScore, LocationScore
)
from ..entities import JobOffer


class SkillSimilarityCalculator(ABC):
    """
    Interface pour les calculateurs de similarité de compétences.
    """
    
    @abstractmethod
    def calculate_similarity(self, skills1: SkillSet, skills2: SkillSet) -> float:
        """Calcule la similarité entre deux ensembles de compétences."""
        pass


class TravelTimeCalculator(ABC):
    """
    Interface pour les calculateurs de temps de trajet.
    """
    
    @abstractmethod
    def calculate_travel_time(self, origin: Location, destination: Location) -> int:
        """Calcule le temps de trajet en minutes."""
        pass


class ScoreCalculator:
    """
    Service de domaine pour le calcul des scores de matching.
    
    Utilise des calculateurs spécialisés injectés pour les calculs complexes.
    """
    
    def __init__(self,
                 skill_similarity_calculator: SkillSimilarityCalculator,
                 travel_time_calculator: TravelTimeCalculator):
        self._skill_calculator = skill_similarity_calculator
        self._travel_calculator = travel_time_calculator
    
    def calculate_skill_score(self, candidate_skills: SkillSet, job_skills: SkillSet) -> SkillScore:
        """
        Calcule le score de compétences entre un candidat et une offre.
        
        Args:
            candidate_skills: Compétences du candidat
            job_skills: Compétences requises pour le poste
            
        Returns:
            Score détaillé des compétences
        """
        if candidate_skills.is_empty() or job_skills.is_empty():
            return SkillScore(
                raw_score=0.5,
                matched_skills=set(),
                missing_skills=job_skills.to_names(),
                additional_skills=candidate_skills.to_names()
            )
        
        # Calcul de la similarité brute
        raw_score = self._skill_calculator.calculate_similarity(candidate_skills, job_skills)
        
        # Analyse des compétences
        matched_skills = candidate_skills.intersection(job_skills)
        missing_skills = job_skills.difference(candidate_skills)
        additional_skills = candidate_skills.difference(job_skills)
        
        return SkillScore(
            raw_score=raw_score,
            matched_skills={skill.name for skill in matched_skills.skills},
            missing_skills={skill.name for skill in missing_skills.skills},
            additional_skills={skill.name for skill in additional_skills.skills}
        )
    
    def calculate_location_score(self, candidate_location: Location, job_location: Location) -> LocationScore:
        """
        Calcule le score de localisation entre un candidat et une offre.
        
        Args:
            candidate_location: Localisation du candidat
            job_location: Localisation du poste
            
        Returns:
            Score détaillé de localisation
        """
        # Si l'une des localisations est manquante
        if not candidate_location or not job_location:
            return LocationScore(raw_score=0.5)
        
        # Calcul du temps de trajet
        try:
            travel_time = self._travel_calculator.calculate_travel_time(
                candidate_location, job_location
            )
            
            # Conversion en score
            score = self._travel_time_to_score(travel_time)
            
            return LocationScore(
                raw_score=score,
                travel_time_minutes=travel_time
            )
            
        except Exception:
            # En cas d'erreur, score neutre
            return LocationScore(raw_score=0.5)
    
    def calculate_experience_score(self, candidate_experience: ExperienceLevel, job_range: ExperienceRange) -> float:
        """
        Calcule le score d'expérience.
        
        Args:
            candidate_experience: Niveau d'expérience du candidat
            job_range: Gamme d'expérience requise
            
        Returns:
            Score d'expérience
        """
        # Utiliser la valeur moyenne du niveau d'expérience
        candidate_years = (candidate_experience.min_years + candidate_experience.max_years) / 2
        
        # Vérifier si dans la gamme
        if job_range.contains(int(candidate_years)):
            return 1.0
        
        # Calculer l'écart
        if candidate_years < job_range.min_years:
            gap = job_range.min_years - candidate_years
            if gap >= 5:
                return 0.2  # Trop peu d'expérience
            else:
                return max(0.2, 1.0 - (gap * 0.15))  # Pénalité progressive
        
        else:  # candidate_years > job_range.max_years (si défini)
            if job_range.max_years is None:
                return 1.0  # Pas de maximum défini
            
            gap = candidate_years - job_range.max_years
            if gap >= 10:
                return 0.5  # Très surqualifié
            else:
                return max(0.7, 1.0 - (gap * 0.03))  # Légère pénalité
    
    def calculate_education_score(self, candidate_education: EducationLevel, required_education: EducationLevel) -> float:
        """
        Calcule le score d'éducation.
        
        Args:
            candidate_education: Niveau d'éducation du candidat
            required_education: Niveau d'éducation requis
            
        Returns:
            Score d'éducation
        """
        # Vérifier si le candidat répond aux exigences
        if candidate_education.meets_requirement(required_education):
            # Calculer bonus/malus selon l'écart
            gap = candidate_education.gap_from(required_education)
            
            if gap == 0:
                return 1.0  # Parfaite correspondance
            elif gap == 1:
                return 0.9  # Un niveau au-dessus
            elif gap == 2:
                return 0.8  # Deux niveaux au-dessus
            else:
                return 0.7  # Plus de deux niveaux
        
        else:
            # Le candidat ne répond pas aux exigences
            gap = abs(candidate_education.gap_from(required_education))
            
            if gap == 1:
                return 0.4  # Un niveau en dessous
            elif gap == 2:
                return 0.2  # Deux niveaux en dessous
            else:
                return 0.1  # Plus de deux niveaux en dessous
    
    def calculate_preference_score(self, preferences: CandidatePreferences, job: JobOffer) -> float:
        """
        Calcule le score de préférences.
        
        Args:
            preferences: Préférences du candidat
            job: Offre d'emploi
            
        Returns:
            Score de préférences
        """
        scores = []
        
        # Type de poste
        if preferences.accepts_job_type(job.requirements.job_type):
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        # Mode de travail
        work_mode_score = job.requirements.work_mode_compatibility(preferences.work_mode)
        scores.append(work_mode_score)
        
        # Salaire
        if preferences.expected_salary_min:
            salary_score = preferences.salary_compatibility_score(
                job.salary_range.min_amount,
                job.salary_range.max_amount or job.salary_range.min_amount
            )
            scores.append(salary_score)
        
        # Secteur d'activité
        industry_score = preferences.industry_match_score(job.industry)
        scores.append(industry_score)
        
        # Date de disponibilité
        start_date_score = job.requirements.start_date_compatibility(preferences.availability_date)
        scores.append(start_date_score)
        
        # Calculer la moyenne
        return sum(scores) / len(scores) if scores else 0.5
    
    def _travel_time_to_score(self, travel_time_minutes: int) -> float:
        """
        Convertit un temps de trajet en score.
        
        Args:
            travel_time_minutes: Temps de trajet en minutes
            
        Returns:
            Score entre 0 et 1
        """
        if travel_time_minutes <= 0:
            return 1.0  # Pas de trajet (remote ou même lieu)
        elif travel_time_minutes <= 30:
            return 1.0  # Excellent
        elif travel_time_minutes <= 45:
            return 0.9  # Très bon
        elif travel_time_minutes <= 60:
            return 0.8  # Bon
        elif travel_time_minutes <= 90:
            return 0.6  # Acceptable
        elif travel_time_minutes <= 120:
            return 0.4  # Médiocre
        else:
            return 0.2  # Mauvais
