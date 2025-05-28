#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stub implementation for the enhanced matching engine
This file provides a fallback implementation for backward compatibility
"""

import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def enhanced_match_candidate_with_jobs(
    cv_data: Dict[str, Any], 
    questionnaire_data: Dict[str, Any], 
    job_data: List[Dict[str, Any]], 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Enhanced matching engine implementation (stub)
    
    Args:
        cv_data: CV data
        questionnaire_data: Questionnaire data
        job_data: Job offers
        limit: Maximum number of results
        
    Returns:
        List of matching results with enhanced scoring
    """
    logger.info("Utilisation du moteur de matching enhanced (stub)")
    
    results = []
    
    # Extract candidate preferences for dynamic weighting
    preferences = _extract_preferences(cv_data, questionnaire_data)
    weights = _calculate_dynamic_weights(preferences)
    
    for i, job in enumerate(job_data[:limit]):
        # Enhanced scoring with multiple criteria
        scores = {
            'skills': _calculate_skills_score(cv_data, job),
            'experience': _calculate_experience_score(cv_data, job),
            'location': _calculate_location_score(questionnaire_data, job),
            'salary': _calculate_salary_score(questionnaire_data, job),
            'contract': _calculate_contract_score(questionnaire_data, job),
            'culture': _calculate_culture_score(cv_data, job),
            'soft_skills': _calculate_soft_skills_score(cv_data, job)
        }
        
        # Weighted final score
        final_score = sum(scores[criterion] * weights[criterion] for criterion in scores)
        
        result = {
            'id': job.get('id', f'job_{i}'),
            'titre': job.get('titre', job.get('title', 'Poste sans titre')),
            'matching_score': int(min(100, max(0, final_score))),
            'scores_details': {k: int(v) for k, v in scores.items()},
            'weights_used': weights,
            'matching_explanations': _generate_explanations(cv_data, questionnaire_data, job, scores),
            'algorithm': 'enhanced',
            **job
        }
        
        results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    
    logger.info(f"Matching enhanced terminé - {len(results)} résultats")
    return results


