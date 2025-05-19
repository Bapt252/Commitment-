"""
Détecteur de biais pour le système de matching ML.

Ce module identifie et quantifie les biais potentiels dans les recommandations
(genre, âge, origine, etc.) et propose des mesures correctives.
"""

import logging
import numpy as np
import statistics
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum

from ..core.models import CV, JobOffer, MatchResult

logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Types de biais détectables."""
    GENDER = "gender"
    AGE = "age"
    ETHNICITY = "ethnicity"
    EDUCATION = "education"
    LOCATION = "location"
    EXPERIENCE = "experience"
    INDUSTRY = "industry"
    SALARY = "salary"


class BiasStatus(Enum):
    """Statut d'un biais détecté."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BiasInstance:
    """Instance de biais détectée."""
    bias_type: BiasType
    affected_group: str
    reference_group: str
    metric: str
    affected_value: float
    reference_value: float
    bias_score: float  # 0-1, 0 = pas de biais, 1 = biais maximum
    statistical_significance: float  # p-value si applicable
    sample_size_affected: int
    sample_size_reference: int
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BiasReport:
    """Rapport complet de détection de biais."""
    analysis_period: Tuple[datetime, datetime]
    total_matches_analyzed: int
    bias_instances: List[BiasInstance]
    overall_bias_score: float
    recommendations: List[str]
    statistical_summary: Dict[str, Any]
    protected_groups_analysis: Dict[str, Dict[str, float]]


@dataclass
class FairnessMetric:
    """Métrique de fairness/équité."""
    name: str
    value: float
    threshold: float
    status: BiasStatus
    description: str


