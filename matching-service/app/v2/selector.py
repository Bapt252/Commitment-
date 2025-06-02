"""
SuperSmartMatch V2 - Sélecteur Intelligent d'Algorithmes
========================================================

Sélecteur qui applique l'intelligence artificielle pour choisir automatiquement
l'algorithme optimal selon le contexte et les données disponibles.

Basé sur l'audit technique révélant que:
- Nexten Matcher = +13% précision avec questionnaires complets
- SmartMatch = optimal pour géolocalisation complexe
- Enhanced = idéal pour profils seniors
- Semantic = spécialisé analyse NLP
- Hybrid = consensus pour validation critique
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

# ================================
# MODÈLES DE CONTEXTE AVANCÉS
# ================================

@dataclass
class AlgorithmCapabilities:
    """Capacités et forces de chaque algorithme"""
    precision_baseline: float
    precision_with_questionnaires: float
    best_for_geo: bool
    best_for_senior: bool
    best_for_semantic: bool
    best_for_validation: bool
    avg_response_time_ms: float
    min_data_quality: float
    supported_features: List[str]

@dataclass
class SelectionContext:
    """Contexte étendu pour la sélection d'algorithme"""
    # Données disponibles
    has_candidate_questionnaire: bool
    has_company_questionnaires: bool
    questionnaire_completeness: float  # 0.0 à 1.0
    
    # Profil candidat
    skills_count: int
    experience_years: int
    seniority_level: str  # junior, mid, senior, expert
    
    # Contraintes géographiques
    mobility_type: str
    has_geo_constraints: bool
    geo_complexity_score: float  # 0.0 à 1.0
    
    # Analyse des offres
    offers_count: int
    offers_diversity_score: float  # 0.0 à 1.0
    semantic_analysis_needed: bool
    
    # Méta-données
    data_quality_score: float
    urgency_level: str  # low, medium, high, critical
    validation_required: bool

# ================================
# SÉLECTEUR INTELLIGENT PRINCIPAL
# ================================

