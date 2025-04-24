from typing import List, Dict, Any
from datetime import datetime
from app.services.experiment_manager import ExperimentManager
from app.services.matching_algorithm_factory import MatchingAlgorithmFactory
from app.services.metrics_collector import MetricsCollector
from app.models.match import MatchResult

class MatchingService:
    def __init__(self, db_session, redis_conn):
        self.db = db_session
        self.redis = redis_conn
        self.experiment_manager = ExperimentManager(db_session)
        self.algorithm_factory = MatchingAlgorithmFactory()
        self.metrics_collector = MetricsCollector(db_session)
    
    async def get_matches(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtenir les matches pour un utilisateur avec A/B testing"""
        # Trouver l'expérience active
        active_experiment = self.experiment_manager.get_active_experiment()
        
        if not active_experiment:
            # Utiliser l'algorithme par défaut
            matches = await self.algorithm_factory.get_algorithm('default').find_matches(user_id)
            algorithm_version = 'default'
        else:
            # Affecter l'utilisateur à une variante
            variant = self.experiment_manager.assign_user_to_variant(user_id)
            
            # Déterminer l'algorithme à utiliser
            if variant == 'control':
                algorithm_name = 'default'
            else:
                variant_config = next(
                    v for v in active_experiment.traffic_allocation['variants'] 
                    if v['name'] == variant
                )
                algorithm_name = variant_config['algorithm']
            
            # Exécuter l'algorithme
            matches = await self.algorithm_factory.get_algorithm(algorithm_name).find_matches(user_id)
            algorithm_version = f"{variant}:{algorithm_name}"
            
            # Collecter les métriques
            await self.metrics_collector.record_matching_event({
                'user_id': user_id,
                'experiment_id': active_experiment.id,
                'variant': variant,
                'match_count': len(matches),
                'timestamp': datetime.utcnow()
            })
        
        # Sauvegarder les résultats
        for match in matches:
            match_result = MatchResult(
                user_id=user_id,
                matched_id=match['id'],
                score=match['score'],
                algorithm_version=algorithm_version,
                created_at=datetime.utcnow()
            )
            self.db.add(match_result)
        
        self.db.commit()
        return matches