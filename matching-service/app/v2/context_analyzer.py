# Context Analyzer - Analyseur de Contexte SuperSmartMatch V2
# Analyse contextuelle complète pour optimiser la sélection d'algorithme

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .models import (
    MatchingContext, MatchingConfig, DataCompleteness, 
    ProfileType, GeoConstraints, AnalysisType
)

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """
    🔍 ANALYSEUR DE CONTEXTE SUPERSMARTMATCH V2
    
    Analyse complète du contexte de la requête pour optimiser 
    la sélection automatique d'algorithme selon les règles d'audit.
    
    ANALYSES EFFECTUÉES :
    📊 Complétude des données (questionnaires, CV, compétences)
    👤 Profil candidat (séniorité, mobilité, expertise)
    🗺️ Contraintes géographiques (distance, relocalisation, remote)
    🧮 Complexité globale (scoring multi-facteurs)
    🎯 Type d'analyse requis (sémantique, géographique, hybride)
    
    Objectif: Fournir le contexte optimal pour +13% précision
    """
    
    def __init__(self):
        self.analysis_cache = {}
        self.context_stats = {
            'total_analyses': 0,
            'high_completeness': 0,
            'geo_critical': 0,
            'senior_profiles': 0,
            'complex_requests': 0
        }
        
        logger.info("🔍 Context Analyzer initialized for V2 optimization")

    def analyze(self, 
                candidate_data: Dict[str, Any], 
                offers_data: List[Dict[str, Any]], 
                config: MatchingConfig) -> MatchingContext:
        """
        🚀 ANALYSE CONTEXTUELLE COMPLÈTE
        
        Analyse tous les aspects de la requête pour optimiser 
        la sélection d'algorithme et maximiser la précision.
        
        Args:
            candidate_data: Données candidat (V1 + extensions V2)
            offers_data: Liste des offres à analyser
            config: Configuration de matching
            
        Returns:
            MatchingContext: Contexte analysé complet
        """
        
        # Cache key pour optimisation
        cache_key = self._generate_cache_key(candidate_data, offers_data, config)
        if cache_key in self.analysis_cache:
            logger.debug("📋 Context cache hit")
            return self.analysis_cache[cache_key]
        
        logger.info(f"🔍 Starting context analysis - {len(offers_data)} offers")
        
        # Initialisation du contexte
        context = MatchingContext()
        
        # 1. ANALYSE DE COMPLÉTUDE DES DONNÉES
        context.data_completeness = self._assess_data_completeness(
            candidate_data, offers_data
        )
        
        # 2. ANALYSE DU PROFIL CANDIDAT
        context.profile_type = self._analyze_candidate_profile(candidate_data)
        
        # 3. ANALYSE DES CONTRAINTES GÉOGRAPHIQUES
        context.geo_constraints = self._analyze_geo_constraints(
            candidate_data, offers_data
        )
        
        # 4. CALCUL DE LA COMPLEXITÉ GLOBALE
        context.complexity_score = self._calculate_complexity_score(
            context.data_completeness,
            context.profile_type,
            context.geo_constraints,
            len(offers_data)
        )
        
        # 5. DÉTERMINATION DU TYPE D'ANALYSE
        context.analysis_type = self._determine_analysis_type(context)
        
        # 6. DÉTECTION DU BESOIN DE VALIDATION
        context.requires_validation = self._requires_validation(context, config)
        
        # 7. PRIORITÉ PERFORMANCE
        context.performance_priority = config.performance_mode if hasattr(config, 'performance_mode') else True
        
        # Cache et stats
        self.analysis_cache[cache_key] = context
        self._update_context_stats(context)
        
        logger.info(f"✅ Context analysis complete - "
                   f"completeness: {context.data_completeness.overall_score:.2f}, "
                   f"complexity: {context.complexity_score:.2f}, "
                   f"type: {context.analysis_type.value if context.analysis_type else 'standard'}")
        
        return context

    def _assess_data_completeness(self, 
                                 candidate_data: Dict[str, Any], 
                                 offers_data: List[Dict[str, Any]]) -> DataCompleteness:
        """
        📊 ÉVALUATION COMPLÉTUDE DES DONNÉES
        
        Analyse la qualité et complétude des données disponibles
        pour optimiser la sélection Nexten Matcher.
        """
        completeness = DataCompleteness()
        
        # ANALYSE QUESTIONNAIRE CANDIDAT
        candidate_questionnaire = candidate_data.get('questionnaire', {})
        if candidate_questionnaire:
            # Vérification qualité questionnaire
            completion_rate = candidate_questionnaire.get('completion_rate', 0)
            response_count = len(candidate_questionnaire.get('responses', {}))
            response_quality = sum(
                1 for response in candidate_questionnaire.get('responses', {}).values()
                if response and len(str(response).strip()) > 0
            ) / max(response_count, 1)
            
            # Critères pour questionnaire valide
            completeness.candidate_questionnaire = (
                completion_rate > 0.8 and 
                response_count >= 10 and 
                response_quality > 0.7
            )
            completeness.candidate_questionnaire_quality = completion_rate
            
            logger.debug(f"📝 Candidate questionnaire: {completion_rate:.1%} complete, "
                        f"{response_count} responses, quality: {response_quality:.1%}")

        # ANALYSE QUESTIONNAIRES ENTREPRISES
        company_questionnaires = []
        for offer in offers_data:
            company_q = offer.get('questionnaire', {})
            if company_q and len(company_q) > 0:
                # Vérification contenu questionnaire entreprise
                fields_count = len([k for k, v in company_q.items() if v])
                if fields_count >= 5:  # Minimum 5 champs remplis
                    company_questionnaires.append(company_q)
        
        if company_questionnaires:
            completeness.company_questionnaires = len(company_questionnaires) > len(offers_data) * 0.4
            completeness.company_questionnaire_ratio = len(company_questionnaires) / len(offers_data)
            
            logger.debug(f"🏢 Company questionnaires: {len(company_questionnaires)}/{len(offers_data)} "
                        f"({completeness.company_questionnaire_ratio:.1%})")

        # ANALYSE COMPLÉTUDE CV
        cv_data = candidate_data.get('profile', {}).get('cv_data', {})
        cv_fields = ['experience', 'skills', 'education', 'certifications', 'projects']
        cv_field_scores = []
        
        for field in cv_fields:
            field_data = cv_data.get(field, [])
            if isinstance(field_data, list):
                field_score = min(len(field_data) / 3, 1.0)  # Max 3 éléments par champ
            elif isinstance(field_data, dict):
                field_score = min(len(field_data) / 5, 1.0)  # Max 5 clés par dict
            else:
                field_score = 1.0 if field_data else 0.0
            cv_field_scores.append(field_score)
        
        completeness.cv_completeness = sum(cv_field_scores) / len(cv_field_scores)
        
        # SCORE GLOBAL DE COMPLÉTUDE (pondéré pour Nexten Matcher)
        completeness.overall_score = self._calculate_completeness_score(completeness)
        
        logger.debug(f"📋 Data completeness overall: {completeness.overall_score:.2f}")
        
        return completeness

    def _analyze_candidate_profile(self, candidate_data: Dict[str, Any]) -> ProfileType:
        """
        👤 ANALYSE APPROFONDIE DU PROFIL CANDIDAT
        
        Analyse le profil pour optimiser la sélection Enhanced/Semantic.
        """
        profile = ProfileType()
        candidate_profile = candidate_data.get('profile', {})
        
        # ANALYSE EXPÉRIENCE
        profile.experience_years = candidate_profile.get('experience_years', 0)
        
        # Calcul plus précis si données CV disponibles
        if profile.experience_years == 0:
            cv_experience = candidate_profile.get('cv_data', {}).get('experience', [])
            if isinstance(cv_experience, list):
                # Calcul basé sur les postes
                total_years = 0
                for exp in cv_experience:
                    if isinstance(exp, dict):
                        years = exp.get('duration_years', exp.get('years', 1))
                        total_years += years
                profile.experience_years = min(total_years, 30)  # Cap à 30 ans
        
        # DÉTERMINATION NIVEAU SÉNIORITÉ
        if profile.experience_years < 2:
            profile.seniority_level = "junior"
        elif profile.experience_years < 5:
            profile.seniority_level = "mid"
        elif profile.experience_years < 10:
            profile.seniority_level = "senior"
        else:
            profile.seniority_level = "expert"

        # ANALYSE MOBILITÉ AVANCÉE
        location_prefs = candidate_profile.get('location_preferences', {})
        current_location = candidate_profile.get('location', {})
        
        # Analyse fine de la mobilité
        remote_only = location_prefs.get('remote_only', False)
        hybrid_pref = location_prefs.get('hybrid_preferred', False)
        relocation_ok = location_prefs.get('relocation_possible', False)
        max_commute = location_prefs.get('max_commute_distance', 50)
        
        if remote_only:
            profile.mobility_type = "remote"
        elif hybrid_pref:
            profile.mobility_type = "hybrid"
        elif relocation_ok and max_commute > 100:
            profile.mobility_type = "flexible"
        elif max_commute < 20:
            profile.mobility_type = "local"
        else:
            profile.mobility_type = "standard"

        # ANALYSE COMPÉTENCES DÉTAILLÉE
        skills = candidate_profile.get('skills', [])
        if isinstance(skills, list):
            profile.skills_count = len([s for s in skills if s and len(str(s).strip()) > 2])
        else:
            profile.skills_count = 0
        
        # Comptage enrichi depuis CV
        cv_skills = candidate_profile.get('cv_data', {}).get('skills', [])
        if isinstance(cv_skills, list):
            profile.skills_count = max(profile.skills_count, len(cv_skills))

        # ANALYSE EXPÉRIENCE SECTORIELLE
        cv_experience = candidate_profile.get('cv_data', {}).get('experience', [])
        profile.industry_experience = []
        if isinstance(cv_experience, list):
            for exp in cv_experience:
                if isinstance(exp, dict):
                    industry = exp.get('industry', exp.get('sector'))
                    if industry and industry not in profile.industry_experience:
                        profile.industry_experience.append(industry)
        
        logger.debug(f"👤 Profile: {profile.seniority_level} with {profile.experience_years}y, "
                    f"{profile.skills_count} skills, mobility: {profile.mobility_type}")
        
        return profile

    def _analyze_geo_constraints(self, 
                                candidate_data: Dict[str, Any], 
                                offers_data: List[Dict[str, Any]]) -> GeoConstraints:
        """
        🗺️ ANALYSE CONTRAINTES GÉOGRAPHIQUES AVANCÉE
        
        Analyse fine des contraintes géo pour optimiser Smart Match.
        """
        constraints = GeoConstraints()
        
        candidate_location = candidate_data.get('profile', {}).get('location', {})
        candidate_prefs = candidate_data.get('profile', {}).get('location_preferences', {})
        
        # ANALYSE CONTRAINTES OFFRES
        geo_constrained_offers = 0
        remote_offers = 0
        distance_requirements = []
        
        for offer in offers_data:
            offer_location = offer.get('job_data', {}).get('location', {})
            offer_remote = offer_location.get('remote_work', False)
            
            if offer_remote:
                remote_offers += 1
            else:
                geo_constrained_offers += 1
                
            # Collecte des exigences de distance
            required_distance = offer.get('job_data', {}).get('max_commute_required', 50)
            distance_requirements.append(required_distance)

        # CALCUL CRITICITÉ GÉOGRAPHIQUE
        geo_constraint_ratio = geo_constrained_offers / len(offers_data) if offers_data else 0
        remote_ratio = remote_offers / len(offers_data) if offers_data else 0
        
        # Contraintes candidat
        max_commute = candidate_prefs.get('max_commute_distance', 50)
        relocation_possible = candidate_prefs.get('relocation_possible', True)
        remote_acceptable = candidate_prefs.get('remote_acceptable', True)
        
        # DÉTERMINATION CRITICITÉ
        constraints.is_critical = (
            # Majorité des offres ont des contraintes géo
            geo_constraint_ratio > 0.7 or
            # Distance de commute très limitée
            max_commute < 25 or
            # Pas de relocalisation ET pas de remote
            (not relocation_possible and not remote_acceptable) or
            # Beaucoup d'offres exigent proximité
            (distance_requirements and 
             sum(d < 30 for d in distance_requirements) > len(distance_requirements) * 0.6)
        )
        
        constraints.max_distance = max_commute
        constraints.remote_acceptable = remote_acceptable
        constraints.relocation_possible = relocation_possible
        
        # SCORE DE CONTRAINTE (0=flexible, 1=très contraint)
        constraint_factors = [
            1.0 - min(max_commute / 100, 1.0),  # Distance normalisée
            0.5 if not relocation_possible else 0.0,
            0.3 if not remote_acceptable else 0.0,
            geo_constraint_ratio * 0.7
        ]
        constraints.constraint_score = sum(constraint_factors) / len(constraint_factors)
        
        logger.debug(f"🗺️ Geo constraints: {'CRITICAL' if constraints.is_critical else 'standard'}, "
                    f"score: {constraints.constraint_score:.2f}, max_distance: {max_commute}km")
        
        return constraints

    def _calculate_complexity_score(self,
                                   completeness: DataCompleteness,
                                   profile: ProfileType,
                                   geo: GeoConstraints,
                                   offers_count: int) -> float:
        """
        🧮 CALCUL SCORE DE COMPLEXITÉ GLOBAL
        
        Score composite pour déterminer le besoin d'algorithmes avancés.
        """
        
        # Facteurs de complexité (0-1 chacun)
        complexity_factors = {
            # Données: Plus de données = plus complexe à traiter
            'data_richness': min(completeness.overall_score * 1.2, 1.0),
            
            # Profil: Senior + beaucoup de compétences = plus complexe
            'profile_complexity': min(
                (profile.experience_years / 15) + (profile.skills_count / 25), 1.0
            ),
            
            # Géographie: Contraintes fortes = plus complexe
            'geo_complexity': geo.constraint_score,
            
            # Volume: Plus d'offres = plus complexe
            'volume_complexity': min(offers_count / 100, 1.0),
            
            # Mobilité: Types non-standard = plus complexe
            'mobility_complexity': 0.8 if profile.mobility_type in ["remote", "hybrid"] else 0.3
        }
        
        # Pondération des facteurs
        weights = {
            'data_richness': 0.25,
            'profile_complexity': 0.30,
            'geo_complexity': 0.20,
            'volume_complexity': 0.15,
            'mobility_complexity': 0.10
        }
        
        # Score pondéré
        complexity_score = sum(
            complexity_factors[factor] * weights[factor]
            for factor in complexity_factors
        )
        
        logger.debug(f"🧮 Complexity score: {complexity_score:.3f} "
                    f"(data: {complexity_factors['data_richness']:.2f}, "
                    f"profile: {complexity_factors['profile_complexity']:.2f}, "
                    f"geo: {complexity_factors['geo_complexity']:.2f})")
        
        return round(complexity_score, 3)

    def _determine_analysis_type(self, context: MatchingContext) -> Optional[AnalysisType]:
        """
        🎯 DÉTERMINATION TYPE D'ANALYSE REQUIS
        """
        
        # Analyse sémantique pure si beaucoup de compétences
        if context.profile_type.skills_count >= 20:
            return AnalysisType.SEMANTIC_PURE
        
        # Focus géolocalisation si contraintes critiques
        if context.geo_constraints.is_critical:
            return AnalysisType.GEOLOCATION_FOCUSED
        
        # Pondération expérience si profil senior
        if context.profile_type.experience_years >= 7:
            return AnalysisType.EXPERIENCE_WEIGHTED
        
        # Validation hybride si complexité élevée
        if context.complexity_score > 0.8:
            return AnalysisType.HYBRID_VALIDATION
        
        return None  # Analyse standard

    def _requires_validation(self, context: MatchingContext, config: MatchingConfig) -> bool:
        """
        ✅ DÉTECTION BESOIN DE VALIDATION CRITIQUE
        """
        return (
            # Complexité très élevée
            context.complexity_score > 0.9 or
            # Profil expert avec données mixtes
            (context.profile_type.seniority_level == "expert" and
             0.4 < context.data_completeness.overall_score < 0.8) or
            # Validation explicitement demandée
            getattr(config, 'require_validation', False)
        )

    def _calculate_completeness_score(self, completeness: DataCompleteness) -> float:
        """
        Calcul score global complétude (pondéré pour Nexten Matcher)
        """
        weights = {
            'candidate_questionnaire': 0.4,  # Important pour Nexten
            'company_questionnaires': 0.3,   # Important pour Nexten
            'cv_completeness': 0.3           # Base toujours utile
        }
        
        score = 0.0
        score += weights['candidate_questionnaire'] * (1.0 if completeness.candidate_questionnaire else 0.0)
        score += weights['company_questionnaires'] * (1.0 if completeness.company_questionnaires else 0.0)
        score += weights['cv_completeness'] * completeness.cv_completeness
        
        return round(score, 3)

    def _generate_cache_key(self, candidate_data: Dict, offers_data: List[Dict], config: MatchingConfig) -> str:
        """Génération clé de cache pour optimisation"""
        candidate_hash = hash(str(sorted(candidate_data.get('profile', {}).items())))
        offers_hash = hash(tuple(offer.get('job_data', {}).get('id', str(i)) for i, offer in enumerate(offers_data)))
        config_hash = hash(f"{config.algorithm}_{getattr(config, 'performance_mode', True)}")
        
        return f"ctx_{candidate_hash}_{offers_hash}_{config_hash}"

    def _update_context_stats(self, context: MatchingContext):
        """Mise à jour statistiques contexte pour analytics"""
        self.context_stats['total_analyses'] += 1
        
        if context.data_completeness.overall_score > 0.7:
            self.context_stats['high_completeness'] += 1
        
        if context.geo_constraints.is_critical:
            self.context_stats['geo_critical'] += 1
        
        if context.profile_type.experience_years >= 7:
            self.context_stats['senior_profiles'] += 1
        
        if context.complexity_score > 0.8:
            self.context_stats['complex_requests'] += 1

    def get_analytics(self) -> Dict[str, Any]:
        """
        📊 ANALYTICS DU CONTEXTE
        
        Statistiques d'analyse pour optimisation continue.
        """
        total = self.context_stats['total_analyses']
        if total == 0:
            return {"message": "No analyses performed yet"}
        
        return {
            'total_analyses': total,
            'cache_size': len(self.analysis_cache),
            'patterns': {
                'high_completeness_rate': f"{self.context_stats['high_completeness'] / total:.1%}",
                'geo_critical_rate': f"{self.context_stats['geo_critical'] / total:.1%}",
                'senior_profile_rate': f"{self.context_stats['senior_profiles'] / total:.1%}",
                'complex_request_rate': f"{self.context_stats['complex_requests'] / total:.1%}"
            },
            'optimization_opportunities': {
                'nexten_eligible': f"{self.context_stats['high_completeness']} requests",
                'smart_match_needed': f"{self.context_stats['geo_critical']} requests",
                'enhanced_suitable': f"{self.context_stats['senior_profiles']} requests",
                'hybrid_required': f"{self.context_stats['complex_requests']} requests"
            }
        }

    def clear_cache(self):
        """Nettoyage cache pour gestion mémoire"""
        self.analysis_cache.clear()
        logger.info("🧹 Context analysis cache cleared")
