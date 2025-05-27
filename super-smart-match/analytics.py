#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch Analytics - Suivi des performances et statistiques
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class SuperSmartMatchAnalytics:
    """
    Système d'analytics pour SuperSmartMatch
    Suit les performances, tendances et optimisations
    """
    
    def __init__(self, log_file="logs/supersmartmatch_analytics.json"):
        self.log_file = log_file
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Crée le fichier de logs s'il n'existe pas"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def log_matching_session(
        self, 
        matching_type: str,  # "candidate_to_jobs" ou "company_to_candidates"
        algorithm_used: str,
        input_data: Dict[str, Any],
        results: List[Dict[str, Any]],
        execution_time: float
    ):
        """
        Enregistre une session de matching pour analytics
        
        Args:
            matching_type: Type de matching
            algorithm_used: Algorithme utilisé
            input_data: Données d'entrée
            results: Résultats du matching
            execution_time: Temps d'exécution en secondes
        """
        try:
            # Analyser les résultats
            analytics_entry = {
                "timestamp": datetime.now().isoformat(),
                "matching_type": matching_type,
                "algorithm_used": algorithm_used,
                "execution_time_seconds": execution_time,
                "input_stats": self._analyze_input(input_data, matching_type),
                "output_stats": self._analyze_output(results, matching_type),
                "performance_metrics": self._calculate_performance_metrics(results, matching_type)
            }
            
            # Sauvegarder
            self._append_to_log(analytics_entry)
            
        except Exception as e:
            logger.error(f"Erreur lors du logging analytics: {e}")
    
    def _analyze_input(self, input_data: Dict[str, Any], matching_type: str) -> Dict[str, Any]:
        """Analyse les données d'entrée"""
        stats = {}
        
        if matching_type == "company_to_candidates":
            # Analyser l'offre d'emploi
            job_data = input_data.get('job_data', {})
            candidates = input_data.get('candidates_data', [])
            
            stats.update({
                "job_title": job_data.get('titre', 'Non spécifié'),
                "job_location": job_data.get('localisation', 'Non spécifié'),
                "required_skills_count": len(job_data.get('competences', [])),
                "salary_range": job_data.get('salaire', 'Non spécifié'),
                "candidates_count": len(candidates),
                "candidates_avg_experience": self._calculate_avg_experience(candidates),
                "candidates_skill_diversity": self._calculate_skill_diversity(candidates)
            })
            
        elif matching_type == "candidate_to_jobs":
            # Analyser le candidat
            cv_data = input_data.get('cv_data', {})
            jobs = input_data.get('job_data', [])
            
            stats.update({
                "candidate_experience": cv_data.get('annees_experience', 0),
                "candidate_skills_count": len(cv_data.get('competences', [])),
                "jobs_count": len(jobs),
                "avg_job_experience_required": self._calculate_avg_job_experience(jobs)
            })
        
        return stats
    
    def _analyze_output(self, results: List[Dict[str, Any]], matching_type: str) -> Dict[str, Any]:
        """Analyse les résultats de sortie"""
        if not results:
            return {"results_count": 0}
        
        # Statistiques générales
        scores = []
        intelligence_bonuses = []
        
        for result in results:
            if matching_type == "company_to_candidates":
                score = result.get('matching_score_entreprise', 0)
                scores.append(score)
                
                intelligence = result.get('intelligence', {})
                bonus = intelligence.get('bonus_applique', 0)
                intelligence_bonuses.append(bonus)
            else:
                score = result.get('matching_score', 0)
                scores.append(score)
        
        stats = {
            "results_count": len(results),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "scores_above_80": len([s for s in scores if s >= 80]),
            "scores_above_90": len([s for s in scores if s >= 90])
        }
        
        if intelligence_bonuses:
            stats.update({
                "avg_intelligence_bonus": sum(intelligence_bonuses) / len(intelligence_bonuses),
                "max_intelligence_bonus": max(intelligence_bonuses),
                "results_with_intelligence_bonus": len([b for b in intelligence_bonuses if b > 0])
            })
        
        return stats
    
    def _calculate_performance_metrics(self, results: List[Dict[str, Any]], matching_type: str) -> Dict[str, Any]:
        """Calcule des métriques de performance"""
        metrics = {}
        
        if matching_type == "company_to_candidates" and results:
            # Métriques spécifiques côté entreprise
            location_scores = []
            experience_scores = []
            salary_scores = []
            skills_scores = []
            
            for result in results:
                scores_detail = result.get('scores_detailles', {})
                
                if 'localisation' in scores_detail:
                    location_scores.append(scores_detail['localisation']['pourcentage'])
                if 'experience' in scores_detail:
                    experience_scores.append(scores_detail['experience']['pourcentage'])
                if 'remuneration' in scores_detail:
                    salary_scores.append(scores_detail['remuneration']['pourcentage'])
                if 'competences' in scores_detail:
                    skills_scores.append(scores_detail['competences']['pourcentage'])
            
            metrics.update({
                "avg_location_score": sum(location_scores) / len(location_scores) if location_scores else 0,
                "avg_experience_score": sum(experience_scores) / len(experience_scores) if experience_scores else 0,
                "avg_salary_score": sum(salary_scores) / len(salary_scores) if salary_scores else 0,
                "avg_skills_score": sum(skills_scores) / len(skills_scores) if skills_scores else 0,
                "location_excellent_candidates": len([s for s in location_scores if s >= 85]),
                "salary_compatible_candidates": len([s for s in salary_scores if s >= 70])
            })
        
        return metrics
    
    def _calculate_avg_experience(self, candidates: List[Dict[str, Any]]) -> float:
        """Calcule l'expérience moyenne des candidats"""
        experiences = []
        for candidate in candidates:
            cv_data = candidate.get('cv_data', {})
            exp = cv_data.get('annees_experience', 0)
            if exp > 0:
                experiences.append(exp)
        
        return sum(experiences) / len(experiences) if experiences else 0
    
    def _calculate_skill_diversity(self, candidates: List[Dict[str, Any]]) -> int:
        """Calcule la diversité des compétences"""
        all_skills = set()
        for candidate in candidates:
            cv_data = candidate.get('cv_data', {})
            skills = cv_data.get('competences', [])
            all_skills.update(skill.lower() for skill in skills)
        
        return len(all_skills)
    
    def _calculate_avg_job_experience(self, jobs: List[Dict[str, Any]]) -> float:
        """Calcule l'expérience moyenne requise pour les jobs"""
        experiences = [job.get('experience_requise', 0) for job in jobs if job.get('experience_requise', 0) > 0]
        return sum(experiences) / len(experiences) if experiences else 0
    
    def _append_to_log(self, entry: Dict[str, Any]):
        """Ajoute une entrée au fichier de logs"""
        try:
            # Lire les logs existants
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Ajouter la nouvelle entrée
            logs.append(entry)
            
            # Garder seulement les 1000 dernières entrées
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Sauvegarder
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des analytics: {e}")
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Retourne les statistiques des N derniers jours
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dictionnaire des statistiques
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Filtrer par date
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            recent_logs = [
                log for log in logs 
                if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_date
            ]
            
            if not recent_logs:
                return {"message": "Aucune donnée pour la période spécifiée"}
            
            # Calculer les statistiques
            stats = {
                "period_days": days,
                "total_sessions": len(recent_logs),
                "algorithms_usage": self._count_algorithm_usage(recent_logs),
                "matching_types": self._count_matching_types(recent_logs),
                "performance_trends": self._calculate_performance_trends(recent_logs),
                "average_execution_time": sum(log['execution_time_seconds'] for log in recent_logs) / len(recent_logs),
                "intelligence_effectiveness": self._analyze_intelligence_effectiveness(recent_logs)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {"error": str(e)}
    
    def _count_algorithm_usage(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Compte l'utilisation des algorithmes"""
        usage = {}
        for log in logs:
            algo = log.get('algorithm_used', 'unknown')
            usage[algo] = usage.get(algo, 0) + 1
        return usage
    
    def _count_matching_types(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Compte les types de matching"""
        types = {}
        for log in logs:
            match_type = log.get('matching_type', 'unknown')
            types[match_type] = types.get(match_type, 0) + 1
        return types
    
    def _calculate_performance_trends(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les tendances de performance"""
        company_sessions = [log for log in logs if log.get('matching_type') == 'company_to_candidates']
        
        if not company_sessions:
            return {"message": "Aucune session côté entreprise"}
        
        avg_scores = []
        avg_bonuses = []
        
        for session in company_sessions:
            output_stats = session.get('output_stats', {})
            avg_scores.append(output_stats.get('avg_score', 0))
            avg_bonuses.append(output_stats.get('avg_intelligence_bonus', 0))
        
        return {
            "avg_matching_score": sum(avg_scores) / len(avg_scores) if avg_scores else 0,
            "avg_intelligence_bonus": sum(avg_bonuses) / len(avg_bonuses) if avg_bonuses else 0,
            "sessions_with_high_scores": len([s for s in avg_scores if s >= 80]),
            "intelligence_bonus_trend": "positive" if avg_bonuses and avg_bonuses[-1] > sum(avg_bonuses) / len(avg_bonuses) else "stable"
        }
    
    def _analyze_intelligence_effectiveness(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse l'efficacité du système d'intelligence"""
        company_sessions = [log for log in logs if log.get('matching_type') == 'company_to_candidates']
        
        if not company_sessions:
            return {"message": "Aucune session côté entreprise"}
        
        total_bonuses = 0
        bonus_sessions = 0
        
        for session in company_sessions:
            output_stats = session.get('output_stats', {})
            bonus_count = output_stats.get('results_with_intelligence_bonus', 0)
            if bonus_count > 0:
                bonus_sessions += 1
                total_bonuses += bonus_count
        
        return {
            "sessions_with_intelligence": bonus_sessions,
            "total_intelligence_applications": total_bonuses,
            "intelligence_usage_rate": (bonus_sessions / len(company_sessions)) * 100 if company_sessions else 0,
            "avg_bonuses_per_session": total_bonuses / bonus_sessions if bonus_sessions > 0 else 0
        }

# Instance globale pour l'analytics
analytics = SuperSmartMatchAnalytics()
