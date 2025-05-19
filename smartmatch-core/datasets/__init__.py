"""
Module de génération de datasets synthétiques pour tests et entraînement.

Ce module fournit:
- Générateur de CV et offres d'emploi synthétiques
- Simulateur de comportement utilisateur
- Validateur de données générées
- Datasets pour benchmarking et tests
"""

from .synthetic_generator import (
    SyntheticDataGenerator,
    CVGenerator,
    JobOfferGenerator,
    DatasetConfig,
    GenerationQuality
)

from .behavior_simulator import (
    BehaviorSimulator,
    UserAction,
    InteractionPattern,
    SimulationResult,
    ActionType,
    UserType
)

from .validator import (
    DataValidator,
    ValidationResult,
    ValidationRule,
    QualityMetrics,
    ValidationLevel,
    ValidationStatus
)

__all__ = [
    # Synthetic data generation
    'SyntheticDataGenerator',
    'CVGenerator', 
    'JobOfferGenerator',
    'DatasetConfig',
    'GenerationQuality',
    
    # Behavior simulation
    'BehaviorSimulator',
    'UserAction',
    'InteractionPattern', 
    'SimulationResult',
    'ActionType',
    'UserType',
    
    # Data validation
    'DataValidator',
    'ValidationResult',
    'ValidationRule',
    'QualityMetrics',
    'ValidationLevel',
    'ValidationStatus'
]

# Configuration par défaut
DEFAULT_DATASET_CONFIG = {
    'num_cvs': 1000,
    'num_jobs': 500,
    'diversity_enabled': True,
    'bias_injection': False,
    'language': 'fr',
    'sectors': ['tech', 'finance', 'retail', 'healthcare', 'engineering'],
    'quality_level': 'high'  # 'low', 'medium', 'high'
}


def create_synthetic_dataset(config=None, seed=42):
    """
    Crée un dataset synthétique complet.
    
    Args:
        config: Configuration du dataset
        seed: Seed pour reproductibilité
        
    Returns:
        Tuple (cvs, jobs, ground_truth_matches)
    """
    import random
    import numpy as np
    
    # Set seed pour reproductibilité
    random.seed(seed)
    np.random.seed(seed)
    
    config = config or DEFAULT_DATASET_CONFIG
    
    generator = SyntheticDataGenerator(config)
    cvs = generator.generate_cvs(config['num_cvs'])
    jobs = generator.generate_jobs(config['num_jobs'])
    
    # Générer une vérité terrain pour les matches
    ground_truth = generator.generate_ground_truth_matches(cvs, jobs)
    
    return cvs, jobs, ground_truth


def create_behavior_simulation(users, actions_per_user=50, seed=42, duration_days=7):
    """
    Crée une simulation de comportement utilisateur.
    
    Args:
        users: Liste des utilisateurs
        actions_per_user: Nombre d'actions par utilisateur
        seed: Seed pour reproductibilité
        duration_days: Durée de simulation en jours
        
    Returns:
        SimulationResult avec historique d'actions
    """
    import random
    random.seed(seed)
    
    # Créer des données factices pour la simulation si nécessaire
    fake_data = [{'id': f'item_{i}', 'type': 'cv'} for i in range(100)]
    
    simulator = BehaviorSimulator()
    return simulator.simulate_user_behavior(users, fake_data, duration_days, actions_per_user)


def validate_dataset_quality(cvs, jobs, ground_truth=None, validation_level='standard'):
    """
    Valide la qualité d'un dataset.
    
    Args:
        cvs: Liste des CV
        jobs: Liste des offres d'emploi
        ground_truth: Vérité terrain optionnelle
        validation_level: Niveau de validation ('basic', 'standard', 'strict')
        
    Returns:
        ValidationResult avec métriques de qualité
    """
    level_map = {
        'basic': ValidationLevel.BASIC,
        'standard': ValidationLevel.STANDARD, 
        'strict': ValidationLevel.STRICT
    }
    
    validator = DataValidator(level_map.get(validation_level, ValidationLevel.STANDARD))
    return validator.validate_full_dataset(cvs, jobs, ground_truth)


def run_ab_test_simulation(group_a_config, group_b_config, test_duration_days=14, seed=42):
    """
    Lance une simulation de test A/B complète.
    
    Args:
        group_a_config: Configuration pour le groupe de contrôle
        group_b_config: Configuration pour le groupe de test
        test_duration_days: Durée du test en jours
        seed: Seed pour reproductibilité
        
    Returns:
        Dict avec résultats pour chaque groupe et analyse comparative
    """
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    
    # Générer les utilisateurs pour chaque groupe
    group_a_users = [
        {'id': f'user_a_{i}', 'type': 'candidate', 'experience_level': random.choice(['junior', 'mid', 'senior'])}
        for i in range(group_a_config.get('num_users', 100))
    ]
    
    group_b_users = [
        {'id': f'user_b_{i}', 'type': 'candidate', 'experience_level': random.choice(['junior', 'mid', 'senior'])}
        for i in range(group_b_config.get('num_users', 100))
    ]
    
    # Générer les données communes
    dataset_config = DatasetConfig(
        num_cvs=group_a_config.get('num_cvs', 500),
        num_jobs=group_b_config.get('num_jobs', 250),
        seed=seed
    )
    generator = SyntheticDataGenerator(dataset_config)
    cvs = generator.generate_cvs()
    jobs = generator.generate_jobs()
    
    # Simuler le comportement pour les deux groupes
    simulator = BehaviorSimulator()
    results = simulator.simulate_ab_test_behavior(
        group_a_users,
        group_b_users, 
        cvs + jobs,  # Données combinées pour simulation
        test_duration_days
    )
    
    # Ajouter une analyse comparative basique
    results['comparison'] = _compare_ab_results(results['group_a'], results['group_b'])
    
    return results