class SmartAlgorithmSelector:
    """
    Sélecteur intelligent qui applique les règles d'audit pour choisir
    l'algorithme optimal selon le contexte et maximiser la précision
    """
    
    def __init__(self):
        # Métriques de sélection pour optimisation continue
        self.selection_metrics = defaultdict(int)
        self.performance_history = defaultdict(list)
        self.success_patterns = defaultdict(list)
        
        # Configuration basée sur l'audit technique
        self.config = {
            # Seuils pour Nexten Matcher (algorithme principal)
            'nexten_min_skills': 5,
            'nexten_min_questionnaire_completeness': 0.7,
            'nexten_precision_boost': 0.13,  # +13% selon audit
            
            # Seuils pour autres algorithmes
            'senior_experience_threshold': 7,
            'geo_complexity_threshold': 0.6,
            'semantic_text_threshold': 100,  # caractères minimum
            
            # Poids pour la sélection
            'precision_weight': 0.4,
            'speed_weight': 0.3,
            'data_compatibility_weight': 0.3,
            
            # Limites de performance
            'max_response_time_ms': 100,
            'min_confidence_threshold': 0.6
        }
        
        # Définition des capacités de chaque algorithme (basé sur audit)
        self.algorithm_capabilities = {
            'nexten': AlgorithmCapabilities(
                precision_baseline=0.87,
                precision_with_questionnaires=0.98,  # +13% boost
                best_for_geo=False,
                best_for_senior=True,
                best_for_semantic=True,
                best_for_validation=False,
                avg_response_time_ms=95,
                min_data_quality=0.6,
                supported_features=['questionnaires', 'ml_analysis', 'bidirectional']
            ),
            'smart': AlgorithmCapabilities(
                precision_baseline=0.74,
                precision_with_questionnaires=0.79,
                best_for_geo=True,
                best_for_senior=False,
                best_for_semantic=False,
                best_for_validation=False,
                avg_response_time_ms=75,
                min_data_quality=0.4,
                supported_features=['geolocation', 'mobility', 'transport']
            ),
            'enhanced': AlgorithmCapabilities(
                precision_baseline=0.78,
                precision_with_questionnaires=0.83,
                best_for_geo=False,
                best_for_senior=True,
                best_for_semantic=False,
                best_for_validation=False,
                avg_response_time_ms=70,
                min_data_quality=0.5,
                supported_features=['adaptive_weights', 'experience_boost']
            ),
            'semantic': AlgorithmCapabilities(
                precision_baseline=0.71,
                precision_with_questionnaires=0.76,
                best_for_geo=False,
                best_for_senior=False,
                best_for_semantic=True,
                best_for_validation=False,
                avg_response_time_ms=85,
                min_data_quality=0.3,
                supported_features=['nlp', 'text_analysis', 'semantic_similarity']
            ),
            'hybrid': AlgorithmCapabilities(
                precision_baseline=0.76,
                precision_with_questionnaires=0.81,
                best_for_geo=False,
                best_for_senior=False,
                best_for_semantic=False,
                best_for_validation=True,
                avg_response_time_ms=120,
                min_data_quality=0.7,
                supported_features=['consensus', 'validation', 'multi_algorithm']
            )
        }
        
        logger.info("🧠 SmartAlgorithmSelector initialisé avec configuration d'audit")
    
    def select_algorithm(self, candidate_data: Dict[str, Any], 
                        offers_data: List[Dict[str, Any]],
                        candidate_questionnaire: Optional[Dict[str, Any]] = None,
                        company_questionnaires: Optional[List[Dict[str, Any]]] = None,
                        options: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélection intelligente d'algorithme basée sur l'analyse contextuelle
        
        Returns:
            Tuple[algorithm_name, selection_details]
        """
        start_time = time.time()
        
        # 1. Analyse du contexte étendu
        context = self._analyze_extended_context(
            candidate_data, offers_data, candidate_questionnaire, 
            company_questionnaires, options or {}
        )
        
        # 2. Application des règles de sélection (audit technique)
        algorithm, confidence, reasoning = self._apply_selection_rules(context)
        
        # 3. Validation et ajustement si nécessaire
        final_algorithm, adjustments = self._validate_and_adjust_selection(
            algorithm, context, confidence
        )
        
        # 4. Enregistrement pour apprentissage
        selection_details = {
            'algorithm': final_algorithm,
            'confidence': confidence,
            'reasoning': reasoning,
            'context_analysis': context.__dict__,
            'adjustments': adjustments,
            'selection_time_ms': (time.time() - start_time) * 1000,
            'expected_precision': self._calculate_expected_precision(final_algorithm, context)
        }
        
        self._record_selection(final_algorithm, context, selection_details)
        
        logger.info(f"🎯 Algorithme sélectionné: {final_algorithm} "
                   f"(confiance: {confidence:.2f}, temps: {selection_details['selection_time_ms']:.1f}ms)")
        
        return final_algorithm, selection_details
    
    def _analyze_extended_context(self, candidate_data: Dict[str, Any],
                                offers_data: List[Dict[str, Any]],
                                candidate_questionnaire: Optional[Dict[str, Any]],
                                company_questionnaires: Optional[List[Dict[str, Any]]],
                                options: Dict[str, Any]) -> SelectionContext:
        """Analyse contextuelle approfondie pour optimiser la sélection"""
        
        # Analyse questionnaires
        has_candidate_q = bool(candidate_questionnaire)
        has_company_q = bool(company_questionnaires and any(q for q in company_questionnaires))
        q_completeness = self._calculate_questionnaire_completeness(
            candidate_questionnaire, company_questionnaires
        )
        
        # Analyse profil candidat
        skills = candidate_data.get('skills', [])
        skills_count = len(skills) if isinstance(skills, list) else 0
        experience_years = candidate_data.get('experience_years', 0)
        seniority_level = self._determine_seniority_level(experience_years)
        
        # Analyse géographique
        mobility = candidate_data.get('mobility', 'standard')
        geo_constraints, geo_complexity = self._analyze_geo_complexity(
            candidate_data, offers_data
        )
        
        # Analyse des offres
        offers_count = len(offers_data)
        offers_diversity = self._calculate_offers_diversity(offers_data)
        semantic_needed = self._detect_semantic_analysis_need(candidate_data, offers_data)
        
        # Score de qualité global
        data_quality = self._calculate_comprehensive_data_quality(
            candidate_data, candidate_questionnaire, offers_data, company_questionnaires
        )
        
        # Urgence et validation
        urgency = options.get('urgency', 'medium')
        validation_required = options.get('require_validation', False)
        
        return SelectionContext(
            has_candidate_questionnaire=has_candidate_q,
            has_company_questionnaires=has_company_q,
            questionnaire_completeness=q_completeness,
            skills_count=skills_count,
            experience_years=experience_years,
            seniority_level=seniority_level,
            mobility_type=mobility,
            has_geo_constraints=geo_constraints,
            geo_complexity_score=geo_complexity,
            offers_count=offers_count,
            offers_diversity_score=offers_diversity,
            semantic_analysis_needed=semantic_needed,
            data_quality_score=data_quality,
            urgency_level=urgency,
            validation_required=validation_required
        )
    
    def _apply_selection_rules(self, context: SelectionContext) -> Tuple[str, float, str]:
        """
        Application des règles de sélection basées sur l'audit technique
        
        Returns:
            Tuple[algorithm, confidence, reasoning]
        """
        
        # RÈGLE 1: Nexten Matcher prioritaire si données complètes
        # Précision +13% validée par audit technique
        if (context.has_candidate_questionnaire and 
            context.has_company_questionnaires and 
            context.questionnaire_completeness >= self.config['nexten_min_questionnaire_completeness'] and
            context.skills_count >= self.config['nexten_min_skills']):
            
            self.selection_metrics['nexten_complete_data'] += 1
            return 'nexten', 0.95, (
                f"Données complètes détectées: questionnaires candidat+entreprise "
                f"({context.questionnaire_completeness:.1%}), {context.skills_count} compétences. "
                f"Précision attendue +{self.config['nexten_precision_boost']:.0%}"
            )
        
        # RÈGLE 2: SmartMatch pour géolocalisation complexe
        if (context.geo_complexity_score >= self.config['geo_complexity_threshold'] or
            context.mobility_type in ['remote', 'hybrid', 'international']):
            
            self.selection_metrics['smart_geo_complex'] += 1
            return 'smart', 0.88, (
                f"Complexité géographique détectée: score {context.geo_complexity_score:.2f}, "
                f"mobilité {context.mobility_type}. SmartMatch optimisé pour géolocalisation."
            )
        
        # RÈGLE 3: Enhanced pour profils seniors avec données partielles
        if (context.seniority_level in ['senior', 'expert'] and 
            context.experience_years >= self.config['senior_experience_threshold'] and
            0.3 <= context.questionnaire_completeness < 0.7):
            
            self.selection_metrics['enhanced_senior'] += 1
            return 'enhanced', 0.85, (
                f"Profil senior détecté: {context.experience_years} ans d'expérience, "
                f"données partielles ({context.questionnaire_completeness:.1%}). "
                f"Enhanced optimisé pour pondération expérience."
            )
        
        # RÈGLE 4: Semantic pour analyse NLP intensive
        if context.semantic_analysis_needed:
            self.selection_metrics['semantic_nlp'] += 1
            return 'semantic', 0.82, (
                "Analyse sémantique requise: textes longs détectés dans profil/offres. "
                "Semantic spécialisé pour NLP et similarité textuelle."
            )
        
        # RÈGLE 5: Hybrid pour validation critique
        if (context.validation_required or 
            context.urgency_level == 'critical' or
            context.offers_count > 50):
            
            self.selection_metrics['hybrid_validation'] += 1
            return 'hybrid', 0.90, (
                f"Validation critique requise: urgence {context.urgency_level}, "
                f"{context.offers_count} offres. Hybrid pour consensus multi-algorithmes."
            )
        
        # RÈGLE 6: Défaut intelligent - Nexten comme meilleur algorithme général
        # Même sans questionnaires complets, Nexten reste supérieur
        if context.data_quality_score >= 0.5:
            self.selection_metrics['nexten_default'] += 1
            return 'nexten', 0.80, (
                f"Défaut intelligent: qualité données suffisante ({context.data_quality_score:.2f}). "
                f"Nexten comme algorithme principal même sans questionnaires complets."
            )
        
        # RÈGLE 7: Fallback pour données très limitées
        self.selection_metrics['enhanced_fallback'] += 1
        return 'enhanced', 0.65, (
            f"Données limitées (qualité: {context.data_quality_score:.2f}). "
            f"Enhanced comme fallback robuste."
        )
    
    def _validate_and_adjust_selection(self, algorithm: str, context: SelectionContext, 
                                     confidence: float) -> Tuple[str, List[str]]:
        """Validation et ajustement de la sélection si nécessaire"""
        adjustments = []
        
        # Vérification des capacités de l'algorithme
        capabilities = self.algorithm_capabilities[algorithm]
        
        # Ajustement si qualité des données insuffisante
        if context.data_quality_score < capabilities.min_data_quality:
            if context.data_quality_score >= 0.4:
                algorithm = 'smart'  # Plus tolérant aux données incomplètes
                adjustments.append(f"Ajustement qualité données: {algorithm} plus robuste")
            else:
                algorithm = 'enhanced'  # Très tolérant
                adjustments.append(f"Ajustement données très limitées: {algorithm} en fallback")
        
        # Ajustement si contrainte de temps stricte
        if (context.urgency_level == 'high' and 
            capabilities.avg_response_time_ms > self.config['max_response_time_ms']):
            algorithm = 'enhanced'  # Plus rapide
            adjustments.append("Ajustement urgence: algorithme plus rapide sélectionné")
        
        # Ajustement selon historique de performance
        if algorithm in self.performance_history:
            recent_performance = self.performance_history[algorithm][-10:]  # 10 derniers
            if recent_performance and sum(recent_performance) / len(recent_performance) < 0.7:
                algorithm = 'nexten' if algorithm != 'nexten' else 'enhanced'
                adjustments.append("Ajustement performance: historique dégradé détecté")
        
        return algorithm, adjustments
    
    def _calculate_questionnaire_completeness(self, candidate_q: Optional[Dict[str, Any]],
                                            company_q: Optional[List[Dict[str, Any]]]) -> float:
        """Calcul du score de complétude des questionnaires"""
        if not candidate_q and not company_q:
            return 0.0
        
        score = 0.0
        max_score = 2.0
        
        # Score candidat (0-1)
        if candidate_q:
            filled_fields = sum(1 for v in candidate_q.values() if v not in [None, '', []])
            total_fields = len(candidate_q)
            score += (filled_fields / total_fields) if total_fields > 0 else 0
        
        # Score entreprises (0-1)
        if company_q:
            total_completeness = 0
            for q in company_q:
                if q:
                    filled = sum(1 for v in q.values() if v not in [None, '', []])
                    total = len(q)
                    total_completeness += (filled / total) if total > 0 else 0
            score += (total_completeness / len(company_q)) if company_q else 0
        
        return min(score / max_score, 1.0)
    
    def _determine_seniority_level(self, experience_years: int) -> str:
        """Détermination du niveau de séniorité"""
        if experience_years < 2:
            return 'junior'
        elif experience_years < 5:
            return 'mid'
        elif experience_years < 10:
            return 'senior'
        else:
            return 'expert'
    
    def _analyze_geo_complexity(self, candidate: Dict[str, Any], 
                              offers: List[Dict[str, Any]]) -> Tuple[bool, float]:
        """Analyse de la complexité géographique"""
        candidate_location = candidate.get('location', {})
        
        if not candidate_location:
            return False, 0.0
        
        # Analyse des localisations d'offres
        offer_locations = []
        for offer in offers:
            loc = offer.get('location', {})
            if loc:
                offer_locations.append(loc)
        
        if not offer_locations:
            return False, 0.0
        
        # Calcul de la diversité géographique
        unique_cities = set(loc.get('city', '') for loc in offer_locations if loc.get('city'))
        unique_countries = set(loc.get('country', '') for loc in offer_locations if loc.get('country'))
        
        # Score de complexité basé sur la diversité
        complexity_score = 0.0
        
        # Diversité des villes
        if len(unique_cities) > 5:
            complexity_score += 0.4
        elif len(unique_cities) > 2:
            complexity_score += 0.2
        
        # Diversité des pays (international)
        if len(unique_countries) > 2:
            complexity_score += 0.4
        elif len(unique_countries) > 1:
            complexity_score += 0.2
        
        # Modes de travail à distance
        remote_offers = sum(1 for offer in offers 
                          if offer.get('remote_policy') in ['full_remote', 'hybrid'])
        if remote_offers > len(offers) * 0.3:  # >30% remote
            complexity_score += 0.2
        
        has_constraints = complexity_score > 0.3
        return has_constraints, min(complexity_score, 1.0)
    
    def _calculate_offers_diversity(self, offers: List[Dict[str, Any]]) -> float:
        """Calcul de la diversité des offres"""
        if not offers:
            return 0.0
        
        # Analyse des secteurs
        sectors = set()
        companies = set()
        titles = set()
        
        for offer in offers:
            if offer.get('sector'):
                sectors.add(offer['sector'])
            if offer.get('company'):
                companies.add(offer['company'])
            if offer.get('title'):
                titles.add(offer['title'])
        
        # Score de diversité
        diversity_score = 0.0
        diversity_score += min(len(sectors) / max(len(offers) * 0.3, 1), 1.0) * 0.4
        diversity_score += min(len(companies) / len(offers), 1.0) * 0.4
        diversity_score += min(len(titles) / max(len(offers) * 0.5, 1), 1.0) * 0.2
        
        return diversity_score
    
    def _detect_semantic_analysis_need(self, candidate: Dict[str, Any], 
                                     offers: List[Dict[str, Any]]) -> bool:
        """Détection du besoin d'analyse sémantique approfondie"""
        
        # Analyse de la longueur des textes
        candidate_text_length = 0
        candidate_desc = candidate.get('description', '')
        if isinstance(candidate_desc, str):
            candidate_text_length = len(candidate_desc)
        
        offers_text_length = 0
        for offer in offers:
            desc = offer.get('description', '')
            if isinstance(desc, str):
                offers_text_length += len(desc)
        
        # Seuil pour analyse sémantique
        text_threshold = self.config['semantic_text_threshold']
        
        return (candidate_text_length > text_threshold or 
                offers_text_length > text_threshold * len(offers))
    
    def _calculate_comprehensive_data_quality(self, candidate: Dict[str, Any],
                                            candidate_q: Optional[Dict[str, Any]],
                                            offers: List[Dict[str, Any]],
                                            company_q: Optional[List[Dict[str, Any]]]) -> float:
        """Calcul complet de la qualité des données"""
        score = 0.0
        max_score = 10.0
        
        # Score candidat (0-4 points)
        if candidate.get('skills'):
            score += 1.5
        if candidate.get('experience_years', 0) > 0:
            score += 1.0
        if candidate.get('location'):
            score += 0.5
        if candidate_q:
            score += 1.0
        
        # Score offres (0-3 points)
        if offers:
            score += 1.0
        
        offers_with_requirements = sum(1 for offer in offers if offer.get('requirements'))
        if offers_with_requirements > len(offers) * 0.7:
            score += 1.0
        
        if company_q and any(q for q in company_q):
            score += 1.0
        
        # Score richesse données (0-3 points)
        total_fields = 0
        filled_fields = 0
        
        for key, value in candidate.items():
            total_fields += 1
            if value not in [None, '', [], {}]:
                filled_fields += 1
        
        if total_fields > 0:
            richness_score = (filled_fields / total_fields) * 3
            score += richness_score
        
        return min(score / max_score, 1.0)
    
    def _calculate_expected_precision(self, algorithm: str, context: SelectionContext) -> float:
        """Calcul de la précision attendue pour l'algorithme sélectionné"""
        capabilities = self.algorithm_capabilities[algorithm]
        
        base_precision = capabilities.precision_baseline
        
        # Boost si questionnaires disponibles
        if (context.has_candidate_questionnaire and context.has_company_questionnaires):
            base_precision = capabilities.precision_with_questionnaires
        
        # Ajustements selon le contexte
        adjustments = 0.0
        
        # Boost pour spécialisation
        if algorithm == 'smart' and context.has_geo_constraints:
            adjustments += 0.05
        elif algorithm == 'enhanced' and context.seniority_level in ['senior', 'expert']:
            adjustments += 0.03
        elif algorithm == 'semantic' and context.semantic_analysis_needed:
            adjustments += 0.04
        
        # Pénalité pour données de faible qualité
        if context.data_quality_score < 0.5:
            adjustments -= 0.05
        
        return min(base_precision + adjustments, 1.0)
    
    def _record_selection(self, algorithm: str, context: SelectionContext, 
                         details: Dict[str, Any]):
        """Enregistrement de la sélection pour apprentissage continu"""
        self.selection_metrics[algorithm] += 1
        
        # Enregistrement du pattern de sélection
        pattern = {
            'algorithm': algorithm,
            'context_hash': self._hash_context(context),
            'data_quality': context.data_quality_score,
            'expected_precision': details['expected_precision'],
            'timestamp': time.time()
        }
        
        self.success_patterns[algorithm].append(pattern)
        
        # Nettoyage automatique (garder seulement les 1000 derniers)
        if len(self.success_patterns[algorithm]) > 1000:
            self.success_patterns[algorithm] = self.success_patterns[algorithm][-1000:]
    
    def _hash_context(self, context: SelectionContext) -> str:
        """Génération d'un hash du contexte pour analyse des patterns"""
        context_str = f"{context.has_candidate_questionnaire}_{context.has_company_questionnaires}_" \
                     f"{context.skills_count}_{context.experience_years}_{context.mobility_type}_" \
                     f"{context.has_geo_constraints}_{context.offers_count}"
        
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    # ================================
    # MÉTHODES D'OPTIMISATION ET REPORTING
    # ================================
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Statistiques de sélection pour monitoring"""
        total_selections = sum(self.selection_metrics.values())
        
        if total_selections == 0:
            return {'status': 'no_selections', 'total': 0}
        
        return {
            'total_selections': total_selections,
            'algorithm_distribution': {
                algo: {
                    'count': count,
                    'percentage': (count / total_selections) * 100
                }
                for algo, count in self.selection_metrics.items()
            },
            'patterns': {
                algo: len(patterns) for algo, patterns in self.success_patterns.items()
            },
            'top_algorithms': sorted(
                self.selection_metrics.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        }
    
    def optimize_thresholds(self, performance_feedback: Dict[str, float]):
        """Optimisation automatique des seuils basée sur le feedback"""
        logger.info("🔧 Optimisation des seuils de sélection...")
        
        # Ajustement basé sur la performance réelle
        for algorithm, performance in performance_feedback.items():
            if algorithm == 'nexten' and performance > 0.9:
                # Nexten performe bien, on peut baisser les seuils
                self.config['nexten_min_skills'] = max(3, self.config['nexten_min_skills'] - 1)
                self.config['nexten_min_questionnaire_completeness'] = max(
                    0.5, self.config['nexten_min_questionnaire_completeness'] - 0.1
                )
            elif performance < 0.7:
                # Performance dégradée, on resserre les critères
                if algorithm == 'nexten':
                    self.config['nexten_min_skills'] = min(7, self.config['nexten_min_skills'] + 1)
        
        logger.info(f"✅ Seuils optimisés: {self.config}")
    
    def get_algorithm_recommendation(self, context_description: str) -> Dict[str, Any]:
        """Recommandation d'algorithme basée sur une description textuelle"""
        # Analyse simple de mots-clés pour demo
        keywords = context_description.lower()
        
        recommendations = []
        
        if 'questionnaire' in keywords and 'complet' in keywords:
            recommendations.append(('nexten', 0.95, "Questionnaires complets détectés"))
        
        if any(word in keywords for word in ['géo', 'distance', 'remote', 'mobilité']):
            recommendations.append(('smart', 0.88, "Contraintes géographiques détectées"))
        
        if any(word in keywords for word in ['senior', 'expérience', 'expert']):
            recommendations.append(('enhanced', 0.85, "Profil senior détecté"))
        
        if any(word in keywords for word in ['texte', 'description', 'sémantique']):
            recommendations.append(('semantic', 0.82, "Analyse textuelle requise"))
        
        if any(word in keywords for word in ['validation', 'critique', 'important']):
            recommendations.append(('hybrid', 0.90, "Validation critique requise"))
        
        if not recommendations:
            recommendations.append(('nexten', 0.80, "Défaut intelligent"))
        
        # Tri par confiance
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'recommended_algorithm': recommendations[0][0],
            'confidence': recommendations[0][1],
            'reasoning': recommendations[0][2],
            'alternatives': recommendations[1:3] if len(recommendations) > 1 else []
        }

