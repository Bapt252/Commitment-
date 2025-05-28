#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SmartMatch Engine implementation
Provides backward compatibility for the original SmartMatch system
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SmartMatchEngine:
    """
    SmartMatch Engine class for backward compatibility
    """
    
    def __init__(self):
        self.name = "smartmatch"
        self.version = "1.0"
        self.initialized = True
        logger.info("SmartMatchEngine initialisé")
    
    def match(
        self, 
        candidates: List[Dict[str, Any]], 
        companies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Bidirectional matching between candidates and companies
        
        Args:
            candidates: List of candidates
            companies: List of companies/jobs
            
        Returns:
            Matching results
        """
        logger.info(f"SmartMatch matching {len(candidates)} candidats avec {len(companies)} entreprises")
        
        results = []
        
        for candidate in candidates:
            for i, company in enumerate(companies):
                # Calculate bidirectional score
                score = self._calculate_bidirectional_score(candidate, company)
                
                result = {
                    'candidate_id': candidate.get('id', 'candidate_1'),
                    'company_id': company.get('id', f'company_{i}'),
                    'company_name': company.get('name', company.get('titre', 'Entreprise')),
                    'score': score,
                    'details': {
                        'skills_match': self._calculate_skills_match(candidate, company),
                        'location_compatibility': self._calculate_location_compatibility(candidate, company),
                        'experience_fit': self._calculate_experience_fit(candidate, company),
                        'remote_alignment': self._calculate_remote_alignment(candidate, company)
                    },
                    'explanations': {
                        'skills': self._explain_skills_match(candidate, company),
                        'location': self._explain_location_match(candidate, company),
                        'remote': self._explain_remote_match(candidate, company)
                    }
                }
                
                results.append(result)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _calculate_bidirectional_score(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> float:
        """Calculate bidirectional matching score"""
        weights = {
            'skills': 0.4,
            'location': 0.25,
            'experience': 0.2,
            'remote': 0.15
        }
        
        scores = {
            'skills': self._calculate_skills_match(candidate, company),
            'location': self._calculate_location_compatibility(candidate, company),
            'experience': self._calculate_experience_fit(candidate, company),
            'remote': self._calculate_remote_alignment(candidate, company)
        }
        
        return sum(scores[k] * weights[k] for k in scores)
    
    def _calculate_skills_match(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> float:
        """Calculate skills matching score"""
        candidate_skills = set(s.lower() for s in candidate.get('skills', []))
        required_skills = set(s.lower() for s in company.get('required_skills', []))
        
        if not required_skills:
            return 0.7
        
        if not candidate_skills:
            return 0.2
        
        matching_skills = candidate_skills.intersection(required_skills)
        return len(matching_skills) / len(required_skills)
    
    def _calculate_location_compatibility(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> float:
        """Calculate location compatibility"""
        candidate_location = candidate.get('location', '').lower()
        company_location = company.get('location', '').lower()
        
        if not candidate_location or not company_location:
            return 0.5
        
        if candidate_location in company_location or company_location in candidate_location:
            return 1.0
        
        # Check for same region/city keywords
        candidate_words = set(candidate_location.split())
        company_words = set(company_location.split())
        
        if candidate_words.intersection(company_words):
            return 0.8
        
        return 0.3
    
    def _calculate_experience_fit(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> float:
        """Calculate experience fit"""
        candidate_exp = candidate.get('experience', 0)
        required_exp = company.get('required_experience', 0)
        
        if required_exp == 0:
            return 0.8
        
        if candidate_exp >= required_exp:
            if candidate_exp <= required_exp * 1.5:
                return 1.0
            else:
                return 0.8  # Overqualified
        else:
            ratio = candidate_exp / required_exp
            return max(0.3, ratio)
    
    def _calculate_remote_alignment(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> float:
        """Calculate remote work alignment"""
        candidate_pref = candidate.get('remote_preference', '').lower()
        company_policy = company.get('remote_policy', '').lower()
        
        if not candidate_pref and not company_policy:
            return 0.7
        
        # Simple alignment check
        if ('remote' in candidate_pref and 'remote' in company_policy) or \
           ('onsite' in candidate_pref and 'onsite' in company_policy) or \
           ('hybrid' in candidate_pref and 'hybrid' in company_policy):
            return 1.0
        
        return 0.4
    
    def _explain_skills_match(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> str:
        """Explain skills matching"""
        candidate_skills = set(s.lower() for s in candidate.get('skills', []))
        required_skills = set(s.lower() for s in company.get('required_skills', []))
        
        matching_skills = candidate_skills.intersection(required_skills)
        
        if len(matching_skills) == len(required_skills):
            return "Toutes les compétences requises correspondent"
        elif len(matching_skills) >= len(required_skills) * 0.7:
            return f"{len(matching_skills)}/{len(required_skills)} compétences correspondent"
        else:
            return f"Correspondance partielle des compétences"
    
    def _explain_location_match(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> str:
        """Explain location matching"""
        candidate_location = candidate.get('location', '')
        company_location = company.get('location', '')
        
        if candidate_location.lower() in company_location.lower():
            return "Même localisation"
        else:
            return f"Localisations différentes ({candidate_location} vs {company_location})"
    
    def _explain_remote_match(
        self, 
        candidate: Dict[str, Any], 
        company: Dict[str, Any]
    ) -> str:
        """Explain remote work alignment"""
        candidate_pref = candidate.get('remote_preference', '')
        company_policy = company.get('remote_policy', '')
        
        return f"Télétravail: {candidate_pref} vs {company_policy}"


# Helper functions for backward compatibility
def create_smartmatch_engine():
    """Create a SmartMatch engine instance"""
    return SmartMatchEngine()


def smartmatch_candidate_with_jobs(
    candidate_data: Dict[str, Any],
    job_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    SmartMatch a candidate with jobs (backward compatibility function)
    
    Args:
        candidate_data: Candidate information
        job_data: List of job offers
        
    Returns:
        Matching results
    """
    engine = SmartMatchEngine()
    
    # Adapt data format
    candidates = [candidate_data]
    companies = job_data
    
    results = engine.match(candidates, companies)
    
    # Convert results to expected format
    adapted_results = []
    for result in results:
        adapted_result = {
            'id': result['company_id'],
            'titre': result['company_name'],
            'matching_score': int(result['score'] * 100),
            'matching_details': result['details'],
            'matching_explanations': result['explanations'],
            'algorithm': 'smartmatch'
        }
        adapted_results.append(adapted_result)
    
    return adapted_results


if __name__ == "__main__":
    # Test SmartMatch engine
    engine = SmartMatchEngine()
    
    test_candidate = {
        'id': 'candidate_1',
        'name': 'Test Candidate',
        'skills': ['Python', 'JavaScript', 'React'],
        'location': 'Paris',
        'experience': 3,
        'remote_preference': 'hybrid'
    }
    
    test_companies = [{
        'id': 'company_1',
        'name': 'Test Company',
        'required_skills': ['Python', 'JavaScript'],
        'location': 'Paris',
        'required_experience': 2,
        'remote_policy': 'hybrid'
    }]
    
    results = engine.match([test_candidate], test_companies)
    
    if results:
        print(f"Test SmartMatch réussi - Score: {results[0]['score']:.2f}")
    else:
        print("Erreur dans le test SmartMatch")
