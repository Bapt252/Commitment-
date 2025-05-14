"""Module pour générer des insights à partir des résultats du matching.
"""

import logging
import pandas as pd
import numpy as np
from collections import Counter, defaultdict

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InsightGenerator")

class InsightGenerator:
    """
    Classe pour générer des insights à partir des résultats de matching.
    """
    
    def __init__(self):
        """
        Initialise le générateur d'insights.
        """
        logger.info("Générateur d'insights initialisé")
    
    def generate_insights(self, matching_results):
        """
        Génère des insights à partir des résultats de matching.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Liste des insights générés
        """
        if not matching_results:
            logger.warning("Aucun résultat de matching fourni pour générer des insights")
            return []
        
        logger.info(f"Génération d'insights à partir de {len(matching_results)} résultats de matching")
        
        insights = []
        
        # 1. Analyse des scores par critère
        score_insights = self._analyze_scores_by_criteria(matching_results)
        insights.extend(score_insights)
        
        # 2. Analyse des compétences les plus demandées et manquantes
        skill_insights = self._analyze_skills(matching_results)
        insights.extend(skill_insights)
        
        # 3. Analyse des temps de trajet
        travel_insights = self._analyze_travel_times(matching_results)
        insights.extend(travel_insights)
        
        # 4. Analyse des tendances salariales
        salary_insights = self._analyze_salary_trends(matching_results)
        insights.extend(salary_insights)
        
        # 5. Identification des candidats et entreprises à haut potentiel
        potential_insights = self._identify_high_potential_matches(matching_results)
        insights.extend(potential_insights)
        
        logger.info(f"{len(insights)} insights générés")
        return insights
    
    def _analyze_scores_by_criteria(self, matching_results):
        """
        Analyse les scores par critère pour identifier les forces et faiblesses.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Insights sur les scores par critère
        """
        insights = []
        
        # Extraire tous les scores détaillés
        all_criteria = ["skills_score", "location_score", "remote_score", "experience_score", "salary_score"]
        scores_by_criteria = {criterion: [] for criterion in all_criteria}
        
        for match in matching_results:
            details = match.get("details", {})
            for criterion in all_criteria:
                if criterion in details:
                    scores_by_criteria[criterion].append(details[criterion])
        
        # Calculer les statistiques pour chaque critère
        stats = {}
        for criterion, scores in scores_by_criteria.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                
                stats[criterion] = {
                    "avg": avg_score,
                    "min": min_score,
                    "max": max_score
                }
                
                # Générer des insights basés sur ces statistiques
                if avg_score < 0.5:
                    insights.append({
                        "type": "warning",
                        "criterion": criterion,
                        "message": f"Le critère '{criterion}' a un score moyen bas ({avg_score:.2f}), ce qui indique un problème général de compatibilité."
                    })
                elif avg_score > 0.8:
                    insights.append({
                        "type": "strength",
                        "criterion": criterion,
                        "message": f"Le critère '{criterion}' a un score moyen élevé ({avg_score:.2f}), ce qui est un point fort dans les matchings."
                    })
        
        # Trouver le critère le plus fort et le plus faible
        if stats:
            strongest_criterion = max(stats.items(), key=lambda x: x[1]["avg"])
            weakest_criterion = min(stats.items(), key=lambda x: x[1]["avg"])
            
            insights.append({
                "type": "analysis",
                "message": f"Le critère le plus fort est '{strongest_criterion[0]}' (score moyen: {strongest_criterion[1]['avg']:.2f}), tandis que le plus faible est '{weakest_criterion[0]}' (score moyen: {weakest_criterion[1]['avg']:.2f})."
            })
        
        return insights
    
    def _analyze_skills(self, matching_results):
        """
        Analyse les compétences les plus demandées et les plus souvent manquantes.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Insights sur les compétences
        """
        insights = []
        
        # Collecter toutes les compétences manquantes
        all_missing_skills = []
        for match in matching_results:
            details = match.get("details", {})
            missing_skills = details.get("missing_skills", [])
            all_missing_skills.extend(missing_skills)
        
        # Compter les occurrences
        missing_skills_count = Counter(all_missing_skills)
        
        # Générer des insights sur les compétences les plus souvent manquantes
        if missing_skills_count:
            top_missing_skills = missing_skills_count.most_common(5)
            
            insights.append({
                "type": "skills_gap",
                "message": f"Les compétences les plus souvent manquantes sont: {', '.join([f'{skill[0]} ({skill[1]} occurrences)' for skill in top_missing_skills])}"
            })
            
            # Recommandation pour combler les lacunes les plus importantes
            if top_missing_skills:
                insights.append({
                    "type": "recommendation",
                    "message": f"Priorité devrait être donnée au développement ou recrutement de la compétence '{top_missing_skills[0][0]}', qui est la plus souvent manquante."
                })
        
        return insights
    
    def _analyze_travel_times(self, matching_results):
        """
        Analyse les temps de trajet et leur impact sur les scores.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Insights sur les temps de trajet
        """
        insights = []
        
        # Collecter tous les temps de trajet
        travel_times = []
        for match in matching_results:
            details = match.get("details", {})
            travel_time = details.get("travel_time_minutes")
            if travel_time and travel_time != "N/A" and isinstance(travel_time, (int, float)) and travel_time > 0:
                travel_times.append(travel_time)
        
        # Générer des insights basés sur les temps de trajet
        if travel_times:
            avg_travel_time = sum(travel_times) / len(travel_times)
            max_travel_time = max(travel_times)
            
            insights.append({
                "type": "travel_analysis",
                "message": f"Le temps de trajet moyen est de {avg_travel_time:.0f} minutes, avec un maximum de {max_travel_time:.0f} minutes."
            })
            
            # Recommandation basée sur les temps de trajet
            if avg_travel_time > 45:
                insights.append({
                    "type": "recommendation",
                    "message": "Les temps de trajet sont généralement longs. Considérez de mettre davantage l'accent sur les politiques de travail à distance ou de rechercher des candidats plus proches géographiquement."
                })
            elif avg_travel_time < 20:
                insights.append({
                    "type": "strength",
                    "message": "Les temps de trajet sont généralement courts, ce qui est un avantage pour l'équilibre travail-vie personnelle."
                })
        
        return insights
    
    def _analyze_salary_trends(self, matching_results):
        """
        Analyse les tendances salariales dans les résultats de matching.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Insights sur les salaires
        """
        # Note: cette fonction nécessiterait d'avoir les données complètes des candidats et entreprises,
        # pas seulement les résultats de matching. Pour l'exemple, on suppose qu'on les a.
        
        # Cette fonction est un placeholder et devrait être implémentée avec les données réelles
        insights = []
        
        # Exemple d'insight générique sur les salaires
        insights.append({
            "type": "salary_insight",
            "message": "L'analyse des tendances salariales requiert des données supplémentaires. Implémentez cette fonction avec les données réelles des candidats et entreprises."
        })
        
        return insights
    
    def _identify_high_potential_matches(self, matching_results):
        """
        Identifie les candidats et entreprises à haut potentiel de matching.
        
        Args:
            matching_results (list): Résultats du matching
            
        Returns:
            list: Insights sur les matchings à haut potentiel
        """
        insights = []
        
        # Trouver les meilleurs matchings
        if matching_results:
            # Trier les résultats par score décroissant
            sorted_results = sorted(matching_results, key=lambda x: x.get("score", 0), reverse=True)
            
            # Prendre les 5 meilleurs matchings
            top_matches = sorted_results[:5]
            
            if top_matches:
                insights.append({
                    "type": "top_matches",
                    "message": f"Les 5 meilleurs matchings ont des scores entre {top_matches[0].get('score', 0):.2f} et {top_matches[-1].get('score', 0):.2f}."
                })
                
                # Identifier les candidats qui apparaissent souvent dans les meilleurs matchings
                candidate_counts = Counter([match.get("candidate_id") for match in top_matches])
                top_candidates = candidate_counts.most_common(2)
                
                if top_candidates:
                    insights.append({
                        "type": "top_candidates",
                        "message": f"Les candidats les plus demandés sont: {', '.join([f'{cand[0]} ({cand[1]} matchings)' for cand in top_candidates])}"
                    })
                
                # Identifier les entreprises qui apparaissent souvent dans les meilleurs matchings
                company_counts = Counter([match.get("company_id") for match in top_matches])
                top_companies = company_counts.most_common(2)
                
                if top_companies:
                    insights.append({
                        "type": "top_companies",
                        "message": f"Les entreprises les plus attrayantes sont: {', '.join([f'{comp[0]} ({comp[1]} matchings)' for comp in top_companies])}"
                    })
        
        return insights