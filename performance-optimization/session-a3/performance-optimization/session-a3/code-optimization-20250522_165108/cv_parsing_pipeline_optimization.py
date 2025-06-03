"""
Session A3 - CV Parsing Pipeline Optimization
Target: -25% response time for critical path
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
import aioredis
import json

class OptimizedCVParsingPipeline:
    def __init__(self, redis_pool, openai_client):
        self.redis_pool = redis_pool
        self.openai_client = openai_client
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def parse_cv_optimized(self, file_data: bytes, file_name: str) -> Dict[str, Any]:
        """Optimized CV parsing with parallel processing"""
        
        start_time = time.time()
        
        # Step 1: Check cache first (fastest path)
        cache_key = f"cv_parsed:{hash(file_data)}"
        cached_result = await self.redis_pool.get(cache_key)
        
        if cached_result:
            result = json.loads(cached_result)
            result['cache_hit'] = True
            result['response_time'] = time.time() - start_time
            return result
        
        # Step 2: Parallel preprocessing
        preprocessing_tasks = await asyncio.gather(
            self.extract_text_async(file_data),
            self.detect_file_format(file_name),
            self.validate_file_content(file_data)
        )
        
        text_content, file_format, is_valid = preprocessing_tasks
        
        if not is_valid:
            return {'error': 'Invalid file content', 'response_time': time.time() - start_time}
        
        # Step 3: Parallel AI analysis with smart chunking
        analysis_tasks = [
            self.extract_personal_info_fast(text_content),
            self.extract_skills_concurrent(text_content),
            self.extract_experience_concurrent(text_content),
            self.extract_education_concurrent(text_content)
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Step 4: Combine results
        final_result = {
            'personal_info': analysis_results[0],
            'skills': analysis_results[1],
            'experience': analysis_results[2],
            'education': analysis_results[3],
            'file_format': file_format,
            'processing_time': time.time() - start_time,
            'cache_hit': False,
            'optimization_version': 'session_a3'
        }
        
        # Step 5: Cache result asynchronously (fire and forget)
        asyncio.create_task(
            self.cache_result_async(cache_key, final_result)
        )
        
        final_result['response_time'] = time.time() - start_time
        return final_result
    
    async def extract_text_async(self, file_data: bytes) -> str:
        """Extract text using thread pool for CPU-intensive work"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.extract_text_sync, 
            file_data
        )
    
    async def extract_skills_concurrent(self, text: str) -> List[str]:
        """Extract skills with optimized prompt and concurrent processing"""
        
        # Use optimized prompt for faster processing
        optimized_prompt = """Extract skills ONLY. Return JSON array of strings.
        No explanations, no formatting, just: ["skill1", "skill2", ...]
        
        Text: {text}"""
        
        return await self.call_openai_optimized(
            optimized_prompt.format(text=text[:2000]),  # Limit text size
            max_tokens=200  # Smaller response for faster processing
        )
    
    async def extract_experience_concurrent(self, text: str) -> List[Dict[str, Any]]:
        """Extract experience with optimized processing"""
        
        optimized_prompt = """Extract work experience ONLY. Return JSON array.
        Format: [{"company": "X", "position": "Y", "duration": "Z"}]
        
        Text: {text}"""
        
        return await self.call_openai_optimized(
            optimized_prompt.format(text=text[:3000]),
            max_tokens=300
        )
    
    async def extract_education_concurrent(self, text: str) -> List[Dict[str, Any]]:
        """Extract education with optimized processing"""
        
        optimized_prompt = """Extract education ONLY. Return JSON array.
        Format: [{"institution": "X", "degree": "Y", "year": "Z"}]
        
        Text: {text}"""
        
        return await self.call_openai_optimized(
            optimized_prompt.format(text=text[:2000]),
            max_tokens=200
        )
    
    async def extract_personal_info_fast(self, text: str) -> Dict[str, Any]:
        """Fast personal info extraction with regex + AI fallback"""
        
        # Step 1: Try regex patterns first (fastest)
        regex_result = await self.extract_personal_info_regex(text)
        
        # Step 2: If regex didn't find enough, use AI for missing parts only
        if self.is_personal_info_complete(regex_result):
            return regex_result
        
        # Use AI only for missing fields
        missing_fields = self.get_missing_personal_fields(regex_result)
        ai_result = await self.extract_missing_personal_info_ai(text, missing_fields)
        
        # Combine regex and AI results
        return {**regex_result, **ai_result}
    
    async def call_openai_optimized(self, prompt: str, max_tokens: int = 150) -> Any:
        """Optimized OpenAI API call with connection reuse"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Use fastest model for speed
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0,  # Deterministic for caching
                timeout=10  # Shorter timeout for faster failure
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
                
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return []  # Return empty result instead of failing
    
    async def cache_result_async(self, cache_key: str, result: Dict[str, Any]):
        """Cache result asynchronously"""
        try:
            await self.redis_pool.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(result, default=str)
            )
        except Exception as e:
            logging.error(f"Cache error: {e}")
    
    # Helper methods
    def extract_text_sync(self, file_data: bytes) -> str:
        """Synchronous text extraction for thread pool"""
        # Implementation for PDF/DOCX text extraction
        pass
    
    async def detect_file_format(self, filename: str) -> str:
        """Quick file format detection"""
        if filename.lower().endswith('.pdf'):
            return 'pdf'
        elif filename.lower().endswith(('.doc', '.docx')):
            return 'docx'
        else:
            return 'unknown'
    
    async def validate_file_content(self, file_data: bytes) -> bool:
        """Quick file validation"""
        return len(file_data) > 100  # Basic size check
    
    async def extract_personal_info_regex(self, text: str) -> Dict[str, Any]:
        """Fast regex-based personal info extraction"""
        # Implementation with regex patterns
        pass
    
    def is_personal_info_complete(self, info: Dict[str, Any]) -> bool:
        """Check if personal info extraction is complete"""
        required_fields = ['name', 'email', 'phone']
        return all(field in info and info[field] for field in required_fields)
    
    def get_missing_personal_fields(self, current_info: Dict[str, Any]) -> List[str]:
        """Get list of missing personal info fields"""
        # Implementation to identify missing fields
        pass
    
    async def extract_missing_personal_info_ai(self, text: str, missing_fields: List[str]) -> Dict[str, Any]:
        """Use AI to extract only missing personal info fields"""
        # Implementation for targeted AI extraction
        pass

# Performance monitoring decorator
def monitor_performance(func):
    """Monitor function performance for critical path optimization"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations
            if execution_time > 2.0:  # Threshold: 2 seconds
                logging.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Error in {func.__name__} after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper
