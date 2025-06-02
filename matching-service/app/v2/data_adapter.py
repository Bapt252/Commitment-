"""
SuperSmartMatch V2 - Data Format Adapter

Unified data format converter that bridges between different algorithm formats
while maintaining the integrity of the original 40K lines Nexten Matcher.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UnifiedCandidateProfile:
    """Unified candidate profile format for V2"""
    # Core Information
    id: str
    name: str
    email: str
    
    # Profile Data
    technical_skills: List[Dict[str, Any]]
    soft_skills: List[Dict[str, Any]]
    experiences: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    
    # Enhanced V2 Fields
    questionnaire_responses: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    mobility_preferences: str = "flexible"
    availability: str = "immediate"
    salary_expectation: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass 
class UnifiedCompanyOffer:
    """Unified company offer format for V2"""
    # Core Information
    id: str
    company_name: str
    position_title: str
    
    # Job Requirements
    required_skills: List[Dict[str, Any]]
    preferred_skills: List[Dict[str, Any]]
    experience_requirements: Dict[str, Any]
    
    # Enhanced V2 Fields
    company_questionnaire: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    remote_policy: str = "office"
    salary_range: Optional[Dict[str, Any]] = None
    contract_type: str = "permanent"
    
    # Job Details
    description: str = ""
    requirements: List[str] = None
    benefits: List[str] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class UnifiedMatchingConfig:
    """Unified matching configuration for all algorithms"""
    # Algorithm Selection
    algorithm_preference: str = "auto"
    enable_fallback: bool = True
    
    # Performance Settings
    max_response_time_ms: int = 100
    cache_enabled: bool = True
    
    # Scoring Weights
    skill_weight: float = 0.4
    experience_weight: float = 0.3
    location_weight: float = 0.2
    culture_weight: float = 0.1
    
    # Additional Configuration
    questionnaire_weight: float = 0.5
    semantic_analysis_enabled: bool = True
    geographical_optimization: bool = True
    
    # V2 Extensions
    context_data: Optional[Dict[str, Any]] = None
    custom_weights: Optional[Dict[str, float]] = None

@dataclass
class UnifiedMatchingResult:
    """Unified matching result format"""
    # Core Result
    offer_id: str
    candidate_id: str
    
    # Scoring
    overall_score: float
    confidence: float
    
    # Detailed Breakdown
    skill_match_score: float
    experience_match_score: float
    location_match_score: float
    culture_match_score: float
    questionnaire_match_score: Optional[float] = None
    
    # Analysis Details
    matched_skills: List[Dict[str, Any]] = None
    missing_skills: List[str] = None
    experience_analysis: Dict[str, Any] = None
    location_analysis: Dict[str, Any] = None
    
    # Algorithm Metadata
    algorithm_used: str = ""
    processing_time_ms: float = 0.0
    explanation: str = ""
    
    # V2 Extensions
    insights: List[str] = None
    recommendations: List[str] = None
    risk_factors: List[str] = None

class DataFormatAdapter:
    """
    Universal data format adapter that converts between different algorithm formats
    while preserving the integrity of data and maintaining performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._conversion_cache = {}
        self._cache_enabled = self.config.get('cache_enabled', True)
        self._max_cache_size = self.config.get('max_cache_size', 1000)
        
        logger.info("DataFormatAdapter initialized with caching: %s", self._cache_enabled)
    
    # ==============================
    # PUBLIC API METHODS
    # ==============================
    
    async def prepare_data_for_algorithm(self,
                                       candidate_data: Dict[str, Any],
                                       offers_data: List[Dict[str, Any]],
                                       algorithm_type: str,
                                       additional_data: Optional[Dict[str, Any]] = None) -> Tuple[Any, Any, Any]:
        """
        Prepare data in the format expected by the specified algorithm.
        
        Args:
            candidate_data: Raw candidate data
            offers_data: Raw offers data
            algorithm_type: Target algorithm type
            additional_data: Additional data like questionnaires
            
        Returns:
            Tuple of (prepared_candidate, prepared_offers, prepared_config)
        """
        
        additional_data = additional_data or {}
        
        # Add questionnaire data to candidate and offers
        enhanced_candidate = candidate_data.copy()
        if additional_data.get('candidate_questionnaire'):
            enhanced_candidate['questionnaire_responses'] = additional_data['candidate_questionnaire']
        
        enhanced_offers = []
        company_questionnaires = additional_data.get('company_questionnaires', [])
        for i, offer in enumerate(offers_data):
            enhanced_offer = offer.copy()
            if i < len(company_questionnaires) and company_questionnaires[i]:
                enhanced_offer['company_questionnaire'] = company_questionnaires[i]
            enhanced_offers.append(enhanced_offer)
        
        if algorithm_type == "nexten":
            return await self._prepare_for_nexten(enhanced_candidate, enhanced_offers, additional_data)
        elif algorithm_type in ["smart", "enhanced", "semantic", "hybrid"]:
            return await self._prepare_for_legacy(enhanced_candidate, enhanced_offers, algorithm_type)
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    def normalize_results(self, results: List[Any], algorithm_type: str) -> List[UnifiedMatchingResult]:
        """
        Normalize results from any algorithm to unified format.
        
        Args:
            results: Raw results from algorithm
            algorithm_type: Source algorithm type
            
        Returns:
            List of unified matching results
        """
        
        if algorithm_type == "nexten":
            return self._normalize_nexten_results(results)
        elif algorithm_type in ["smart", "enhanced", "semantic", "hybrid"]:
            return self._normalize_legacy_results(results, algorithm_type)
        else:
            logger.warning(f"Unknown algorithm type for normalization: {algorithm_type}")
            return self._create_fallback_results(results)
    
    # ==============================
    # NEXTEN MATCHER INTEGRATION
    # ==============================
    
    async def _prepare_for_nexten(self, candidate_data: Dict, offers_data: List[Dict], 
                                additional_data: Dict) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Convert data to Nexten Matcher format (preserving 40K lines logic).
        
        Nexten expects: {cv: {...}, questionnaire: {...}}
        """
        
        # Nexten Candidate Format
        nexten_candidate = {
            'cv': {
                'personal_info': {
                    'name': candidate_data.get('name', ''),
                    'email': candidate_data.get('email', ''),
                    'phone': candidate_data.get('phone', ''),
                    'location': self._convert_location(candidate_data.get('location', {}))
                },
                'experiences': self._convert_experiences_for_nexten(candidate_data.get('experiences', [])),
                'skills': self._convert_skills_for_nexten(
                    candidate_data.get('technical_skills', []) + 
                    candidate_data.get('soft_skills', [])
                ),
                'education': self._convert_education_for_nexten(candidate_data.get('education', [])),
                'languages': candidate_data.get('languages', []),
                'certifications': candidate_data.get('certifications', [])
            },
            'questionnaire': candidate_data.get('questionnaire_responses', {}),
            'preferences': {
                'mobility': candidate_data.get('mobility_preferences', 'flexible'),
                'salary_expectation': candidate_data.get('salary_expectation'),
                'availability': candidate_data.get('availability', 'immediate'),
                'remote_work': candidate_data.get('remote_work_preference', 'hybrid')
            }
        }
        
        # Nexten Offers Format
        nexten_offers = []
        for offer in offers_data:
            nexten_offer = {
                'job_info': {
                    'id': offer.get('id', ''),
                    'title': offer.get('position_title', ''),
                    'description': offer.get('description', ''),
                    'requirements': offer.get('requirements', []),
                    'location': self._convert_location(offer.get('location', {})),
                    'remote_policy': offer.get('remote_policy', 'office')
                },
                'company_info': {
                    'name': offer.get('company_name', ''),
                    'sector': offer.get('sector', ''),
                    'size': offer.get('company_size', ''),
                    'culture': offer.get('company_culture', {})
                },
                'requirements': {
                    'required_skills': self._convert_skills_for_nexten(
                        offer.get('required_skills', [])
                    ),
                    'preferred_skills': self._convert_skills_for_nexten(
                        offer.get('preferred_skills', [])
                    ),
                    'experience': offer.get('experience_requirements', {}),
                    'education': offer.get('education_requirements', {})
                },
                'questionnaire': offer.get('company_questionnaire', {}),
                'conditions': {
                    'salary_range': offer.get('salary_range', {}),
                    'contract_type': offer.get('contract_type', 'permanent'),
                    'benefits': offer.get('benefits', [])
                }
            }
            nexten_offers.append(nexten_offer)
        
        # Nexten Configuration
        nexten_config = {
            'algorithm': 'nexten',
            'enable_questionnaire_matching': bool(
                nexten_candidate.get('questionnaire') and 
                any(offer.get('questionnaire') for offer in nexten_offers)
            ),
            'weights': {
                'skills': 0.4,
                'experience': 0.3,
                'location': 0.2,
                'questionnaire': 0.1
            },
            'performance': {
                'max_processing_time_ms': 80,  # Leave buffer for overall <100ms target
                'enable_caching': True,
                'enable_parallel_processing': True
            }
        }
        
        return nexten_candidate, nexten_offers, nexten_config
    
    def _convert_experiences_for_nexten(self, experiences: List[Dict]) -> List[Dict]:
        """Convert experiences to Nexten format"""
        nexten_experiences = []
        
        for exp in experiences:
            nexten_exp = {
                'company': exp.get('company', ''),
                'position': exp.get('position', ''),
                'duration_months': exp.get('duration_months', 0),
                'start_date': exp.get('start_date', ''),
                'end_date': exp.get('end_date', ''),
                'description': exp.get('description', ''),
                'skills_used': exp.get('skills_used', []),
                'achievements': exp.get('achievements', []),
                'responsibilities': exp.get('responsibilities', []),
                'sector': exp.get('sector', ''),
                'team_size': exp.get('team_size', 0),
                'technologies': exp.get('technologies', [])
            }
            nexten_experiences.append(nexten_exp)
        
        return nexten_experiences
    
    def _convert_skills_for_nexten(self, skills: List[Dict]) -> List[Dict]:
        """Convert skills to Nexten format"""
        nexten_skills = []
        
        for skill in skills:
            if isinstance(skill, str):
                # Simple string skill
                nexten_skill = {
                    'name': skill,
                    'level': 'intermediate',
                    'years_experience': 1,
                    'category': 'general',
                    'verified': False
                }
            else:
                # Detailed skill object
                nexten_skill = {
                    'name': skill.get('name', ''),
                    'level': skill.get('level', 'intermediate'),
                    'years_experience': skill.get('years_experience', 1),
                    'category': skill.get('category', 'technical'),
                    'verified': skill.get('verified', False),
                    'certifications': skill.get('certifications', []),
                    'last_used': skill.get('last_used', ''),
                    'proficiency_score': skill.get('proficiency_score', 0.5)
                }
            
            nexten_skills.append(nexten_skill)
        
        return nexten_skills
    
    def _convert_education_for_nexten(self, education: List[Dict]) -> List[Dict]:
        """Convert education to Nexten format"""
        nexten_education = []
        
        for edu in education:
            nexten_edu = {
                'degree': edu.get('degree', ''),
                'field': edu.get('field', ''),
                'institution': edu.get('institution', ''),
                'graduation_year': edu.get('graduation_year', 0),
                'grade': edu.get('grade', ''),
                'honors': edu.get('honors', []),
                'relevant_courses': edu.get('relevant_courses', []),
                'thesis_topic': edu.get('thesis_topic', ''),
                'gpa': edu.get('gpa', 0.0)
            }
            nexten_education.append(nexten_edu)
        
        return nexten_education
    
    def _normalize_nexten_results(self, nexten_results: List[Dict]) -> List[UnifiedMatchingResult]:
        """Convert Nexten results to unified format"""
        unified_results = []
        
        for result in nexten_results:
            unified_result = UnifiedMatchingResult(
                offer_id=result.get('offer_id', ''),
                candidate_id=result.get('candidate_id', ''),
                overall_score=result.get('overall_score', 0.0),
                confidence=result.get('confidence', 0.8),
                skill_match_score=result.get('skills_score', 0.0),
                experience_match_score=result.get('experience_score', 0.0),
                location_match_score=result.get('location_score', 0.0),
                culture_match_score=result.get('culture_score', 0.0),
                questionnaire_match_score=result.get('questionnaire_score'),
                matched_skills=result.get('matched_skills', []),
                missing_skills=result.get('missing_skills', []),
                experience_analysis=result.get('experience_analysis', {}),
                location_analysis=result.get('location_analysis', {}),
                algorithm_used='nexten',
                processing_time_ms=result.get('processing_time_ms', 0.0),
                explanation=result.get('explanation', 'Advanced ML analysis with questionnaires'),
                insights=result.get('insights', []),
                recommendations=result.get('recommendations', []),
                risk_factors=result.get('risk_factors', [])
            )
            unified_results.append(unified_result)
        
        return unified_results
    
    # ==============================
    # LEGACY ALGORITHMS INTEGRATION
    # ==============================
    
    async def _prepare_for_legacy(self, candidate_data: Dict, offers_data: List[Dict], 
                                algorithm_type: str) -> Tuple[Any, Any, Any]:
        """
        Convert data for legacy algorithms (Smart, Enhanced, Semantic, Hybrid).
        
        These algorithms expect the traditional CandidateProfile/CompanyOffer format.
        """
        
        # For legacy algorithms, we'll need to import the model classes
        # and convert our unified format to their expected format
        
        from ..models.candidate import CandidateProfile
        from ..models.job import CompanyOffer
        from ..models.matching import MatchingConfig
        
        # Convert candidate data
        legacy_candidate = CandidateProfile(
            id=candidate_data.get('id', ''),
            name=candidate_data.get('name', ''),
            email=candidate_data.get('email', ''),
            technical_skills=candidate_data.get('technical_skills', []),
            soft_skills=candidate_data.get('soft_skills', []),
            experiences=candidate_data.get('experiences', []),
            education=candidate_data.get('education', []),
            location=candidate_data.get('location', {}),
            mobility_preferences=candidate_data.get('mobility_preferences', 'flexible')
        )
        
        # Convert offers data
        legacy_offers = []
        for offer in offers_data:
            legacy_offer = CompanyOffer(
                id=offer.get('id', ''),
                company_name=offer.get('company_name', ''),
                position_title=offer.get('position_title', ''),
                required_skills=offer.get('required_skills', []),
                preferred_skills=offer.get('preferred_skills', []),
                experience_requirements=offer.get('experience_requirements', {}),
                location=offer.get('location', {}),
                salary_range=offer.get('salary_range', {}),
                description=offer.get('description', ''),
                requirements=offer.get('requirements', [])
            )
            legacy_offers.append(legacy_offer)
        
        # Create configuration
        legacy_config = MatchingConfig(
            algorithm=algorithm_type,
            skill_weight=0.4,
            experience_weight=0.3,
            location_weight=0.2,
            questionnaire_weight=0.1 if algorithm_type in ['enhanced', 'semantic'] else 0.0
        )
        
        return legacy_candidate, legacy_offers, legacy_config
    
    def _normalize_legacy_results(self, legacy_results: List[Any], algorithm_type: str) -> List[UnifiedMatchingResult]:
        """Convert legacy algorithm results to unified format"""
        unified_results = []
        
        for result in legacy_results:
            # Legacy results might be in different formats, so we need to handle gracefully
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                # Try to extract common attributes
                result_dict = {
                    'offer_id': getattr(result, 'offer_id', ''),
                    'match_score': getattr(result, 'match_score', 0.0),
                    'confidence_score': getattr(result, 'confidence_score', 0.5)
                }
            
            unified_result = UnifiedMatchingResult(
                offer_id=result_dict.get('offer_id', ''),
                candidate_id=result_dict.get('candidate_id', ''),
                overall_score=result_dict.get('match_score', result_dict.get('overall_score', 0.0)),
                confidence=result_dict.get('confidence_score', result_dict.get('confidence', 0.5)),
                skill_match_score=result_dict.get('skill_matches', 0.0),
                experience_match_score=result_dict.get('experience_match', 0.0),
                location_match_score=result_dict.get('location_compatibility', 0.0),
                culture_match_score=result_dict.get('culture_match', 0.0),
                matched_skills=result_dict.get('skill_matches', []),
                algorithm_used=algorithm_type,
                explanation=f'{algorithm_type.title()} algorithm analysis',
                insights=result_dict.get('insights', []),
                recommendations=result_dict.get('recommendations', [])
            )
            unified_results.append(unified_result)
        
        return unified_results
    
    # ==============================
    # UTILITY METHODS
    # ==============================
    
    def _convert_location(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize location format"""
        return {
            'city': location.get('city', ''),
            'country': location.get('country', ''),
            'region': location.get('region', ''),
            'postal_code': location.get('postal_code', ''),
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'timezone': location.get('timezone', 'UTC')
        }
    
    def _create_fallback_results(self, raw_results: List[Any]) -> List[UnifiedMatchingResult]:
        """Create fallback results when normalization fails"""
        fallback_results = []
        
        for i, result in enumerate(raw_results):
            fallback_result = UnifiedMatchingResult(
                offer_id=f'fallback_{i}',
                candidate_id='unknown',
                overall_score=0.5,
                confidence=0.2,
                skill_match_score=0.5,
                experience_match_score=0.5,
                location_match_score=0.5,
                culture_match_score=0.5,
                algorithm_used='fallback',
                explanation='Fallback result due to normalization error',
                insights=['Manual review recommended']
            )
            fallback_results.append(fallback_result)
        
        return fallback_results
    
    # ==============================
    # LEGACY CONVERSION HELPERS
    # ==============================
    
    def profile_to_dict(self, profile: Any) -> Dict[str, Any]:
        """Convert CandidateProfile object to dictionary"""
        if hasattr(profile, 'to_dict'):
            return profile.to_dict()
        elif hasattr(profile, '__dict__'):
            return profile.__dict__
        else:
            return {}
    
    def offer_to_dict(self, offer: Any) -> Dict[str, Any]:
        """Convert CompanyOffer object to dictionary"""
        if hasattr(offer, 'to_dict'):
            return offer.to_dict()
        elif hasattr(offer, '__dict__'):
            return offer.__dict__
        else:
            return {}
    
    # ==============================
    # PERFORMANCE OPTIMIZATION
    # ==============================
    
    def clear_cache(self) -> None:
        """Clear conversion cache"""
        self._conversion_cache.clear()
        logger.info("DataFormatAdapter cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_enabled': self._cache_enabled,
            'cache_size': len(self._conversion_cache),
            'max_cache_size': self._max_cache_size,
            'cache_keys': list(self._conversion_cache.keys())
        }
