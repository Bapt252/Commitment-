#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stub implementation for the reverse matching engine (company to candidates)
This file provides a fallback implementation for backward compatibility
"""

import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def reverse_match_job_with_candidates(
    job_data: Dict[str, Any], 
    candidates_data: List[Dict[str, Any]], 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Reverse matching engine implementation (job to candidates)
    
    Args:
        job_data: Job offer data
        candidates_data: List of candidates
        limit: Maximum number of results
        
    Returns:
        List of matching candidates with scores
    """
    logger.info("Utilisation du moteur de matching reverse (stub)")
    
    results = []
    
    for i, candidate in enumerate(candidates_data[:limit]):
        # Extract CV and questionnaire data
        cv_data = candidate.get('cv_data', {})
        questionnaire_data = candidate.get('questionnaire_data', {})
        
        # Calculate matching scores from company perspective
        scores = {
            'skills_match': _calculate_reverse_skills_score(job_data, cv_data),
            'experience_match': _calculate_reverse_experience_score(job_data, cv_data),
            'location_compatibility': _calculate_reverse_location_score(job_data, questionnaire_data),
            'salary_budget_fit': _calculate_reverse_salary_score(job_data, questionnaire_data),
            'contract_alignment': _calculate_reverse_contract_score(job_data, questionnaire_data),
            'cultural_fit': _calculate_reverse_culture_score(job_data, cv_data),
            'career_goals_match': _calculate_career_goals_score(job_data, questionnaire_data)
        }
        
        # Company-focused weighting (what matters most to employers)
        weights = {
            'skills_match': 0.35,          # Skills are crucial
            'experience_match': 0.25,      # Experience matters a lot
            'location_compatibility': 0.15, # Location logistics
            'salary_budget_fit': 0.15,     # Budget constraints
            'contract_alignment': 0.05,    # Usually flexible
            'cultural_fit': 0.03,          # Nice to have
            'career_goals_match': 0.02     # Future consideration
        }
        
        # Calculate weighted final score
        final_score = sum(scores[criterion] * weights[criterion] for criterion in scores)
        
        # Add company-specific insights
        insights = _generate_company_insights(job_data, cv_data, questionnaire_data, scores)
        
        result = {
            'candidate_id': candidate.get('candidate_id', f'candidate_{i}'),
            'nom': cv_data.get('nom', f'Candidat {i+1}'),
            'matching_score': int(min(100, max(0, final_score))),
            'scores_details': {k: int(v) for k, v in scores.items()},
            'weights_used': weights,
            'company_insights': insights,
            'recommendation_level': _get_recommendation_level(final_score),
            'next_steps': _suggest_next_steps(final_score, scores),
            'algorithm': 'reverse',
            'cv_data': cv_data,
            'questionnaire_data': questionnaire_data,
            **candidate
        }
        
        results.append(result)
    
    # Sort by score (best candidates first)
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    
    logger.info(f"Matching reverse terminé - {len(results)} candidats évalués")
    return results


def _calculate_reverse_skills_score(job_data: Dict[str, Any], cv_data: Dict[str, Any]) -> float:
    """Calculate how well candidate skills match job requirements (company perspective)"""
    required_skills = set(skill.lower() for skill in job_data.get('competences', []))
    candidate_skills = set(skill.lower() for skill in cv_data.get('competences', []))
    
    if not required_skills:
        return 70.0  # No specific requirements
    
    if not candidate_skills:
        return 20.0  # No skills listed
    
    # Essential skills coverage
    matching_skills = candidate_skills.intersection(required_skills)
    coverage_ratio = len(matching_skills) / len(required_skills)
    
    # Bonus for additional relevant skills
    additional_skills = candidate_skills - required_skills
    bonus = min(15, len(additional_skills) * 2)
    
    base_score = coverage_ratio * 85
    return min(100.0, base_score + bonus)


def _calculate_reverse_experience_score(job_data: Dict[str, Any], cv_data: Dict[str, Any]) -> float:
    """Calculate experience fit from company perspective"""
    required_exp = job_data.get('experience_requise', 0)
    candidate_exp = cv_data.get('annees_experience', 0)
    
    if isinstance(candidate_exp, str):
        candidate_exp = _extract_years_from_string(candidate_exp)
    if isinstance(required_exp, str):
        required_exp = _extract_years_from_string(required_exp)
    
    if required_exp == 0:
        return 80.0  # No specific requirement
    
    if candidate_exp >= required_exp:
        # Candidate meets or exceeds requirements
        if candidate_exp <= required_exp * 1.5:
            return 95.0  # Perfect fit
        elif candidate_exp <= required_exp * 2:
            return 85.0  # Good fit, not overqualified
        else:
            return 70.0  # Potentially overqualified (flight risk)
    else:
        # Candidate has less experience
        if candidate_exp >= required_exp * 0.7:
            return 75.0  # Close enough, trainable
        elif candidate_exp >= required_exp * 0.5:
            return 60.0  # Significant gap but potential
        else:
            return 35.0  # Major experience gap


