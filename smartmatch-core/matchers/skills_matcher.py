"""
Skills Matcher Implementation
-----------------------------
Matcher spécialisé pour l'évaluation de la correspondance des compétences
entre un candidat et une offre d'emploi.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from .base_matcher import AbstractBaseMatcher
from ..core.models import Candidate, Job, MatchInsight
from ..core.interfaces import NLPService

logger = logging.getLogger(__name__)


class SkillsMatcher(AbstractBaseMatcher):
    """
    Matcher spécialisé pour l'évaluation des compétences.
    Utilise l'analyse sémantique et la correspondance avec synonymes.
    """
    
    def __init__(self, nlp_service: Optional[NLPService] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise le matcher de compétences
        
        Args:
            nlp_service: Service NLP pour l'analyse sémantique
            config: Configuration spécifique
        """
        super().__init__(config)
        self.nlp_service = nlp_service
        
        # Configuration spécifique aux compétences
        self.essential_skill_bonus = config.get('essential_skill_bonus', 1.5)
        self.nice_to_have_factor = config.get('nice_to_have_factor', 0.7)
        self.synonym_threshold = config.get('synonym_threshold', 0.85)
        self.enable_semantic_matching = config.get('enable_semantic_matching', True)
        
        # Dictionnaire de synonymes intégré
        self.skill_synonyms = self._build_skill_synonyms_dict()
        
        logger.debug(f"SkillsMatcher initialized with semantic matching: {self.enable_semantic_matching}")
    
    def _get_default_weight(self) -> float:
        """Retourne le poids par défaut pour le matcher de compétences"""
        return 0.40  # 40% du score total
    
    async def _calculate_specific_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score de correspondance des compétences
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire et normaliser les compétences
        candidate_skills = self._extract_and_normalize_skills(candidate)
        required_skills = self._normalize_skills(job.required_skills)
        preferred_skills = self._normalize_skills(job.preferred_skills)
        
        # Si aucune compétence n'est disponible, retourner score neutre
        if not candidate_skills:
            logger.debug(f"No skills found for candidate {candidate.id}")
            return 0.5
        
        if not required_skills and not preferred_skills:
            logger.debug(f"No required or preferred skills for job {job.id}")
            return 0.5
        
        # Calculer la correspondance pour les compétences requises
        required_score = 0.0
        if required_skills:
            required_matches = await self._find_skill_matches(
                candidate_skills, required_skills
            )
            required_score = len(required_matches) / len(required_skills)
        
        # Calculer la correspondance pour les compétences préférées
        preferred_score = 0.0
        if preferred_skills:
            preferred_matches = await self._find_skill_matches(
                candidate_skills, preferred_skills
            )
            preferred_score = len(preferred_matches) / len(preferred_skills)
        
        # Pondérer les scores : plus de poids pour les compétences requises
        if required_skills and preferred_skills:
            # 70% pour requises, 30% pour préférées
            total_score = (required_score * 0.7) + (preferred_score * 0.3)
        elif required_skills:
            # Seulement des compétences requises
            total_score = required_score
        else:
            # Seulement des compétences préférées
            total_score = preferred_score
        
        # Appliquer un bonus si beaucoup de compétences correspondent
        total_skills = len(required_skills) + len(preferred_skills)
        matched_skills_count = len(await self._find_skill_matches(
            candidate_skills, required_skills + preferred_skills
        ))
        
        coverage_ratio = matched_skills_count / total_skills if total_skills > 0 else 0
        
        # Bonus progressif pour une couverture élevée
        if coverage_ratio >= 0.8:
            total_score = min(1.0, total_score * 1.1)  # 10% de bonus
        elif coverage_ratio >= 0.6:
            total_score = min(1.0, total_score * 1.05)  # 5% de bonus
        
        return total_score
    
    def _generate_specific_insights(self, candidate: Candidate, job: Job, 
                                  score: float) -> List[MatchInsight]:
        """
        Génère des insights spécifiques pour les compétences
        
        Args:
            candidate: Le candidat évalué
            job: L'offre d'emploi évaluée
            score: Le score calculé
            
        Returns:
            Liste d'insights spécifiques aux compétences
        """
        insights = []
        
        try:
            candidate_skills = self._extract_and_normalize_skills(candidate)
            required_skills = self._normalize_skills(job.required_skills)
            preferred_skills = self._normalize_skills(job.preferred_skills)
            
            # Analyser les compétences manquantes
            missing_required = self._find_missing_skills(candidate_skills, required_skills)
            missing_preferred = self._find_missing_skills(candidate_skills, preferred_skills)
            
            # Analyser les compétences en commun
            common_required = self._find_common_skills(candidate_skills, required_skills)
            common_preferred = self._find_common_skills(candidate_skills, preferred_skills)
            
            # Insight sur les compétences requises manquantes
            if missing_required:
                insights.append(MatchInsight(
                    type='weakness',
                    category='skills',
                    message=f"Compétences requises manquantes: {', '.join(missing_required[:3])}",
                    priority=3
                ))
            
            # Insight sur les compétences requises présentes
            if common_required:
                insights.append(MatchInsight(
                    type='strength',
                    category='skills',
                    message=f"Compétences requises maîtrisées: {', '.join(common_required[:3])}",
                    priority=3
                ))
            
            # Insight sur les compétences préférées
            if common_preferred:
                insights.append(MatchInsight(
                    type='strength',
                    category='skills',
                    message=f"Compétences préférées présentes: {', '.join(common_preferred[:2])}",
                    priority=2
                ))
            
            # Insight sur la couverture globale
            total_skills = len(required_skills) + len(preferred_skills)
            matched_skills = len(common_required) + len(common_preferred)
            
            if total_skills > 0:
                coverage = matched_skills / total_skills
                if coverage >= 0.8:
                    insights.append(MatchInsight(
                        type='strength',
                        category='skills',
                        message=f"Excellente couverture des compétences ({coverage:.0%})",
                        priority=3
                    ))
                elif coverage <= 0.3:
                    insights.append(MatchInsight(
                        type='weakness',
                        category='skills',
                        message=f"Couverture insuffisante des compétences ({coverage:.0%})",
                        priority=3
                    ))
            
            # Insight sur les compétences supplémentaires du candidat
            candidate_extra_skills = self._find_extra_skills(
                candidate_skills, required_skills + preferred_skills
            )
            
            if len(candidate_extra_skills) >= 3:
                insights.append(MatchInsight(
                    type='neutral',
                    category='skills',
                    message=f"Compétences supplémentaires: {', '.join(candidate_extra_skills[:3])}",
                    priority=1
                ))
            
        except Exception as e:
            logger.error(f"Error generating skills insights: {str(e)}", exc_info=True)
            insights.append(MatchInsight(
                type='error',
                category='skills',
                message="Erreur lors de l'analyse des compétences",
                priority=1
            ))
        
        return insights
    
    def _extract_and_normalize_skills(self, candidate: Candidate) -> List[str]:
        """
        Extrait et normalise toutes les compétences d'un candidat
        
        Args:
            candidate: Le candidat
            
        Returns:
            Liste de compétences normalisées
        """
        skills = []
        
        # Compétences explicites
        if candidate.skills:
            skills.extend(candidate.skills)
        
        # Extraire des compétences depuis la description via NLP si disponible
        if self.nlp_service and self.enable_semantic_matching:
            try:
                if candidate.summary:
                    extracted = self.nlp_service.extract_skills_from_text(candidate.summary)
                    skills.extend(extracted)
                
                if candidate.experience_description:
                    extracted = self.nlp_service.extract_skills_from_text(candidate.experience_description)
                    skills.extend(extracted)
            except Exception as e:
                logger.warning(f"Failed to extract skills via NLP: {str(e)}\")\n        \n        return self._normalize_skills(skills)\n    \n    def _normalize_skills(self, skills: List[str]) -> List[str]:\n        \"\"\"\n        Normalise une liste de compétences (lowercase, déduplication)\n        \n        Args:\n            skills: Liste de compétences raw\n            \n        Returns:\n            Liste de compétences normalisées\n        \"\"\"\n        if not skills:\n            return []\n        \n        normalized = []\n        seen = set()\n        \n        for skill in skills:\n            if not skill or not skill.strip():\n                continue\n            \n            # Normalisation : lowercase, strip, suppression caractères spéciaux\n            normalized_skill = skill.strip().lower()\n            normalized_skill = ''.join(c for c in normalized_skill if c.isalnum() or c.isspace())\n            normalized_skill = ' '.join(normalized_skill.split())  # Normaliser les espaces\n            \n            if normalized_skill and normalized_skill not in seen:\n                normalized.append(normalized_skill)\n                seen.add(normalized_skill)\n        \n        return normalized\n    \n    async def _find_skill_matches(self, candidate_skills: List[str], \n                                 target_skills: List[str]) -> List[str]:\n        \"\"\"\n        Trouve les compétences du candidat qui correspondent aux compétences cibles\n        \n        Args:\n            candidate_skills: Compétences du candidat\n            target_skills: Compétences cibles (requises ou préférées)\n            \n        Returns:\n            Liste des compétences correspondantes\n        \"\"\"\n        matches = []\n        \n        for target_skill in target_skills:\n            # 1. Correspondance exacte\n            if target_skill in candidate_skills:\n                matches.append(target_skill)\n                continue\n            \n            # 2. Correspondance par synonymes\n            synonym_match = self._find_synonym_match(target_skill, candidate_skills)\n            if synonym_match:\n                matches.append(target_skill)\n                continue\n            \n            # 3. Correspondance sémantique via NLP si disponible\n            if self.nlp_service and self.enable_semantic_matching:\n                try:\n                    semantic_match = await self._find_semantic_match(\n                        target_skill, candidate_skills\n                    )\n                    if semantic_match:\n                        matches.append(target_skill)\n                        continue\n                except Exception as e:\n                    logger.warning(f\"Semantic matching failed for '{target_skill}': {str(e)}\")\n        \n        return matches\n    \n    def _find_synonym_match(self, target_skill: str, candidate_skills: List[str]) -> bool:\n        \"\"\"\n        Vérifie s'il y a une correspondance par synonymes\n        \n        Args:\n            target_skill: Compétence cible\n            candidate_skills: Compétences du candidat\n            \n        Returns:\n            True si une correspondance est trouvée\n        \"\"\"\n        # Vérifier dans le dictionnaire de synonymes\n        for skill_group, synonyms in self.skill_synonyms.items():\n            # Si la compétence cible est dans ce groupe\n            if target_skill == skill_group or target_skill in synonyms:\n                # Vérifier si le candidat a une compétence de ce groupe\n                for candidate_skill in candidate_skills:\n                    if (candidate_skill == skill_group or \n                        candidate_skill in synonyms or\n                        any(syn in candidate_skill for syn in synonyms) or\n                        any(candidate_skill in syn for syn in synonyms)):\n                        return True\n        \n        # Correspondance partielle (contient)\n        for candidate_skill in candidate_skills:\n            if (target_skill in candidate_skill or \n                candidate_skill in target_skill):\n                # Vérifier que c'est suffisamment similaire\n                if len(target_skill) >= 3 and len(candidate_skill) >= 3:\n                    return True\n        \n        return False\n    \n    async def _find_semantic_match(self, target_skill: str, \n                                  candidate_skills: List[str]) -> bool:\n        \"\"\"\n        Vérifie s'il y a une correspondance sémantique via NLP\n        \n        Args:\n            target_skill: Compétence cible\n            candidate_skills: Compétences du candidat\n            \n        Returns:\n            True si une correspondance sémantique est trouvée\n        \"\"\"\n        if not self.nlp_service:\n            return False\n        \n        try:\n            for candidate_skill in candidate_skills:\n                similarity = self.nlp_service.calculate_text_similarity(\n                    target_skill, candidate_skill\n                )\n                \n                if similarity >= self.synonym_threshold:\n                    logger.debug(\n                        f\"Semantic match found: '{target_skill}' <-> '{candidate_skill}' \"\n                        f\"(similarity: {similarity:.3f})\"\n                    )\n                    return True\n            \n            return False\n            \n        except Exception as e:\n            logger.warning(f\"Error in semantic matching: {str(e)}\")\n            return False\n    \n    def _find_missing_skills(self, candidate_skills: List[str], \n                           target_skills: List[str]) -> List[str]:\n        \"\"\"\n        Trouve les compétences cibles que le candidat n'a pas\n        \n        Args:\n            candidate_skills: Compétences du candidat\n            target_skills: Compétences cibles\n            \n        Returns:\n            Liste des compétences manquantes\n        \"\"\"\n        missing = []\n        \n        for target_skill in target_skills:\n            # Vérifier correspondance exacte\n            if target_skill in candidate_skills:\n                continue\n            \n            # Vérifier correspondance par synonymes\n            if self._find_synonym_match(target_skill, candidate_skills):\n                continue\n            \n            missing.append(target_skill)\n        \n        return missing\n    \n    def _find_common_skills(self, candidate_skills: List[str], \n                          target_skills: List[str]) -> List[str]:\n        \"\"\"\n        Trouve les compétences communes entre le candidat et les cibles\n        \n        Args:\n            candidate_skills: Compétences du candidat\n            target_skills: Compétences cibles\n            \n        Returns:\n            Liste des compétences communes\n        \"\"\"\n        common = []\n        \n        for target_skill in target_skills:\n            # Vérifier correspondance exacte\n            if target_skill in candidate_skills:\n                common.append(target_skill)\n                continue\n            \n            # Vérifier correspondance par synonymes\n            if self._find_synonym_match(target_skill, candidate_skills):\n                common.append(target_skill)\n        \n        return common\n    \n    def _find_extra_skills(self, candidate_skills: List[str], \n                         target_skills: List[str]) -> List[str]:\n        \"\"\"\n        Trouve les compétences du candidat qui ne sont pas dans les cibles\n        \n        Args:\n            candidate_skills: Compétences du candidat\n            target_skills: Compétences cibles\n            \n        Returns:\n            Liste des compétences supplémentaires\n        \"\"\"\n        extra = []\n        \n        for candidate_skill in candidate_skills:\n            # Vérifier si cette compétence est dans les cibles\n            if candidate_skill in target_skills:\n                continue\n            \n            # Vérifier correspondance par synonymes\n            is_target = False\n            for target_skill in target_skills:\n                if self._find_synonym_match(candidate_skill, [target_skill]):\n                    is_target = True\n                    break\n            \n            if not is_target:\n                extra.append(candidate_skill)\n        \n        return extra\n    \n    def _build_skill_synonyms_dict(self) -> Dict[str, List[str]]:\n        \"\"\"\n        Construit le dictionnaire de synonymes pour les compétences\n        \n        Returns:\n            Dictionnaire avec compétence principale -> liste de synonymes\n        \"\"\"\n        return {\n            \"javascript\": [\n                \"js\", \"ecmascript\", \"node.js\", \"nodejs\", \"react.js\", \"reactjs\", \n                \"vue.js\", \"vuejs\", \"angular\", \"jquery\", \"typescript\", \"ts\"\n            ],\n            \"python\": [\n                \"py\", \"python3\", \"django\", \"flask\", \"fastapi\", \"pandas\", \n                \"numpy\", \"scipy\", \"pytorch\", \"tensorflow\", \"scikit-learn\"\n            ],\n            \"java\": [\n                \"spring\", \"hibernate\", \"j2ee\", \"javase\", \"javaee\", \"spring boot\",\n                \"maven\", \"gradle\", \"junit\", \"jpa\", \"jsp\", \"servlet\"\n            ],\n            \"php\": [\n                \"laravel\", \"symfony\", \"wordpress\", \"drupal\", \"codeigniter\",\n                \"zend\", \"cake php\", \"yii\", \"composer\"\n            ],\n            \"c#\": [\n                \"csharp\", \".net\", \"dotnet\", \"asp.net\", \"aspnet\", \"mvc\", \n                \"entity framework\", \"wpf\", \"xamarin\", \"unity\"\n            ],\n            \"c++\": [\n                \"cpp\", \"cplusplus\", \"c plus plus\", \"stl\", \"boost\", \"qt\"\n            ],\n            \"ruby\": [\n                \"ror\", \"rails\", \"ruby on rails\", \"sinatra\", \"gem\", \"bundler\"\n            ],\n            \"go\": [\n                \"golang\", \"go lang\"\n            ],\n            \"rust\": [\n                \"rust lang\", \"cargo\"\n            ],\n            \"machine learning\": [\n                \"ml\", \"ai\", \"artificial intelligence\", \"deep learning\", \n                \"neural networks\", \"tensorflow\", \"pytorch\", \"keras\", \"scikit-learn\",\n                \"nlp\", \"computer vision\", \"data science\"\n            ],\n            \"devops\": [\n                \"ci/cd\", \"continuous integration\", \"continuous deployment\", \n                \"docker\", \"kubernetes\", \"k8s\", \"jenkins\", \"gitlab ci\", \"github actions\",\n                \"terraform\", \"ansible\", \"chef\", \"puppet\", \"aws\", \"azure\", \"gcp\"\n            ],\n            \"frontend\": [\n                \"front-end\", \"ui\", \"user interface\", \"ux\", \"user experience\",\n                \"html\", \"css\", \"sass\", \"less\", \"responsive design\", \"bootstrap\",\n                \"tailwind\", \"material ui\", \"chakra ui\"\n            ],\n            \"backend\": [\n                \"back-end\", \"server-side\", \"api\", \"rest api\", \"graphql\", \n                \"middleware\", \"microservices\", \"serverless\"\n            ],\n            \"fullstack\": [\n                \"full-stack\", \"full stack\", \"frontend and backend\", \n                \"front-end and back-end\", \"isomorphic\", \"universal\"\n            ],\n            \"database\": [\n                \"sql\", \"mysql\", \"postgresql\", \"postgres\", \"sqlite\", \"oracle\",\n                \"mongodb\", \"redis\", \"elasticsearch\", \"cassandra\", \"dynamodb\",\n                \"nosql\", \"acid\", \"oltp\", \"olap\", \"etl\"\n            ],\n            \"cloud\": [\n                \"aws\", \"amazon web services\", \"azure\", \"microsoft azure\",\n                \"gcp\", \"google cloud platform\", \"cloud computing\", \"saas\",\n                \"paas\", \"iaas\", \"serverless\", \"lambda\", \"ec2\", \"s3\"\n            ]\n        }\n    \n    def get_configuration(self) -> Dict[str, Any]:\n        \"\"\"Retourne la configuration étendue du matcher\"\"\"\n        config = super().get_configuration()\n        config.update({\n            'essential_skill_bonus': self.essential_skill_bonus,\n            'nice_to_have_factor': self.nice_to_have_factor,\n            'synonym_threshold': self.synonym_threshold,\n            'enable_semantic_matching': self.enable_semantic_matching,\n            'has_nlp_service': self.nlp_service is not None,\n            'synonym_groups_count': len(self.skill_synonyms)\n        })\n        return config\n