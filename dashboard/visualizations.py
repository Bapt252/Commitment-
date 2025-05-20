from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import json

class DashboardVisualizer:
    def __init__(self, data_connector):
        self.data_connector = data_connector
        
    async def generate_acceptance_rate_chart(self, period_days: int = 30, interval_days: int = 1) -> Dict[str, Any]:
        """Génère les données pour un graphique de taux d'acceptation au fil du temps"""
        # Définir la période
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Générer des intervalles de temps
        intervals = []
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timedelta(days=interval_days)
            intervals.append((current_date, next_date))
            current_date = next_date
            
        # Collecter les données pour chaque intervalle
        data_points = []
        for start, end in intervals:
            # Récupérer les matchs proposés pour cet intervalle
            proposed = await self.data_connector.count_events(
                event_type="match_proposed", 
                start_date=start,
                end_date=end
            )
            
            # Récupérer les matchs acceptés pour cet intervalle
            accepted = await self.data_connector.count_events(
                event_type="match_accepted", 
                start_date=start,
                end_date=end
            )
            
            # Calculer le taux d'acceptation
            rate = (accepted / proposed) * 100 if proposed > 0 else 0
            
            data_points.append({
                "date": start.strftime("%Y-%m-%d"),
                "proposed": proposed,
                "accepted": accepted,
                "acceptance_rate": rate
            })
            
        return {
            "chart_type": "line",
            "data": data_points,
            "labels": {
                "x": "Date",
                "y": "Taux d'acceptation (%)"
            }
        }
        
    async def generate_feedback_distribution_chart(self, period_days: int = 30) -> Dict[str, Any]:
        """Génère les données pour un graphique de distribution des feedbacks"""
        # Définir la période
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les événements de feedback
        feedback_events = await self.data_connector.get_events(
            event_type="match_feedback",
            since=since
        )
        
        # Compter les feedbacks par rating
        rating_counts = {i: 0 for i in range(1, 6)}
        for event in feedback_events:
            rating = event.get("rating")
            if rating is not None:
                rating_counts[rating] += 1
                
        # Formater pour le graphique
        data_points = [
            {"rating": f"{i} - {rating_label(i)}", "count": count}
            for i, count in rating_counts.items()
        ]
        
        return {
            "chart_type": "bar",
            "data": data_points,
            "labels": {
                "x": "Evaluation",
                "y": "Nombre de feedbacks"
            }
        }
        
    async def generate_constraint_impact_chart(self, period_days: int = 30) -> Dict[str, Any]:
        """Génère les données pour un graphique d'impact des contraintes"""
        from ..analysis.metrics_calculator import MatchingMetricsCalculator
        
        # Utiliser le calculateur de métriques
        metrics_calculator = MatchingMetricsCalculator(self.data_connector)
        impact_data = await metrics_calculator.calculate_constraint_satisfaction_impact(period_days)
        
        # Transformer les données pour le graphique
        data_points = []
        for constraint, impact in impact_data["impact_analysis"].items():
            correlation = impact["correlation"]
            data_points.append({
                "constraint": constraint,
                "correlation": correlation,
                "importance": abs(correlation)
            })
            
        # Trier par importance
        data_points.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "chart_type": "bar",
            "data": data_points[:10],  # Top 10 contraintes
            "labels": {
                "x": "Contrainte",
                "y": "Corrélation avec l'acceptation"
            }
        }
        
    async def generate_rating_trend_chart(self, period_days: int = 90, interval_days: int = 7) -> Dict[str, Any]:
        """Génère les données pour un graphique d'évolution des ratings"""
        from ..analysis.feedback_analyzer import FeedbackAnalyzer
        
        # Utiliser l'analyseur de feedback
        analyzer = FeedbackAnalyzer(self.data_connector)
        trends_data = await analyzer.analyze_rating_trends(period_days, interval_days)
        
        # Transformer les données pour le graphique
        data_points = []
        for trend in trends_data["trends"]:
            if trend["avg_rating"] is not None:
                data_points.append({
                    "start_date": trend["interval_start"].split("T")[0],  # Juste la date
                    "avg_rating": trend["avg_rating"],
                    "count": trend["count"]
                })
                
        return {
            "chart_type": "line",
            "data": data_points,
            "labels": {
                "x": "Date",
                "y": "Note moyenne"
            },
            "y_domain": [1, 5]  # Fixer l'échelle de 1 à 5
        }
        
    async def generate_dashboard_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """Génère un résumé des métriques clés pour le dashboard"""
        from ..analysis.metrics_calculator import MatchingMetricsCalculator
        
        # Utiliser le calculateur de métriques
        metrics_calculator = MatchingMetricsCalculator(self.data_connector)
        efficiency_data = await metrics_calculator.calculate_matching_efficiency(period_days)
        
        # Extraire les métriques clés
        metrics = {
            "overall_efficiency": {
                "value": round(efficiency_data["overall_efficiency"] * 100, 1),
                "unit": "%",
                "label": "Efficacité globale"
            },
            "acceptance_rate": {
                "value": round(efficiency_data["acceptance_metrics"]["acceptance_rate"] * 100, 1),
                "unit": "%",
                "label": "Taux d'acceptation"
            },
            "avg_rating": {
                "value": round(efficiency_data["satisfaction_metrics"]["avg_rating"], 2) if efficiency_data["satisfaction_metrics"]["avg_rating"] else None,
                "unit": "/5",
                "label": "Note moyenne"
            },
            "completion_rate": {
                "value": round(efficiency_data["engagement_metrics"]["completion_rate"] * 100, 1),
                "unit": "%",
                "label": "Taux de complétion"
            },
            "total_matches": {
                "value": efficiency_data["acceptance_metrics"]["total_proposed"],
                "unit": "",
                "label": "Total des matchs proposés"
            }
        }
        
        return metrics

def rating_label(rating: int) -> str:
    """Renvoie une étiquette pour un niveau de rating"""
    labels = {
        1: "Très mauvais",
        2: "Mauvais",
        3: "Neutre",
        4: "Bon",
        5: "Très bon"
    }
    return labels.get(rating, "")