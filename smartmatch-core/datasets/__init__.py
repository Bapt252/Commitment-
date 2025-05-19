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
    DatasetConfig
)

from .behavior_simulator import (
    BehaviorSimulator,
    UserAction,
    InteractionPattern,
    SimulationResult
)

from .validator import (
    DataValidator,
    ValidationResult,
    ValidationRule,
    QualityMetrics
)

__all__ = [
    # Synthetic data generation
    'SyntheticDataGenerator',
    'CVGenerator', 
    'JobOfferGenerator',
    'DatasetConfig',
    
    # Behavior simulation
    'BehaviorSimulator',
    'UserAction',
    'InteractionPattern', 
    'SimulationResult',
    
    # Data validation
    'DataValidator',
    'ValidationResult',
    'ValidationRule',
    'QualityMetrics'
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


def create_behavior_simulation(users, actions_per_user=50, seed=42):
    """
    Crée une simulation de comportement utilisateur.
    
    Args:
        users: Liste des utilisateurs
        actions_per_user: Nombre d'actions par utilisateur
        seed: Seed pour reproductibilité
        
    Returns:
        SimulationResult avec historique d'actions
    """
    import random
    random.seed(seed)
    
    simulator = BehaviorSimulator()
    return simulator.simulate_user_behavior(users, actions_per_user)


def validate_dataset_quality(cvs, jobs, ground_truth=None):
    """
    Valide la qualité d'un dataset.
    
    Args:
        cvs: Liste des CV
        jobs: Liste des offres d'emploi
        ground_truth: Vérité terrain optionnelle
        
    Returns:
        ValidationResult avec métriques de qualité
    """
    validator = DataValidator()
    return validator.validate_full_dataset(cvs, jobs, ground_truth)
