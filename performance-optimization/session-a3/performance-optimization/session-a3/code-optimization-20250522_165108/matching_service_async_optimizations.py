"""
Session A3 - Matching Service Async Optimizations
Target: -25% response time through concurrent database operations
"""

import asyncio
import asyncpg
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime

class OptimizedMatchingService:
    def __init__(self, db_pool: asyncpg.Pool, redis_pool):
        self.db_pool = db_pool
        self.redis_pool = redis_pool
    
    async def find_matches_concurrent(self, cv_id: int, job_ids: List[int]) -> List[Dict[str, Any]]:
        """Find matches for CV against multiple jobs concurrently"""
        
        # Concurrent database queries
        async def get_cv_data(cv_id: int) -> Dict[str, Any]:
            async with self.db_pool.acquire() as conn:
                cv_data = await conn.fetchrow(
                    "SELECT skills, experience, education FROM cvs WHERE id = $1", cv_id
                )
                return dict(cv_data) if cv_data else {}
        
        async def get_job_data(job_id: int) -> Dict[str, Any]:
            async with self.db_pool.acquire() as conn:
                job_data = await conn.fetchrow(
                    "SELECT requirements, skills_required, experience_level FROM jobs WHERE id = $1", 
                    job_id
                )
                return dict(job_data) if job_data else {}
        
        async def get_multiple_jobs(job_ids: List[int]) -> List[Dict[str, Any]]:
            async with self.db_pool.acquire() as conn:
                jobs_data = await conn.fetch(
                    "SELECT id, requirements, skills_required, experience_level FROM jobs WHERE id = ANY($1)",
                    job_ids
                )
                return [dict(job) for job in jobs_data]
        
        # Execute concurrent queries
        cv_task = get_cv_data(cv_id)
        jobs_task = get_multiple_jobs(job_ids)
        
        cv_data, jobs_data = await asyncio.gather(cv_task, jobs_task)
        
        # Concurrent matching calculations
        matching_tasks = [
            self.calculate_match_score_async(cv_data, job_data)
            for job_data in jobs_data
        ]
        
        match_scores = await asyncio.gather(*matching_tasks)
        
        # Prepare results
        results = []
        for i, job_data in enumerate(jobs_data):
            results.append({
                'job_id': job_data['id'],
                'cv_id': cv_id,
                'score': match_scores[i],
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Cache results concurrently
        await self.cache_results_async(results)
        
        return results
    
    async def calculate_match_score_async(self, cv_data: Dict, job_data: Dict) -> float:
        """Calculate match score asynchronously"""
        
        # Use thread pool for CPU-intensive calculations
        loop = asyncio.get_event_loop()
        
        async def calculate_skills_match() -> float:
            return await loop.run_in_executor(
                None, 
                self.calculate_skills_similarity,
                cv_data.get('skills', []), 
                job_data.get('skills_required', [])
            )
        
        async def calculate_experience_match() -> float:
            return await loop.run_in_executor(
                None,
                self.calculate_experience_match,
                cv_data.get('experience', []),
                job_data.get('experience_level', '')
            )
        
        # Calculate components concurrently
        skills_score, experience_score = await asyncio.gather(
            calculate_skills_match(),
            calculate_experience_match()
        )
        
        # Weighted final score
        final_score = (skills_score * 0.6) + (experience_score * 0.4)
        return round(final_score, 2)
    
    async def cache_results_async(self, results: List[Dict[str, Any]]):
        """Cache matching results asynchronously"""
        
        async def cache_single_result(result: Dict[str, Any]):
            cache_key = f"match:{result['cv_id']}:{result['job_id']}"
            await self.redis_pool.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(result)
            )
        
        # Cache all results concurrently
        cache_tasks = [cache_single_result(result) for result in results]
        await asyncio.gather(*cache_tasks)
    
    async def bulk_matching_pipeline(self, cv_ids: List[int], job_ids: List[int]) -> List[Dict[str, Any]]:
        """Process bulk matching with optimized pipeline"""
        
        # Batch database queries to reduce round trips
        async def get_bulk_cvs(cv_ids: List[int]) -> Dict[int, Dict[str, Any]]:
            async with self.db_pool.acquire() as conn:
                cvs_data = await conn.fetch(
                    "SELECT id, skills, experience, education FROM cvs WHERE id = ANY($1)",
                    cv_ids
                )
                return {cv['id']: dict(cv) for cv in cvs_data}
        
        async def get_bulk_jobs(job_ids: List[int]) -> Dict[int, Dict[str, Any]]:
            async with self.db_pool.acquire() as conn:
                jobs_data = await conn.fetch(
                    "SELECT id, requirements, skills_required, experience_level FROM jobs WHERE id = ANY($1)",
                    job_ids
                )
                return {job['id']: dict(job) for job in jobs_data}
        
        # Fetch all data concurrently
        cvs_data, jobs_data = await asyncio.gather(
            get_bulk_cvs(cv_ids),
            get_bulk_jobs(job_ids)
        )
        
        # Create all matching tasks
        all_matching_tasks = []
        for cv_id in cv_ids:
            for job_id in job_ids:
                if cv_id in cvs_data and job_id in jobs_data:
                    task = self.calculate_match_score_async(
                        cvs_data[cv_id], 
                        jobs_data[job_id]
                    )
                    all_matching_tasks.append((cv_id, job_id, task))
        
        # Execute all matching calculations concurrently
        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(20)  # Max 20 concurrent calculations
        
        async def calculate_with_semaphore(cv_id: int, job_id: int, task):
            async with semaphore:
                score = await task
                return {
                    'cv_id': cv_id,
                    'job_id': job_id,
                    'score': score,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        limited_tasks = [
            calculate_with_semaphore(cv_id, job_id, task)
            for cv_id, job_id, task in all_matching_tasks
        ]
        
        # Execute all with controlled concurrency
        results = await asyncio.gather(*limited_tasks)
        
        # Cache results concurrently
        await self.cache_results_async(results)
        
        return results
    
    def calculate_skills_similarity(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """CPU-intensive skills similarity calculation"""
        # Implementation for skills matching algorithm
        pass
    
    def calculate_experience_match(self, cv_experience: List[Dict], job_experience_level: str) -> float:
        """CPU-intensive experience matching calculation"""
        # Implementation for experience matching algorithm
        pass

# Database connection pool optimization
async def create_optimized_db_pool() -> asyncpg.Pool:
    """Create optimized database connection pool"""
    return await asyncpg.create_pool(
        host='postgres',
        port=5432,
        user='postgres',
        password='postgres',
        database='nexten',
        min_size=5,        # Minimum connections
        max_size=20,       # Maximum connections
        max_queries=50000, # Max queries per connection
        max_inactive_connection_lifetime=300,  # 5 minutes
        command_timeout=30,  # 30 seconds timeout
    )