def _calculate_reverse_location_score(job_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> float:
    """Calculate location compatibility from company perspective"""
    job_location = job_data.get('localisation', '').lower()
    candidate_location = questionnaire_data.get('adresse', '').lower()
    candidate_mobility = questionnaire_data.get('mobilite', '').lower()
    
    # Remote work policy check
    remote_policy = job_data.get('politique_remote', '').lower()
    if 'télétravail' in remote_policy or 'remote' in remote_policy:
        return 90.0  # Location not a concern
    
    if not candidate_location:
        return 50.0  # Unknown location
    
    # Exact location match
    if candidate_location in job_location or job_location in candidate_location:
        return 95.0
    
    # Check candidate mobility
    if 'mobile' in candidate_mobility or 'élevée' in candidate_mobility:
        return 80.0  # Willing to relocate/commute
    
    # Partial location match (same region/department)
    candidate_words = set(candidate_location.split())
    job_words = set(job_location.split())
    
    if candidate_words.intersection(job_words):
        return 70.0
    
    return 30.0  # Different locations, no indicated mobility


def _calculate_reverse_salary_score(job_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> float:
    """Calculate salary budget compatibility from company perspective"""
    job_budget = job_data.get('budget_max', 0)
    job_salary_str = job_data.get('salaire', '')
    candidate_expectation = questionnaire_data.get('salaire_souhaite', 0)
    
    # Extract job budget if not directly available
    if not job_budget and job_salary_str:
        salary_range = _extract_salary_range(job_salary_str)
        if salary_range:
            _, job_budget = salary_range
    
    if not candidate_expectation:
        return 75.0  # No salary expectation (potentially negotiable)
    
    if not job_budget:
        return 60.0  # No budget info
    
    # Company perspective: prefer candidates who ask for less
    if candidate_expectation <= job_budget * 0.8:
        return 95.0  # Well within budget
    elif candidate_expectation <= job_budget:
        return 85.0  # Within budget
    elif candidate_expectation <= job_budget * 1.1:
        return 70.0  # Slightly over budget, negotiable
    elif candidate_expectation <= job_budget * 1.2:
        return 50.0  # Over budget, difficult negotiation
    else:
        return 25.0  # Far over budget


def _calculate_reverse_contract_score(job_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> float:
    """Calculate contract type alignment"""
    job_contract = job_data.get('type_contrat', '').lower()
    candidate_preferences = [c.lower() for c in questionnaire_data.get('contrats_recherches', [])]
    
    if not candidate_preferences:
        return 75.0  # No preference stated
    
    if not job_contract:
        return 70.0  # Job contract type not specified
    
    # Direct match
    if job_contract in candidate_preferences:
        return 95.0
    
    # Compatible matches
    if 'cdi' in job_contract and ('cdd' in candidate_preferences or 'freelance' in candidate_preferences):
        return 60.0  # Company offers more security than candidate expects
    
    return 35.0  # Mismatch


def _calculate_reverse_culture_score(job_data: Dict[str, Any], cv_data: Dict[str, Any]) -> float:
    """Calculate cultural fit from company perspective"""
    company_values = job_data.get('culture_entreprise', {}).get('valeurs', [])
    candidate_values = cv_data.get('valeurs_importantes', [])
    
    if not company_values or not candidate_values:
        return 60.0  # Neutral score
    
    company_values_set = set(v.lower() for v in company_values)
    candidate_values_set = set(v.lower() for v in candidate_values)
    
    matching_values = company_values_set.intersection(candidate_values_set)
    
    if matching_values:
        overlap_ratio = len(matching_values) / len(company_values_set)
        return min(95.0, 60 + (overlap_ratio * 35))
    
    return 40.0


def _calculate_career_goals_score(job_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> float:
    """Calculate alignment between job opportunities and candidate career goals"""
    job_evolution = job_data.get('perspectives_evolution', False)
    job_level = job_data.get('niveau_poste', '').lower()
    
    candidate_goals = questionnaire_data.get('objectifs_carriere', {})
    wants_evolution = candidate_goals.get('evolution_rapide', False)
    career_ambitions = candidate_goals.get('ambitions', [])
    
    if not candidate_goals:
        return 60.0  # No specific goals stated
    
    score = 50.0
    
    # Evolution opportunities
    if wants_evolution and job_evolution:
        score += 30.0
    elif wants_evolution and not job_evolution:
        score -= 10.0  # Mismatch
    
    # Career level alignment
    if 'management' in career_ambitions and ('senior' in job_level or 'lead' in job_level):
        score += 15.0
    elif 'technique' in career_ambitions and ('technique' in job_level or 'expert' in job_level):
        score += 15.0
    
    return min(95.0, score)


def _generate_company_insights(
    job_data: Dict[str, Any], 
    cv_data: Dict[str, Any], 
    questionnaire_data: Dict[str, Any],
    scores: Dict[str, float]
) -> Dict[str, Any]:
    """Generate insights for the company about this candidate"""
    insights = {
        'strengths': [],
        'concerns': [],
        'potential_fit': 'Unknown',
        'salary_negotiation': 'Standard',
        'retention_risk': 'Medium'
    }
    
    # Analyze strengths
    if scores['skills_match'] >= 80:
        insights['strengths'].append("Excellentes compétences techniques")
    
    if scores['experience_match'] >= 80:
        insights['strengths'].append("Expérience très adaptée au poste")
    
    if scores['location_compatibility'] >= 80:
        insights['strengths'].append("Aucun problème de localisation")
    
    # Analyze concerns
    if scores['salary_budget_fit'] < 60:
        insights['concerns'].append("Attentes salariales élevées")
        insights['salary_negotiation'] = 'Difficile'
    
    if scores['experience_match'] > 90 and cv_data.get('annees_experience', 0) > job_data.get('experience_requise', 0) * 2:
        insights['concerns'].append("Risque de surqualification")
        insights['retention_risk'] = 'High'
    
    if scores['location_compatibility'] < 60:
        insights['concerns'].append("Contraintes géographiques")
    
    # Overall fit assessment
    avg_score = sum(scores.values()) / len(scores)
    if avg_score >= 80:
        insights['potential_fit'] = 'Excellent'
    elif avg_score >= 65:
        insights['potential_fit'] = 'Bon'
    elif avg_score >= 50:
        insights['potential_fit'] = 'Acceptable'
    else:
        insights['potential_fit'] = 'Faible'
    
    return insights


def _get_recommendation_level(score: float) -> str:
    """Get recommendation level for the candidate"""
    if score >= 85:
        return "Fortement recommandé"
    elif score >= 70:
        return "Recommandé"
    elif score >= 55:
        return "À considérer"
    else:
        return "Non recommandé"


def _suggest_next_steps(score: float, scores: Dict[str, float]) -> List[str]:
    """Suggest next steps for the company"""
    steps = []
    
    if score >= 80:
        steps.append("Programmer un entretien rapidement")
        steps.append("Préparer une offre competitive")
    elif score >= 65:
        steps.append("Entretien approfondi recommandé")
        if scores['salary_budget_fit'] < 70:
            steps.append("Préparer la négociation salariale")
    elif score >= 50:
        steps.append("Évaluation complémentaire nécessaire")
        steps.append("Vérifier les compétences manquantes")
    else:
        steps.append("Candidat non prioritaire")
        steps.append("Conserver pour futures opportunités")
    
    return steps


def _extract_years_from_string(text: str) -> int:
    """Extract years from a string"""
    if isinstance(text, (int, float)):
        return int(text)
    
    matches = re.findall(r'(\d+)', str(text))
    if matches:
        return int(matches[0])
    return 0


def _extract_salary_range(salary_str: str) -> Optional[tuple]:
    """Extract salary range from string"""
    try:
        salary_str = salary_str.replace('€', '').replace(' ', '').lower()
        
        if 'k' in salary_str:
            numbers = re.findall(r'(\d+)k', salary_str)
            if len(numbers) >= 2:
                return int(numbers[0]) * 1000, int(numbers[1]) * 1000
            elif len(numbers) == 1:
                base = int(numbers[0]) * 1000
                return base, base
        else:
            numbers = re.findall(r'(\d+)', salary_str)
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                base = int(numbers[0])
                return base, base
        
        return None
    except:
        return None


class ReverseMatchingEngine:
    """
    Reverse matching engine class (stub)
    """
    
    def __init__(self):
        self.name = "reverse"
        self.version = "1.0"
        self.initialized = True
        logger.info("ReverseMatchingEngine initialisé (stub)")
    
    def match(
        self, 
        job_data: Dict[str, Any], 
        candidates_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match job with candidates using reverse algorithm
        
        Args:
            job_data: Job offer data
            candidates_data: List of candidates
            
        Returns:
            Reverse matching results
        """
        return reverse_match_job_with_candidates(job_data, candidates_data)
