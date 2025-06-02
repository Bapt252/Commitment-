"""
Sélecteur d'algorithme intelligent pour SuperSmartMatch V2

Logique métier centrale qui détermine l'algorithme optimal à utiliser
selon les règles métier et la qualité des données d'entrée.

Règles de sélection :
1. Nexten Matcher : Si questionnaires complets
2. Smart-Match : Pour géolocalisation
3. Enhanced : Pour profils seniors
4. Semantic : Pour NLP complexe
5. Basic : Fallback
"""

import logging
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.matching_models import CVData, JobData
from ..models.algorithm_models import (
    AlgorithmType,
    AlgorithmSelection,
    InputDataAnalysis,
    AlgorithmSelectionConfig
)
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AlgorithmSelector:
    """
    Sélecteur intelligent d'algorithme de matching
    
    Analyse les données d'entrée et sélectionne automatiquement
    l'algorithme optimal selon les règles métier définies.
    """
    
    def __init__(self):
        self.config = AlgorithmSelectionConfig(
            nexten_min_score=settings.nexten_matcher_threshold,
            senior_experience_threshold=settings.senior_experience_threshold,
            complex_skills_threshold=settings.complex_skills_threshold
        )
        self._selection_cache: Dict[str, AlgorithmSelection] = {}
        
        logger.info("🧠 AlgorithmSelector initialisé")
        logger.debug(f"Configuration: {self.config.dict()}")
    
    def select_algorithm(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        force_algorithm: Optional[str] = None
    ) -> AlgorithmSelection:
        """
        Sélectionne l'algorithme optimal
        
        Args:
            cv_data: Données du CV candidat
            jobs: Liste des jobs à matcher
            force_algorithm: Forcer un algorithme spécifique
            
        Returns:
            AlgorithmSelection avec l'algorithme choisi et les raisons
        """
        start_time = datetime.now()
        
        # Vérifier le cache
        cache_key = self._generate_cache_key(cv_data, jobs, force_algorithm)
        if cache_key in self._selection_cache:
            cached_selection = self._selection_cache[cache_key]
            logger.debug(f"📀 Sélection depuis cache: {cached_selection.selected_algorithm}")
            return cached_selection
        
        try:
            # Algorithme forcé
            if force_algorithm:
                algorithm_type = self._parse_algorithm_type(force_algorithm)
                if algorithm_type:
                    selection = AlgorithmSelection(
                        selected_algorithm=algorithm_type,
                        selection_score=100.0,
                        selection_reasons=[f"Algorithme forcé: {force_algorithm}"],
                        forced=True
                    )
                    logger.info(f"🔧 Algorithme forcé: {algorithm_type}")
                    return selection
            
            # Analyse des données d'entrée
            input_analysis = self._analyze_input_data(cv_data, jobs)
            
            # Sélection automatique
            selected_algorithm = self._automatic_selection(input_analysis)
            
            # Création de la réponse
            selection = AlgorithmSelection(
                selected_algorithm=selected_algorithm,
                selection_score=input_analysis.global_data_richness_score,
                selection_reasons=self._generate_selection_reasons(input_analysis, selected_algorithm),
                input_analysis=input_analysis.dict(),
                alternative_algorithms=self._get_alternative_algorithms(selected_algorithm),
                fallback_order=settings.fallback_algorithm_order
            )
            
            # Mise en cache
            if settings.enable_caching:
                self._selection_cache[cache_key] = selection
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(
                f"🎯 Algorithme sélectionné: {selected_algorithm} "
                f"(score: {input_analysis.global_data_richness_score:.1f}, "
                f"durée: {duration_ms:.1f}ms)"
            )
            
            return selection
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sélection d'algorithme: {e}", exc_info=True)
            
            # Fallback vers algorithme de base
            return AlgorithmSelection(
                selected_algorithm=AlgorithmType.BASIC,
                selection_score=0.0,
                selection_reasons=[f"Erreur de sélection, fallback vers basic: {str(e)}"],
                forced=False
            )
    
    def _analyze_input_data(self, cv_data: CVData, jobs: List[JobData]) -> InputDataAnalysis:
        """
        Analyse la qualité et richesse des données d'entrée
        
        Args:
            cv_data: Données CV
            jobs: Liste des jobs
            
        Returns:
            InputDataAnalysis avec scores et indicateurs
        """
        logger.debug("Analyse des données d'entrée...")
        
        # === ANALYSE CV ===
        
        # Complétude du questionnaire
        questionnaire_score = 0.0
        if cv_data.questionnaire_complete:
            questionnaire_score += 40
        if cv_data.profil_comportemental:
            questionnaire_score += 20
        if cv_data.preferences_detaillees:
            questionnaire_score += 20
        if cv_data.score_completude:
            questionnaire_score += cv_data.score_completude * 0.2
        
        questionnaire_score = min(questionnaire_score, 100)
        
        # Qualité des données de localisation
        location_score = 0.0
        has_location_data = False
        if cv_data.localisation:
            location_score += 30
            has_location_data = True
        if cv_data.mobilite_km:
            location_score += 25
        if any(job.localisation for job in jobs):
            location_score += 45
            has_location_data = True
        
        location_score = min(location_score, 100)
        
        # Complexité des compétences
        skills_score = 0.0
        num_skills = len(cv_data.competences)
        has_complex_skills = num_skills >= self.config.complex_skills_threshold
        
        if num_skills > 0:
            skills_score = min((num_skills / 10) * 100, 100)
        
        # Analyse des compétences jobs
        total_job_skills = sum(len(job.competences) for job in jobs)
        if total_job_skills > 0:
            skills_score = min(skills_score + (total_job_skills / len(jobs) / 10) * 50, 100)
        
        # Niveau d'expérience
        experience_score = 0.0
        is_senior_profile = False
        if cv_data.experience:
            experience_score = min((cv_data.experience / 20) * 100, 100)
            is_senior_profile = cv_data.experience >= self.config.senior_experience_threshold
        
        # === ANALYSE JOBS ===
        
        num_jobs = len(jobs)
        num_locations = len(set(job.localisation for job in jobs if job.localisation))
        
        # Score global de richesse des données
        global_score = (
            questionnaire_score * self.config.questionnaire_weight +
            location_score * self.config.location_weight +
            skills_score * self.config.skills_weight +
            experience_score * self.config.experience_weight
        )
        
        # Algorithmes recommandés
        recommended_algorithms = self._recommend_algorithms(
            questionnaire_score, location_score, skills_score, experience_score
        )
        
        # Warnings sur la qualité des données
        warnings = []
        if questionnaire_score < 50:
            warnings.append("Questionnaire incomplet - précision réduite")
        if not has_location_data:
            warnings.append("Données de localisation manquantes")
        if num_skills < 3:
            warnings.append("Peu de compétences renseignées")
        
        analysis = InputDataAnalysis(
            questionnaire_completeness_score=questionnaire_score,
            location_data_quality_score=location_score,
            skills_complexity_score=skills_score,
            experience_level_score=experience_score,
            has_complete_questionnaire=cv_data.questionnaire_complete,
            has_location_data=has_location_data,
            has_complex_skills=has_complex_skills,
            is_senior_profile=is_senior_profile,
            num_skills=num_skills,
            num_jobs=num_jobs,
            num_locations=num_locations,
            global_data_richness_score=global_score,
            recommended_algorithms=recommended_algorithms,
            data_quality_warnings=warnings
        )
        
        logger.debug(f"Analyse terminée - Score global: {global_score:.1f}")
        return analysis
    
    def _automatic_selection(self, analysis: InputDataAnalysis) -> AlgorithmType:
        """
        Sélection automatique basée sur l'analyse des données
        
        Règles de sélection :
        1. Nexten : Score global ≥ 80 (questionnaires complets)
        2. Smart-Match : Données de localisation disponibles
        3. Enhanced : Profil senior (expérience ≥ 10 ans)
        4. Semantic : Compétences complexes (≥ 5)
        5. Basic : Fallback
        """
        global_score = analysis.global_data_richness_score
        
        # 1. Nexten Matcher : Données riches et questionnaire complet
        if (global_score >= self.config.nexten_min_score and 
            analysis.has_complete_questionnaire):
            logger.debug(f"Sélection Nexten: score={global_score}, questionnaire complet")
            return AlgorithmType.NEXTEN
        
        # 2. Smart-Match : Données de localisation disponibles
        if analysis.has_location_data and analysis.location_data_quality_score > 50:
            logger.debug("Sélection Smart-Match: données de localisation")
            return AlgorithmType.SMART_MATCH
        
        # 3. Enhanced : Profil senior
        if analysis.is_senior_profile and analysis.experience_level_score > 60:
            logger.debug("Sélection Enhanced: profil senior")
            return AlgorithmType.ENHANCED
        
        # 4. Semantic : Compétences complexes
        if analysis.has_complex_skills and analysis.skills_complexity_score > 50:
            logger.debug("Sélection Semantic: compétences complexes")
            return AlgorithmType.SEMANTIC
        
        # 5. Basic : Fallback par défaut
        logger.debug("Sélection Basic: fallback par défaut")
        return AlgorithmType.BASIC
    
    def _recommend_algorithms(self, questionnaire_score: float, location_score: float, 
                            skills_score: float, experience_score: float) -> List[AlgorithmType]:
        """Recommande plusieurs algorithmes basés sur les scores"""
        recommendations = []
        
        if questionnaire_score >= 80:
            recommendations.append(AlgorithmType.NEXTEN)
        if location_score > 50:
            recommendations.append(AlgorithmType.SMART_MATCH)
        if experience_score > 60:
            recommendations.append(AlgorithmType.ENHANCED)
        if skills_score > 50:
            recommendations.append(AlgorithmType.SEMANTIC)
        
        # Toujours inclure basic comme fallback
        if AlgorithmType.BASIC not in recommendations:
            recommendations.append(AlgorithmType.BASIC)
        
        return recommendations
    
    def _generate_selection_reasons(self, analysis: InputDataAnalysis, 
                                   selected_algorithm: AlgorithmType) -> List[str]:
        """Génère les raisons de sélection"""
        reasons = []
        
        if selected_algorithm == AlgorithmType.NEXTEN:
            reasons.append(f"Score global élevé: {analysis.global_data_richness_score:.1f}/100")
            if analysis.has_complete_questionnaire:
                reasons.append("Questionnaire complet disponible")
        
        elif selected_algorithm == AlgorithmType.SMART_MATCH:
            reasons.append("Données de géolocalisation disponibles")
            if analysis.location_data_quality_score > 0:
                reasons.append(f"Qualité localisation: {analysis.location_data_quality_score:.1f}/100")
        
        elif selected_algorithm == AlgorithmType.ENHANCED:
            reasons.append("Profil senior détecté")
            if analysis.experience_level_score > 0:
                reasons.append(f"Score expérience: {analysis.experience_level_score:.1f}/100")
        
        elif selected_algorithm == AlgorithmType.SEMANTIC:
            reasons.append("Compétences complexes détectées")
            reasons.append(f"Nombre de compétences: {analysis.num_skills}")
        
        elif selected_algorithm == AlgorithmType.BASIC:
            reasons.append("Algorithme de fallback sélectionné")
            if analysis.data_quality_warnings:
                reasons.extend(analysis.data_quality_warnings)
        
        return reasons
    
    def _get_alternative_algorithms(self, selected: AlgorithmType) -> List[AlgorithmType]:
        """Retourne les algorithmes alternatifs dans l'ordre de priorité"""
        all_algorithms = list(self.config.priority_order)
        
        # Retirer l'algorithme sélectionné
        if selected in all_algorithms:
            all_algorithms.remove(selected)
        
        return all_algorithms
    
    def _parse_algorithm_type(self, algorithm: str) -> Optional[AlgorithmType]:
        """Parse une chaîne en AlgorithmType"""
        algorithm_mapping = {
            "auto": AlgorithmType.AUTO,
            "nexten": AlgorithmType.NEXTEN,
            "smart-match": AlgorithmType.SMART_MATCH,
            "enhanced": AlgorithmType.ENHANCED,
            "semantic": AlgorithmType.SEMANTIC,
            "hybrid": AlgorithmType.HYBRID,
            "basic": AlgorithmType.BASIC
        }
        
        return algorithm_mapping.get(algorithm.lower())
    
    def _generate_cache_key(self, cv_data: CVData, jobs: List[JobData], 
                           force_algorithm: Optional[str]) -> str:
        """Génère une clé de cache pour la sélection"""
        # Créer un hash des données pertinentes
        data_for_hash = {
            "cv_competences": sorted(cv_data.competences),
            "cv_experience": cv_data.experience,
            "cv_localisation": cv_data.localisation,
            "cv_questionnaire_complete": cv_data.questionnaire_complete,
            "jobs_count": len(jobs),
            "jobs_competences": sorted(set(
                skill for job in jobs for skill in job.competences
            )),
            "jobs_locations": sorted(set(
                job.localisation for job in jobs if job.localisation
            )),
            "force_algorithm": force_algorithm
        }
        
        # Créer le hash
        hash_input = str(data_for_hash).encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()
    
    def clear_cache(self):
        """Vide le cache de sélection"""
        self._selection_cache.clear()
        logger.info("🔄 Cache de sélection vidé")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        return {
            "cache_size": len(self._selection_cache),
            "cache_enabled": settings.enable_caching
        }