def _compare_ab_results(result_a, result_b):
    """Compare les résultats de deux groupes A/B."""
    comparison = {
        'total_actions': {
            'group_a': result_a.total_actions,
            'group_b': result_b.total_actions,
            'difference': result_b.total_actions - result_a.total_actions,
            'relative_change': (result_b.total_actions - result_a.total_actions) / result_a.total_actions if result_a.total_actions > 0 else 0
        },
        'engagement_metrics': {},
        'quality_scores': {
            'group_a': result_a.quality_metrics.get('overall_quality', 0),
            'group_b': result_b.quality_metrics.get('overall_quality', 0)
        }
    }
    
    # Comparer les types d'actions
    for action_type in result_a.actions_by_type:
        a_count = result_a.actions_by_type.get(action_type, 0)
        b_count = result_b.actions_by_type.get(action_type, 0)
        
        comparison['engagement_metrics'][action_type.value] = {
            'group_a': a_count,
            'group_b': b_count,
            'difference': b_count - a_count,
            'relative_change': (b_count - a_count) / a_count if a_count > 0 else 0
        }
    
    return comparison


def generate_quality_report(cvs, jobs, ground_truth=None, include_behavior_sim=True):
    """
    Génère un rapport de qualité complet pour un dataset.
    
    Args:
        cvs: Liste des CV
        jobs: Liste des offres d'emploi
        ground_truth: Vérité terrain optionnelle
        include_behavior_sim: Inclure une simulation de comportement
        
    Returns:
        Dict avec rapport complet et métriques
    """
    # Validation du dataset
    metrics = validate_dataset_quality(cvs, jobs, ground_truth, 'standard')
    
    report = {
        'validation_metrics': metrics,
        'text_report': DataValidator().generate_validation_report(metrics),
        'dataset_summary': {
            'cv_count': len(cvs),
            'job_count': len(jobs),
            'ground_truth_matches': len(ground_truth) if ground_truth else 0,
            'validation_timestamp': metrics.validation_timestamp,
            'overall_quality_score': metrics.overall_score
        }
    }
    
    # Simulation de comportement optionnelle
    if include_behavior_sim:
        # Créer des utilisateurs factices
        sample_users = [
            {'id': f'user_{i}', 'type': random.choice(['candidate', 'recruiter'])}
            for i in range(min(50, max(10, (len(cvs) + len(jobs)) // 20)))
        ]
        
        sim_result = create_behavior_simulation(sample_users, actions_per_user=25, duration_days=3)
        
        report['behavior_simulation'] = {
            'total_actions': sim_result.total_actions,
            'actions_by_type': {at.value: count for at, count in sim_result.actions_by_type.items()},
            'summary_stats': sim_result.summary_stats,
            'quality_metrics': sim_result.quality_metrics
        }
    
    return report


def export_dataset_package(cvs, jobs, ground_truth=None, output_format='json', include_validation=True):
    """
    Exporte un package complet de dataset avec toutes les métadonnées.
    
    Args:
        cvs: Liste des CV
        jobs: Liste des offres d'emploi  
        ground_truth: Vérité terrain optionnelle
        output_format: Format d'export ('json', 'csv', 'pickle')
        include_validation: Inclure un rapport de validation
        
    Returns:
        Dict ou string selon le format choisi
    """
    package = {
        'metadata': {
            'creation_timestamp': datetime.now().isoformat(),
            'cv_count': len(cvs),
            'job_count': len(jobs),
            'ground_truth_count': len(ground_truth) if ground_truth else 0,
            'format_version': '1.0',
            'generator_info': 'Commitment- Session 5 Synthetic Data Generator'
        },
        'data': {
            'cvs': cvs,
            'jobs': jobs,
            'ground_truth': ground_truth
        }
    }
    
    # Ajouter la validation si demandée
    if include_validation:
        metrics = validate_dataset_quality(cvs, jobs, ground_truth)
        package['validation'] = DataValidator().export_validation_metrics(metrics, output_format)
    
    if output_format == 'json':
        import json
        # Sérialisation JSON custom pour gérer les objets complexes
        return json.dumps(package, default=str, indent=2)
    elif output_format == 'pickle':
        import pickle
        return pickle.dumps(package)
    else:  # dict par défaut
        return package