class BiasDetector:
    """
    Détecteur de biais pour le système de matching.
    
    Fonctionnalités:
    - Détection automatique de biais dans différentes dimensions
    - Calcul de métriques de fairness (demographic parity, equal opportunity, etc.)
    - Analyse intersectionnelle des biais
    - Recommandations de mitigation
    - Monitoring continu avec alertes
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 protected_attributes: Optional[Dict[str, List[str]]] = None):
        """
        Initialise le détecteur de biais.
        
        Args:
            config: Configuration du détecteur
            protected_attributes: Attributs protégés par groupe
        """
        self.config = config or self._get_default_config()
        self.protected_attributes = protected_attributes or self._get_default_protected_attributes()
        
        # Cache des analyses
        self.bias_history = []
        self.fairness_baselines = {}
        
        # Patterns de biais connus
        self.bias_patterns = self._load_bias_patterns()
        
        logger.info("BiasDetector initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'enabled': True,
            'min_sample_size': 50,  # Taille minimum pour analyse statistique
            'significance_level': 0.05,  # Seuil de significativité
            'bias_threshold_moderate': 0.1,  # 10% de différence
            'bias_threshold_high': 0.2,  # 20% de différence
            'bias_threshold_critical': 0.3,  # 30% de différence
            
            # Métriques de fairness à calculer
            'fairness_metrics': [
                'demographic_parity',
                'equal_opportunity',
                'equalized_odds',
                'calibration'
            ],
            
            # Types de biais à détecter
            'bias_types_enabled': [
                BiasType.GENDER,
                BiasType.AGE,
                BiasType.ETHNICITY,
                BiasType.EDUCATION,
                BiasType.LOCATION
            ],
            
            # Intersections à analyser (combinaisons de attributs)
            'intersectional_analysis': True,
            'max_intersection_depth': 2,
            
            # Alertes
            'alert_on_bias': True,
            'alert_threshold': BiasStatus.MODERATE
        }
    
    def _get_default_protected_attributes(self) -> Dict[str, List[str]]:
        """Attributs protégés par défaut."""
        return {
            'gender': ['male', 'female', 'non_binary', 'other', 'prefer_not_to_say'],
            'age_group': ['18-25', '26-35', '36-45', '46-55', '56-65', '65+'],
            'ethnicity': ['white', 'black', 'hispanic', 'asian', 'mixed', 'other'],
            'education_level': ['high_school', 'bachelor', 'master', 'phd', 'other'],
            'location_type': ['urban', 'suburban', 'rural'],
            'experience_level': ['entry', 'junior', 'mid', 'senior', 'executive']
        }
    
    def _load_bias_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Charge les patterns de biais connus."""
        return {
            'gender_tech_bias': {
                'description': 'Sous-représentation des femmes en tech',
                'affected_groups': ['female'],
                'reference_groups': ['male'],
                'industries': ['technology', 'engineering', 'software'],
                'expected_bias_score': 0.3
            },
            'age_discrimination': {
                'description': 'Discrimination par l\'âge',
                'affected_groups': ['55+', '65+'],
                'reference_groups': ['26-35', '36-45'],
                'severity_threshold': 0.25
            },
            'education_privilege': {
                'description': 'Privilège éducationnel',
                'affected_groups': ['high_school'],
                'reference_groups': ['bachelor', 'master', 'phd'],
                'severity_threshold': 0.2
            }
        }
    
    def analyze_bias(self, 
                    matches: List[MatchResult],
                    candidates: List[CV],
                    jobs: List[JobOffer],
                    period_days: Optional[int] = None) -> BiasReport:
        """
        Analyse complète des biais dans un ensemble de matches.
        
        Args:
            matches: Résultats de matching
            candidates: Candidats évalués
            jobs: Offres d'emploi
            period_days: Période d'analyse en jours
            
        Returns:
            Rapport complet des biais détectés
        """
        try:
            start_time = datetime.now()
            if period_days:
                end_time = start_time
                start_time = end_time - timedelta(days=period_days)
            else:
                end_time = start_time
                start_time = start_time - timedelta(days=30)  # Défaut 30 jours
            
            # Enrichir les données avec métadonnées démographiques
            enriched_data = self._enrich_data_with_demographics(matches, candidates, jobs)
            
            # Analyser chaque type de biais
            bias_instances = []
            
            for bias_type in self.config['bias_types_enabled']:
                instances = self._analyze_bias_type(enriched_data, bias_type)
                bias_instances.extend(instances)
            
            # Analyse intersectionnelle
            if self.config['intersectional_analysis']:
                intersectional_bias = self._analyze_intersectional_bias(enriched_data)
                bias_instances.extend(intersectional_bias)
            
            # Calculer score global de biais
            overall_bias_score = self._calculate_overall_bias_score(bias_instances)
            
            # Générer recommandations
            recommendations = self._generate_recommendations(bias_instances)
            
            # Résumé statistique
            statistical_summary = self._generate_statistical_summary(enriched_data, bias_instances)
            
            # Analyse par groupe protégé
            protected_groups_analysis = self._analyze_protected_groups(enriched_data)
            
            # Créer le rapport
            report = BiasReport(
                analysis_period=(start_time, end_time),
                total_matches_analyzed=len(matches),
                bias_instances=bias_instances,
                overall_bias_score=overall_bias_score,
                recommendations=recommendations,
                statistical_summary=statistical_summary,
                protected_groups_analysis=protected_groups_analysis
            )
            
            # Sauvegarder dans l'historique
            self.bias_history.append(report)
            
            # Alertes si nécessaire
            if self.config['alert_on_bias']:
                self._check_bias_alerts(report)
            
            logger.info(f"Bias analysis completed: {len(bias_instances)} instances detected")
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing bias: {e}")
            return BiasReport(
                analysis_period=(start_time, end_time),
                total_matches_analyzed=0,
                bias_instances=[],
                overall_bias_score=0.0,
                recommendations=[],
                statistical_summary={},
                protected_groups_analysis={}
            )
    
    def calculate_fairness_metrics(self, 
                                 predictions: List[Dict[str, Any]],
                                 ground_truth: List[bool],
                                 protected_attribute: str) -> Dict[str, FairnessMetric]:
        """
        Calcule les métriques de fairness pour un attribut protégé.
        
        Args:
            predictions: Prédictions avec métadonnées
            ground_truth: Vérité terrain
            protected_attribute: Nom de l'attribut protégé
            
        Returns:
            Dictionnaire des métriques de fairness
        """
        try:
            metrics = {}
            
            # Grouper par valeur de l'attribut protégé
            groups = defaultdict(list)
            for i, pred in enumerate(predictions):
                attr_value = pred.get(protected_attribute)
                if attr_value:
                    groups[attr_value].append({
                        'prediction': pred.get('predicted_score', 0),
                        'truth': ground_truth[i] if i < len(ground_truth) else False,
                        'binary_pred': pred.get('predicted_score', 0) > 0.5
                    })
            
            if len(groups) < 2:
                return metrics
            
            # Demographic Parity (Statistical Parity)
            if 'demographic_parity' in self.config['fairness_metrics']:
                dp_metric = self._calculate_demographic_parity(groups)
                metrics['demographic_parity'] = dp_metric
            
            # Equal Opportunity
            if 'equal_opportunity' in self.config['fairness_metrics']:
                eo_metric = self._calculate_equal_opportunity(groups)
                metrics['equal_opportunity'] = eo_metric
            
            # Equalized Odds
            if 'equalized_odds' in self.config['fairness_metrics']:
                eqo_metric = self._calculate_equalized_odds(groups)
                metrics['equalized_odds'] = eqo_metric
            
            # Calibration
            if 'calibration' in self.config['fairness_metrics']:
                cal_metric = self._calculate_calibration(groups)
                metrics['calibration'] = cal_metric
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating fairness metrics: {e}")
            return {}
    
    def monitor_bias_trends(self, 
                          window_days: int = 7) -> Dict[str, Any]:
        """
        Surveille les tendances de biais sur une fenêtre temporelle.
        
        Args:
            window_days: Fenêtre en jours
            
        Returns:
            Analyse des tendances
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=window_days)
            recent_reports = [
                report for report in self.bias_history
                if report.analysis_period[1] >= cutoff_date
            ]
            
            if not recent_reports:
                return {'status': 'no_data', 'reports_analyzed': 0}
            
            # Analyser les tendances par type de biais
            trends = {}
            
            for bias_type in BiasType:
                type_scores = []
                for report in recent_reports:
                    type_instances = [
                        bi for bi in report.bias_instances 
                        if bi.bias_type == bias_type
                    ]
                    if type_instances:
                        avg_score = statistics.mean([bi.bias_score for bi in type_instances])
                        type_scores.append(avg_score)
                
                if type_scores:
                    if len(type_scores) > 1:
                        # Calculer la tendance (corrélation avec le temps)
                        x = list(range(len(type_scores)))
                        correlation = np.corrcoef(x, type_scores)[0, 1] if len(type_scores) > 2 else 0
                        
                        if correlation > 0.3:
                            trend = 'increasing'
                        elif correlation < -0.3:
                            trend = 'decreasing'
                        else:
                            trend = 'stable'
                    else:
                        trend = 'insufficient_data'
                    
                    trends[bias_type.value] = {
                        'trend': trend,
                        'current_score': type_scores[-1],
                        'average_score': statistics.mean(type_scores),
                        'data_points': len(type_scores)
                    }
            
            # Score global de tendance
            overall_scores = [report.overall_bias_score for report in recent_reports]
            overall_trend = 'stable'
            if len(overall_scores) > 2:
                correlation = np.corrcoef(range(len(overall_scores)), overall_scores)[0, 1]
                if correlation > 0.3:
                    overall_trend = 'worsening'
                elif correlation < -0.3:
                    overall_trend = 'improving'
            
            return {
                'status': 'analyzed',
                'window_days': window_days,
                'reports_analyzed': len(recent_reports),
                'overall_trend': overall_trend,
                'current_bias_score': overall_scores[-1],
                'bias_type_trends': trends,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring bias trends: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def suggest_bias_mitigation(self, 
                              bias_instances: List[BiasInstance]) -> List[Dict[str, Any]]:
        """
        Suggère des stratégies de mitigation pour les biais détectés.
        
        Args:
            bias_instances: Instances de biais à traiter
            
        Returns:
            Liste de suggestions de mitigation
        """
        try:
            suggestions = []
            
            # Grouper par type de biais
            bias_by_type = defaultdict(list)
            for instance in bias_instances:
                bias_by_type[instance.bias_type].append(instance)
            
            for bias_type, instances in bias_by_type.items():
                max_score = max(instance.bias_score for instance in instances)
                
                if bias_type == BiasType.GENDER:
                    suggestions.append({
                        'bias_type': bias_type.value,
                        'severity': 'high' if max_score > 0.2 else 'moderate',
                        'strategy': 'adjust_gender_weights',
                        'description': 'Ajuster les poids pour réduire le biais de genre',
                        'specific_actions': [
                            'Réentraîner le modèle avec des données équilibrées',
                            'Implémenter un post-processing pour équilibrer les résultats',
                            'Ajouter des features de fairness dans le modèle'
                        ],
                        'expected_impact': 'Réduction de 30-50% du biais de genre',
                        'implementation_complexity': 'medium'
                    })
                
                elif bias_type == BiasType.AGE:
                    suggestions.append({
                        'bias_type': bias_type.value,
                        'severity': 'high' if max_score > 0.25 else 'moderate',
                        'strategy': 'age_aware_matching',
                        'description': 'Implémenter un matching conscient de l\'âge',
                        'specific_actions': [
                            'Analyser la corrélation âge-performance',
                            'Ajuster les seuils par groupe d\'âge',
                            'Diversifier les données d\'entraînement'
                        ],
                        'expected_impact': 'Réduction de 20-40% du biais d\'âge',
                        'implementation_complexity': 'medium'
                    })
                
                elif bias_type == BiasType.EDUCATION:
                    suggestions.append({
                        'bias_type': bias_type.value,
                        'severity': 'moderate' if max_score > 0.15 else 'low',
                        'strategy': 'skill_based_matching',
                        'description': 'Privilégier les compétences vs diplômes',
                        'specific_actions': [
                            'Augmenter le poids des compétences pratiques',
                            'Réduire le poids des diplômes',
                            'Implémenter des évaluations de compétences'
                        ],
                        'expected_impact': 'Réduction de 15-30% du biais éducationnel',
                        'implementation_complexity': 'low'
                    })
                
                elif bias_type == BiasType.LOCATION:
                    suggestions.append({
                        'bias_type': bias_type.value,
                        'severity': 'moderate',
                        'strategy': 'location_normalization',
                        'description': 'Normaliser l\'impact de la localisation',
                        'specific_actions': [
                            'Implémenter un matching remote-first',
                            'Ajuster pour les différences de marché local',
                            'Considérer la mobilité des candidats'
                        ],
                        'expected_impact': 'Réduction de 25-35% du biais géographique',
                        'implementation_complexity': 'medium'
                    })
            
            # Suggestions générales
            if max(instance.bias_score for instance in bias_instances) > 0.3:
                suggestions.append({
                    'bias_type': 'general',
                    'severity': 'critical',
                    'strategy': 'comprehensive_audit',
                    'description': 'Audit complet du système de matching',
                    'specific_actions': [
                        'Audit externe des algorithmes',
                        'Révision complète des données d\'entraînement',
                        'Implémentation de contraintes de fairness',
                        'Formation de l\'équipe sur les biais algorithmiques'
                    ],
                    'expected_impact': 'Réduction globale de 40-60% des biais',
                    'implementation_complexity': 'high'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating bias mitigation suggestions: {e}")
            return []
    
    def evaluate_mitigation_effectiveness(self, 
                                        before_report: BiasReport,
                                        after_report: BiasReport) -> Dict[str, Any]:
        """
        Évalue l'efficacité des actions de mitigation.
        
        Args:
            before_report: Rapport avant mitigation
            after_report: Rapport après mitigation
            
        Returns:
            Évaluation de l'efficacité
        """
        try:
            # Comparer les scores globaux
            overall_improvement = (
                before_report.overall_bias_score - after_report.overall_bias_score
            ) / before_report.overall_bias_score if before_report.overall_bias_score > 0 else 0
            
            # Comparer par type de biais
            type_improvements = {}
            before_by_type = defaultdict(list)
            after_by_type = defaultdict(list)
            
            for instance in before_report.bias_instances:
                before_by_type[instance.bias_type].append(instance.bias_score)
            
            for instance in after_report.bias_instances:
                after_by_type[instance.bias_type].append(instance.bias_score)
            
            for bias_type in BiasType:
                if bias_type in before_by_type and bias_type in after_by_type:
                    before_avg = statistics.mean(before_by_type[bias_type])
                    after_avg = statistics.mean(after_by_type[bias_type])
                    improvement = (before_avg - after_avg) / before_avg if before_avg > 0 else 0
                    type_improvements[bias_type.value] = improvement
                elif bias_type in before_by_type:
                    # Biais éliminé
                    type_improvements[bias_type.value] = 1.0
            
            # Résumé de l'efficacité
            effectiveness_summary = {
                'overall_improvement_percent': overall_improvement * 100,
                'type_improvements': type_improvements,
                'bias_instances_before': len(before_report.bias_instances),
                'bias_instances_after': len(after_report.bias_instances),
                'instances_eliminated': max(0, len(before_report.bias_instances) - len(after_report.bias_instances)),
                'analysis_timestamp': datetime.now()
            }
            
            # Évaluation qualitative
            if overall_improvement > 0.5:
                effectiveness_summary['effectiveness_rating'] = 'excellent'
            elif overall_improvement > 0.3:
                effectiveness_summary['effectiveness_rating'] = 'good'
            elif overall_improvement > 0.1:
                effectiveness_summary['effectiveness_rating'] = 'moderate'
            elif overall_improvement > 0:
                effectiveness_summary['effectiveness_rating'] = 'slight'
            else:
                effectiveness_summary['effectiveness_rating'] = 'none_or_negative'
            
            return effectiveness_summary
            
        except Exception as e:
            logger.error(f"Error evaluating mitigation effectiveness: {e}")
            return {'error': str(e)}
    
    # Méthodes privées d'analyse
    
    def _enrich_data_with_demographics(self, 
                                     matches: List[MatchResult],
                                     candidates: List[CV],
                                     jobs: List[JobOffer]) -> List[Dict[str, Any]]:
        """Enrichit les données avec informations démographiques."""
        enriched_data = []
        
        # Créer des mappes pour accès rapide
        candidate_map = {cv.id: cv for cv in candidates}
        job_map = {job.id: job for job in jobs}
        
        for match in matches:
            candidate = candidate_map.get(match.candidate_id)
            job = job_map.get(match.job_id)
            
            if candidate and job:
                # Extraire/inférer démographiques du candidat
                demographics = self._extract_demographics(candidate)
                
                # Extraire caractéristiques du job
                job_features = self._extract_job_features(job)
                
                enriched_item = {
                    'match_score': match.score,
                    'candidate_id': candidate.id,
                    'job_id': job.id,
                    'demographics': demographics,
                    'job_features': job_features,
                    'match': match
                }
                
                enriched_data.append(enriched_item)
        
        return enriched_data
    
    def _extract_demographics(self, candidate: CV) -> Dict[str, Any]:
        """Extrait les informations démographiques d'un CV."""
        demographics = {}
        
        # Extraction/inférence basée sur les données disponibles
        # Note: En production, ceci devrait respecter les lois sur la protection des données
        
        # Âge (si disponible)
        if hasattr(candidate, 'age') and candidate.age:
            demographics['age'] = candidate.age
            demographics['age_group'] = self._categorize_age(candidate.age)
        
        # Genre (si disponible - attention aux lois)
        if hasattr(candidate, 'gender') and candidate.gender:
            demographics['gender'] = candidate.gender
        
        # Éducation
        education_level = 'other'
        if hasattr(candidate, 'education') and candidate.education:
            education_level = self._categorize_education(candidate.education)
        demographics['education_level'] = education_level
        
        # Expérience
        exp_level = 'entry'
        if hasattr(candidate, 'experience_years') and candidate.experience_years:
            exp_level = self._categorize_experience(candidate.experience_years)
        demographics['experience_level'] = exp_level
        
        # Localisation
        if hasattr(candidate, 'location') and candidate.location:
            demographics['location'] = candidate.location
            demographics['location_type'] = self._categorize_location(candidate.location)
        
        return demographics
    
    def _extract_job_features(self, job: JobOffer) -> Dict[str, Any]:
        """Extrait les caractéristiques d'une offre d'emploi."""
        features = {}
        
        # Secteur/Industrie
        if hasattr(job, 'industry') and job.industry:
            features['industry'] = job.industry
        
        # Niveau de poste
        if hasattr(job, 'seniority_level') and job.seniority_level:
            features['seniority_level'] = job.seniority_level
        
        # Type de contrat
        if hasattr(job, 'contract_type') and job.contract_type:
            features['contract_type'] = job.contract_type
        
        # Fourchette salariale
        if hasattr(job, 'salary_range') and job.salary_range:
            features['salary_range'] = job.salary_range
            features['salary_category'] = self._categorize_salary(job.salary_range)
        
        # Localisation
        if hasattr(job, 'location') and job.location:
            features['location'] = job.location
            features['location_type'] = self._categorize_location(job.location)
        
        return features
    
    def _analyze_bias_type(self, 
                          enriched_data: List[Dict[str, Any]], 
                          bias_type: BiasType) -> List[BiasInstance]:
        """Analyse un type spécifique de biais."""
        bias_instances = []
        
        try:
            # Mapper le type de biais vers l'attribut démographique
            attr_mapping = {
                BiasType.GENDER: 'gender',
                BiasType.AGE: 'age_group',
                BiasType.ETHNICITY: 'ethnicity',
                BiasType.EDUCATION: 'education_level',
                BiasType.LOCATION: 'location_type',
                BiasType.EXPERIENCE: 'experience_level'
            }
            
            demographic_attr = attr_mapping.get(bias_type)
            if not demographic_attr:
                return bias_instances
            
            # Grouper par valeur de l'attribut
            groups = defaultdict(list)
            for item in enriched_data:
                attr_value = item['demographics'].get(demographic_attr)
                if attr_value:
                    groups[attr_value].append(item)
            
            # Analyser les différences entre groupes
            group_names = list(groups.keys())
            
            for i, group1 in enumerate(group_names):
                for group2 in group_names[i+1:]:
                    if len(groups[group1]) < self.config['min_sample_size'] or \
                       len(groups[group2]) < self.config['min_sample_size']:
                        continue
                    
                    # Calculer les métriques pour chaque groupe
                    group1_scores = [item['match_score'] for item in groups[group1]]
                    group2_scores = [item['match_score'] for item in groups[group2]]
                    
                    group1_avg = statistics.mean(group1_scores)
                    group2_avg = statistics.mean(group2_scores)
                    
                    # Calculer le biais
                    bias_score = abs(group1_avg - group2_avg)
                    relative_bias = bias_score / max(group1_avg, group2_avg) if max(group1_avg, group2_avg) > 0 else 0
                    
                    # Test statistique (t-test)
                    try:
                        from scipy import stats
                        t_stat, p_value = stats.ttest_ind(group1_scores, group2_scores)
                    except ImportError:
                        # Fallback sans scipy
                        p_value = 0.05  # Valeur par défaut
                    
                    # Déterminer quel groupe est affecté (moyenne plus faible)
                    if group1_avg < group2_avg:
                        affected_group = group1
                        reference_group = group2
                        affected_value = group1_avg
                        reference_value = group2_avg
                    else:
                        affected_group = group2
                        reference_group = group1
                        affected_value = group2_avg
                        reference_value = group1_avg
                    
                    # Créer l'instance de biais si significative
                    if (p_value < self.config['significance_level'] and 
                        relative_bias > self.config['bias_threshold_moderate']):
                        
                        bias_instance = BiasInstance(
                            bias_type=bias_type,
                            affected_group=affected_group,
                            reference_group=reference_group,
                            metric='average_match_score',
                            affected_value=affected_value,
                            reference_value=reference_value,
                            bias_score=relative_bias,
                            statistical_significance=p_value,
                            sample_size_affected=len(groups[affected_group]),
                            sample_size_reference=len(groups[reference_group]),
                            timestamp=datetime.now(),
                            details={
                                'group1_size': len(groups[group1]),
                                'group2_size': len(groups[group2]),
                                'group1_std': statistics.stdev(group1_scores) if len(group1_scores) > 1 else 0,
                                'group2_std': statistics.stdev(group2_scores) if len(group2_scores) > 1 else 0
                            }
                        )
                        
                        bias_instances.append(bias_instance)
            
        except Exception as e:
            logger.error(f"Error analyzing bias type {bias_type}: {e}")
        
        return bias_instances
    
    def _analyze_intersectional_bias(self, 
                                   enriched_data: List[Dict[str, Any]]) -> List[BiasInstance]:
        """Analyse les biais intersectionnels."""
        bias_instances = []
        
        try:
            # Combinations d'attributs à analyser
            key_attributes = ['gender', 'age_group', 'education_level']
            
            from itertools import combinations
            
            # Analyser les intersections 2 à 2
            for attr_combo in combinations(key_attributes, 2):
                # Créer les groupes intersectionnels
                intersection_groups = defaultdict(list)
                
                for item in enriched_data:
                    values = []
                    for attr in attr_combo:
                        value = item['demographics'].get(attr)
                        if value:
                            values.append(f"{attr}:{value}")
                    
                    if len(values) == len(attr_combo):
                        intersection_key = " & ".join(values)
                        intersection_groups[intersection_key].append(item)
                
                # Analyser les différences
                for group_name, group_items in intersection_groups.items():
                    if len(group_items) < self.config['min_sample_size']:
                        continue
                    
                    # Comparer avec la moyenne générale
                    group_scores = [item['match_score'] for item in group_items]
                    all_scores = [item['match_score'] for item in enriched_data]
                    
                    group_avg = statistics.mean(group_scores)
                    overall_avg = statistics.mean(all_scores)
                    
                    # Calculer le biais intersectionnel
                    bias_score = abs(group_avg - overall_avg) / overall_avg if overall_avg > 0 else 0
                    
                    if bias_score > self.config['bias_threshold_moderate']:
                        bias_instance = BiasInstance(
                            bias_type=BiasType.GENDER,  # Type générique pour intersectionnel
                            affected_group=group_name,
                            reference_group="overall_population",
                            metric='intersectional_match_score',
                            affected_value=group_avg,
                            reference_value=overall_avg,
                            bias_score=bias_score,
                            statistical_significance=0.05,  # À calculer proprement
                            sample_size_affected=len(group_items),
                            sample_size_reference=len(enriched_data),
                            timestamp=datetime.now(),
                            details={
                                'intersection_attributes': attr_combo,
                                'is_intersectional': True
                            }
                        )
                        
                        bias_instances.append(bias_instance)
        
        except Exception as e:
            logger.error(f"Error analyzing intersectional bias: {e}")
        
        return bias_instances
    
    def _calculate_overall_bias_score(self, bias_instances: List[BiasInstance]) -> float:
        """Calcule un score global de biais."""
        if not bias_instances:
            return 0.0
        
        # Pondérer par gravité et taille d'échantillon
        weighted_scores = []
        total_weight = 0
        
        for instance in bias_instances:
            # Poids basé sur la taille d'échantillon
            weight = min(1.0, instance.sample_size_affected / 1000)
            
            # Ajuster le poids par significativité statistique
            weight *= (1 / max(instance.statistical_significance, 0.001))
            
            weighted_scores.append(instance.bias_score * weight)
            total_weight += weight
        
        return sum(weighted_scores) / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, bias_instances: List[BiasInstance]) -> List[str]:
        """Génère des recommandations basées sur les biais détectés."""
        recommendations = []
        
        # Compter par type de biais
        bias_counts = Counter(instance.bias_type for instance in bias_instances)
        
        # Recommandations génériques basées sur la prévalence
        if bias_counts[BiasType.GENDER] > 0:
            recommendations.append("Implementer un re-balancing post-processing pour réduire le biais de genre")
        
        if bias_counts[BiasType.AGE] > 0:
            recommendations.append("Revoir les critères d'expérience pour éviter la discrimination par l'âge")
        
        if bias_counts[BiasType.EDUCATION] > 0:
            recommendations.append("Augmenter l'importance des compétences pratiques vs diplômes")
        
        # Recommandations basées sur la sévérité
        max_bias_score = max((instance.bias_score for instance in bias_instances), default=0)
        
        if max_bias_score > self.config['bias_threshold_critical']:
            recommendations.append("URGENT: Suspendre le modèle et effectuer un audit complet")
        elif max_bias_score > self.config['bias_threshold_high']:
            recommendations.append("Révision immédiate des algorithmes de matching")
        
        # Recommandations par défaut
        if not recommendations:
            recommendations.append("Continuer le monitoring régulier des biais")
        
        return recommendations
    
    def _generate_statistical_summary(self, 
                                    enriched_data: List[Dict[str, Any]],
                                    bias_instances: List[BiasInstance]) -> Dict[str, Any]:
        """Génère un résumé statistique."""
        try:
            # Distribution démographique
            demographic_distribution = {}
            
            for attr in ['gender', 'age_group', 'education_level']:
                attr_counts = Counter()
                for item in enriched_data:
                    value = item['demographics'].get(attr)
                    if value:
                        attr_counts[value] += 1
                
                if attr_counts:
                    total = sum(attr_counts.values())
                    demographic_distribution[attr] = {
                        key: count / total 
                        for key, count in attr_counts.items()
                    }
            
            # Statistiques des biais
            bias_stats = {
                'total_instances': len(bias_instances),
                'avg_bias_score': statistics.mean([bi.bias_score for bi in bias_instances]) if bias_instances else 0,
                'max_bias_score': max([bi.bias_score for bi in bias_instances]) if bias_instances else 0,
                'bias_by_type': dict(Counter(bi.bias_type.value for bi in bias_instances))
            }
            
            # Distribution des scores de matching
            all_scores = [item['match_score'] for item in enriched_data]
            score_stats = {
                'mean': statistics.mean(all_scores),
                'median': statistics.median(all_scores),
                'std': statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
                'min': min(all_scores),
                'max': max(all_scores)
            }
            
            return {
                'demographic_distribution': demographic_distribution,
                'bias_statistics': bias_stats,
                'score_statistics': score_stats,
                'sample_size': len(enriched_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating statistical summary: {e}")
            return {}
    
    def _analyze_protected_groups(self, 
                                enriched_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Analyse approfondie des groupes protégés."""
        try:
            analysis = {}
            
            for attr_name, attr_values in self.protected_attributes.items():
                if attr_name in ['gender', 'age_group', 'ethnicity']:  # Focus sur les principaux
                    group_analysis = {}
                    
                    for value in attr_values:
                        group_items = [
                            item for item in enriched_data 
                            if item['demographics'].get(attr_name) == value
                        ]
                        
                        if group_items:
                            scores = [item['match_score'] for item in group_items]
                            group_analysis[value] = {
                                'sample_size': len(group_items),
                                'avg_score': statistics.mean(scores),
                                'score_std': statistics.stdev(scores) if len(scores) > 1 else 0,
                                'representation_pct': len(group_items) / len(enriched_data) * 100
                            }
                    
                    analysis[attr_name] = group_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing protected groups: {e}")
            return {}
    
    def _check_bias_alerts(self, report: BiasReport) -> None:
        """Vérifie et déclenche des alertes de biais."""
        try:
            # Alertes basées sur le score global
            if report.overall_bias_score > self.config['bias_threshold_critical']:
                self._trigger_bias_alert('critical', f"Score de biais critique: {report.overall_bias_score:.3f}")
            elif report.overall_bias_score > self.config['bias_threshold_high']:
                self._trigger_bias_alert('high', f"Score de biais élevé: {report.overall_bias_score:.3f}")
            
            # Alertes par instance critique
            for instance in report.bias_instances:
                if instance.bias_score > self.config['bias_threshold_critical']:
                    self._trigger_bias_alert(
                        'critical',
                        f"Biais critique détecté: {instance.bias_type.value} "
                        f"({instance.affected_group} vs {instance.reference_group})"
                    )
                    
        except Exception as e:
            logger.error(f"Error checking bias alerts: {e}")
    
    def _trigger_bias_alert(self, level: str, message: str) -> None:
        """Déclenche une alerte de biais."""
        logger.warning(f"BIAS ALERT [{level.upper()}]: {message}")
        # En production, ceci déclencherait des notifications externes
    
    # Méthodes utilitaires de catégorisation
    
    def _categorize_age(self, age: int) -> str:
        """Catégorise l'âge en groupes."""
        if age <= 25:
            return '18-25'
        elif age <= 35:
            return '26-35'
        elif age <= 45:
            return '36-45'
        elif age <= 55:
            return '46-55'
        elif age <= 65:
            return '56-65'
        else:
            return '65+'
    
    def _categorize_education(self, education: str) -> str:
        """Catégorise le niveau d'éducation."""
        education_lower = education.lower()
        
        if 'phd' in education_lower or 'doctorate' in education_lower:
            return 'phd'
        elif 'master' in education_lower or 'mba' in education_lower:
            return 'master'
        elif 'bachelor' in education_lower or 'licence' in education_lower:
            return 'bachelor'
        elif 'high school' in education_lower or 'bac' in education_lower:
            return 'high_school'
        else:
            return 'other'
    
    def _categorize_experience(self, years: int) -> str:
        """Catégorise l'expérience en niveaux."""
        if years < 2:
            return 'entry'
        elif years < 5:
            return 'junior'
        elif years < 10:
            return 'mid'
        elif years < 15:
            return 'senior'
        else:
            return 'executive'
    
    def _categorize_location(self, location: str) -> str:
        """Catégorise le type de localisation."""
        location_lower = location.lower()
        
        # Liste simplifiée - à adapter selon les besoins
        urban_keywords = ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes']
        
        if any(keyword in location_lower for keyword in urban_keywords):
            return 'urban'
        else:
            return 'suburban'  # Simplification
    
    def _categorize_salary(self, salary_range: Dict[str, int]) -> str:
        """Catégorise la fourchette salariale."""
        if 'max' in salary_range:
            max_salary = salary_range['max']
            
            if max_salary < 30000:
                return 'low'
            elif max_salary < 50000:
                return 'medium'
            elif max_salary < 80000:
                return 'high'
            else:
                return 'very_high'
        
        return 'unknown'
    
    # Méthodes de calcul des métriques de fairness
    
    def _calculate_demographic_parity(self, groups: Dict[str, List[Dict]]) -> FairnessMetric:
        """Calcule la parité démographique."""
        try:
            group_rates = {}
            
            for group_name, group_data in groups.items():
                positive_rate = sum(1 for item in group_data if item['binary_pred']) / len(group_data)
                group_rates[group_name] = positive_rate
            
            # Différence max entre groupes
            rates = list(group_rates.values())
            max_diff = max(rates) - min(rates) if rates else 0
            
            # Score de parité (1 - différence)
            parity_score = 1 - max_diff
            
            # Déterminer le statut
            if max_diff < 0.05:
                status = BiasStatus.NONE
            elif max_diff < 0.1:
                status = BiasStatus.LOW
            elif max_diff < 0.2:
                status = BiasStatus.MODERATE
            else:
                status = BiasStatus.HIGH
            
            return FairnessMetric(
                name='demographic_parity',
                value=parity_score,
                threshold=0.9,  # Seuil pour considérer comme fair
                status=status,
                description=f"Maximum difference in positive rates: {max_diff:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating demographic parity: {e}")
            return FairnessMetric('demographic_parity', 0.0, 0.9, BiasStatus.HIGH, 'Error in calculation')
    
    def _calculate_equal_opportunity(self, groups: Dict[str, List[Dict]]) -> FairnessMetric:
        """Calcule l'égalité des chances (TPR égal)."""
        try:
            group_tpr = {}
            
            for group_name, group_data in groups.items():
                # Calculer le True Positive Rate (sensibilité)
                true_positives = [item for item in group_data if item['binary_pred'] and item['truth']]
                positives = [item for item in group_data if item['truth']]
                
                tpr = len(true_positives) / len(positives) if positives else 0
                group_tpr[group_name] = tpr
            
            # Différence max en TPR
            tprs = list(group_tpr.values())
            max_diff = max(tprs) - min(tprs) if tprs else 0
            
            opportunity_score = 1 - max_diff
            
            # Statut
            if max_diff < 0.05:
                status = BiasStatus.NONE
            elif max_diff < 0.1:
                status = BiasStatus.LOW
            elif max_diff < 0.2:
                status = BiasStatus.MODERATE
            else:
                status = BiasStatus.HIGH
            
            return FairnessMetric(
                name='equal_opportunity',
                value=opportunity_score,
                threshold=0.9,
                status=status,
                description=f"Maximum TPR difference: {max_diff:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating equal opportunity: {e}")
            return FairnessMetric('equal_opportunity', 0.0, 0.9, BiasStatus.HIGH, 'Error in calculation')
    
    def _calculate_equalized_odds(self, groups: Dict[str, List[Dict]]) -> FairnessMetric:
        """Calcule l'égalisation des chances (TPR et FPR égaux)."""
        try:
            group_metrics = {}
            
            for group_name, group_data in groups.items():
                # TPR
                true_positives = [item for item in group_data if item['binary_pred'] and item['truth']]
                positives = [item for item in group_data if item['truth']]
                tpr = len(true_positives) / len(positives) if positives else 0
                
                # FPR
                false_positives = [item for item in group_data if item['binary_pred'] and not item['truth']]
                negatives = [item for item in group_data if not item['truth']]
                fpr = len(false_positives) / len(negatives) if negatives else 0
                
                group_metrics[group_name] = {'tpr': tpr, 'fpr': fpr}
            
            # Calculer les différences max
            tprs = [metrics['tpr'] for metrics in group_metrics.values()]
            fprs = [metrics['fpr'] for metrics in group_metrics.values()]
            
            max_tpr_diff = max(tprs) - min(tprs) if tprs else 0
            max_fpr_diff = max(fprs) - min(fprs) if fprs else 0
            
            # Score global (moyenne des deux métriques)
            odds_score = 1 - (max_tpr_diff + max_fpr_diff) / 2
            
            # Statut basé sur la pire des deux métriques
            max_diff = max(max_tpr_diff, max_fpr_diff)
            if max_diff < 0.05:
                status = BiasStatus.NONE
            elif max_diff < 0.1:
                status = BiasStatus.LOW
            elif max_diff < 0.2:
                status = BiasStatus.MODERATE
            else:
                status = BiasStatus.HIGH
            
            return FairnessMetric(
                name='equalized_odds',
                value=odds_score,
                threshold=0.9,
                status=status,
                description=f"Max TPR diff: {max_tpr_diff:.3f}, Max FPR diff: {max_fpr_diff:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating equalized odds: {e}")
            return FairnessMetric('equalized_odds', 0.0, 0.9, BiasStatus.HIGH, 'Error in calculation')
    
    def _calculate_calibration(self, groups: Dict[str, List[Dict]]) -> FairnessMetric:
        """Calcule la calibration entre groupes."""
        try:
            group_calibration = {}
            
            for group_name, group_data in groups.items():
                # Grouper par score prédit pour calculer calibration
                score_buckets = defaultdict(list)
                
                for item in group_data:
                    # Bucket par tranche de 0.1
                    bucket = int(item['prediction'] * 10) / 10
                    score_buckets[bucket].append(item['truth'])
                
                # Calculer la calibration moyenne
                calibration_errors = []
                for bucket_score, truths in score_buckets.items():
                    if truths:  # Au moins une observation
                        actual_rate = sum(truths) / len(truths)
                        calibration_error = abs(bucket_score - actual_rate)
                        calibration_errors.append(calibration_error)
                
                avg_calibration_error = statistics.mean(calibration_errors) if calibration_errors else 0
                group_calibration[group_name] = avg_calibration_error
            
            # Différence max en erreur de calibration
            errors = list(group_calibration.values())
            max_diff = max(errors) - min(errors) if errors else 0
            
            calibration_score = 1 - max_diff
            
            # Statut
            if max_diff < 0.05:
                status = BiasStatus.NONE
            elif max_diff < 0.1:
                status = BiasStatus.LOW
            elif max_diff < 0.15:
                status = BiasStatus.MODERATE
            else:
                status = BiasStatus.HIGH
            
            return FairnessMetric(
                name='calibration',
                value=calibration_score,
                threshold=0.9,
                status=status,
                description=f"Max calibration error difference: {max_diff:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating calibration: {e}")
            return FairnessMetric('calibration', 0.0, 0.9, BiasStatus.HIGH, 'Error in calculation')
