"""
Session A3 - Matching Service Critical Path Optimization
Target: -25% response time for job-CV matching
"""

import asyncio
import time
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import hashlib

class OptimizedMatchingEngine:
    def __init__(self, redis_pool, db_pool):
        self.redis_pool = redis_pool
        self.db_pool = db_pool
        self.vectorizer = None
        self.skills_cache = {}
        
    async def initialize(self):
        """Initialize the matching engine with pre-computed data"""
        # Load or create TF-IDF vectorizer
        await self.load_or_create_vectorizer()
        
        # Pre-cache common skills
        await self.preload_skills_cache()
    
    async def find_best_matches_optimized(
        self, 
        cv_id: int, 
        job_ids: List[int], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Optimized matching with multiple performance improvements"""
        
        start_time = time.time()
        
        # Step 1: Check cache for recent matches
        cache_key = f"matches:{cv_id}:{hash(tuple(sorted(job_ids)))}"
        cached_matches = await self.get_cached_matches(cache_key)
        
        if cached_matches:
            return cached_matches[:limit]
        
        # Step 2: Parallel data fetching
        cv_data_task = self.get_cv_data_optimized(cv_id)
        jobs_data_task = self.get_jobs_data_batch(job_ids)
        
        cv_data, jobs_data = await asyncio.gather(cv_data_task, jobs_data_task)
        
        # Step 3: Vectorized similarity calculation
        matches = await self.calculate_similarity_vectorized(cv_data, jobs_data)
        
        # Step 4: Sort and limit results
        sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)[:limit]
        
        # Step 5: Cache results asynchronously
        asyncio.create_task(self.cache_matches(cache_key, sorted_matches))
        
        processing_time = time.time() - start_time
        
        # Add metadata
        for match in sorted_matches:
            match['processing_time'] = processing_time
            match['optimization'] = 'session_a3_vectorized'
        
        return sorted_matches
    
    async def calculate_similarity_vectorized(
        self, 
        cv_data: Dict[str, Any], 
        jobs_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Vectorized similarity calculation for speed"""
        
        # Prepare text data for vectorization
        cv_text = self.prepare_cv_text(cv_data)
        job_texts = [self.prepare_job_text(job) for job in jobs_data]
        
        # Combine all texts for vectorization
        all_texts = [cv_text] + job_texts
        
        # Use asyncio to run CPU-intensive work in thread pool
        loop = asyncio.get_event_loop()
        
        # Vectorize all texts at once
        tfidf_matrix = await loop.run_in_executor(
            None,
            self.vectorizer.fit_transform,
            all_texts
        )
        
        # Calculate cosine similarities
        similarities = await loop.run_in_executor(
            None,
            cosine_similarity,
            tfidf_matrix[0:1],  # CV vector
            tfidf_matrix[1:]    # Job vectors
        )
        
        # Prepare results
        matches = []
        for i, job_data in enumerate(jobs_data):
            base_score = float(similarities[0][i])
            
            # Apply additional scoring factors
            final_score = await self.apply_scoring_factors(
                cv_data, job_data, base_score
            )
            
            matches.append({
                'job_id': job_data['id'],
                'cv_id': cv_data['id'],
                'score': round(final_score * 100, 2),  # Convert to percentage
                'base_similarity': round(base_score, 3),
                'timestamp': time.time()
            })
        
        return matches
    
    async def apply_scoring_factors(
        self, 
        cv_data: Dict[str, Any], 
        job_data: Dict[str, Any], 
        base_score: float
    ) -> float:
        """Apply additional scoring factors efficiently"""
        
        # Experience level matching (quick calculation)
        experience_factor = self.calculate_experience_factor(
            cv_data.get('years_experience', 0),
            job_data.get('required_experience', 0)
        )
        
        # Location matching (if available)
        location_factor = self.calculate_location_factor(
            cv_data.get('location', ''),
            job_data.get('location', '')
        )
        
        # Skills overlap (pre-calculated when possible)
        skills_factor = await self.calculate_skills_overlap_fast(
            cv_data.get('skills', []),
            job_data.get('required_skills', [])
        )
        
        # Weighted final score
        final_score = (
            base_score * 0.5 +           # Text similarity
            skills_factor * 0.3 +        # Skills match
            experience_factor * 0.15 +   # Experience match
            location_factor * 0.05       # Location match
        )
        
        return min(final_score, 1.0)  # Cap at 1.0
    
    async def calculate_skills_overlap_fast(
        self, 
        cv_skills: List[str], 
        job_skills: List[str]
    ) -> float:
        """Fast skills overlap calculation with caching"""
        
        # Create cache key for this skills combination
        skills_key = hashlib.md5(
            f"{sorted(cv_skills)}:{sorted(job_skills)}".encode()
        ).hexdigest()
        
        # Check cache first
        if skills_key in self.skills_cache:
            return self.skills_cache[skills_key]
        
        # Calculate overlap
        cv_skills_set = set(skill.lower().strip() for skill in cv_skills)
        job_skills_set = set(skill.lower().strip() for skill in job_skills)
        
        if not job_skills_set:
            overlap = 0.0
        else:
            overlap = len(cv_skills_set & job_skills_set) / len(job_skills_set)
        
        # Cache result
        self.skills_cache[skills_key] = overlap
        
        return overlap
    
    def calculate_experience_factor(self, cv_experience: int, required_experience: int) -> float:
        """Quick experience matching calculation"""
        if required_experience == 0:
            return 1.0
        
        ratio = cv_experience / required_experience
        
        if ratio >= 1.0:
            return 1.0
        elif ratio >= 0.8:
            return 0.9
        elif ratio >= 0.6:
            return 0.7
        elif ratio >= 0.4:
            return 0.5
        else:
            return 0.2
    
    def calculate_location_factor(self, cv_location: str, job_location: str) -> float:
        """Quick location matching"""
        if not cv_location or not job_location:
            return 0.5  # Neutral if no location data
        
        # Simple string matching (can be enhanced with geocoding)
        cv_location_clean = cv_location.lower().strip()
        job_location_clean = job_location.lower().strip()
        
        if cv_location_clean == job_location_clean:
            return 1.0
        elif cv_location_clean in job_location_clean or job_location_clean in cv_location_clean:
            return 0.8
        else:
            return 0.3  # Remote work penalty
    
    def prepare_cv_text(self, cv_data: Dict[str, Any]) -> str:
        """Prepare CV text for vectorization"""
        text_parts = []
        
        # Add skills
        if 'skills' in cv_data:
            text_parts.extend(cv_data['skills'])
        
        # Add experience descriptions
        if 'experience' in cv_data:
            for exp in cv_data['experience']:
                if isinstance(exp, dict) and 'description' in exp:
                    text_parts.append(exp['description'])
        
        # Add education
        if 'education' in cv_data:
            for edu in cv_data['education']:
                if isinstance(edu, dict):
                    text_parts.extend([
                        edu.get('degree', ''),
                        edu.get('field', ''),
                        edu.get('institution', '')
                    ])
        
        return ' '.join(filter(None, text_parts))
    
    def prepare_job_text(self, job_data: Dict[str, Any]) -> str:
        """Prepare job text for vectorization"""
        text_parts = []
        
        # Add job description
        if 'description' in job_data:
            text_parts.append(job_data['description'])
        
        # Add required skills
        if 'required_skills' in job_data:
            text_parts.extend(job_data['required_skills'])
        
        # Add requirements
        if 'requirements' in job_data:
            text_parts.append(job_data['requirements'])
        
        return ' '.join(filter(None, text_parts))
    
    async def get_cv_data_optimized(self, cv_id: int) -> Dict[str, Any]:
        """Get CV data with optimized query"""
        async with self.db_pool.acquire() as conn:
            cv_data = await conn.fetchrow("""
                SELECT id, skills, experience, education, years_experience, location
                FROM cvs 
                WHERE id = $1
            """, cv_id)
            
            return dict(cv_data) if cv_data else {}
    
    async def get_jobs_data_batch(self, job_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple jobs data in a single query"""
        async with self.db_pool.acquire() as conn:
            jobs_data = await conn.fetch("""
                SELECT id, description, required_skills, requirements, required_experience, location
                FROM jobs 
                WHERE id = ANY($1)
            """, job_ids)
            
            return [dict(job) for job in jobs_data]
    
    async def get_cached_matches(self, cache_key: str) -> List[Dict[str, Any]]:
        """Get cached matching results"""
        try:
            cached_data = await self.redis_pool.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            logging.error(f"Cache retrieval error: {e}")
        
        return None
    
    async def cache_matches(self, cache_key: str, matches: List[Dict[str, Any]]):
        """Cache matching results"""
        try:
            serialized_data = pickle.dumps(matches)
            await self.redis_pool.setex(cache_key, 1800, serialized_data)  # 30 minutes
        except Exception as e:
            logging.error(f"Cache storage error: {e}")
    
    async def load_or_create_vectorizer(self):
        """Load existing vectorizer or create new one"""
        try:
            # Try to load from cache
            vectorizer_data = await self.redis_pool.get("tfidf_vectorizer")
            if vectorizer_data:
                self.vectorizer = pickle.loads(vectorizer_data)
            else:
                # Create new vectorizer
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    lowercase=True
                )
                
        except Exception as e:
            logging.error(f"Vectorizer initialization error: {e}")
            # Fallback to simple vectorizer
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    async def preload_skills_cache(self):
        """Preload common skills combinations"""
        # This would be populated with frequent skills combinations
        # from your actual data patterns
        pass
