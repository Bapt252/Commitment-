from typing import Dict, Optional, List
from datetime import datetime
import hashlib
from sqlalchemy import and_
from app.models.experiment import Experiment
from app.database import db_session

class ExperimentManager:
    def __init__(self, db_session):
        self.db = db_session
    
    def create_experiment(self, config: Dict) -> Experiment:
        """Créer une nouvelle expérience"""
        # Valider la configuration
        self._validate_traffic_allocation(config['traffic_allocation'])
        
        experiment = Experiment(
            name=config['name'],
            description=config.get('description'),
            status='draft',
            start_date=config['start_date'],
            end_date=config.get('end_date'),
            traffic_allocation=config['traffic_allocation'],
            metrics=config.get('metrics', ['match_count', 'feedback_score'])
        )
        
        self.db.add(experiment)
        self.db.commit()
        return experiment
    
    def assign_user_to_variant(self, user_id: int, experiment_id: Optional[int] = None) -> str:
        """Affecter un utilisateur à une variante de manière déterministe"""
        if experiment_id is None:
            experiment = self.get_active_experiment()
            if not experiment:
                return 'control'
            experiment_id = experiment.id
        else:
            experiment = self.db.query(Experiment).filter_by(id=experiment_id).first()
        
        if not experiment or experiment.status != 'running':
            return 'control'
        
        # Générer un hash stable
        hash_input = f"{user_id}-{experiment_id}"
        hash_value = int(hashlib.sha1(hash_input.encode()).hexdigest(), 16)
        percentage = hash_value % 100
        
        # Déterminer la variante
        traffic = experiment.traffic_allocation
        if percentage < traffic['control']:
            return 'control'
        
        cumulative = traffic['control']
        for variant in traffic['variants']:
            cumulative += variant['percentage']
            if percentage < cumulative:
                return variant['name']
        
        return 'control'  # Fallback
    
    def get_active_experiment(self) -> Optional[Experiment]:
        """Récupérer l'expérience active"""
        now = datetime.utcnow()
        return self.db.query(Experiment).filter(
            and_(
                Experiment.status == 'running',
                Experiment.start_date <= now,
                (Experiment.end_date.is_(None) | (Experiment.end_date > now))
            )
        ).first()
    
    def pause_experiment(self, experiment_id: int) -> bool:
        """Mettre en pause une expérience"""
        experiment = self.db.query(Experiment).filter_by(id=experiment_id).first()
        if experiment and experiment.status == 'running':
            experiment.status = 'paused'
            self.db.commit()
            return True
        return False
    
    def _validate_traffic_allocation(self, traffic_allocation: Dict) -> None:
        """Valider que l'allocation de trafic totalise 100%"""
        total = traffic_allocation.get('control', 0)
        for variant in traffic_allocation.get('variants', []):
            total += variant['percentage']
        
        if total != 100:
            raise ValueError(f"Traffic allocation must sum to 100%, currently {total}%")