def _extract_preferences(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract candidate preferences from data"""
    return {
        'salary_important': questionnaire_data.get('criteres_importants', {}).get('salaire_important', False),
        'location_important': questionnaire_data.get('criteres_importants', {}).get('localisation_importante', False),
        'culture_important': questionnaire_data.get('criteres_importants', {}).get('culture_importante', False),
        'evolution_important': questionnaire_data.get('criteres_importants', {}).get('evolution_rapide', False),
        'has_soft_skills': bool(cv_data.get('soft_skills', [])),
        'has_preferences': bool(questionnaire_data.get('valeurs_importantes', []))
    }


def _calculate_dynamic_weights(preferences: Dict[str, Any]) -> Dict[str, float]:
    """Calculate dynamic weights based on candidate preferences"""
    # Default weights
    weights = {
        'skills': 0.30,
        'experience': 0.15,
        'location': 0.20,
        'salary': 0.15,
        'contract': 0.10,
        'culture': 0.05,
        'soft_skills': 0.05
    }
    
    # Adjust weights based on preferences
    if preferences.get('salary_important'):
        weights['salary'] = 0.25
        weights['skills'] = 0.25
    
    if preferences.get('location_important'):
        weights['location'] = 0.30
        weights['skills'] = 0.25
    
    if preferences.get('culture_important'):
        weights['culture'] = 0.15
        weights['soft_skills'] = 0.10
        weights['skills'] = 0.25
    
    if preferences.get('evolution_important'):
        weights['experience'] = 0.20
        weights['culture'] = 0.10
    
    if preferences.get('has_soft_skills'):
        weights['soft_skills'] = 0.10
    
    # Normalize weights to sum to 1
    total = sum(weights.values())
    if total > 0:
        weights = {k: v/total for k, v in weights.items()}
    
    return weights


def _calculate_skills_score(cv_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate skills matching score"""
    candidate_skills = set(skill.lower() for skill in cv_data.get('competences', []))
    job_skills = set(skill.lower() for skill in job.get('competences', []))
    
    if not job_skills:
        return 70.0
    
    if not candidate_skills:
        return 30.0
    
    matching_skills = candidate_skills.intersection(job_skills)
    coverage = len(matching_skills) / len(job_skills)
    
    # Bonus for additional skills
    additional_skills = candidate_skills - job_skills
    bonus = min(20, len(additional_skills) * 3)
    
    return min(100.0, (coverage * 80) + bonus)


def _calculate_experience_score(cv_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate experience matching score"""
    candidate_exp = cv_data.get('annees_experience', 0)
    required_exp = job.get('experience_requise', 0)
    
    if isinstance(candidate_exp, str):
        candidate_exp = _extract_years_from_string(candidate_exp)
    if isinstance(required_exp, str):
        required_exp = _extract_years_from_string(required_exp)
    
    if required_exp == 0:
        return 80.0
    
    if candidate_exp >= required_exp:
        if candidate_exp <= required_exp * 1.5:
            return 95.0  # Perfect match
        elif candidate_exp <= required_exp * 2:
            return 85.0  # Good match
        else:
            return 75.0  # Overqualified
    else:
        ratio = candidate_exp / required_exp
        return max(30.0, ratio * 70)


def _calculate_location_score(questionnaire_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate location matching score"""
    candidate_location = questionnaire_data.get('adresse', '').lower()
    job_location = job.get('localisation', '').lower()
    
    if not candidate_location or not job_location:
        return 60.0
    
    # Check for remote work
    remote_policy = job.get('politique_remote', '').lower()
    if 'télétravail' in remote_policy or 'remote' in remote_policy:
        return 90.0
    
    # Exact match
    if candidate_location in job_location or job_location in candidate_location:
        return 95.0
    
    # Partial match (same words)
    candidate_words = set(candidate_location.split())
    job_words = set(job_location.split())
    
    if candidate_words.intersection(job_words):
        return 80.0
    
    return 40.0


def _calculate_salary_score(questionnaire_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate salary matching score"""
    candidate_salary = questionnaire_data.get('salaire_souhaite', 0)
    job_salary_str = job.get('salaire', '')
    
    if not candidate_salary or not job_salary_str:
        return 70.0
    
    # Extract salary range from job offer
    try:
        salary_range = _extract_salary_range(job_salary_str)
        if not salary_range:
            return 70.0
        
        min_salary, max_salary = salary_range
        
        if min_salary <= candidate_salary <= max_salary:
            return 95.0
        elif candidate_salary < min_salary:
            # Candidate asks for less (good for employer)
            ratio = candidate_salary / min_salary
            return min(100.0, 70 + (ratio * 25))
        else:
            # Candidate asks for more
            ratio = max_salary / candidate_salary
            return max(20.0, ratio * 60)
    
    except:
        return 70.0


def _calculate_contract_score(questionnaire_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate contract type matching score"""
    candidate_contracts = [c.lower() for c in questionnaire_data.get('contrats_recherches', [])]
    job_contract = job.get('type_contrat', '').lower()
    
    if not candidate_contracts or not job_contract:
        return 70.0
    
    if job_contract in candidate_contracts:
        return 95.0
    
    # Partial matches
    if 'cdi' in candidate_contracts and 'cdi' in job_contract:
        return 95.0
    if 'cdd' in candidate_contracts and 'cdd' in job_contract:
        return 95.0
    
    return 30.0


def _calculate_culture_score(cv_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate culture matching score"""
    candidate_values = cv_data.get('valeurs_importantes', [])
    job_culture = job.get('culture_entreprise', {})
    
    if not candidate_values or not job_culture:
        return 60.0
    
    job_values = job_culture.get('valeurs', [])
    
    if not job_values:
        return 60.0
    
    candidate_values_set = set(v.lower() for v in candidate_values)
    job_values_set = set(v.lower() for v in job_values)
    
    matching_values = candidate_values_set.intersection(job_values_set)
    
    if matching_values:
        return min(95.0, 50 + (len(matching_values) / len(candidate_values_set)) * 45)
    
    return 40.0


def _calculate_soft_skills_score(cv_data: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate soft skills matching score"""
    candidate_soft_skills = set(skill.lower() for skill in cv_data.get('soft_skills', []))
    job_soft_skills = set(skill.lower() for skill in job.get('soft_skills', []))
    
    if not job_soft_skills:
        return 70.0
    
    if not candidate_soft_skills:
        return 40.0
    
    matching_skills = candidate_soft_skills.intersection(job_soft_skills)
    
    if matching_skills:
        return min(95.0, 50 + (len(matching_skills) / len(job_soft_skills)) * 45)
    
    return 30.0


def _generate_explanations(
    cv_data: Dict[str, Any], 
    questionnaire_data: Dict[str, Any], 
    job: Dict[str, Any], 
    scores: Dict[str, float]
) -> Dict[str, str]:
    """Generate explanations for matching results"""
    explanations = {}
    
    # Skills explanation
    candidate_skills = cv_data.get('competences', [])
    job_skills = job.get('competences', [])
    matching_skills = set(s.lower() for s in candidate_skills).intersection(
        set(s.lower() for s in job_skills)
    )
    
    if len(matching_skills) >= len(job_skills) * 0.8:
        explanations['skills'] = "Excellente correspondance des compétences"
    elif len(matching_skills) >= len(job_skills) * 0.6:
        explanations['skills'] = "Bonne correspondance des compétences"
    else:
        explanations['skills'] = "Correspondance partielle des compétences"
    
    # Location explanation
    candidate_location = questionnaire_data.get('adresse', '')
    job_location = job.get('localisation', '')
    
    if candidate_location.lower() in job_location.lower():
        explanations['location'] = "Localisation parfaitement compatible"
    else:
        explanations['location'] = f"Localisation différente ({candidate_location} vs {job_location})"
    
    # Salary explanation
    candidate_salary = questionnaire_data.get('salaire_souhaite', 0)
    job_salary = job.get('salaire', '')
    
    if candidate_salary and job_salary:
        explanations['salary'] = f"Attentes salariales: {candidate_salary}€ vs {job_salary}"
    else:
        explanations['salary'] = "Informations salariales à préciser"
    
    return explanations


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
        # Handle formats like "45-55K€", "45000-55000€"
        salary_str = salary_str.replace('€', '').replace(' ', '').lower()
        
        if 'k' in salary_str:
            # Extract numbers before 'k'
            numbers = re.findall(r'(\d+)k', salary_str)
            if len(numbers) >= 2:
                return int(numbers[0]) * 1000, int(numbers[1]) * 1000
            elif len(numbers) == 1:
                base = int(numbers[0]) * 1000
                return base, base
        else:
            # Extract regular numbers
            numbers = re.findall(r'(\d+)', salary_str)
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                base = int(numbers[0])
                return base, base
        
        return None
    except:
        return None


class EnhancedMatchingEngine:
    """
    Enhanced matching engine class (stub)
    """
    
    def __init__(self):
        self.name = "enhanced"
        self.version = "1.0"
        self.initialized = True
        logger.info("EnhancedMatchingEngine initialisé (stub)")
    
    def match(
        self, 
        cv_data: Dict[str, Any], 
        questionnaire_data: Dict[str, Any], 
        job_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match candidate with jobs using enhanced algorithm
        
        Args:
            cv_data: CV data
            questionnaire_data: Questionnaire data
            job_data: Job offers
            
        Returns:
            Enhanced matching results
        """
        return enhanced_match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
