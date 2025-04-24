from app.services.matching_algorithm_factory import MatchingAlgorithmFactory
from app.services.custom_algorithms import ImprovedMatchingAlgorithm, MLBasedMatchingAlgorithm

def init_ab_testing(app):
    """Initialiser le système A/B testing"""
    # Enregistrer le blueprint des expériences
    from app.api.experiments import experiments_bp
    app.register_blueprint(experiments_bp)
    
    # Initialiser la factory d'algorithmes
    algorithm_factory = MatchingAlgorithmFactory()
    algorithm_factory.register_algorithm('improved_v1', ImprovedMatchingAlgorithm())
    algorithm_factory.register_algorithm('ml_based', MLBasedMatchingAlgorithm())
    
    return algorithm_factory