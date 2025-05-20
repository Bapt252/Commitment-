from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3
import json
import pandas as pd
import logging
from ..tracking.schema import EventType

logger = logging.getLogger(__name__)

class MatchingMetricsCalculator:
    def __init__(self, db_path: str = 'data/tracking.db'):
        self.db_path = db_path
        
    def calculate_acceptance_rate(self, period_days: int = 30) -> Dict[str, float]:
        """Calcule le taux d'acceptation des matchs proposés"""
        since = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les matchs proposés
            cursor.execute(
                "SELECT COUNT(*) FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_PROPOSED.value, since)
            )
            proposed = cursor.fetchone()[0]
            
            # Récupérer les matchs acceptés
            cursor.execute(
                "SELECT COUNT(*) FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_ACCEPTED.value, since)
            )
            accepted = cursor.fetchone()[0]
            
            # Calculer le taux
            rate = accepted / proposed if proposed > 0 else 0
            
            return {
                "total_proposed": proposed,
                "total_accepted": accepted,
                "acceptance_rate": rate
            }
        except Exception as e:
            logger.error(f"Error calculating acceptance rate: {str(e)}")
            return {
                "total_proposed": 0,
                "total_accepted": 0,
                "acceptance_rate": 0
            }
        finally:
            conn.close()
    
    def calculate_satisfaction_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcule les métriques de satisfaction basées sur les feedbacks"""
        since = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les événements de feedback
            cursor.execute(
                "SELECT data FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_FEEDBACK.value, since)
            )
            feedbacks = cursor.fetchall()
            
            if not feedbacks:
                return {
                    "avg_rating": None,
                    "rating_counts": {},
                    "total_feedbacks": 0
                }
            
            # Extraire les ratings
            ratings = []
            for fb in feedbacks:
                data = json.loads(fb[0])
                if 'rating' in data:
                    ratings.append(data['rating'])
            
            # Calculer les métriques
            avg_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Compter par niveau de rating
            rating_counts = {}
            for r in range(1, 6):
                rating_counts[r] = ratings.count(r)
                
            return {
                "avg_rating": avg_rating,
                "rating_counts": rating_counts,
                "total_feedbacks": len(feedbacks)
            }
        except Exception as e:
            logger.error(f"Error calculating satisfaction metrics: {str(e)}")
            return {
                "avg_rating": None,
                "rating_counts": {},
                "total_feedbacks": 0
            }
        finally:
            conn.close()
    
    def calculate_constraint_impact(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcule l'impact des contraintes sur l'acceptation des matchs"""
        since = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les propositions de match avec leurs contraintes
            cursor.execute(
                "SELECT match_id, data FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_PROPOSED.value, since)
            )
            proposed = cursor.fetchall()
            
            # Récupérer les IDs des matchs acceptés
            cursor.execute(
                "SELECT match_id FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.MATCH_ACCEPTED.value, since)
            )
            accepted_ids = [row[0] for row in cursor.fetchall()]
            
            if not proposed:
                return {
                    "constraints": {},
                    "total_matches": 0
                }
            
            # Analyser l'impact des contraintes
            constraints_data = {}
            all_constraints = set()
            
            for match_id, data_json in proposed:
                data = json.loads(data_json)
                if 'constraint_satisfaction' in data:
                    for constraint, value in data['constraint_satisfaction'].items():
                        all_constraints.add(constraint)
                        if constraint not in constraints_data:
                            constraints_data[constraint] = []
                        
                        # Ajouter une paire (valeur de satisfaction, acceptation)
                        is_accepted = match_id in accepted_ids
                        constraints_data[constraint].append((value, 1 if is_accepted else 0))
            
            # Calculer les corrélations pour chaque contrainte
            impact = {}
            for constraint, values in constraints_data.items():
                if len(values) > 5:  # Besoin d'un minimum d'échantillons
                    df = pd.DataFrame(values, columns=['satisfaction', 'accepted'])
                    correlation = df['satisfaction'].corr(df['accepted'])
                    impact[constraint] = {
                        'correlation': correlation,
                        'sample_size': len(values),
                        'avg_satisfaction': df['satisfaction'].mean()
                    }
            
            return {
                "constraints": impact,
                "total_matches": len(proposed)
            }
        except Exception as e:
            logger.error(f"Error calculating constraint impact: {str(e)}")
            return {
                "constraints": {},
                "total_matches": 0
            }
        finally:
            conn.close()