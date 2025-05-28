#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stub implementation for the original matching engine
This file provides a fallback implementation for backward compatibility
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def match_candidate_with_jobs(
    cv_data: Dict[str, Any], 
    questionnaire_data: Dict[str, Any], 
    job_data: List[Dict[str, Any]], 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Original matching engine implementation (stub)
    
    Args:
        cv_data: CV data
        questionnaire_data: Questionnaire data
        job_data: Job offers
        limit: Maximum number of results
        
    Returns:
        List of matching results
    """
    logger.info("Utilisation du moteur de matching original (stub)")
    
    results = []
    
    for i, job in enumerate(job_data[:limit]):
        # Simple matching based on skills
        candidate_skills = set(skill.lower() for skill in cv_data.get('competences', []))
        job_skills = set(skill.lower() for skill in job.get('competences', []))
        
        if candidate_skills and job_skills:
            common_skills = candidate_skills.intersection(job_skills)
            skill_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 50
        else:
            skill_score = 50
        
        # Simple location matching
        candidate_location = cv_data.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if candidate_location and job_location:
            if candidate_location in job_location or job_location in candidate_location:
                location_score = 90
            else:
                location_score = 40
        else:
            location_score = 50
        
        # Simple contract matching
        candidate_contracts = [c.lower() for c in questionnaire_data.get('contrats_recherches', [])]
        job_contract = job.get('type_contrat', '').lower()
        
        if candidate_contracts and job_contract:
            contract_score = 90 if job_contract in candidate_contracts else 30
        else:
            contract_score = 50
        
        # Weighted final score
        final_score = (skill_score * 0.5) + (location_score * 0.3) + (contract_score * 0.2)
        
        result = {
            'id': job.get('id', f'job_{i}'),
            'titre': job.get('titre', job.get('title', 'Poste sans titre')),
            'matching_score': int(min(100, max(0, final_score))),
            'scores_details': {
                'competences': int(skill_score),
                'localisation': int(location_score),
                'contrat': int(contract_score)
            },
            'algorithm': 'original',
            **job
        }
        
        results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    
    logger.info(f"Matching original terminé - {len(results)} résultats")
    return results


class MatchingEngine:
    """
    Original matching engine class (stub)
    """
    
    def __init__(self):
        self.name = "original"
        self.version = "1.0"
        self.initialized = True
        logger.info("MatchingEngine original initialisé (stub)")
    
    def match(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], job_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match candidate with jobs
        
        Args:
            cv_data: CV data
            questionnaire_data: Questionnaire data
            job_data: Job offers
            
        Returns:
            Matching results
        """
        return match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
