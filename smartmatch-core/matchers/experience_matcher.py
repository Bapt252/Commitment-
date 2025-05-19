"""
Experience Matcher - Matching basé sur l'expérience professionnelle
------------------------------------------------------------------
Matcher spécialisé pour évaluer la correspondance d'expérience
entre candidats et offres d'emploi.

Features:
- Analyse multi-dimensionnelle de l'expérience
- Prise en compte de l'expérience par domaine/technologie
- Gestion des transitions de carrière
- Évaluation du leadership et management
- Correspondance de séniorité
- Insights détaillés sur les écarts d'expérience
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..core.models import Candidate, Job, MatchInsight, Experience
from ..core.interfaces import BaseMatchEngine
from ..core.exceptions import MatcherError
from .base_matcher import BaseMatcher

logger = logging.getLogger(__name__)


class ExperienceMatcher(BaseMatcher):
    """
    Matcher spécialisé pour l'évaluation de l'expérience professionnelle.
    
    Évalue la correspondance basée sur:
    - Années d'expérience totales
    - Expérience par domaine/technologie
    - Niveau de séniorité
    - Expérience de management/leadership
    - Transitions et évolution de carrière
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le matcher d'expérience.
        
        Args:
            config: Configuration personnalisée du matcher
        """
        super().__init__(config)
        
        # Configuration par défaut
        self.default_config = {
            "weights": {
                "total_years": 0.3,
                "relevant_experience": 0.4,
                "seniority_level": 0.2,
                "leadership": 0.1
            },
            "thresholds": {
                "ideal_match": 0.9,
                "underqualified": 0.5,
                "overqualified": 0.7,
                "max_overqualification_years": 10
            },
            "seniority_levels": {
                "intern": {"min_years": 0, "max_years": 1},
                "junior": {"min_years": 0, "max_years": 3},
                "mid": {"min_years": 2, "max_years": 7},
                "senior": {"min_years": 5, "max_years": 12},
                "lead": {"min_years": 7, "max_years": 15},
                "principal": {"min_years": 10, "max_years": 20},
                "executive": {"min_years": 15, "max_years": 50}
            },
            "experience_decay": {
                "enabled": True,
                "decay_start_years": 5,
                "decay_rate": 0.1  # 10% par an après 5 ans
            }
        }
        self.config = {**self.default_config, **(config or {})}
        
        logger.info("ExperienceMatcher initialisé")
    
    async def calculate_match(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score de correspondance d'expérience.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        try:
            scores = {}
            
            # 1. Score basé sur les années totales d'expérience
            scores["total_years"] = self._calculate_total_years_score(candidate, job)
            
            # 2. Score basé sur l'expérience pertinente
            scores["relevant_experience"] = self._calculate_relevant_experience_score(candidate, job)
            
            # 3. Score basé sur le niveau de séniorité
            scores["seniority_level"] = self._calculate_seniority_score(candidate, job)
            
            # 4. Score basé sur l'expérience de leadership
            scores["leadership"] = self._calculate_leadership_score(candidate, job)
            
            # Calculer le score total pondéré
            total_score = sum(
                scores[category] * self.config["weights"][category]
                for category in scores.keys()
            )
            
            # Appliquer les ajustements
            final_score = self._apply_adjustments(total_score, candidate, job)
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"Erreur dans ExperienceMatcher: {str(e)}")
            return 0.5  # Score neutre en cas d'erreur
    
    def _calculate_total_years_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score basé sur les années totales d'expérience.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        candidate_years = self._get_total_experience_years(candidate)
        min_required = job.requirements.experience.min_years if job.requirements.experience else 0
        max_preferred = job.requirements.experience.max_years if job.requirements.experience else float('inf')
        
        # Cas où le candidat a moins que le minimum requis
        if candidate_years < min_required:
            gap = min_required - candidate_years
            # Pénalité progressive selon l'écart
            if gap <= 1:
                return 0.7  # Écart mineur
            elif gap <= 2:
                return 0.5  # Écart modéré
            elif gap <= 3:
                return 0.3  # Écart important
            else:
                return 0.1  # Écart très important
        
        # Cas où le candidat est dans la fourchette idéale
        if min_required <= candidate_years <= max_preferred:
            return 1.0
        
        # Cas où le candidat est surqualifié
        if candidate_years > max_preferred:
            overqualification = candidate_years - max_preferred
            max_over = self.config["thresholds"]["max_overqualification_years"]
            
            if overqualification <= 2:
                return 0.9  # Légèrement surqualifié
            elif overqualification <= 5:
                return 0.7  # Modérément surqualifié
            elif overqualification <= max_over:
                return 0.5  # Très surqualifié mais acceptable
            else:
                return 0.3  # Excessive surqualification
        
        return 0.5  # Cas par défaut
    
    def _calculate_relevant_experience_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score basé sur l'expérience pertinente par domaine.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        if not candidate.experience or not job.requirements.experience:
            return 0.5
        
        # Analyser l'expérience par domaine/technologie
        required_areas = getattr(job.requirements.experience, 'specific_areas', [])
        if not required_areas:
            return 0.8  # Si pas d'exigences spécifiques, score élevé
        
        matched_areas = 0
        total_relevant_years = 0
        
        for area in required_areas:
            area_name = area.get("name", "").lower()
            required_years = area.get("min_years", 0)
            
            # Chercher l'expérience correspondante chez le candidat
            candidate_years = self._find_experience_in_area(candidate, area_name)
            
            if candidate_years >= required_years:
                matched_areas += 1
                total_relevant_years += candidate_years
        
        if not required_areas:
            return 0.8
        
        # Score basé sur le pourcentage d'exigences satisfaites
        coverage_score = matched_areas / len(required_areas)
        
        # Bonus pour l'expérience supplémentaire
        avg_years_per_area = total_relevant_years / len(required_areas) if required_areas else 0
        experience_bonus = min(0.2, avg_years_per_area * 0.02)  # 2% par année, max 20%
        
        return min(1.0, coverage_score + experience_bonus)
    
    def _calculate_seniority_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score basé sur le niveau de séniorité.
        
        Args:
            candidate: Profil du candidat
            job: Offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        candidate_level = getattr(candidate, 'seniority_level', None)
        required_level = getattr(job.requirements, 'seniority_level', None)
        
        if not candidate_level or not required_level:
            return 0.7  # Score neutre si information manquante
        
        # Mapping des niveaux de séniorité
        seniority_order = ["intern", "junior", "mid", "senior", "lead", "principal", "executive"]
        
        try:
            candidate_index = seniority_order.index(candidate_level.lower())
            required_index = seniority_order.index(required_level.lower())
        except ValueError:
            return 0.5  # Niveau inconnu
        
        # Score selon la différence de niveau
        if candidate_index == required_index:
            return 1.0  # Niveau exact
        elif candidate_index == required_index - 1:
            return 0.8  # Un niveau en dessous (acceptable)\n        elif candidate_index == required_index + 1:\n            return 0.9  # Un niveau au dessus (très bien)\n        elif candidate_index < required_index - 1:\n            return 0.4  # Trop junior\n        else:\n            return 0.6  # Trop senior\n    \n    def _calculate_leadership_score(self, candidate: Candidate, job: Job) -> float:\n        \"\"\"\n        Calcule le score basé sur l'expérience de leadership/management.\n        \n        Args:\n            candidate: Profil du candidat\n            job: Offre d'emploi\n            \n        Returns:\n            Score entre 0 et 1\n        \"\"\"\n        requires_leadership = getattr(job.requirements, 'requires_leadership', False)\n        candidate_leadership = self._get_leadership_experience(candidate)\n        \n        # Si le poste ne requiert pas de leadership\n        if not requires_leadership:\n            return 1.0  # Score parfait\n        \n        # Si le poste requiert du leadership\n        if candidate_leadership['has_experience']:\n            years = candidate_leadership['years']\n            team_size = candidate_leadership['max_team_size']\n            \n            # Score basé sur les années d'expérience de management\n            years_score = min(1.0, years / 5)  # Score max à 5 ans\n            \n            # Bonus basé sur la taille d'équipe gérée\n            team_bonus = min(0.3, team_size * 0.03) if team_size else 0\n            \n            return min(1.0, years_score + team_bonus)\n        else:\n            return 0.3  # Pénalité si pas d'expérience de leadership requise\n    \n    def _get_total_experience_years(self, candidate: Candidate) -> float:\n        \"\"\"\n        Calcule le nombre total d'années d'expérience du candidat.\n        \n        Args:\n            candidate: Profil du candidat\n            \n        Returns:\n            Nombre d'années d'expérience\n        \"\"\"\n        if not candidate.experience:\n            return 0.0\n        \n        total_years = 0.0\n        \n        for exp in candidate.experience:\n            if hasattr(exp, 'duration_years'):\n                total_years += exp.duration_years\n            elif hasattr(exp, 'start_date') and hasattr(exp, 'end_date'):\n                # Calculer la durée si les dates sont disponibles\n                start = exp.start_date if exp.start_date else datetime.now()\n                end = exp.end_date if exp.end_date else datetime.now()\n                duration = (end - start).days / 365.25\n                total_years += max(0, duration)\n        \n        return total_years\n    \n    def _find_experience_in_area(self, candidate: Candidate, area: str) -> float:\n        \"\"\"\n        Trouve l'expérience du candidat dans un domaine spécifique.\n        \n        Args:\n            candidate: Profil du candidat\n            area: Domaine/technologie recherché\n            \n        Returns:\n            Nombre d'années d'expérience dans ce domaine\n        \"\"\"\n        if not candidate.experience:\n            return 0.0\n        \n        total_years = 0.0\n        \n        for exp in candidate.experience:\n            # Chercher dans le titre du poste\n            if hasattr(exp, 'position_title') and area in exp.position_title.lower():\n                total_years += self._get_experience_duration(exp)\n            \n            # Chercher dans la description\n            if hasattr(exp, 'description') and area in exp.description.lower():\n                total_years += self._get_experience_duration(exp)\n            \n            # Chercher dans les technologies utilisées\n            if hasattr(exp, 'technologies') and any(area in tech.lower() for tech in exp.technologies):\n                total_years += self._get_experience_duration(exp)\n        \n        return total_years\n    \n    def _get_experience_duration(self, experience: Experience) -> float:\n        \"\"\"\n        Calcule la durée d'une expérience.\n        \n        Args:\n            experience: Expérience professionnelle\n            \n        Returns:\n            Durée en années\n        \"\"\"\n        if hasattr(experience, 'duration_years'):\n            return experience.duration_years\n        \n        if hasattr(experience, 'start_date') and hasattr(experience, 'end_date'):\n            start = experience.start_date\n            end = experience.end_date or datetime.now()\n            duration = (end - start).days / 365.25\n            return max(0, duration)\n        \n        return 0.0\n    \n    def _get_leadership_experience(self, candidate: Candidate) -> Dict[str, Any]:\n        \"\"\"\n        Analyse l'expérience de leadership du candidat.\n        \n        Args:\n            candidate: Profil du candidat\n            \n        Returns:\n            Dict avec informations sur l'expérience de leadership\n        \"\"\"\n        leadership_info = {\n            \"has_experience\": False,\n            \"years\": 0,\n            \"max_team_size\": 0,\n            \"positions\": []\n        }\n        \n        if not candidate.experience:\n            return leadership_info\n        \n        leadership_keywords = [\n            \"manager\", \"lead\", \"director\", \"head\", \"chief\", \"supervisor\",\n            \"team lead\", \"tech lead\", \"project manager\", \"scrum master\"\n        ]\n        \n        for exp in candidate.experience:\n            # Chercher des mots-clés de leadership dans le titre\n            title = getattr(exp, 'position_title', '').lower()\n            \n            if any(keyword in title for keyword in leadership_keywords):\n                leadership_info[\"has_experience\"] = True\n                leadership_info[\"years\"] += self._get_experience_duration(exp)\n                leadership_info[\"positions\"].append(title)\n                \n                # Analyser la taille d'équipe si disponible\n                if hasattr(exp, 'team_size'):\n                    leadership_info[\"max_team_size\"] = max(\n                        leadership_info[\"max_team_size\"],\n                        exp.team_size\n                    )\n        \n        return leadership_info\n    \n    def _apply_adjustments(self, base_score: float, candidate: Candidate, job: Job) -> float:\n        \"\"\"\n        Applique des ajustements finaux au score de base.\n        \n        Args:\n            base_score: Score de base calculé\n            candidate: Profil du candidat\n            job: Offre d'emploi\n            \n        Returns:\n            Score ajusté\n        \"\"\"\n        adjusted_score = base_score\n        \n        # Ajustement pour la diversité des expériences\n        if self._has_diverse_experience(candidate):\n            adjusted_score += 0.05  # Bonus pour la polyvalence\n        \n        # Ajustement pour l'évolution de carrière\n        if self._shows_career_progression(candidate):\n            adjusted_score += 0.1  # Bonus pour la progression\n        \n        # Ajustement pour les périodes d'inactivité\n        gaps_penalty = self._calculate_employment_gaps_penalty(candidate)\n        adjusted_score -= gaps_penalty\n        \n        return adjusted_score\n    \n    def _has_diverse_experience(self, candidate: Candidate) -> bool:\n        \"\"\"\n        Vérifie si le candidat a une expérience diversifiée.\n        \n        Args:\n            candidate: Profil du candidat\n            \n        Returns:\n            True si expérience diversifiée\n        \"\"\"\n        if not candidate.experience or len(candidate.experience) < 3:\n            return False\n        \n        # Analyser la diversité des industries/domaines\n        industries = set()\n        for exp in candidate.experience:\n            if hasattr(exp, 'industry'):\n                industries.add(exp.industry.lower())\n        \n        return len(industries) >= 2\n    \n    def _shows_career_progression(self, candidate: Candidate) -> bool:\n        \"\"\"\n        Vérifie si le candidat montre une progression de carrière.\n        \n        Args:\n            candidate: Profil du candidat\n            \n        Returns:\n            True si progression visible\n        \"\"\"\n        if not candidate.experience or len(candidate.experience) < 2:\n            return False\n        \n        # Trier les expériences par date de début\n        sorted_experience = sorted(\n            candidate.experience,\n            key=lambda x: getattr(x, 'start_date', datetime.min),\n            reverse=True\n        )\n        \n        # Analyser l'évolution des titres/responsabilités\n        leadership_levels = []\n        for exp in sorted_experience:\n            title = getattr(exp, 'position_title', '').lower()\n            level = self._extract_seniority_from_title(title)\n            leadership_levels.append(level)\n        \n        # Vérifier s'il y a une tendance croissante\n        return len(set(leadership_levels)) > 1 and leadership_levels[0] > leadership_levels[-1]\n    \n    def _extract_seniority_from_title(self, title: str) -> int:\n        \"\"\"\n        Extrait un niveau de séniorité numérique d'un titre de poste.\n        \n        Args:\n            title: Titre du poste\n            \n        Returns:\n            Niveau numérique (plus élevé = plus senior)\n        \"\"\"\n        title = title.lower()\n        \n        if any(word in title for word in [\"director\", \"head\", \"chief\", \"vp\"]):\n            return 5\n        elif any(word in title for word in [\"principal\", \"staff\"]):\n            return 4\n        elif any(word in title for word in [\"senior\", \"lead\"]):\n            return 3\n        elif any(word in title for word in [\"mid\", \"intermediate\"]):\n            return 2\n        elif any(word in title for word in [\"junior\", \"associate\"]):\n            return 1\n        else:\n            return 2  # Niveau par défaut\n    \n    def _calculate_employment_gaps_penalty(self, candidate: Candidate) -> float:\n        \"\"\"\n        Calcule la pénalité pour les périodes d'inactivité.\n        \n        Args:\n            candidate: Profil du candidat\n            \n        Returns:\n            Pénalité à appliquer (0 à 0.2)\n        \"\"\"\n        if not candidate.experience:\n            return 0.0\n        \n        # Analyser les écarts entre les emplois\n        sorted_experience = sorted(\n            candidate.experience,\n            key=lambda x: getattr(x, 'start_date', datetime.min)\n        )\n        \n        gaps = []\n        for i in range(1, len(sorted_experience)):\n            prev_end = getattr(sorted_experience[i-1], 'end_date', None)\n            curr_start = getattr(sorted_experience[i], 'start_date', None)\n            \n            if prev_end and curr_start and curr_start > prev_end:\n                gap_months = (curr_start - prev_end).days / 30\n                gaps.append(gap_months)\n        \n        # Calculer la pénalité basée sur les écarts\n        total_gap_months = sum(gaps)\n        \n        if total_gap_months <= 6:\n            return 0.0  # Pas de pénalité pour des écarts courts\n        elif total_gap_months <= 12:\n            return 0.05  # Pénalité légère\n        elif total_gap_months <= 24:\n            return 0.1   # Pénalité modérée\n        else:\n            return 0.2   # Pénalité importante\n    \n    async def generate_insights(\n        self,\n        candidate: Candidate,\n        job: Job,\n        score: float\n    ) -> List[MatchInsight]:\n        \"\"\"\n        Génère des insights détaillés sur le matching d'expérience.\n        \n        Args:\n            candidate: Profil du candidat\n            job: Offre d'emploi\n            score: Score calculé\n            \n        Returns:\n            Liste d'insights\n        \"\"\"\n        insights = []\n        \n        try:\n            # Insight sur les années d'expérience\n            candidate_years = self._get_total_experience_years(candidate)\n            min_required = job.requirements.experience.min_years if job.requirements.experience else 0\n            \n            if candidate_years >= min_required:\n                if candidate_years >= min_required * 1.5:\n                    insights.append(MatchInsight(\n                        category=\"experience\",\n                        type=\"strength\",\n                        title=\"Expérience solide\",\n                        message=f\"Candidat très expérimenté : {candidate_years:.1f} ans (min requis: {min_required})\",\n                        score=score,\n                        details={\n                            \"candidate_years\": candidate_years,\n                            \"required_years\": min_required,\n                            \"excess_years\": candidate_years - min_required\n                        }\n                    ))\n                else:\n                    insights.append(MatchInsight(\n                        category=\"experience\",\n                        type=\"strength\",\n                        title=\"Expérience adéquate\",\n                        message=f\"Expérience suffisante : {candidate_years:.1f} ans (min requis: {min_required})\",\n                        score=score,\n                        details={\n                            \"candidate_years\": candidate_years,\n                            \"required_years\": min_required\n                        }\n                    ))\n            else:\n                gap = min_required - candidate_years\n                insights.append(MatchInsight(\n                    category=\"experience\",\n                    type=\"weakness\",\n                    title=\"Expérience insuffisante\",\n                    message=f\"Écart d'expérience : {gap:.1f} ans manquantes\",\n                    score=score,\n                    details={\n                        \"candidate_years\": candidate_years,\n                        \"required_years\": min_required,\n                        \"gap_years\": gap\n                    }\n                ))\n            \n            # Insight sur l'expérience de leadership\n            leadership_info = self._get_leadership_experience(candidate)\n            requires_leadership = getattr(job.requirements, 'requires_leadership', False)\n            \n            if requires_leadership:\n                if leadership_info[\"has_experience\"]:\n                    insights.append(MatchInsight(\n                        category=\"experience\",\n                        type=\"strength\",\n                        title=\"Expérience de leadership\",\n                        message=f\"Expérience de management : {leadership_info['years']:.1f} ans\",\n                        score=score,\n                        details=leadership_info\n                    ))\n                else:\n                    insights.append(MatchInsight(\n                        category=\"experience\",\n                        type=\"weakness\",\n                        title=\"Manque d'expérience de leadership\",\n                        message=\"Aucune expérience de management détectée\",\n                        score=score,\n                        details={\"required\": True, \"found\": False}\n                    ))\n            \n            # Insight sur la progression de carrière\n            if self._shows_career_progression(candidate):\n                insights.append(MatchInsight(\n                    category=\"experience\",\n                    type=\"strength\",\n                    title=\"Progression de carrière\",\n                    message=\"Évolution positive visible dans le parcours professionnel\",\n                    score=score,\n                    details={\"career_progression\": True}\n                ))\n            \n            # Insight sur la diversité d'expérience\n            if self._has_diverse_experience(candidate):\n                insights.append(MatchInsight(\n                    category=\"experience\",\n                    type=\"strength\",\n                    title=\"Expérience diversifiée\",\n                    message=\"Profil polyvalent avec expérience dans plusieurs domaines\",\n                    score=score,\n                    details={\"diverse_experience\": True}\n                ))\n        \n        except Exception as e:\n            logger.error(f\"Erreur génération insights ExperienceMatcher: {str(e)}\")\n            insights.append(MatchInsight(\n                category=\"experience\",\n                type=\"info\",\n                title=\"Analyse d'expérience limitée\",\n                message=\"Impossible d'analyser complètement l'expérience\",\n                score=score,\n                details={\"error\": str(e)}\n            ))\n        \n        return insights\n