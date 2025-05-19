"""
Validateur de qualité des données pour les datasets synthétiques.

Ce module fournit:
- Validation de la cohérence des données générées
- Métriques de qualité des datasets
- Détection d'anomalies et de biais
- Rapports de validation détaillés
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum
import re

from ..core.models import CV, JobOffer, MatchResult

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Niveaux de validation."""
    BASIC = "basic"           # Validation basique
    STANDARD = "standard"     # Validation complète standard
    STRICT = "strict"         # Validation stricte avec critères élevés


class ValidationStatus(Enum):
    """Statuts de validation."""
    PASSED = "passed"         # Validation réussie
    WARNING = "warning"       # Avertissements détectés
    FAILED = "failed"         # Validation échouée
    ERROR = "error"           # Erreur pendant la validation


@dataclass
class ValidationRule:
    """Définit une règle de validation."""
    name: str
    description: str
    category: str             # 'consistency', 'quality', 'bias', 'completeness'
    severity: str             # 'low', 'medium', 'high', 'critical'
    validator_func: callable
    threshold: Optional[float] = None
    
    
@dataclass 
class ValidationResult:
    """Résultat d'une validation."""
    rule_name: str
    status: ValidationStatus
    score: float              # 0-1, score de la validation
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class QualityMetrics:
    """Métriques globales de qualité d'un dataset."""
    overall_score: float                    # Score global 0-1
    completeness_score: float              # Complétude des données
    consistency_score: float               # Cohérence interne
    diversity_score: float                 # Diversité du dataset
    realism_score: float                   # Réalisme des données
    bias_score: float                      # Score de biais (1 = pas de biais)
    
    # Métriques détaillées par catégorie
    category_scores: Dict[str, float] = field(default_factory=dict)
    
    # Statistiques descriptives
    item_count: int = 0
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Résultats détaillés
    validation_results: List[ValidationResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class DataValidator:
    """
    Validateur de qualité pour les datasets synthétiques.
    
    Effectue une validation complète des données générées:
    - Cohérence structurelle
    - Qualité des contenus
    - Détection de biais
    - Métriques de diversité
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialise le validateur.
        
        Args:
            validation_level: Niveau de validation à appliquer
        """
        self.validation_level = validation_level
        self.rules = self._initialize_validation_rules()
        
        logger.info(f"DataValidator initialized with {validation_level.value} validation level")
    
    def validate_cvs(self, cvs: List[CV]) -> QualityMetrics:
        """
        Valide une liste de CV.
        
        Args:
            cvs: Liste des CV à valider
            
        Returns:
            QualityMetrics avec les résultats de validation
        """
        logger.info(f"Validating {len(cvs)} CVs...")
        
        validation_results = []
        
        # Appliquer les règles de validation
        for rule in self.rules:
            if rule.category in ['consistency', 'quality', 'completeness'] or 'cv' in rule.name.lower():
                try:
                    result = rule.validator_func(cvs, rule.threshold)
                    validation_results.append(result)
                except Exception as e:
                    logger.error(f"Error validating rule {rule.name}: {str(e)}")
                    validation_results.append(ValidationResult(
                        rule_name=rule.name,
                        status=ValidationStatus.ERROR,
                        score=0.0,
                        message=f"Validation error: {str(e)}"
                    ))
        
        # Calculer les métriques globales
        metrics = self._calculate_cv_metrics(cvs, validation_results)
        
        logger.info(f"CV validation completed. Overall score: {metrics.overall_score:.3f}")
        return metrics
    
    def validate_jobs(self, jobs: List[JobOffer]) -> QualityMetrics:
        """
        Valide une liste d'offres d'emploi.
        
        Args:
            jobs: Liste des offres d'emploi à valider
            
        Returns:
            QualityMetrics avec les résultats de validation
        """
        logger.info(f"Validating {len(jobs)} job offers...")
        
        validation_results = []
        
        # Appliquer les règles de validation
        for rule in self.rules:
            if rule.category in ['consistency', 'quality', 'completeness'] or 'job' in rule.name.lower():
                try:
                    result = rule.validator_func(jobs, rule.threshold)
                    validation_results.append(result)
                except Exception as e:
                    logger.error(f"Error validating rule {rule.name}: {str(e)}")
                    validation_results.append(ValidationResult(
                        rule_name=rule.name,
                        status=ValidationStatus.ERROR,
                        score=0.0,
                        message=f"Validation error: {str(e)}"
                    ))
        
        # Calculer les métriques globales
        metrics = self._calculate_job_metrics(jobs, validation_results)
        
        logger.info(f"Job validation completed. Overall score: {metrics.overall_score:.3f}")
        return metrics
    
    def validate_full_dataset(self,
                             cvs: List[CV],
                             jobs: List[JobOffer],
                             ground_truth: Optional[List[MatchResult]] = None) -> QualityMetrics:
        """
        Valide un dataset complet avec CV, jobs et vérité terrain.
        
        Args:
            cvs: Liste des CV
            jobs: Liste des offres d'emploi
            ground_truth: Matches de vérité terrain optionnels
            
        Returns:
            QualityMetrics globales pour tout le dataset
        """
        logger.info(f"Validating full dataset: {len(cvs)} CVs, {len(jobs)} jobs")
        
        # Valider chaque composant
        cv_metrics = self.validate_cvs(cvs)
        job_metrics = self.validate_jobs(jobs)
        
        # Validation inter-composants
        dataset_results = []
        for rule in self.rules:
            if rule.category == 'consistency' and 'dataset' in rule.name.lower():
                try:
                    result = rule.validator_func((cvs, jobs, ground_truth), rule.threshold)
                    dataset_results.append(result)
                except Exception as e:
                    logger.error(f"Error validating dataset rule {rule.name}: {str(e)}")
        
        # Combiner les métriques
        combined_metrics = self._combine_validation_metrics(
            cv_metrics, 
            job_metrics, 
            dataset_results
        )
        
        # Validation de la vérité terrain si fournie
        if ground_truth:
            gt_metrics = self.validate_ground_truth(ground_truth, cvs, jobs)
            combined_metrics = self._merge_ground_truth_metrics(combined_metrics, gt_metrics)
        
        logger.info(f"Full dataset validation completed. Overall score: {combined_metrics.overall_score:.3f}")
        return combined_metrics
    
    def validate_ground_truth(self,
                             ground_truth: List[MatchResult],
                             cvs: List[CV],
                             jobs: List[JobOffer]) -> QualityMetrics:
        """
        Valide la qualité de la vérité terrain de matching.
        
        Args:
            ground_truth: Matches de vérité terrain
            cvs: CV de référence
            jobs: Jobs de référence
            
        Returns:
            QualityMetrics pour la vérité terrain
        """
        logger.info(f"Validating ground truth with {len(ground_truth)} matches")
        
        validation_results = []
        
        # Règles spécifiques à la vérité terrain
        gt_rules = [rule for rule in self.rules if 'ground_truth' in rule.name.lower()]
        
        for rule in gt_rules:
            try:
                result = rule.validator_func((ground_truth, cvs, jobs), rule.threshold)
                validation_results.append(result)
            except Exception as e:
                logger.error(f"Error validating ground truth rule {rule.name}: {str(e)}")
        
        # Calculer les métriques spécifiques
        metrics = self._calculate_ground_truth_metrics(ground_truth, cvs, jobs, validation_results)
        
        return metrics
    
    def generate_validation_report(self, metrics: QualityMetrics) -> str:
        """
        Génère un rapport de validation détaillé.
        
        Args:
            metrics: Métriques de validation
            
        Returns:
            Rapport au format texte
        """
        report_lines = []
        
        # En-tête
        report_lines.append("=" * 80)
        report_lines.append("RAPPORT DE VALIDATION DE DATASET")
        report_lines.append("=" * 80)
        report_lines.append(f"Date: {metrics.validation_timestamp}")
        report_lines.append(f"Items validés: {metrics.item_count}")
        report_lines.append("")
        
        # Score global
        report_lines.append("SCORE GLOBAL DE QUALITÉ")
        report_lines.append("-" * 40)
        report_lines.append(f"Score global: {metrics.overall_score:.1%} {self._get_score_emoji(metrics.overall_score)}")
        
        # Scores par catégorie
        report_lines.append("")
        report_lines.append("SCORES PAR CATÉGORIE")
        report_lines.append("-" * 40)
        report_lines.append(f"Complétude:   {metrics.completeness_score:.1%} {self._get_score_emoji(metrics.completeness_score)}")
        report_lines.append(f"Cohérence:    {metrics.consistency_score:.1%} {self._get_score_emoji(metrics.consistency_score)}")
        report_lines.append(f"Diversité:    {metrics.diversity_score:.1%} {self._get_score_emoji(metrics.diversity_score)}")
        report_lines.append(f"Réalisme:     {metrics.realism_score:.1%} {self._get_score_emoji(metrics.realism_score)}")
        report_lines.append(f"Absence biais: {metrics.bias_score:.1%} {self._get_score_emoji(metrics.bias_score)}")
        
        # Détail des validations
        if metrics.validation_results:
            report_lines.append("")
            report_lines.append("DÉTAIL DES VALIDATIONS")
            report_lines.append("-" * 40)
            
            # Grouper par statut
            by_status = defaultdict(list)
            for result in metrics.validation_results:
                by_status[result.status].append(result)
            
            # Afficher les échecs et avertissements en premier
            for status in [ValidationStatus.FAILED, ValidationStatus.WARNING, ValidationStatus.PASSED]:
                if status not in by_status:
                    continue
                
                status_emoji = {
                    ValidationStatus.FAILED: "❌",
                    ValidationStatus.WARNING: "⚠️", 
                    ValidationStatus.PASSED: "✅"
                }[status]
                
                report_lines.append(f"\n{status_emoji} {status.value.upper()} ({len(by_status[status])})")
                
                for result in by_status[status]:
                    score_str = f"({result.score:.1%})" if result.score is not None else ""
                    report_lines.append(f"  • {result.rule_name}: {result.message} {score_str}")
                    
                    if result.recommendations:
                        for rec in result.recommendations:
                            report_lines.append(f"    → {rec}")
        
        # Erreurs et avertissements
        if metrics.errors:
            report_lines.append("")
            report_lines.append("ERREURS DÉTECTÉES")
            report_lines.append("-" * 40)
            for error in metrics.errors:
                report_lines.append(f"❌ {error}")
        
        if metrics.warnings:
            report_lines.append("")
            report_lines.append("AVERTISSEMENTS")
            report_lines.append("-" * 40)
            for warning in metrics.warnings:
                report_lines.append(f"⚠️  {warning}")
        
        # Recommandations générales
        report_lines.append("")
        report_lines.append("RECOMMANDATIONS GÉNÉRALES")
        report_lines.append("-" * 40)
        
        if metrics.overall_score < 0.5:
            report_lines.append("❌ Qualité insuffisante - Révision majeure nécessaire")
        elif metrics.overall_score < 0.7:
            report_lines.append("⚠️  Qualité acceptable - Améliorations recommandées")
        elif metrics.overall_score < 0.9:
            report_lines.append("✅ Bonne qualité - Optimisations mineures possibles")
        else:
            report_lines.append("🌟 Excellente qualité - Dataset prêt pour utilisation")
        
        # Suggestions d'amélioration
        suggestions = self._generate_improvement_suggestions(metrics)
        if suggestions:
            report_lines.append("")
            report_lines.append("SUGGESTIONS D'AMÉLIORATION")
            report_lines.append("-" * 40)
            for suggestion in suggestions:
                report_lines.append(f"💡 {suggestion}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def export_validation_metrics(self, metrics: QualityMetrics, format: str = 'json') -> Dict[str, Any]:
        """
        Exporte les métriques de validation dans différents formats.
        
        Args:
            metrics: Métriques à exporter
            format: Format d'export ('json', 'csv', 'dict')
            
        Returns:
            Données exportées
        """
        if format == 'json':
            return self._export_to_json(metrics)
        elif format == 'csv':
            return self._export_to_csv(metrics)
        else:  # dict
            return self._export_to_dict(metrics)
    
    # Méthodes privées
    
    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """Initialise les règles de validation."""
        rules = []
        
        # === RÈGLES DE COMPLÉTUDE ===
        rules.append(ValidationRule(
            name="cv_required_fields",
            description="Vérification des champs obligatoires des CV",
            category="completeness",
            severity="high",
            validator_func=self._validate_cv_required_fields,
            threshold=0.95
        ))
        
        rules.append(ValidationRule(
            name="job_required_fields", 
            description="Vérification des champs obligatoires des offres",
            category="completeness",
            severity="high",
            validator_func=self._validate_job_required_fields,
            threshold=0.95
        ))
        
        # === RÈGLES DE COHÉRENCE ===
        rules.append(ValidationRule(
            name="cv_skills_consistency",
            description="Cohérence des compétences avec l'expérience",
            category="consistency",
            severity="medium",
            validator_func=self._validate_cv_skills_consistency,
            threshold=0.8
        ))
        
        rules.append(ValidationRule(
            name="job_requirements_consistency",
            description="Cohérence des exigences des offres",
            category="consistency",
            severity="medium", 
            validator_func=self._validate_job_requirements_consistency,
            threshold=0.8
        ))
        
        rules.append(ValidationRule(
            name="dataset_sector_balance",
            description="Équilibre des secteurs dans le dataset",
            category="consistency",
            severity="low",
            validator_func=self._validate_sector_balance,
            threshold=0.7
        ))
        
        # === RÈGLES DE QUALITÉ ===
        rules.append(ValidationRule(
            name="cv_content_quality",
            description="Qualité du contenu des CV",
            category="quality",
            severity="medium",
            validator_func=self._validate_cv_content_quality,
            threshold=0.7
        ))
        
        rules.append(ValidationRule(
            name="job_content_quality",
            description="Qualité du contenu des offres",
            category="quality",
            severity="medium",
            validator_func=self._validate_job_content_quality,
            threshold=0.7
        ))
        
        rules.append(ValidationRule(
            name="data_diversity",
            description="Diversité des données générées",
            category="quality",
            severity="medium",
            validator_func=self._validate_data_diversity,
            threshold=0.6
        ))
        
        # === RÈGLES DE DÉTECTION DE BIAIS ===
        rules.append(ValidationRule(
            name="gender_bias_detection",
            description="Détection de biais de genre",
            category="bias",
            severity="high",
            validator_func=self._validate_gender_bias,
            threshold=0.8
        ))
        
        rules.append(ValidationRule(
            name="geographic_bias_detection",
            description="Détection de biais géographique",
            category="bias",
            severity="medium",
            validator_func=self._validate_geographic_bias,
            threshold=0.7
        ))
        
        rules.append(ValidationRule(
            name="educational_bias_detection",
            description="Détection de biais éducationnel",
            category="bias",
            severity="medium",
            validator_func=self._validate_educational_bias,
            threshold=0.8
        ))
        
        # === RÈGLES POUR LA VÉRITÉ TERRAIN ===
        rules.append(ValidationRule(
            name="ground_truth_coverage",
            description="Couverture de la vérité terrain",
            category="quality",
            severity="medium",
            validator_func=self._validate_ground_truth_coverage,
            threshold=0.5
        ))
        
        rules.append(ValidationRule(
            name="ground_truth_score_distribution",
            description="Distribution des scores de matching",
            category="quality",
            severity="medium",
            validator_func=self._validate_score_distribution,
            threshold=0.7
        ))
        
        # Filtrer selon le niveau de validation
        if self.validation_level == ValidationLevel.BASIC:
            rules = [r for r in rules if r.severity in ['high', 'critical']]
        elif self.validation_level == ValidationLevel.STRICT:
            # Ajuster les seuils pour être plus stricts
            for rule in rules:
                if rule.threshold:
                    rule.threshold = min(0.95, rule.threshold + 0.1)
        
        return rules
    
    # === VALIDATEURS POUR CHAMPS OBLIGATOIRES ===
    
    def _validate_cv_required_fields(self, cvs: List[CV], threshold: float) -> ValidationResult:
        """Valide la présence des champs obligatoires dans les CV."""
        required_fields = ['id', 'skills']
        
        missing_counts = defaultdict(int)
        total_cvs = len(cvs)
        
        for cv in cvs:
            if not hasattr(cv, 'id') or not cv.id:
                missing_counts['id'] += 1
            if not hasattr(cv, 'skills') or not cv.skills:
                missing_counts['skills'] += 1
        
        # Calculer le score de complétude
        total_required = len(required_fields) * total_cvs
        total_missing = sum(missing_counts.values())
        completeness_score = 1 - (total_missing / total_required)
        
        if completeness_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Champs obligatoires présents ({completeness_score:.1%})"
        elif completeness_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Quelques champs manquants ({completeness_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Trop de champs manquants ({completeness_score:.1%})"
        
        recommendations = []
        if missing_counts:
            missing_details = [f"{field}: {count} manquants" for field, count in missing_counts.items()]
            recommendations.append(f"Compléter les champs: {', '.join(missing_details)}")
        
        return ValidationResult(
            rule_name="cv_required_fields",
            status=status,
            score=completeness_score,
            message=message,
            details=dict(missing_counts),
            recommendations=recommendations
        )
    
    def _validate_job_required_fields(self, jobs: List[JobOffer], threshold: float) -> ValidationResult:
        """Valide la présence des champs obligatoires dans les offres."""
        required_fields = ['id', 'title', 'company', 'required_skills']
        
        missing_counts = defaultdict(int)
        total_jobs = len(jobs)
        
        for job in jobs:
            if not hasattr(job, 'id') or not job.id:
                missing_counts['id'] += 1
            if not hasattr(job, 'title') or not job.title:
                missing_counts['title'] += 1
            if not hasattr(job, 'company') or not job.company:
                missing_counts['company'] += 1
            if not hasattr(job, 'required_skills') or not job.required_skills:
                missing_counts['required_skills'] += 1
        
        # Calculer le score de complétude
        total_required = len(required_fields) * total_jobs
        total_missing = sum(missing_counts.values())
        completeness_score = 1 - (total_missing / total_required)
        
        if completeness_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Champs obligatoires présents ({completeness_score:.1%})"
        elif completeness_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Quelques champs manquants ({completeness_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Trop de champs manquants ({completeness_score:.1%})"
        
        recommendations = []
        if missing_counts:
            missing_details = [f"{field}: {count} manquants" for field, count in missing_counts.items()]
            recommendations.append(f"Compléter les champs: {', '.join(missing_details)}")
        
        return ValidationResult(
            rule_name="job_required_fields",
            status=status,
            score=completeness_score,
            message=message,
            details=dict(missing_counts),
            recommendations=recommendations
        )
    
    # === VALIDATEURS DE COHÉRENCE ===
    
    def _validate_cv_skills_consistency(self, cvs: List[CV], threshold: float) -> ValidationResult:
        """Valide la cohérence entre compétences et expérience."""
        consistent_count = 0
        
        for cv in cvs:
            if not hasattr(cv, 'skills') or not cv.skills:
                continue
                
            # Vérifier la cohérence basique (pas de compétences vides)
            skills_valid = all(skill.strip() for skill in cv.skills)
            
            # Vérifier la cohérence avec l'expérience si disponible
            if hasattr(cv, 'experience') and cv.experience:
                exp_consistency = self._check_skills_experience_match(cv.skills, cv.experience)
            else:
                exp_consistency = True  # Pas d'expérience à vérifier
            
            if skills_valid and exp_consistency:
                consistent_count += 1
        
        consistency_score = consistent_count / len(cvs) if cvs else 0
        
        if consistency_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Compétences cohérentes ({consistency_score:.1%})"
        elif consistency_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Cohérence acceptable ({consistency_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Manque de cohérence ({consistency_score:.1%})"
        
        recommendations = []
        if consistency_score < threshold:
            recommendations.append("Vérifier l'alignement compétences-expérience")
            recommendations.append("Éliminer les compétences vides ou invalides")
        
        return ValidationResult(
            rule_name="cv_skills_consistency",
            status=status,
            score=consistency_score,
            message=message,
            details={'consistent_cvs': consistent_count, 'total_cvs': len(cvs)},
            recommendations=recommendations
        )
    
    def _validate_job_requirements_consistency(self, jobs: List[JobOffer], threshold: float) -> ValidationResult:
        """Valide la cohérence des exigences des offres."""
        consistent_count = 0
        
        for job in jobs:
            consistent = True
            
            # Vérifier que les compétences requises ne sont pas vides
            if hasattr(job, 'required_skills') and job.required_skills:
                skills_valid = all(skill.strip() for skill in job.required_skills)
                consistent = consistent and skills_valid
            
            # Vérifier la cohérence titre-secteur si disponible
            if hasattr(job, 'title') and hasattr(job, 'metadata'):
                sector = job.metadata.get('sector') if job.metadata else None
                if sector:
                    title_sector_consistent = self._check_title_sector_consistency(job.title, sector)
                    consistent = consistent and title_sector_consistent
            
            if consistent:
                consistent_count += 1
        
        consistency_score = consistent_count / len(jobs) if jobs else 0
        
        if consistency_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Exigences cohérentes ({consistency_score:.1%})"
        elif consistency_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Cohérence acceptable ({consistency_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Incohérences détectées ({consistency_score:.1%})"
        
        recommendations = []
        if consistency_score < threshold:
            recommendations.append("Vérifier l'alignement titre-secteur-compétences")
            recommendations.append("Éliminer les compétences vides")
        
        return ValidationResult(
            rule_name="job_requirements_consistency",
            status=status,
            score=consistency_score,
            message=message,
            details={'consistent_jobs': consistent_count, 'total_jobs': len(jobs)},
            recommendations=recommendations
        )
    
    def _validate_sector_balance(self, data: Tuple[List[CV], List[JobOffer], Any], threshold: float) -> ValidationResult:
        """Valide l'équilibre des secteurs dans le dataset."""
        cvs, jobs, _ = data
        
        # Compter les secteurs pour les CV
        cv_sectors = defaultdict(int)
        for cv in cvs:
            if hasattr(cv, 'metadata') and cv.metadata and 'sector' in cv.metadata:
                cv_sectors[cv.metadata['sector']] += 1
        
        # Compter les secteurs pour les jobs
        job_sectors = defaultdict(int)
        for job in jobs:
            if hasattr(job, 'metadata') and job.metadata and 'sector' in job.metadata:
                job_sectors[job.metadata['sector']] += 1
        
        # Calculer l'équilibre (coefficient de variation)
        cv_balance = self._calculate_distribution_balance(list(cv_sectors.values()))
        job_balance = self._calculate_distribution_balance(list(job_sectors.values()))
        
        # Score global (moyenne des deux)
        overall_balance = (cv_balance + job_balance) / 2
        
        if overall_balance >= threshold:
            status = ValidationStatus.PASSED
            message = f"Distribution sectorielle équilibrée ({overall_balance:.1%})"
        elif overall_balance >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Distribution acceptable ({overall_balance:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Distribution déséquilibrée ({overall_balance:.1%})"
        
        recommendations = []
        if overall_balance < threshold:
            recommendations.append("Rééquilibrer la représentation sectorielle")
            recommendations.append("Vérifier la stratégie de génération par secteur")
        
        return ValidationResult(
            rule_name="dataset_sector_balance",
            status=status,
            score=overall_balance,
            message=message,
            details={
                'cv_sectors': dict(cv_sectors),
                'job_sectors': dict(job_sectors),
                'cv_balance': cv_balance,
                'job_balance': job_balance
            },
            recommendations=recommendations
        )
    
    # === VALIDATEURS DE QUALITÉ ===
    
    def _validate_cv_content_quality(self, cvs: List[CV], threshold: float) -> ValidationResult:
        """Valide la qualité du contenu des CV."""
        quality_scores = []
        
        for cv in cvs:
            score = 0.0
            criteria_count = 0
            
            # Critère 1: Diversité des compétences
            if hasattr(cv, 'skills') and cv.skills:
                skill_diversity = len(set(cv.skills)) / len(cv.skills)
                score += skill_diversity
                criteria_count += 1
            
            # Critère 2: Cohérence des informations
            if hasattr(cv, 'personal_info') and cv.personal_info:
                info_completeness = len(cv.personal_info) / 4  # Supposons 4 champs standards
                score += min(1.0, info_completeness)
                criteria_count += 1
            
            # Critère 3: Présence d'expérience
            if hasattr(cv, 'experience'):
                exp_score = 1.0 if cv.experience else 0.5  # 0.5 pour les débutants
                score += exp_score
                criteria_count += 1
            
            # Critère 4: Présence d'éducation
            if hasattr(cv, 'education'):
                edu_score = 1.0 if cv.education else 0.3
                score += edu_score
                criteria_count += 1
            
            # Moyenne des critères
            if criteria_count > 0:
                quality_scores.append(score / criteria_count)
        
        avg_quality = np.mean(quality_scores) if quality_scores else 0
        
        if avg_quality >= threshold:
            status = ValidationStatus.PASSED
            message = f"Qualité de contenu satisfaisante ({avg_quality:.1%})"
        elif avg_quality >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Qualité acceptable ({avg_quality:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Qualité insuffisante ({avg_quality:.1%})"
        
        recommendations = []
        if avg_quality < threshold:
            recommendations.append("Améliorer la diversité des compétences")
            recommendations.append("Enrichir les informations personnelles")
            recommendations.append("Ajouter plus de détails d'expérience")
        
        return ValidationResult(
            rule_name="cv_content_quality",
            status=status,
            score=avg_quality,
            message=message,
            details={'quality_distribution': quality_scores},
            recommendations=recommendations
        )
    
    def _validate_job_content_quality(self, jobs: List[JobOffer], threshold: float) -> ValidationResult:
        """Valide la qualité du contenu des offres."""
        quality_scores = []
        
        for job in jobs:
            score = 0.0
            criteria_count = 0
            
            # Critère 1: Clarté du titre
            if hasattr(job, 'title') and job.title:
                title_clarity = 1.0 if len(job.title.split()) >= 2 else 0.5
                score += title_clarity
                criteria_count += 1
            
            # Critère 2: Précision des compétences
            if hasattr(job, 'required_skills') and job.required_skills:
                skills_precision = min(1.0, len(job.required_skills) / 5)  # Optimal ~5 compétences
                score += skills_precision
                criteria_count += 1
            
            # Critère 3: Informations complémentaires
            optional_fields = ['description', 'location', 'employment_type', 'salary_range']
            present_fields = sum(1 for field in optional_fields if hasattr(job, field) and getattr(job, field))
            completeness = present_fields / len(optional_fields)
            score += completeness
            criteria_count += 1
            
            # Critère 4: Cohérence entreprise-poste
            if hasattr(job, 'company') and hasattr(job, 'title'):
                company_consistency = 1.0 if job.company and job.title else 0.0
                score += company_consistency
                criteria_count += 1
            
            # Moyenne des critères
            if criteria_count > 0:
                quality_scores.append(score / criteria_count)
        
        avg_quality = np.mean(quality_scores) if quality_scores else 0
        
        if avg_quality >= threshold:
            status = ValidationStatus.PASSED
            message = f"Qualité de contenu satisfaisante ({avg_quality:.1%})"
        elif avg_quality >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Qualité acceptable ({avg_quality:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Qualité insuffisante ({avg_quality:.1%})"
        
        recommendations = []
        if avg_quality < threshold:
            recommendations.append("Améliorer la précision des titres de poste")
            recommendations.append("Optimiser le nombre de compétences requises")
            recommendations.append("Enrichir les descriptions d'offres")
        
        return ValidationResult(
            rule_name="job_content_quality",
            status=status,
            score=avg_quality,
            message=message,
            details={'quality_distribution': quality_scores},
            recommendations=recommendations
        )
    
    def _validate_data_diversity(self, data: List[Any], threshold: float) -> ValidationResult:
        """Valide la diversité des données."""
        if not data:
            return ValidationResult(
                rule_name="data_diversity",
                status=ValidationStatus.ERROR,
                score=0.0,
                message="Aucune donnée à valider"
            )
        
        diversity_metrics = {}
        
        # Si ce sont des CV
        if hasattr(data[0], 'skills'):
            # Diversité des compétences
            all_skills = []
            for cv in data:
                if hasattr(cv, 'skills') and cv.skills:
                    all_skills.extend(cv.skills)
            
            if all_skills:
                unique_skills_ratio = len(set(all_skills)) / len(all_skills)
                diversity_metrics['skills_diversity'] = unique_skills_ratio
            
            # Diversité géographique
            if data[0].metadata and 'location' in data[0].metadata:
                locations = [cv.metadata['location'] for cv in data if cv.metadata and 'location' in cv.metadata]
                if locations:
                    unique_locations_ratio = len(set(locations)) / len(locations)
                    diversity_metrics['location_diversity'] = unique_locations_ratio
        
        # Si ce sont des jobs
        elif hasattr(data[0], 'company'):
            # Diversité des entreprises
            companies = [job.company for job in data if hasattr(job, 'company') and job.company]
            if companies:
                unique_companies_ratio = len(set(companies)) / len(companies)
                diversity_metrics['company_diversity'] = unique_companies_ratio
            
            # Diversité des titres
            titles = [job.title for job in data if hasattr(job, 'title') and job.title]
            if titles:
                unique_titles_ratio = len(set(titles)) / len(titles)
                diversity_metrics['title_diversity'] = unique_titles_ratio
        
        # Score global de diversité
        if diversity_metrics:
            avg_diversity = np.mean(list(diversity_metrics.values()))
        else:
            avg_diversity = 0
        
        if avg_diversity >= threshold:
            status = ValidationStatus.PASSED
            message = f"Diversité satisfaisante ({avg_diversity:.1%})"
        elif avg_diversity >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Diversité acceptable ({avg_diversity:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Manque de diversité ({avg_diversity:.1%})"
        
        recommendations = []
        if avg_diversity < threshold:
            recommendations.append("Augmenter la variété dans la génération")
            recommendations.append("Vérifier les paramètres de diversité")
        
        return ValidationResult(
            rule_name="data_diversity",
            status=status,
            score=avg_diversity,
            message=message,
            details=diversity_metrics,
            recommendations=recommendations
        )
    
    # === VALIDATEURS DE BIAIS ===
    
    def _validate_gender_bias(self, data: List[Any], threshold: float) -> ValidationResult:
        """Détecte les biais de genre dans les données."""
        gender_distribution = defaultdict(int)
        sector_gender = defaultdict(lambda: defaultdict(int))
        
        total_items = 0
        for item in data:
            if hasattr(item, 'metadata') and item.metadata:
                gender = item.metadata.get('gender')
                sector = item.metadata.get('sector')
                
                if gender:
                    gender_distribution[gender] += 1
                    if sector:
                        sector_gender[sector][gender] += 1
                    total_items += 1
        
        if total_items == 0:
            return ValidationResult(
                rule_name="gender_bias_detection",
                status=ValidationStatus.WARNING,
                score=1.0,
                message="Aucune information de genre disponible"
            )
        
        # Calculer l'équilibre global de genre
        gender_values = list(gender_distribution.values())
        gender_balance = self._calculate_distribution_balance(gender_values)
        
        # Calculer l'équilibre par secteur
        sector_biases = {}
        for sector, genders in sector_gender.items():
            if sum(genders.values()) > 10:  # Minimum 10 items pour être significatif
                sector_balance = self._calculate_distribution_balance(list(genders.values()))
                sector_biases[sector] = sector_balance
        
        # Score global (pénaliser les biais sectoriels)
        avg_sector_balance = np.mean(list(sector_biases.values())) if sector_biases else 1.0
        overall_score = (gender_balance + avg_sector_balance) / 2
        
        if overall_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Pas de biais de genre détecté ({overall_score:.1%})"
        elif overall_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Léger biais de genre possible ({overall_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Biais de genre détecté ({overall_score:.1%})"
        
        recommendations = []
        if overall_score < threshold:
            recommendations.append("Rééquilibrer la représentation de genre")
            if sector_biases:
                biased_sectors = [s for s, score in sector_biases.items() if score < 0.7]
                if biased_sectors:
                    recommendations.append(f"Secteurs avec biais: {', '.join(biased_sectors)}")
        
        return ValidationResult(
            rule_name="gender_bias_detection",
            status=status,
            score=overall_score,
            message=message,
            details={
                'gender_distribution': dict(gender_distribution),
                'sector_gender': dict(sector_gender),
                'sector_biases': sector_biases
            },
            recommendations=recommendations
        )
    
    def _validate_geographic_bias(self, data: List[Any], threshold: float) -> ValidationResult:
        """Détecte les biais géographiques."""
        location_distribution = defaultdict(int)
        
        for item in data:
            if hasattr(item, 'metadata') and item.metadata:
                location = item.metadata.get('location')
                if location:
                    location_distribution[location] += 1
        
        if not location_distribution:
            return ValidationResult(
                rule_name="geographic_bias_detection",
                status=ValidationStatus.WARNING,
                score=1.0,
                message="Aucune information géographique disponible"
            )
        
        # Calculer l'équilibre géographique
        location_values = list(location_distribution.values())
        geographic_balance = self._calculate_distribution_balance(location_values)
        
        # Vérifier la concentration (principe de Pareto)
        total_items = sum(location_values)
        sorted_counts = sorted(location_values, reverse=True)
        top_20_percent = int(np.ceil(len(sorted_counts) * 0.2))
        concentration = sum(sorted_counts[:top_20_percent]) / total_items
        
        # Score ajusté par la concentration
        concentration_penalty = 1 - max(0, concentration - 0.5) / 0.5  # Pénalité si > 50%
        adjusted_score = geographic_balance * concentration_penalty
        
        if adjusted_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Distribution géographique équilibrée ({adjusted_score:.1%})"
        elif adjusted_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Légère concentration géographique ({adjusted_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Biais géographique détecté ({adjusted_score:.1%})"
        
        recommendations = []
        if adjusted_score < threshold:
            recommendations.append("Améliorer la distribution géographique")
            if concentration > 0.6:
                recommendations.append("Réduire la concentration dans les zones principales")
        
        return ValidationResult(
            rule_name="geographic_bias_detection",
            status=status,
            score=adjusted_score,
            message=message,
            details={
                'location_distribution': dict(location_distribution),
                'concentration_ratio': concentration,
                'balance_score': geographic_balance
            },
            recommendations=recommendations
        )
    
    def _validate_educational_bias(self, cvs: List[CV], threshold: float) -> ValidationResult:
        """Détecte les biais éducationnels dans les CV."""
        education_levels = defaultdict(int)
        institutions = defaultdict(int)
        
        for cv in cvs:
            if hasattr(cv, 'education') and cv.education:
                for edu in cv.education:
                    if isinstance(edu, dict):
                        degree = edu.get('degree', '').lower()
                        institution = edu.get('institution', '')
                        
                        # Catégoriser les niveaux
                        if 'doctorat' in degree or 'phd' in degree:
                            education_levels['doctoral'] += 1
                        elif 'master' in degree or 'mba' in degree:
                            education_levels['master'] += 1
                        elif 'licence' in degree or 'bachelor' in degree:
                            education_levels['bachelor'] += 1
                        elif 'bts' in degree or 'dut' in degree:
                            education_levels['technical'] += 1
                        
                        if institution:
                            institutions[institution] += 1
        
        # Calculer l'équilibre des niveaux
        level_balance = self._calculate_distribution_balance(list(education_levels.values()))
        
        # Calculer la concentration institutionnelle
        inst_values = list(institutions.values())
        if inst_values:
            inst_balance = self._calculate_distribution_balance(inst_values)
            
            # Vérifier la sur-représentation des "grandes écoles"
            total_grads = sum(inst_values)
            prestigious = ['HEC', 'Polytechnique', 'INSEAD', 'Sciences Po']
            prestigious_count = sum(institutions.get(inst, 0) for inst in prestigious)
            prestigious_ratio = prestigious_count / total_grads if total_grads > 0 else 0
        else:
            inst_balance = 1.0
            prestigious_ratio = 0
        
        # Score global (pénaliser la sur-représentation des prestigieuses)
        prestige_penalty = 1 - max(0, prestigious_ratio - 0.3) / 0.7  # Pénalité si > 30%
        overall_score = (level_balance + inst_balance * prestige_penalty) / 2
        
        if overall_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Pas de biais éducationnel détecté ({overall_score:.1%})"
        elif overall_score >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Léger biais éducationnel possible ({overall_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Biais éducationnel détecté ({overall_score:.1%})"
        
        recommendations = []
        if overall_score < threshold:
            recommendations.append("Rééquilibrer les niveaux d'éducation")
            if prestigious_ratio > 0.4:
                recommendations.append("Réduire la sur-représentation des grandes écoles")
            if inst_balance < 0.7:
                recommendations.append("Diversifier les institutions représentées")
        
        return ValidationResult(
            rule_name="educational_bias_detection",
            status=status,
            score=overall_score,
            message=message,
            details={
                'education_levels': dict(education_levels),
                'institution_distribution': dict(institutions),
                'prestigious_ratio': prestigious_ratio,
                'level_balance': level_balance,
                'institution_balance': inst_balance
            },
            recommendations=recommendations
        )
    
    # === VALIDATEURS POUR VÉRITÉ TERRAIN ===
    
    def _validate_ground_truth_coverage(self, data: Tuple[List[MatchResult], List[CV], List[JobOffer]], threshold: float) -> ValidationResult:
        """Valide la couverture de la vérité terrain."""
        ground_truth, cvs, jobs = data
        
        if not ground_truth:
            return ValidationResult(
                rule_name="ground_truth_coverage",
                status=ValidationStatus.WARNING,
                score=0.0,
                message="Aucune vérité terrain fournie"
            )
        
        # Couverture des CV
        cv_ids = set(cv.id for cv in cvs)
        matched_cv_ids = set(match.candidate_id for match in ground_truth)
        cv_coverage = len(matched_cv_ids) / len(cv_ids) if cv_ids else 0
        
        # Couverture des jobs
        job_ids = set(job.id for job in jobs)
        matched_job_ids = set(match.job_id for match in ground_truth)
        job_coverage = len(matched_job_ids) / len(job_ids) if job_ids else 0
        
        # Couverture moyenne
        avg_coverage = (cv_coverage + job_coverage) / 2
        
        if avg_coverage >= threshold:
            status = ValidationStatus.PASSED
            message = f"Couverture satisfaisante ({avg_coverage:.1%})"
        elif avg_coverage >= threshold - 0.1:
            status = ValidationStatus.WARNING
            message = f"Couverture acceptable ({avg_coverage:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Couverture insuffisante ({avg_coverage:.1%})"
        
        recommendations = []
        if avg_coverage < threshold:
            recommendations.append("Augmenter le nombre de matches par item")
            if cv_coverage < job_coverage:
                recommendations.append("Améliorer la couverture des CV")
            else:
                recommendations.append("Améliorer la couverture des offres")
        
        return ValidationResult(
            rule_name="ground_truth_coverage",
            status=status,
            score=avg_coverage,
            message=message,
            details={
                'cv_coverage': cv_coverage,
                'job_coverage': job_coverage,
                'total_matches': len(ground_truth),
                'unique_cvs': len(matched_cv_ids),
                'unique_jobs': len(matched_job_ids)
            },
            recommendations=recommendations
        )
    
    def _validate_score_distribution(self, data: Tuple[List[MatchResult], List[CV], List[JobOffer]], threshold: float) -> ValidationResult:
        """Valide la distribution des scores de matching."""
        ground_truth, _, _ = data
        
        if not ground_truth:
            return ValidationResult(
                rule_name="ground_truth_score_distribution",
                status=ValidationStatus.WARNING,
                score=0.0,
                message="Aucune vérité terrain fournie"
            )
        
        scores = [match.score for match in ground_truth if match.score is not None]
        
        if not scores:
            return ValidationResult(
                rule_name="ground_truth_score_distribution",
                status=ValidationStatus.ERROR,
                score=0.0,
                message="Aucun score trouvé dans la vérité terrain"
            )
        
        # Analyses de distribution
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        score_range = max(scores) - min(scores)
        
        # Vérifier la distribution (doit couvrir une plage raisonnable)
        range_quality = min(1.0, score_range / 0.8)  # Optimal: plage de 0.8
        
        # Vérifier la moyenne (doit être raisonnable, ni trop haute ni trop basse)
        mean_quality = 1 - abs(mean_score - 0.6) / 0.4  # Optimal autour de 0.6
        mean_quality = max(0, mean_quality)
        
        # Vérifier la variance (ni trop uniforme ni trop dispersée)
        variance_quality = 1 - abs(std_score - 0.2) / 0.2  # Optimal autour de 0.2
        variance_quality = max(0, variance_quality)
        
        # Score global
        distribution_score = (range_quality + mean_quality + variance_quality) / 3
        
        if distribution_score >= threshold:
            status = ValidationStatus.PASSED
            message = f"Distribution des scores saine ({distribution_score:.1%})"
        elif distribution_score >= threshold - 0.1:
            status = ValidationStatus.WARNING 
            message = f"Distribution acceptable ({distribution_score:.1%})"
        else:
            status = ValidationStatus.FAILED
            message = f"Distribution problématique ({distribution_score:.1%})"
        
        recommendations = []
        if distribution_score < threshold:
            if score_range < 0.5:
                recommendations.append("Augmenter la plage des scores")
            if mean_score > 0.8:
                recommendations.append("Réduire les scores moyens (trop optimistes)")
            elif mean_score < 0.4:
                recommendations.append("Augmenter les scores moyens (trop pessimistes)")
            if std_score < 0.1:
                recommendations.append("Augmenter la variabilité des scores")
            elif std_score > 0.3:
                recommendations.append("Réduire la variabilité excessive")
        
        return ValidationResult(
            rule_name="ground_truth_score_distribution",
            status=status,
            score=distribution_score,
            message=message,
            details={
                'mean_score': mean_score,
                'std_score': std_score,
                'score_range': score_range,
                'min_score': min(scores),
                'max_score': max(scores),
                'score_count': len(scores)
            },
            recommendations=recommendations
        )
    
    # === MÉTHODES UTILITAIRES ===
    
    def _check_skills_experience_match(self, skills: List[str], experience: List[Any]) -> bool:
        """Vérifie la cohérence entre compétences et expérience."""
        if not experience:
            return True  # Pas d'expérience à vérifier
        
        # Extraction simple: si l'expérience contient certains mots-clés des compétences
        exp_text = " ".join([str(exp) for exp in experience]).lower()
        skill_matches = sum(1 for skill in skills if skill.lower() in exp_text)
        
        # Au moins 30% des compétences doivent être mentionnées dans l'expérience
        return skill_matches >= len(skills) * 0.3
    
    def _check_title_sector_consistency(self, title: str, sector: str) -> bool:
        """Vérifie la cohérence entre titre de poste et secteur."""
        title_lower = title.lower()
        sector_lower = sector.lower()
        
        # Règles basiques de cohérence
        sector_keywords = {
            'technology': ['developer', 'engineer', 'programmer', 'data', 'software', 'tech'],
            'finance': ['analyst', 'manager', 'advisor', 'banker', 'finance', 'investment'],
            'healthcare': ['doctor', 'nurse', 'medical', 'health', 'clinical', 'care'],
            'retail': ['sales', 'manager', 'associate', 'customer', 'retail', 'store'],
            'engineering': ['engineer', 'technical', 'design', 'project', 'quality']
        }
        
        expected_keywords = sector_keywords.get(sector_lower, [])
        return any(keyword in title_lower for keyword in expected_keywords)
    
    def _calculate_distribution_balance(self, values: List[int]) -> float:
        """Calcule l'équilibre d'une distribution (1 = parfaitement équilibrée)."""
        if not values or len(values) <= 1:
            return 1.0
        
        # Utiliser le coefficient de variation inversé
        mean_val = np.mean(values)
        if mean_val == 0:
            return 1.0
        
        cv = np.std(values) / mean_val  # Coefficient de variation
        balance = 1 / (1 + cv)  # Transformation pour avoir 1 = équilibré
        
        return min(1.0, balance)
    
    def _calculate_cv_metrics(self, cvs: List[CV], validation_results: List[ValidationResult]) -> QualityMetrics:
        """Calcule les métriques pour les CV."""
        # Scores par catégorie
        category_scores = defaultdict(list)
        for result in validation_results:
            rule = next((r for r in self.rules if r.name == result.rule_name), None)
            if rule:
                category_scores[rule.category].append(result.score)
        
        # Moyennes par catégorie
        avg_category_scores = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = np.mean(scores)
        
        # Métriques globales
        completeness_score = avg_category_scores.get('completeness', 0.8)
        consistency_score = avg_category_scores.get('consistency', 0.8)
        quality_score = avg_category_scores.get('quality', 0.8)
        bias_score = avg_category_scores.get('bias', 0.9)
        
        # Estimation de diversité basique
        diversity_score = self._estimate_cv_diversity(cvs)
        
        # Estimation de réalisme
        realism_score = (consistency_score + quality_score) / 2
        
        # Score global
        overall_score = np.mean([
            completeness_score, consistency_score, 
            quality_score, diversity_score, realism_score, bias_score
        ])
        
        # Collecter warnings et errors
        warnings = [r.message for r in validation_results if r.status == ValidationStatus.WARNING]
        errors = [r.message for r in validation_results if r.status == ValidationStatus.ERROR]
        
        return QualityMetrics(
            overall_score=overall_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            diversity_score=diversity_score,
            realism_score=realism_score, 
            bias_score=bias_score,
            category_scores=avg_category_scores,
            item_count=len(cvs),
            validation_results=validation_results,
            warnings=warnings,
            errors=errors
        )
    
    def _calculate_job_metrics(self, jobs: List[JobOffer], validation_results: List[ValidationResult]) -> QualityMetrics:
        """Calcule les métriques pour les offres d'emploi."""
        # Similaire à _calculate_cv_metrics mais adapté aux jobs
        category_scores = defaultdict(list)
        for result in validation_results:
            rule = next((r for r in self.rules if r.name == result.rule_name), None)
            if rule:
                category_scores[rule.category].append(result.score)
        
        avg_category_scores = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = np.mean(scores)
        
        completeness_score = avg_category_scores.get('completeness', 0.8)
        consistency_score = avg_category_scores.get('consistency', 0.8)
        quality_score = avg_category_scores.get('quality', 0.8)
        bias_score = avg_category_scores.get('bias', 0.9)
        
        diversity_score = self._estimate_job_diversity(jobs)
        realism_score = (consistency_score + quality_score) / 2
        
        overall_score = np.mean([
            completeness_score, consistency_score,
            quality_score, diversity_score, realism_score, bias_score
        ])
        
        warnings = [r.message for r in validation_results if r.status == ValidationStatus.WARNING]
        errors = [r.message for r in validation_results if r.status == ValidationStatus.ERROR]
        
        return QualityMetrics(
            overall_score=overall_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            diversity_score=diversity_score,
            realism_score=realism_score,
            bias_score=bias_score,
            category_scores=avg_category_scores,
            item_count=len(jobs),
            validation_results=validation_results,
            warnings=warnings,
            errors=errors
        )
    
    def _combine_validation_metrics(self,
                                   cv_metrics: QualityMetrics,
                                   job_metrics: QualityMetrics,
                                   dataset_results: List[ValidationResult]) -> QualityMetrics:
        """Combine les métriques CV et Job en métriques globales."""
        # Moyennes pondérées
        cv_weight = cv_metrics.item_count / (cv_metrics.item_count + job_metrics.item_count)
        job_weight = job_metrics.item_count / (cv_metrics.item_count + job_metrics.item_count)
        
        combined_completeness = cv_metrics.completeness_score * cv_weight + job_metrics.completeness_score * job_weight
        combined_consistency = cv_metrics.consistency_score * cv_weight + job_metrics.consistency_score * job_weight
        combined_quality = cv_metrics.realism_score * cv_weight + job_metrics.realism_score * job_weight
        combined_diversity = cv_metrics.diversity_score * cv_weight + job_metrics.diversity_score * job_weight
        combined_bias = cv_metrics.bias_score * cv_weight + job_metrics.bias_score * job_weight
        
        # Ajustements basés sur les résultats dataset
        dataset_adjustment = 1.0
        if dataset_results:
            dataset_scores = [r.score for r in dataset_results if r.score is not None]
            if dataset_scores:
                dataset_adjustment = np.mean(dataset_scores)
        
        # Score global ajusté
        combined_overall = np.mean([
            combined_completeness, combined_consistency, combined_quality,
            combined_diversity, combined_bias
        ]) * dataset_adjustment
        
        # Combiner tous les résultats de validation
        all_results = cv_metrics.validation_results + job_metrics.validation_results + dataset_results
        all_warnings = cv_metrics.warnings + job_metrics.warnings
        all_errors = cv_metrics.errors + job_metrics.errors
        
        return QualityMetrics(
            overall_score=combined_overall,
            completeness_score=combined_completeness,
            consistency_score=combined_consistency,
            diversity_score=combined_diversity,
            realism_score=combined_quality,
            bias_score=combined_bias,
            item_count=cv_metrics.item_count + job_metrics.item_count,
            validation_results=all_results,
            warnings=all_warnings,
            errors=all_errors
        )
    
    def _merge_ground_truth_metrics(self, base_metrics: QualityMetrics, gt_metrics: QualityMetrics) -> QualityMetrics:
        """Fusionne les métriques de vérité terrain avec les métriques de base."""
        # Pondération: 80% données de base, 20% vérité terrain
        adjusted_overall = base_metrics.overall_score * 0.8 + gt_metrics.overall_score * 0.2
        
        # Ajouter les résultats de validation de la vérité terrain
        combined_results = base_metrics.validation_results + gt_metrics.validation_results
        combined_warnings = base_metrics.warnings + gt_metrics.warnings
        combined_errors = base_metrics.errors + gt_metrics.errors
        
        # Créer les métriques fusionnées
        merged_metrics = QualityMetrics(
            overall_score=adjusted_overall,
            completeness_score=base_metrics.completeness_score,
            consistency_score=base_metrics.consistency_score,
            diversity_score=base_metrics.diversity_score,
            realism_score=base_metrics.realism_score,
            bias_score=base_metrics.bias_score,
            item_count=base_metrics.item_count,
            validation_results=combined_results,
            warnings=combined_warnings,
            errors=combined_errors
        )
        
        # Ajouter des métriques spécifiques à la vérité terrain
        merged_metrics.category_scores = base_metrics.category_scores.copy()
        merged_metrics.category_scores['ground_truth'] = gt_metrics.overall_score
        
        return merged_metrics
    
    def _calculate_ground_truth_metrics(self,
                                      ground_truth: List[MatchResult],
                                      cvs: List[CV],
                                      jobs: List[JobOffer],
                                      validation_results: List[ValidationResult]) -> QualityMetrics:
        """Calcule les métriques spécifiques à la vérité terrain."""
        category_scores = defaultdict(list)
        for result in validation_results:
            rule = next((r for r in self.rules if r.name == result.rule_name), None)
            if rule:
                category_scores[rule.category].append(result.score)
        
        avg_category_scores = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = np.mean(scores)
        
        # Score global pour la vérité terrain
        overall_score = np.mean(list(avg_category_scores.values())) if avg_category_scores else 0.8
        
        warnings = [r.message for r in validation_results if r.status == ValidationStatus.WARNING]
        errors = [r.message for r in validation_results if r.status == ValidationStatus.ERROR]
        
        return QualityMetrics(
            overall_score=overall_score,
            completeness_score=avg_category_scores.get('completeness', 0.8),
            consistency_score=avg_category_scores.get('consistency', 0.8),
            diversity_score=avg_category_scores.get('quality', 0.8),
            realism_score=avg_category_scores.get('quality', 0.8),
            bias_score=avg_category_scores.get('bias', 0.9),
            category_scores=avg_category_scores,
            item_count=len(ground_truth),
            validation_results=validation_results,
            warnings=warnings,
            errors=errors
        )
    
    def _estimate_cv_diversity(self, cvs: List[CV]) -> float:
        """Estime la diversité des CV."""
        if not cvs:
            return 0.0
        
        diversity_metrics = []
        
        # Diversité des compétences
        all_skills = set()
        for cv in cvs:
            if hasattr(cv, 'skills') and cv.skills:
                all_skills.update(cv.skills)
        
        if all_skills:
            avg_skills_per_cv = np.mean([len(set(cv.skills)) for cv in cvs if hasattr(cv, 'skills') and cv.skills])
            skill_diversity = min(1.0, avg_skills_per_cv / 10)  # Normaliser par rapport à 10 compétences
            diversity_metrics.append(skill_diversity)
        
        # Diversité des secteurs
        sectors = set()
        for cv in cvs:
            if hasattr(cv, 'metadata') and cv.metadata and 'sector' in cv.metadata:
                sectors.add(cv.metadata['sector'])
        
        if sectors:
            sector_diversity = min(1.0, len(sectors) / 5)  # Normaliser par rapport à 5 secteurs
            diversity_metrics.append(sector_diversity)
        
        # Diversité des expériences
        experience_years = []
        for cv in cvs:
            if hasattr(cv, 'metadata') and cv.metadata and 'experience_years' in cv.metadata:
                experience_years.append(cv.metadata['experience_years'])
        
        if experience_years:
            exp_std = np.std(experience_years)
            exp_diversity = min(1.0, exp_std / 5)  # Normaliser par rapport à std de 5 ans
            diversity_metrics.append(exp_diversity)
        
        return np.mean(diversity_metrics) if diversity_metrics else 0.5
    
    def _estimate_job_diversity(self, jobs: List[JobOffer]) -> float:
        """Estime la diversité des offres d'emploi."""
        if not jobs:
            return 0.0
        
        diversity_metrics = []
        
        # Diversité des entreprises
        companies = set()
        for job in jobs:
            if hasattr(job, 'company') and job.company:
                companies.add(job.company)
        
        if companies:
            company_diversity = min(1.0, len(companies) / max(10, len(jobs) // 2))
            diversity_metrics.append(company_diversity)
        
        # Diversité des titres
        titles = set()
        for job in jobs:
            if hasattr(job, 'title') and job.title:
                titles.add(job.title.lower())
        
        if titles:
            title_diversity = min(1.0, len(titles) / max(5, len(jobs) // 5))
            diversity_metrics.append(title_diversity)
        
        # Diversité des secteurs
        sectors = set()
        for job in jobs:
            if hasattr(job, 'metadata') and job.metadata and 'sector' in job.metadata:
                sectors.add(job.metadata['sector'])
        
        if sectors:
            sector_diversity = min(1.0, len(sectors) / 5)
            diversity_metrics.append(sector_diversity)
        
        return np.mean(diversity_metrics) if diversity_metrics else 0.5
    
    def _get_score_emoji(self, score: float) -> str:
        """Retourne un emoji basé sur le score."""
        if score >= 0.9:
            return "🌟"
        elif score >= 0.8:
            return "✅"
        elif score >= 0.7:
            return "👍"
        elif score >= 0.5:
            return "⚠️"
        else:
            return "❌"
    
    def _generate_improvement_suggestions(self, metrics: QualityMetrics) -> List[str]:
        """Génère des suggestions d'amélioration basées sur les métriques."""
        suggestions = []
        
        if metrics.completeness_score < 0.8:
            suggestions.append("Améliorer la complétude des champs obligatoires")
        
        if metrics.consistency_score < 0.7:
            suggestions.append("Vérifier la cohérence entre les différents champs")
        
        if metrics.diversity_score < 0.6:
            suggestions.append("Augmenter la diversité des données générées")
        
        if metrics.realism_score < 0.7:
            suggestions.append("Améliorer le réalisme des contenus synthétiques")
        
        if metrics.bias_score < 0.8:
            suggestions.append("Corriger les biais détectés dans la génération")
        
        # Suggestions spécifiques basées sur les erreurs
        error_count = len(metrics.errors)
        if error_count > 0:
            suggestions.append(f"Corriger les {error_count} erreurs critiques détectées")
        
        warning_count = len(metrics.warnings)
        if warning_count > 5:
            suggestions.append(f"Examiner les {warning_count} avertissements")
        
        return suggestions
    
    def _export_to_json(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Exporte les métriques au format JSON."""
        return {
            'overall_score': metrics.overall_score,
            'scores': {
                'completeness': metrics.completeness_score,
                'consistency': metrics.consistency_score,
                'diversity': metrics.diversity_score,
                'realism': metrics.realism_score,
                'bias': metrics.bias_score
            },
            'category_scores': metrics.category_scores,
            'validation_results': [
                {
                    'rule_name': r.rule_name,
                    'status': r.status.value,
                    'score': r.score,
                    'message': r.message,
                    'details': r.details,
                    'recommendations': r.recommendations
                }
                for r in metrics.validation_results
            ],
            'summary': {
                'item_count': metrics.item_count,
                'validation_timestamp': metrics.validation_timestamp.isoformat(),
                'warning_count': len(metrics.warnings),
                'error_count': len(metrics.errors)
            },
            'warnings': metrics.warnings,
            'errors': metrics.errors
        }
    
    def _export_to_csv(self, metrics: QualityMetrics) -> str:
        """Exporte les métriques au format CSV."""
        import io
        output = io.StringIO()
        
        # En-tête global
        output.write(f"Overall Score,{metrics.overall_score:.3f}\n")
        output.write(f"Item Count,{metrics.item_count}\n")
        output.write(f"Validation Date,{metrics.validation_timestamp}\n\n")
        
        # Scores par catégorie
        output.write("Category,Score\n")
        output.write(f"Completeness,{metrics.completeness_score:.3f}\n")
        output.write(f"Consistency,{metrics.consistency_score:.3f}\n")
        output.write(f"Diversity,{metrics.diversity_score:.3f}\n")
        output.write(f"Realism,{metrics.realism_score:.3f}\n")
        output.write(f"Bias,{metrics.bias_score:.3f}\n\n")
        
        # Résultats de validation
        output.write("Rule Name,Status,Score,Message\n")
        for result in metrics.validation_results:
            output.write(f"{result.rule_name},{result.status.value},{result.score:.3f},\"{result.message}\"\n")
        
        return output.getvalue()
    
    def _export_to_dict(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Exporte les métriques sous forme de dictionnaire."""
        return {
            'metrics': {
                'overall_score': metrics.overall_score,
                'completeness_score': metrics.completeness_score,
                'consistency_score': metrics.consistency_score,
                'diversity_score': metrics.diversity_score,
                'realism_score': metrics.realism_score,
                'bias_score': metrics.bias_score,
                'category_scores': metrics.category_scores
            },
            'validation_summary': {
                'total_rules': len(metrics.validation_results),
                'passed': len([r for r in metrics.validation_results if r.status == ValidationStatus.PASSED]),
                'warnings': len([r for r in metrics.validation_results if r.status == ValidationStatus.WARNING]),
                'failed': len([r for r in metrics.validation_results if r.status == ValidationStatus.FAILED]),
                'errors': len([r for r in metrics.validation_results if r.status == ValidationStatus.ERROR])
            },
            'metadata': {
                'item_count': metrics.item_count,
                'validation_timestamp': metrics.validation_timestamp,
                'warnings': metrics.warnings,
                'errors': metrics.errors
            }
        }
