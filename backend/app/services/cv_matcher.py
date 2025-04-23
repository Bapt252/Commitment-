from typing import Dict, List, Tuple, Any
import re
from datetime import datetime

from app.models.cv import CV
from app.models.job import JobPosition
from app.models.matching import MatchingScore


class CVMatcherService:
    def match_cv_to_job(self, cv: CV, job: JobPosition) -> MatchingScore:
        """
        Match a CV to a job position and return a matching score
        """
        # Calculate skills score
        skills_score, skill_breakdown, missing_skills = self._calculate_skills_score(
            cv, job
        )
        
        # Calculate software score
        software_score, software_breakdown, missing_softwares = self._calculate_software_score(
            cv, job
        )
        
        # Calculate experience score
        experience_score = self._calculate_experience_score(cv, job)
        
        # Calculate education score
        education_score = self._calculate_education_score(cv, job)
        
        # Calculate total score
        total_score = self._calculate_total_score(
            skills_score, 
            software_score, 
            experience_score, 
            education_score
        )
        
        return MatchingScore(
            total_score=total_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            software_score=software_score,
            skill_breakdown=skill_breakdown,
            software_breakdown=software_breakdown,
            missing_skills=missing_skills,
            missing_softwares=missing_softwares
        )

    def _calculate_skills_score(
        self, cv: CV, job: JobPosition
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Calculate the skills matching score between a CV and a job position
        """
        if not job.required_skills:
            return 100.0, {}, []
        
        # Extract CV skills as lowercase strings for easier comparison
        cv_skills = [skill.name.lower() for skill in cv.skills]
        
        # Track matched skills and their scores
        skill_scores = {}
        total_importance = sum(skill.importance for skill in job.required_skills)
        missing_skills = []
        
        # Calculate score for each required skill
        for req_skill in job.required_skills:
            skill_name = req_skill.name.lower()
            skill_found = False
            
            # Check if the skill is found in CV skills
            for cv_skill in cv_skills:
                if skill_name in cv_skill:
                    skill_found = True
                    skill_scores[req_skill.name] = req_skill.importance
                    break
            
            if not skill_found:
                skill_scores[req_skill.name] = 0
                missing_skills.append(req_skill.name)
        
        # Calculate overall skills score
        if total_importance > 0:
            overall_score = sum(skill_scores.values()) / total_importance * 100
        else:
            overall_score = 100.0
            
        return overall_score, skill_scores, missing_skills

    def _calculate_software_score(
        self, cv: CV, job: JobPosition
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Calculate the software matching score between a CV and a job position
        """
        if not job.required_softwares:
            return 100.0, {}, []
        
        # Extract CV softwares as lowercase strings for easier comparison
        cv_softwares = [sw.lower() for sw in cv.softwares]
        
        # Track matched softwares and their scores
        software_scores = {}
        total_importance = sum(sw.importance for sw in job.required_softwares)
        missing_softwares = []
        
        # Calculate score for each required software
        for req_software in job.required_softwares:
            software_name = req_software.name.lower()
            software_found = False
            
            # Check if the software is found in CV softwares
            for cv_software in cv_softwares:
                if software_name in cv_software:
                    software_found = True
                    software_scores[req_software.name] = req_software.importance
                    break
            
            if not software_found:
                software_scores[req_software.name] = 0
                missing_softwares.append(req_software.name)
        
        # Calculate overall software score
        if total_importance > 0:
            overall_score = sum(software_scores.values()) / total_importance * 100
        else:
            overall_score = 100.0
            
        return overall_score, software_scores, missing_softwares

    def _calculate_experience_score(self, cv: CV, job: JobPosition) -> float:
        """
        Calculate the experience matching score between a CV and a job position
        """
        if not job.required_experience or not cv.experiences:
            return 50.0  # Score neutre si aucune comparaison possible
        
        # Approche simpliste: vérification du nombre total d'années d'expérience
        total_experience = sum(
            self._calculate_experience_duration(exp) for exp in cv.experiences
        )
        
        # Score basé sur la proportion d'expérience requise
        if total_experience >= job.required_experience:
            return 100.0
        else:
            return (total_experience / job.required_experience) * 100.0

    def _calculate_experience_duration(self, experience) -> float:
        """
        Calculate the duration of an experience in years
        """
        # Si aucune date n'est fournie, estimer 1 an
        if not experience.start_date or not experience.end_date:
            return 1.0
            
        # Essayer d'extraire les dates au format YYYY-MM
        try:
            start_date_str = experience.start_date
            end_date_str = experience.end_date
            
            # Transformation simple pour extraire l'année et le mois
            start_year, start_month = self._extract_year_month(start_date_str)
            end_year, end_month = self._extract_year_month(end_date_str)
            
            if start_year and end_year:
                # Calculer la différence en années
                years_diff = end_year - start_year
                months_diff = end_month - start_month
                
                total_years = years_diff + months_diff / 12.0
                return max(0.0, total_years)
        except:
            # En cas d'erreur de parsing, retourner une valeur par défaut
            return 1.0
            
        return 1.0  # Valeur par défaut
    
    def _extract_year_month(self, date_str: str) -> Tuple[int, int]:
        """
        Extract year and month from a date string
        """
        # Chercher les nombres dans la chaîne
        numbers = re.findall(r'\d+', date_str)
        
        year = None
        month = 1  # Par défaut
        
        for num in numbers:
            if len(num) == 4 and 1900 <= int(num) <= 2100:
                year = int(num)
            elif len(num) <= 2 and 1 <= int(num) <= 12:
                month = int(num)
                
        return year or 2000, month  # Valeur par défaut si pas trouvé

    def _calculate_education_score(self, cv: CV, job: JobPosition) -> float:
        """
        Calculate the education matching score between a CV and a job position
        """
        if not job.required_education or not cv.education:
            return 50.0  # Score neutre si aucune comparaison possible
        
        # Approche simpliste: vérifier si une entrée d'éducation correspond à l'éducation requise
        for edu in cv.education:
            if job.required_education.lower() in edu.degree.lower():
                return 100.0
        
        return 0.0  # Aucune correspondance trouvée

    def _calculate_total_score(
        self, 
        skills_score: float, 
        software_score: float, 
        experience_score: float, 
        education_score: float
    ) -> float:
        """
        Calculate the overall matching score based on individual scores
        """
        # Pondérations pour chaque composante (ajustables)
        weights = {
            "skills": 0.4,
            "software": 0.3,
            "experience": 0.2,
            "education": 0.1
        }
        
        total_score = (
            skills_score * weights["skills"] +
            software_score * weights["software"] +
            experience_score * weights["experience"] +
            education_score * weights["education"]
        )
        
        return total_score


cv_matcher_service = CVMatcherService()
