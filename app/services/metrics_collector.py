from typing import Dict, Any, List
from sqlalchemy import func
from scipy import stats
import numpy as np
from app.models.experiment import ExperimentMetric

class MetricsCollector:
    def __init__(self, db_session):
        self.db = db_session
    
    async def record_matching_event(self, metric_data: Dict[str, Any]) -> None:
        """Enregistrer un événement de matching"""
        metric = ExperimentMetric(
            experiment_id=metric_data['experiment_id'],
            user_id=metric_data['user_id'],
            variant=metric_data['variant'],
            match_count=metric_data.get('match_count', 0),
            timestamp=metric_data['timestamp']
        )
        self.db.add(metric)
        self.db.commit()
    
    async def record_user_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> None:
        """Enregistrer le feedback utilisateur"""
        metric = self.db.query(ExperimentMetric).filter_by(
            user_id=user_id,
            experiment_id=feedback_data['experiment_id']
        ).order_by(ExperimentMetric.timestamp.desc()).first()
        
        if metric:
            metric.feedback_score = feedback_data.get('score')
            metric.conversion_count = feedback_data.get('conversions', 0)
            self.db.commit()
    
    async def analyze_experiment(self, experiment_id: int) -> Dict[str, Any]:
        """Analyser les résultats d'une expérience"""
        metrics = self.db.query(ExperimentMetric).filter_by(experiment_id=experiment_id).all()
        
        # Grouper par variante
        variant_data = {}
        for metric in metrics:
            if metric.variant not in variant_data:
                variant_data[metric.variant] = {
                    'match_counts': [],
                    'feedback_scores': [],
                    'conversion_counts': [],
                    'user_count': 0
                }
            
            variant_data[metric.variant]['match_counts'].append(metric.match_count)
            if metric.feedback_score is not None:
                variant_data[metric.variant]['feedback_scores'].append(metric.feedback_score)
            if metric.conversion_count is not None:
                variant_data[metric.variant]['conversion_counts'].append(metric.conversion_count)
            variant_data[metric.variant]['user_count'] += 1
        
        # Calculer les statistiques
        results = {}
        control_feedback = variant_data.get('control', {}).get('feedback_scores', [])
        
        for variant, data in variant_data.items():
            results[variant] = {
                'user_count': data['user_count'],
                'avg_match_count': np.mean(data['match_counts']) if data['match_counts'] else 0,
                'avg_feedback_score': np.mean(data['feedback_scores']) if data['feedback_scores'] else 0,
                'avg_conversion_rate': np.mean(data['conversion_counts']) / data['user_count'] if data['user_count'] > 0 else 0
            }
            
            # Calcul de la signification statistique vs contrôle
            if variant != 'control' and control_feedback and data['feedback_scores']:
                t_stat, p_value = stats.ttest_ind(control_feedback, data['feedback_scores'])
                results[variant]['significance'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'is_significant': p_value < 0.05
                }
        
        return results