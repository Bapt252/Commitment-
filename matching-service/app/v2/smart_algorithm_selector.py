# Smart Algorithm Selector - Sélecteur Intelligent d'Algorithmes
# Basé sur les règles d'audit technique pour maximiser la précision

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import (
    AlgorithmType, MatchingContext, MatchingConfig,
    DataCompleteness, ProfileType, GeoConstraints, AnalysisType
)

logger = logging.getLogger(__name__)

class SmartAlgorithmSelector:
    """
    🎯 SÉLECTEUR INTELLIGENT D'ALGORITHMES SUPERSMARTMATCH V2
    
    Implémente les règles de sélection identifiées dans l'audit technique
    pour maximiser automatiquement la précision selon le contexte.
    
    RÈGLES DE PRIORITÉ (basées sur audit) :
    1. NEXTEN MATCHER : Si questionnaires complets + 5+ compétences (PRIORITÉ MAX)
    2. SMART MATCH : Si contraintes géographiques critiques / mobilité complexe  
    3. ENHANCED MATCH : Si profil senior (7+ ans) sans questionnaires complets
    4. SEMANTIC MATCH : Si analyse sémantique pure nécessaire (20+ compétences)
    5. HYBRID MATCH : Si validation critique / complexité > 0.9
    6. DÉFAUT INTELLIGENT : NEXTEN MATCHER (algorithme le plus performant)
    
    Objectif : +13% précision via sélection optimale automatique
    """
    
    def __init__(self):
        self.selection_rules = self._initialize_selection_rules()
        self.performance_history = {}
        self.selection_stats = {
            AlgorithmType.NEXTEN_MATCHER: 0,
            AlgorithmType.SMART_MATCH: 0,
            AlgorithmType.ENHANCED_MATCH: 0,
            AlgorithmType.SEMANTIC_MATCH: 0,
            AlgorithmType.HYBRID_MATCH: 0
        }
        
        logger.info("🎯 Smart Algorithm Selector initialized with audit rules")

    def select(self, context: MatchingContext, config: MatchingConfig) -> AlgorithmType:
        """
        🚀 SÉLECTION AUTOMATIQUE INTELLIGENTE D'ALGORITHME
        
        Applique les règles d'audit pour choisir l'algorithme optimal
        selon le contexte de la requête.
        
        Args:
            context: Contexte analysé de la requête
            config: Configuration matching
            
        Returns:
            AlgorithmType optimal selon les règles d'audit
        """
        
        # Sélection manuelle si spécifiée (override)
        if config.algorithm != "auto":
            algorithm = AlgorithmType(config.algorithm)
            logger.info(f"🔧 Manual algorithm selection: {algorithm.value}")
            self._update_selection_stats(algorithm)
            return algorithm
        
        # APPLICATION DES RÈGLES D'AUDIT (par ordre de priorité)
        
        # 🥇 RÈGLE 1: NEXTEN MATCHER si données complètes (PRIORITÉ MAXIMALE)
        if self._should_use_nexten_matcher(context):
            logger.info("🥇 Nexten Matcher selected: Complete questionnaire data available")
            self._update_selection_stats(AlgorithmType.NEXTEN_MATCHER)
            return AlgorithmType.NEXTEN_MATCHER
        
        # 🥈 RÈGLE 2: SMART MATCH pour contraintes géographiques critiques
        if self._should_use_smart_match(context):
            logger.info("🥈 Smart Match selected: Critical geographical constraints")
            self._update_selection_stats(AlgorithmType.SMART_MATCH)
            return AlgorithmType.SMART_MATCH
        
        # 🥉 RÈGLE 3: ENHANCED MATCH pour profils seniors sans questionnaires complets
        if self._should_use_enhanced_match(context):
            logger.info("🥉 Enhanced Match selected: Senior profile optimization")
            self._update_selection_stats(AlgorithmType.ENHANCED_MATCH)
            return AlgorithmType.ENHANCED_MATCH
        
        # 🏅 RÈGLE 4: SEMANTIC MATCH pour analyse sémantique pure
        if self._should_use_semantic_match(context):
            logger.info("🏅 Semantic Match selected: High skills count semantic analysis")
            self._update_selection_stats(AlgorithmType.SEMANTIC_MATCH)
            return AlgorithmType.SEMANTIC_MATCH
        
        # 🎖️ RÈGLE 5: HYBRID MATCH pour validation critique
        if self._should_use_hybrid_match(context):
            logger.info("🎖️ Hybrid Match selected: High complexity cross-validation")
            self._update_selection_stats(AlgorithmType.HYBRID_MATCH)
            return AlgorithmType.HYBRID_MATCH
        
        # 🎯 DÉFAUT INTELLIGENT: NEXTEN MATCHER (le plus performant selon audit)
        logger.info("🎯 Nexten Matcher selected: Default high-performance algorithm")
        self._update_selection_stats(AlgorithmType.NEXTEN_MATCHER)
        return AlgorithmType.NEXTEN_MATCHER

    def _should_use_nexten_matcher(self, context: MatchingContext) -> bool:
        """
        🥇 RÈGLE NEXTEN MATCHER - PRIORITÉ MAXIMALE
        
        Conditions selon audit :
        - Questionnaires candidat ET entreprise disponibles
        - Score complétude globale > 0.7
        - Suffisamment de compétences pour analyse (≥ 5)
        - OU défaut intelligent si aucune autre règle ne s'applique
        """
        return (
            # Données complètes disponibles
            context.data_completeness.candidate_questionnaire and
            context.data_completeness.company_questionnaires and
            context.data_completeness.overall_score > 0.7 and
            # Suffisamment de compétences pour analyse Nexten
            context.profile_type.skills_count >= 5
        )

    def _should_use_smart_match(self, context: MatchingContext) -> bool:
        """
        🥈 RÈGLE SMART MATCH - GÉOLOCALISATION CRITIQUE
        
        Conditions selon audit :
        - Contraintes géographiques critiques détectées
        - Profil remote/hybrid/mobilité complexe
        - Distance de commute très limitée (<25km)
        - Relocalisation impossible
        """
        return (
            # Contraintes géographiques critiques
            context.geo_constraints.is_critical or
            # Profil mobilité complexe
            context.profile_type.mobility_type in ["remote", "hybrid", "flexible"] or
            # Distance très limitée
            (context.geo_constraints.max_distance and 
             context.geo_constraints.max_distance < 25) or
            # Pas de relocalisation possible
            not context.geo_constraints.relocation_possible
        )

    def _should_use_enhanced_match(self, context: MatchingContext) -> bool:
        """
        🥉 RÈGLE ENHANCED MATCH - PROFILS SENIORS
        
        Conditions selon audit :
        - Profil senior ou expert (7+ ans d'expérience)
        - Questionnaires partiels ou inexistants
        - CV suffisamment complet pour compensation
        - Pondération adaptative nécessaire
        """
        return (
            # Profil senior/expert
            context.profile_type.experience_years >= 7 and
            # Questionnaires incomplets
            not context.data_completeness.candidate_questionnaire and
            # CV suffisamment complet pour compensation
            context.data_completeness.cv_completeness > 0.6 and
            # Niveau séniorité confirmé
            context.profile_type.seniority_level in ["senior", "expert"]
        )

    def _should_use_semantic_match(self, context: MatchingContext) -> bool:
        """
        🏅 RÈGLE SEMANTIC MATCH - ANALYSE SÉMANTIQUE PURE
        
        Conditions selon audit :
        - Analyse sémantique pure requise
        - Beaucoup de compétences à analyser (20+)
        - Profil très technique nécessitant analyse fine
        - Pas de questionnaires mais données CV riches
        """
        return (
            # Type d'analyse sémantique requis
            context.analysis_type == AnalysisType.SEMANTIC_PURE or
            # Beaucoup de compétences à analyser
            context.profile_type.skills_count >= 20 or
            # Profil très technique
            (context.profile_type.seniority_level in ["senior", "expert"] and
             context.data_completeness.cv_completeness > 0.8 and
             not context.data_completeness.candidate_questionnaire)
        )

    def _should_use_hybrid_match(self, context: MatchingContext) -> bool:
        """
        🎖️ RÈGLE HYBRID MATCH - VALIDATION CRITIQUE
        
        Conditions selon audit :
        - Validation critique demandée explicitement
        - Complexité très élevée (>0.9)
        - Profil expert avec données mixtes
        - Consensus multi-algorithmes nécessaire
        """
        return (
            # Validation critique explicite
            context.requires_validation or
            # Complexité très élevée
            context.complexity_score > 0.9 or
            # Profil expert avec données mixtes (ni complètes ni vides)
            (context.profile_type.seniority_level == "expert" and
             0.4 < context.data_completeness.overall_score < 0.8) or
            # Performance mode désactivé ET haute complexité
            (not getattr(context, 'performance_priority', True) and
             context.complexity_score > 0.7)
        )

    def _initialize_selection_rules(self) -> Dict[str, Any]:
        """
        Initialisation des règles de sélection avec poids et seuils
        """
        return {
            'nexten_matcher': {
                'priority': 1,
                'completeness_threshold': 0.7,
                'skills_min': 5,
                'expected_precision': 0.95
            },
            'smart_match': {
                'priority': 2,
                'geo_critical_threshold': 25,  # km
                'mobility_types': ["remote", "hybrid", "flexible"],
                'expected_precision': 0.87
            },
            'enhanced_match': {
                'priority': 3,
                'experience_min': 7,
                'cv_completeness_min': 0.6,
                'expected_precision': 0.89
            },
            'semantic_match': {
                'priority': 4,
                'skills_threshold': 20,
                'cv_completeness_min': 0.8,
                'expected_precision': 0.84
            },
            'hybrid_match': {
                'priority': 5,
                'complexity_threshold': 0.9,
                'validation_required': True,
                'expected_precision': 0.91
            }
        }

    def _update_selection_stats(self, algorithm: AlgorithmType):
        """Met à jour les statistiques de sélection"""
        self.selection_stats[algorithm] += 1

    def get_selection_analytics(self) -> Dict[str, Any]:
        """
        �📊 ANALYTICS DE SÉLECTION
        
        Retourne les statistiques d'utilisation des algorithmes
        pour optimisation continue des règles.
        """
        total_selections = sum(self.selection_stats.values())
        
        if total_selections == 0:
            return {"message": "No selections recorded yet"}
        
        selection_percentages = {
            algo.value: round((count / total_selections) * 100, 1)
            for algo, count in self.selection_stats.items()
        }
        
        # Calcul de l'efficacité selon objectifs audit
        nexten_usage = selection_percentages.get('nexten_matcher', 0)
        audit_target_nexten = 70  # Objectif: 70%+ d'utilisation Nexten
        
        return {
            'total_selections': total_selections,
            'algorithm_distribution': selection_percentages,
            'nexten_matcher_usage': f"{nexten_usage}%",
            'audit_compliance': {
                'nexten_target': f"{audit_target_nexten}%",
                'current_nexten': f"{nexten_usage}%",
                'target_met': nexten_usage >= audit_target_nexten,
                'precision_improvement_estimate': f"+{nexten_usage * 0.13 / 70:.1f}%" if nexten_usage > 0 else "0%"
            },
            'optimization_suggestions': self._get_optimization_suggestions(selection_percentages),
            'rules_effectiveness': self._calculate_rules_effectiveness()
        }

    def _get_optimization_suggestions(self, percentages: Dict[str, float]) -> List[str]:
        """Suggestions d'optimisation basées sur l'usage"""
        suggestions = []
        
        nexten_usage = percentages.get('nexten_matcher', 0)
        if nexten_usage < 50:
            suggestions.append("📈 Consider lowering Nexten Matcher thresholds for higher precision")
        
        smart_usage = percentages.get('smart_match', 0)
        if smart_usage > 30:
            suggestions.append("🗺️ High geo-constraint usage detected - consider geo-data optimization")
        
        hybrid_usage = percentages.get('hybrid_match', 0)
        if hybrid_usage > 20:
            suggestions.append("⚡ High hybrid usage suggests complex profiles - consider simplification")
        
        if not suggestions:
            suggestions.append("✅ Algorithm selection distribution is optimal")
        
        return suggestions

    def _calculate_rules_effectiveness(self) -> Dict[str, str]:
        """Calcule l'efficacité des règles de sélection"""
        rules_performance = {}
        
        for rule_name, rule_config in self.selection_rules.items():
            expected_precision = rule_config.get('expected_precision', 0.8)
            priority = rule_config.get('priority', 5)
            
            # Score d'efficacité basé sur précision attendue et priorité
            effectiveness_score = expected_precision * (6 - priority) / 5
            
            if effectiveness_score > 0.9:
                effectiveness = "Excellent"
            elif effectiveness_score > 0.8:
                effectiveness = "Good"
            elif effectiveness_score > 0.7:
                effectiveness = "Fair"
            else:
                effectiveness = "Needs improvement"
            
            rules_performance[rule_name] = effectiveness
        
        return rules_performance

    def explain_selection(self, context: MatchingContext, selected: AlgorithmType) -> Dict[str, Any]:
        """
        🔍 EXPLICATION DÉTAILLÉE DE LA SÉLECTION
        
        Fournit une explication complète du choix d'algorithme
        pour transparence et debug.
        """
        explanation = {
            'selected_algorithm': selected.value,
            'selection_reason': self._get_detailed_reason(context, selected),
            'context_factors': {
                'data_completeness': {
                    'overall_score': context.data_completeness.overall_score,
                    'candidate_questionnaire': context.data_completeness.candidate_questionnaire,
                    'company_questionnaires': context.data_completeness.company_questionnaires,
                    'cv_completeness': context.data_completeness.cv_completeness
                },
                'profile_analysis': {
                    'experience_years': context.profile_type.experience_years,
                    'seniority_level': context.profile_type.seniority_level,
                    'skills_count': context.profile_type.skills_count,
                    'mobility_type': context.profile_type.mobility_type
                },
                'geo_constraints': {
                    'is_critical': context.geo_constraints.is_critical,
                    'max_distance': context.geo_constraints.max_distance,
                    'relocation_possible': context.geo_constraints.relocation_possible
                },
                'complexity_metrics': {
                    'complexity_score': context.complexity_score,
                    'requires_validation': context.requires_validation,
                    'analysis_type': context.analysis_type.value if context.analysis_type else 'standard'
                }
            },
            'rule_evaluation': self._evaluate_all_rules(context),
            'expected_precision': self.selection_rules.get(selected.value.replace('_', ''), {}).get('expected_precision', 0.8),
            'alternative_algorithms': self._get_alternatives_with_scores(context)
        }
        
        return explanation

    def _get_detailed_reason(self, context: MatchingContext, selected: AlgorithmType) -> str:
        """Raison détaillée de la sélection"""
        if selected == AlgorithmType.NEXTEN_MATCHER:
            if self._should_use_nexten_matcher(context):
                return f"Optimal conditions: Complete questionnaires + {context.profile_type.skills_count} skills"
            else:
                return "Default high-performance selection (no specific conditions met)"
        elif selected == AlgorithmType.SMART_MATCH:
            return f"Geographic constraints critical (distance: {context.geo_constraints.max_distance}km)"
        elif selected == AlgorithmType.ENHANCED_MATCH:
            return f"Senior profile optimization ({context.profile_type.experience_years} years experience)"
        elif selected == AlgorithmType.SEMANTIC_MATCH:
            return f"Semantic analysis required ({context.profile_type.skills_count} skills to analyze)"
        elif selected == AlgorithmType.HYBRID_MATCH:
            return f"High complexity validation (score: {context.complexity_score:.2f})"
        
        return "Standard selection"

    def _evaluate_all_rules(self, context: MatchingContext) -> Dict[str, bool]:
        """Évalue toutes les règles pour transparency"""
        return {
            'nexten_matcher_eligible': self._should_use_nexten_matcher(context),
            'smart_match_eligible': self._should_use_smart_match(context),
            'enhanced_match_eligible': self._should_use_enhanced_match(context),
            'semantic_match_eligible': self._should_use_semantic_match(context),
            'hybrid_match_eligible': self._should_use_hybrid_match(context)
        }

    def _get_alternatives_with_scores(self, context: MatchingContext) -> Dict[str, float]:
        """Algorithmes alternatifs avec scores de pertinence"""
        alternatives = {}
        
        # Score pour chaque algorithme basé sur le contexte
        if context.data_completeness.overall_score > 0.5:
            alternatives['nexten_matcher'] = context.data_completeness.overall_score
        
        if context.geo_constraints.is_critical:
            alternatives['smart_match'] = 0.9
        
        if context.profile_type.experience_years >= 5:
            alternatives['enhanced_match'] = min(context.profile_type.experience_years / 15, 1.0)
        
        if context.profile_type.skills_count > 10:
            alternatives['semantic_match'] = min(context.profile_type.skills_count / 25, 1.0)
        
        if context.complexity_score > 0.6:
            alternatives['hybrid_match'] = context.complexity_score
        
        return alternatives
