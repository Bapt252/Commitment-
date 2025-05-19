"""
Insight Generator Service

Service de domaine pour la génération d'insights de matching.
"""

from typing import List

from ..entities import Candidate, JobOffer
from ..value_objects import (
    DetailedScores, MatchInsight, InsightCollection, InsightType,
    InsightCategory, InsightSeverity
)


class InsightGenerator:
    """
    Service de domaine pour générer des insights sur les résultats de matching.
    
    Analyse les scores et les profils pour identifier les points forts,
    faiblesses et opportunités d'amélioration.
    """
    
    def generate_insights(
        self,
        candidate: Candidate,
        job: JobOffer,
        scores: DetailedScores
    ) -> InsightCollection:
        """
        Génère une collection d'insights pour un matching.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            scores: Scores détaillés du matching
            
        Returns:
            Collection d'insights générés
        """
        insights = []
        
        # Insights sur les compétences
        insights.extend(self._generate_skill_insights(candidate, job, scores.skills))
        
        # Insights sur la localisation
        insights.extend(self._generate_location_insights(candidate, job, scores.location))
        
        # Insights sur l'expérience
        insights.extend(self._generate_experience_insights(candidate, job, scores.experience))
        
        # Insights sur l'éducation
        insights.extend(self._generate_education_insights(candidate, job, scores.education))
        
        # Insights sur les préférences
        insights.extend(self._generate_preference_insights(candidate, job, scores.preferences))
        
        # Insights globaux
        insights.extend(self._generate_global_insights(candidate, job, scores))
        
        return InsightCollection(insights)
    
    def _generate_skill_insights(self, candidate: Candidate, job: JobOffer, score: float) -> List[MatchInsight]:
        """
        Génère des insights sur les compétences.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            score: Score de compétences
            
        Returns:
            Liste d'insights sur les compétences
        """
        insights = []
        
        if score >= 0.9:
            insights.append(MatchInsight.create_strength(
                InsightType.SKILL_MATCH,
                "Excellente correspondance des compétences techniques",
                score,
                {"criterion": "skills", "level": "excellent"}
            ))
        elif score >= 0.7:
            insights.append(MatchInsight.create_strength(
                InsightType.SKILL_MATCH,
                "Bonne correspondance des compétences techniques",
                score,
                {"criterion": "skills", "level": "good"}
            ))
        elif score <= 0.4:
            insights.append(MatchInsight.create_weakness(
                InsightType.SKILL_GAP,
                "Écart important dans les compétences techniques requises",
                score,
                {"criterion": "skills", "level": "poor"}
            ))
            
            # Insight d'opportunité pour combler l'écart
            insights.append(MatchInsight.create_opportunity(
                InsightType.DEVELOPMENT_OPPORTUNITY,
                "Opportunité de développement via formation ou mentorat",
                {"area": "skills", "suggestion": "training"}
            ))
        
        # Analyser les compétences supplémentaires
        additional_skills = candidate.skills.difference(job.get_all_desired_skills())
        if additional_skills.size() > 3:
            insights.append(MatchInsight.create_strength(
                InsightType.SKILL_MATCH,
                f"Le candidat apporte {additional_skills.size()} compétences supplémentaires",
                score,
                {"additional_skills": additional_skills.to_names()}
            ))
        
        return insights
    
    def _generate_location_insights(self, candidate: Candidate, job: JobOffer, score: float) -> List[MatchInsight]:
        """
        Génère des insights sur la localisation.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            score: Score de localisation
            
        Returns:
            Liste d'insights sur la localisation
        """
        insights = []
        
        # Vérifier le télétravail
        if candidate.preferences.remote_work_acceptable and job.offers_remote:
            insights.append(MatchInsight.create_strength(
                InsightType.REMOTE_MATCH,
                "Compatibilité parfaite pour le travail à distance",
                1.0,
                {"work_mode": "remote"}
            ))
        elif candidate.preferences.work_mode.value == "remote" and not job.offers_remote:
            insights.append(MatchInsight.create_weakness(
                InsightType.REMOTE_MISMATCH,
                "Le candidat préfère le télétravail mais le poste ne l'offre pas",
                score,
                {"mismatch": "remote_preference"}
            ))
        
        # Analyser le temps de trajet
        if score >= 0.8:
            insights.append(MatchInsight.create_strength(
                InsightType.LOCATION_MATCH,
                "Temps de trajet optimal",
                score,
                {"commute": "optimal"}
            ))
        elif score <= 0.4:
            insights.append(MatchInsight.create_weakness(
                InsightType.LOCATION_ISSUE,
                "Distance de trajet importante",
                score,
                {"commute": "long"}
            ))
            
            # Suggestion d'alternatives
            if job.offers_remote:
                insights.append(MatchInsight.create_opportunity(
                    InsightType.ALTERNATIVE_PATH,
                    "Le télétravail pourrait résoudre le problème de distance",
                    {"solution": "remote_work"}
                ))
        
        return insights
    
    def _generate_experience_insights(self, candidate: Candidate, job: JobOffer, score: float) -> List[MatchInsight]:
        """
        Génère des insights sur l'expérience.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            score: Score d'expérience
            
        Returns:
            Liste d'insights sur l'expérience
        """
        insights = []
        
        candidate_years = (candidate.experience.min_years + candidate.experience.max_years) / 2
        
        if job.experience_range.contains(int(candidate_years)):
            insights.append(MatchInsight.create_strength(
                InsightType.EXPERIENCE_MATCH,
                "Niveau d'expérience idéal pour ce poste",
                score,
                {"experience_years": candidate_years}
            ))
        elif candidate_years < job.experience_range.min_years:
            gap = job.experience_range.min_years - candidate_years
            insights.append(MatchInsight.create_weakness(
                InsightType.EXPERIENCE_GAP,
                f"Expérience inférieure au minimum requis ({candidate_years:.0f} vs {job.experience_range.min_years} ans)",
                score,
                {"gap_years": gap}
            ))
            
            # Opportunité si l'écart est faible
            if gap <= 2:
                insights.append(MatchInsight.create_opportunity(
                    InsightType.CAREER_ADVANCEMENT,
                    "Opportunité d'accélérer la carrière avec ce poste",
                    {"growth_potential": "high"}
                ))
        else:
            # Candidat surqualifié
            insights.append(MatchInsight.create_strength(
                InsightType.OVERQUALIFIED,
                "Candidat avec expérience supérieure aux exigences",
                score,
                {"overqualification": "experience"}
            ))
        
        return insights
    
    def _generate_education_insights(self, candidate: Candidate, job: JobOffer, score: float) -> List[MatchInsight]:
        """
        Génère des insights sur l'éducation.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            score: Score d'éducation
            
        Returns:
            Liste d'insights sur l'éducation
        """
        insights = []
        
        if candidate.education.meets_requirement(job.required_education):
            if score >= 0.9:
                insights.append(MatchInsight.create_strength(
                    InsightType.EDUCATION_MATCH,
                    "Niveau d'éducation parfait pour ce poste",
                    score,
                    {"education_level": candidate.education.description}
                ))
            elif candidate.education.is_higher_than(job.required_education):
                insights.append(MatchInsight.create_strength(
                    InsightType.OVERQUALIFIED,
                    "Niveau d'éducation supérieur aux exigences",
                    score,
                    {"overqualification": "education"}
                ))
        else:
            insights.append(MatchInsight.create_weakness(
                InsightType.EDUCATION_GAP,
                "Niveau d'éducation inférieur aux prérequis",
                score,
                {
                    "candidate_level": candidate.education.description,
                    "required_level": job.required_education.description
                }
            ))
            
            # Suggestion alternative
            insights.append(MatchInsight.create_opportunity(
                InsightType.ALTERNATIVE_PATH,
                "Évaluer l'expérience pratique comme alternative",
                {"alternative": "practical_experience"}
            ))
        
        return insights
    
    def _generate_preference_insights(self, candidate: Candidate, job: JobOffer, score: float) -> List[MatchInsight]:
        """
        Génère des insights sur les préférences.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            score: Score de préférences
            
        Returns:
            Liste d'insights sur les préférences
        """
        insights = []
        
        # Salaire
        if candidate.preferences.expected_salary_min:
            salary_compatible = job.salary_range.contains(candidate.preferences.expected_salary_min)
            if salary_compatible:
                insights.append(MatchInsight.create_strength(
                    InsightType.SALARY_MATCH,
                    "Attentes salariales alignées avec l'offre",
                    score,
                    {"salary_range": job.salary_range.format()}
                ))
            else:
                if candidate.preferences.expected_salary_min > (job.salary_range.max_amount or job.salary_range.min_amount):
                    insights.append(MatchInsight.create_weakness(
                        InsightType.SALARY_MISMATCH,
                        "Attentes salariales supérieures au budget du poste",
                        score,
                        {
                            "expected": candidate.preferences.expected_salary_min,
                            "offered_max": job.salary_range.max_amount or job.salary_range.min_amount
                        }
                    ))
        
        # Type de poste
        if not candidate.preferences.accepts_job_type(job.requirements.job_type):
            insights.append(MatchInsight.create_weakness(
                InsightType.REMOTE_MISMATCH,  # Réutilisation du type pour mismatch général
                f"Type de poste ({job.requirements.job_type.value}) non aligné avec les préférences",
                score,
                {"job_type_mismatch": True}
            ))
        
        # Secteur d'activité
        industry_score = candidate.preferences.industry_match_score(job.industry)
        if industry_score >= 0.8:
            insights.append(MatchInsight.create_strength(
                InsightType.CULTURE_MATCH,
                "Secteur d'activité aligné avec les intérêts",
                industry_score,
                {"industry": job.industry}
            ))
        
        return insights
    
    def _generate_global_insights(self, candidate: Candidate, job: JobOffer, scores: DetailedScores) -> List[MatchInsight]:
        """
        Génère des insights globaux sur le matching.
        
        Args:
            candidate: Candidat
            job: Offre d'emploi
            scores: Scores détaillés
            
        Returns:
            Liste d'insights globaux
        """
        insights = []
        
        # Analyser l'équilibre des scores
        strengths = scores.get_strengths()
        weaknesses = scores.get_weaknesses()
        
        if len(strengths) >= 4:
            insights.append(MatchInsight.create_strength(
                InsightType.SKILL_MATCH,  # Type générique
                "Profil très compatible avec de nombreux points forts",
                max(scores.get_all_scores().values()),
                {"strength_count": len(strengths), "areas": strengths}
            ))
        
        if len(weaknesses) >= 3:
            insights.append(MatchInsight.create_weakness(
                InsightType.SKILL_GAP,  # Type générique
                "Plusieurs points d'amélioration identifiés",
                min(scores.get_all_scores().values()),
                {"weakness_count": len(weaknesses), "areas": weaknesses}
            ))
        
        # Détecter les profils équilibrés vs spécialisés
        score_values = list(scores.get_all_scores().values())
        score_variance = sum((x - sum(score_values)/len(score_values))**2 for x in score_values) / len(score_values)
        
        if score_variance < 0.05:  # Scores très équilibrés
            insights.append(MatchInsight.create_strength(
                InsightType.SKILL_MATCH,
                "Profil équilibré sur tous les critères",
                sum(score_values) / len(score_values),
                {"profile_type": "balanced"}
            ))
        
        return insights