# ================================
# FACTORY ET UTILITAIRES
# ================================

def create_smart_selector(config_override: Optional[Dict[str, Any]] = None) -> SmartAlgorithmSelector:
    """Factory pour créer un sélecteur avec configuration personnalisée"""
    selector = SmartAlgorithmSelector()
    
    if config_override:
        selector.config.update(config_override)
        logger.info(f"🔧 Configuration personnalisée appliquée: {config_override}")
    
    return selector

# Instance globale pour réutilisation
_global_selector = None

def get_global_selector() -> SmartAlgorithmSelector:
    """Récupération de l'instance globale du sélecteur"""
    global _global_selector
    if _global_selector is None:
        _global_selector = SmartAlgorithmSelector()
    return _global_selector

# ================================
# EXEMPLE D'UTILISATION
# ================================

async def example_smart_selection():
    """Exemple d'utilisation du sélecteur intelligent"""
    
    selector = get_global_selector()
    
    # Cas 1: Données complètes (devrait sélectionner Nexten)
    candidate_complete = {
        'skills': ['Python', 'Machine Learning', 'AWS', 'Docker', 'Kubernetes'],
        'experience_years': 8,
        'location': {'city': 'Paris', 'country': 'France'}
    }
    
    questionnaire = {
        'work_style': 'collaborative',
        'career_goals': 'leadership',
        'technology_preferences': ['cloud', 'ai'],
        'work_environment': 'hybrid'
    }
    
    offers = [
        {
            'id': 'offer_001',
            'title': 'Senior ML Engineer',
            'location': {'city': 'Paris', 'country': 'France'},
            'requirements': ['Python', 'ML']
        }
    ]
    
    company_questionnaires = [{'culture': 'innovative', 'environment': 'collaborative'}]
    
    algorithm, details = selector.select_algorithm(
        candidate_complete, offers, questionnaire, company_questionnaires
    )
    
    print(f"✅ Cas données complètes:")
    print(f"   Algorithme: {algorithm}")
    print(f"   Confiance: {details['confidence']:.2f}")
    print(f"   Raison: {details['reasoning']}")
    print(f"   Précision attendue: {details['expected_precision']:.2f}")
    
    # Cas 2: Contraintes géographiques (devrait sélectionner Smart)
    candidate_geo = {
        'skills': ['JavaScript', 'React'],
        'experience_years': 3,
        'location': {'city': 'Lyon', 'country': 'France'},
        'mobility': 'remote'
    }
    
    offers_geo = [
        {'id': 'offer_1', 'location': {'city': 'Paris', 'country': 'France'}},
        {'id': 'offer_2', 'location': {'city': 'London', 'country': 'UK'}},
        {'id': 'offer_3', 'location': {'city': 'Berlin', 'country': 'Germany'}},
        {'id': 'offer_4', 'location': {'city': 'Barcelona', 'country': 'Spain'}}
    ]
    
    algorithm_geo, details_geo = selector.select_algorithm(candidate_geo, offers_geo)
    
    print(f"\n✅ Cas contraintes géographiques:")
    print(f"   Algorithme: {algorithm_geo}")
    print(f"   Confiance: {details_geo['confidence']:.2f}")
    print(f"   Raison: {details_geo['reasoning']}")
    
    # Statistiques
    print(f"\n📊 Statistiques de sélection:")
    stats = selector.get_selection_stats()
    for algo, data in stats['algorithm_distribution'].items():
        print(f"   {algo}: {data['count']} sélections ({data['percentage']:.1f}%)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_smart_selection())
