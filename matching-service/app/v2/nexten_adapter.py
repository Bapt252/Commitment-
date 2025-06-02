"""
Nexten Matcher Adapter for SuperSmartMatch V2

Adapts the existing Nexten Matcher (40K lines) to work within the unified architecture.
Provides bidirectional data conversion and caching for optimal performance.
"""

import logging
import asyncio
import hashlib
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from ..algorithms.nexten_matcher import NextenMatcher
from ..models.candidate import CandidateProfile
from ..models.job import CompanyOffer
from ..models.matching import MatchingResult, MatchingConfig

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for matching results"""
    result: List[MatchingResult]
    timestamp: float
    ttl: int
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

class MatchingCache:
    """High-performance cache for matching results"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, candidate_data: Dict, offers_data: List[Dict]) -> str:
        """Generate cache key from input data"""
        # Create deterministic hash of input data
        content = {
            "candidate": candidate_data,
            "offers": sorted(offers_data, key=lambda x: x.get('id', ''))
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    async def get(self, candidate_data: Dict, offers_data: List[Dict]) -> Optional[List[MatchingResult]]:
        """Get cached result if available and not expired"""
        key = self._generate_key(candidate_data, offers_data)
        
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                self.hit_count += 1
                logger.debug(f"Cache HIT for key {key[:8]}...")
                return entry.result
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache EXPIRED for key {key[:8]}...")
        
        self.miss_count += 1
        logger.debug(f"Cache MISS for key {key[:8]}...")
        return None
    
    async def set(self, candidate_data: Dict, offers_data: List[Dict], 
                  result: List[MatchingResult], ttl: Optional[int] = None) -> None:
        """Cache the result"""
        key = self._generate_key(candidate_data, offers_data)
        
        # Evict oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted oldest entry {oldest_key[:8]}...")
        
        self.cache[key] = CacheEntry(
            result=result,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )
        logger.debug(f"Cache SET for key {key[:8]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "expired_entries": sum(1 for entry in self.cache.values() if entry.is_expired())
        }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Cache cleared")

class NextenDataConverter:
    """
    Bidirectional data converter between SuperSmartMatch and Nexten formats.
    
    Handles the format differences:
    - SuperSmartMatch: CandidateProfile/CompanyOffer objects
    - Nexten: Dict[CV+Questionnaire] format
    """
    
    def supersmartmatch_to_nexten_candidate(self, 
                                          candidate: CandidateProfile,
                                          questionnaire: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convert SuperSmartMatch CandidateProfile to Nexten format.
        
        Nexten expects:
        {
            'cv': { personal_info, experience, education, skills, certifications },
            'questionnaire': { user responses }
        }
        """
        
        # Convert experiences
        experiences = []
        for exp in candidate.experiences or []:
            experiences.append({
                "company": getattr(exp, 'company', ''),
                "position": getattr(exp, 'position', ''),
                "duration_months": getattr(exp, 'duration_months', 0),
                "skills": getattr(exp, 'skills', []),
                "achievements": getattr(exp, 'achievements', []),
                "description": getattr(exp, 'description', ''),
                "start_date": getattr(exp, 'start_date', None),
                "end_date": getattr(exp, 'end_date', None)
            })
        
        # Convert education
        education = []
        for edu in candidate.education or []:
            education.append({
                "institution": getattr(edu, 'institution', ''),
                "degree": getattr(edu, 'degree', ''),
                "field": getattr(edu, 'field', ''),
                "graduation_year": getattr(edu, 'graduation_year', None),
                "gpa": getattr(edu, 'gpa', None)
            })
        
        # Build Nexten format
        nexten_candidate = {
            'cv': {
                'personal_info': {
                    'name': candidate.name or '',
                    'email': candidate.email or '',
                    'phone': getattr(candidate, 'phone', ''),
                    'location': candidate.location or '',
                    'summary': getattr(candidate, 'summary', '')
                },
                'experience': experiences,
                'education': education,
                'skills': {
                    'technical': candidate.technical_skills or [],
                    'soft': candidate.soft_skills or [],
                    'languages': candidate.languages or [],
                    'all_skills': candidate.technical_skills + candidate.soft_skills if candidate.technical_skills and candidate.soft_skills else []
                },
                'certifications': candidate.certifications or [],
                'total_experience_months': sum(exp.get('duration_months', 0) for exp in experiences)
            },
            'questionnaire': questionnaire or {}
        }
        
        logger.debug(f"Converted candidate {candidate.name} to Nexten format")
        return nexten_candidate
    
    def supersmartmatch_to_nexten_offer(self, 
                                       offer: CompanyOffer,
                                       company_questionnaire: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convert SuperSmartMatch CompanyOffer to Nexten job format.
        """
        
        nexten_offer = {
            'id': offer.id,
            'title': offer.position_title or '',
            'company': offer.company_name or '',
            'description': getattr(offer, 'description', ''),
            'requirements': {
                'skills': offer.required_skills or [],
                'experience_years': getattr(offer, 'required_experience_years', 0),
                'education_level': getattr(offer, 'required_education_level', ''),
                'certifications': getattr(offer, 'required_certifications', [])
            },
            'location': {
                'city': getattr(offer, 'city', ''),
                'country': getattr(offer, 'country', ''),
                'remote_allowed': getattr(offer, 'remote_allowed', False),
                'hybrid_allowed': getattr(offer, 'hybrid_allowed', False)
            },
            'compensation': {
                'salary_min': getattr(offer, 'salary_min', 0),
                'salary_max': getattr(offer, 'salary_max', 0),
                'currency': getattr(offer, 'currency', 'EUR'),
                'benefits': getattr(offer, 'benefits', [])
            },
            'company_questionnaire': company_questionnaire or {}
        }
        
        logger.debug(f"Converted offer {offer.position_title} at {offer.company_name} to Nexten format")
        return nexten_offer
    
    def nexten_to_supersmartmatch_result(self, 
                                       nexten_result: Dict[str, Any],
                                       original_offer: CompanyOffer) -> MatchingResult:
        """
        Convert Nexten matching result back to SuperSmartMatch MatchingResult.
        
        Nexten returns comprehensive analysis that we map to MatchingResult fields.
        """
        
        # Extract skill matches from Nexten's detailed analysis
        skill_matches = []
        if 'detailed_analysis' in nexten_result:
            skills_analysis = nexten_result['detailed_analysis'].get('skills_matching', {})
            for skill, score in skills_analysis.items():
                skill_matches.append({
                    'skill': skill,
                    'score': score,
                    'category': 'technical'  # Could be enhanced with Nexten's categorization
                })
        
        # Map Nexten's comprehensive scores to SuperSmartMatch format
        result = MatchingResult(
            offer_id=original_offer.id,
            company_name=original_offer.company_name,
            position_title=original_offer.position_title,
            
            # Core matching scores
            match_score=nexten_result.get('match_score', 0.0),
            confidence_score=nexten_result.get('confidence', 0.0),
            
            # Detailed breakdowns
            skill_matches=skill_matches,
            experience_match=nexten_result.get('experience_compatibility', 0.0),
            location_compatibility=nexten_result.get('location_score', 1.0),
            salary_compatibility=nexten_result.get('salary_compatibility', 1.0),
            
            # Nexten's unique insights
            insights=nexten_result.get('insights', []),
            recommendations=nexten_result.get('recommendations', []),
            
            # Metadata
            matching_algorithm="nexten",
            metadata={
                'nexten_version': '2.0',
                'detailed_analysis': nexten_result.get('detailed_analysis', {}),
                'questionnaire_impact': nexten_result.get('questionnaire_contribution', 0.0),
                'ml_features_used': nexten_result.get('ml_features', []),
                'semantic_analysis': nexten_result.get('semantic_scores', {}),
                'execution_time_ms': nexten_result.get('execution_time', 0)
            }
        )
        
        logger.debug(f"Converted Nexten result for {original_offer.position_title} (score: {result.match_score:.2f})")
        return result

class NextenMatcherAdapter:
    """
    Adapter to integrate Nexten Matcher into SuperSmartMatch V2 architecture.
    
    Provides:
    - Unified interface matching SuperSmartMatch API
    - Bidirectional data conversion
    - High-performance caching
    - Error handling and fallbacks
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.nexten_service = NextenMatcher()
        self.data_converter = NextenDataConverter()
        self.cache = MatchingCache(
            max_size=self.config.get('cache_max_size', 1000),
            default_ttl=self.config.get('cache_ttl', 3600)
        )
        
        # Performance tracking
        self.total_requests = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        
        logger.info("NextenMatcherAdapter initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the adapter"""
        return {
            'cache_max_size': 1000,
            'cache_ttl': 3600,  # 1 hour
            'max_execution_time': 150,  # ms
            'enable_cache': True,
            'enable_fallback': True
        }
    
    async def match(self, 
                   candidate: CandidateProfile, 
                   offers: List[CompanyOffer],
                   config: MatchingConfig) -> List[MatchingResult]:
        """
        Main matching interface compatible with SuperSmartMatch API.
        
        Args:
            candidate: Candidate profile in SuperSmartMatch format
            offers: List of job offers in SuperSmartMatch format
            config: Matching configuration including questionnaire data
            
        Returns:
            List of matching results in SuperSmartMatch format
        """
        
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Extract questionnaire data from config
            questionnaire_data = getattr(config, 'questionnaire_data', {})
            candidate_questionnaire = questionnaire_data.get('candidate', {})
            company_questionnaires = questionnaire_data.get('companies', {})
            
            # Convert to Nexten format
            nexten_candidate = self.data_converter.supersmartmatch_to_nexten_candidate(
                candidate, candidate_questionnaire
            )
            
            nexten_offers = [
                self.data_converter.supersmartmatch_to_nexten_offer(
                    offer, 
                    company_questionnaires.get(offer.id, {})
                )
                for offer in offers
            ]
            
            # Check cache if enabled
            if self.config.get('enable_cache', True):
                cached_result = await self.cache.get(nexten_candidate, nexten_offers)
                if cached_result:
                    logger.debug("Returning cached Nexten result")
                    return cached_result
            
            # Execute Nexten matching
            nexten_results = []
            for i, nexten_offer in enumerate(nexten_offers):
                try:
                    result = await self._execute_nexten_match(nexten_candidate, nexten_offer)
                    nexten_results.append(result)
                except Exception as e:
                    logger.error(f"Nexten matching failed for offer {offers[i].id}: {e}")
                    # Create fallback result
                    nexten_results.append(self._create_fallback_result(offers[i]))
                    self.error_count += 1
            
            # Convert results back to SuperSmartMatch format
            matching_results = [
                self.data_converter.nexten_to_supersmartmatch_result(result, offers[i])
                for i, result in enumerate(nexten_results)
            ]
            
            # Cache results if enabled
            if self.config.get('enable_cache', True):
                await self.cache.set(nexten_candidate, nexten_offers, matching_results)
            
            # Track performance
            execution_time = (time.time() - start_time) * 1000  # ms
            self.total_execution_time += execution_time
            
            logger.info(f"Nexten matching completed: {len(matching_results)} results in {execution_time:.1f}ms")
            return matching_results
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"NextenMatcherAdapter error: {e}")
            
            if self.config.get('enable_fallback', True):
                return self._create_fallback_results(offers)
            else:
                raise
    
    async def _execute_nexten_match(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """
        Execute Nexten matching with proper async handling.
        
        Note: The original Nexten matcher might be synchronous, so we handle it appropriately.
        """
        
        # If Nexten's calculate_match is async
        if asyncio.iscoroutinefunction(self.nexten_service.calculate_match):
            result = await self.nexten_service.calculate_match(candidate_data, job_data)
        else:
            # Run synchronous Nexten matching in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.nexten_service.calculate_match, 
                candidate_data, 
                job_data
            )
        
        return result
    
    def _create_fallback_result(self, offer: CompanyOffer) -> Dict[str, Any]:
        """
        Create a fallback result when Nexten matching fails.
        """
        return {
            'match_score': 0.5,  # Neutral score
            'confidence': 0.3,   # Low confidence
            'experience_compatibility': 0.5,
            'location_score': 1.0,
            'salary_compatibility': 1.0,
            'insights': ['Fallback result - Nexten matching unavailable'],
            'recommendations': ['Review manually'],
            'detailed_analysis': {'error': 'Nexten matching failed'},
            'questionnaire_contribution': 0.0,
            'execution_time': 0
        }
    
    def _create_fallback_results(self, offers: List[CompanyOffer]) -> List[MatchingResult]:
        """
        Create fallback results for all offers when adapter fails completely.
        """
        return [
            MatchingResult(
                offer_id=offer.id,
                company_name=offer.company_name,
                position_title=offer.position_title,
                match_score=0.5,
                confidence_score=0.3,
                skill_matches=[],
                experience_match=0.5,
                location_compatibility=1.0,
                salary_compatibility=1.0,
                insights=['Nexten adapter fallback'],
                recommendations=['Manual review required'],
                matching_algorithm="nexten_fallback",
                metadata={'error': 'Nexten adapter failed'}
            )
            for offer in offers
        ]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        """
        avg_execution_time = (
            self.total_execution_time / self.total_requests 
            if self.total_requests > 0 else 0
        )
        
        error_rate = self.error_count / self.total_requests if self.total_requests > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'avg_execution_time_ms': avg_execution_time,
            'error_count': self.error_count,
            'error_rate': error_rate,
            'cache_stats': self.cache.get_stats()
        }
    
    def clear_cache(self) -> None:
        """Clear the matching cache"""
        self.cache.clear()
        logger.info("Nexten adapter cache cleared")
    
    def reset_stats(self) -> None:
        """Reset performance statistics"""
        self.total_requests = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        logger.info("Nexten adapter stats reset")