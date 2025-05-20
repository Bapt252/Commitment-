from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..tracking.schema import EventType

class MatchingMetricsCalculator:
    def __init__(self, data_connector):
        self.data_connector = data_connector  # Connexion à la source de données
        
    async def calculate_acceptance_rate(self, period_days: int = 30) -> Dict[str, float]:
        """Calcule le taux d'acceptation des matchs proposés"""
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les matchs proposés
        proposed = await self.data_connector.count_events(
            event_type=EventType.MATCH_PROPOSED,
            since=since
        )
        
        # Récupérer les matchs acceptés
        accepted = await self.data_connector.count_events(
            event_type=EventType.MATCH_ACCEPTED,
            since=since
        )
        
        # Calculer le taux
        rate = accepted / proposed if proposed > 0 else 0
        
        return {
            "total_proposed": proposed,
            "total_accepted": accepted,
            "acceptance_rate": rate
        }
    
    async def calculate_satisfaction_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcule les métriques de satisfaction basées sur les feedbacks"""
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les événements de feedback
        feedbacks = await self.data_connector.get_events(
            event_type=EventType.MATCH_FEEDBACK,
            since=since
        )
        
        if not feedbacks:
            return {
                "avg_rating": None,
                "rating_counts": {},
                "total_feedbacks": 0
            }
        
        # Extraire les ratings
        ratings = [f.rating.value for f in feedbacks]
        
        # Calculer les métriques
        avg_rating = sum(ratings) / len(ratings)
        
        # Compter par niveau de rating
        rating_counts = {}
        for r in range(1, 6):
            rating_counts[r] = ratings.count(r)
            
        return {
            "avg_rating": avg_rating,
            "rating_counts": rating_counts,
            "total_feedbacks": len(feedbacks)
        }
    
    async def calculate_engagement_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcule les métriques d'engagement suite aux matchs"""
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les événements de complétion
        completions = await self.data_connector.get_events(
            event_type=EventType.MATCH_COMPLETED,
            since=since
        )
        
        # Récupérer les événements d'abandon
        abandonments = await self.data_connector.get_events(
            event_type=EventType.MATCH_ABANDONED,
            since=since
        )
        
        # Calculer le taux de complétion
        total_matches = len(completions) + len(abandonments)
        completion_rate = len(completions) / total_matches if total_matches > 0 else 0
        
        # Calculer les durées d'engagement
        durations = [c.duration_days for c in completions]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "completion_rate": completion_rate,
            "total_completed": len(completions),
            "total_abandoned": len(abandonments),
            "avg_engagement_duration": avg_duration
        }
    
    async def calculate_matching_efficiency(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcule l'efficacité globale du système de matching"""
        # Récupérer les métriques individuelles
        acceptance = await self.calculate_acceptance_rate(period_days)
        satisfaction = await self.calculate_satisfaction_metrics(period_days)
        engagement = await self.calculate_engagement_metrics(period_days)
        
        # Calculer un score global d'efficacité
        # Exemple de formule: 0.3*acceptance + 0.4*satisfaction + 0.3*engagement
        acceptance_score = acceptance["acceptance_rate"]
        satisfaction_score = (satisfaction["avg_rating"] - 1) / 4 if satisfaction["avg_rating"] else 0
        engagement_score = engagement["completion_rate"]
        
        overall_efficiency = (
            0.3 * acceptance_score +
            0.4 * satisfaction_score +
            0.3 * engagement_score
        )
        
        return {
            "overall_efficiency": overall_efficiency,
            "acceptance_metrics": acceptance,
            "satisfaction_metrics": satisfaction,
            "engagement_metrics": engagement
        }
    
    async def calculate_constraint_satisfaction_impact(self, period_days: int = 30) -> Dict[str, Any]:
        """Analyse l'impact de la satisfaction des contraintes sur l'acceptation"""
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les événements de proposition avec leurs contraintes
        proposed_events = await self.data_connector.get_events(
            event_type=EventType.MATCH_PROPOSED,
            since=since
        )
        
        if not proposed_events:
            return {"impact_analysis": {}, "total_matches": 0}
            
        # Récupérer les IDs des matchs acceptés
        accepted_match_ids = await self.data_connector.get_accepted_match_ids(since)
        
        # Analyser l'impact de chaque contrainte
        constraint_impact = {}
        
        # Extraire toutes les contraintes uniques
        all_constraints = set()
        for event in proposed_events:
            all_constraints.update(event.constraint_satisfaction.keys())
            
        # Pour chaque contrainte, analyser son impact
        for constraint in all_constraints:
            # Diviser les matchs en quartiles basés sur le niveau de satisfaction de cette contrainte
            constraint_values = []
            match_accepted = []
            
            for event in proposed_events:
                if constraint in event.constraint_satisfaction:
                    constraint_values.append(event.constraint_satisfaction[constraint])
                    match_accepted.append(1 if event.match_id in accepted_match_ids else 0)
            
            if not constraint_values:
                continue
                
            # Convertir en DataFrame pour l'analyse
            df = pd.DataFrame({
                'constraint_value': constraint_values,
                'accepted': match_accepted
            })
            
            # Diviser en quartiles
            df['quartile'] = pd.qcut(df['constraint_value'], 4, labels=False)
            
            # Calculer le taux d'acceptation par quartile
            quartile_rates = df.groupby('quartile')['accepted'].mean().to_dict()
            
            # Calculer la corrélation
            correlation = df['constraint_value'].corr(df['accepted'])
            
            constraint_impact[constraint] = {
                'quartile_acceptance_rates': quartile_rates,
                'correlation': correlation
            }
            
        return {
            "impact_analysis": constraint_impact,
            "total_matches": len(proposed_events)
        }