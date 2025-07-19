import redis
import json
import pickle
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for improved performance"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=False,  # We'll handle encoding ourselves
            health_check_interval=30
        )
        self.default_ttl = 3600  # 1 hour default TTL
        self.key_prefix = "hirify:"
        
    def _make_key(self, key: str) -> str:
        """Generate a prefixed cache key"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value).encode('utf-8')
        else:
            return pickle.dumps(value)
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from Redis"""
        try:
            # Try JSON first (for simple types)
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle for complex objects
            return pickle.loads(value)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL"""
        try:
            cache_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            
            if ttl is None:
                ttl = self.default_ttl
            
            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl})")
            return result
            
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            cache_key = self._make_key(key)
            cached_value = self.redis_client.get(cache_key)
            
            if cached_value is None:
                logger.debug(f"Cache MISS: {key}")
                return None
            
            logger.debug(f"Cache HIT: {key}")
            return self._deserialize_value(cached_value)
            
        except Exception as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            cache_key = self._make_key(key)
            result = self.redis_client.delete(cache_key)
            logger.debug(f"Cache DELETE: {key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            cache_key = self._make_key(key)
            return self.redis_client.exists(cache_key) > 0
            
        except Exception as e:
            logger.error(f"Cache EXISTS error for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            cache_key = self._make_key(key)
            result = self.redis_client.expire(cache_key, ttl)
            logger.debug(f"Cache EXPIRE: {key} (TTL: {ttl})")
            return result
            
        except Exception as e:
            logger.error(f"Cache EXPIRE error for key {key}: {e}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache"""
        try:
            cache_key = self._make_key(key)
            result = self.redis_client.incr(cache_key, amount)
            logger.debug(f"Cache INCR: {key} by {amount}")
            return result
            
        except Exception as e:
            logger.error(f"Cache INCR error for key {key}: {e}")
            return 0
    
    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in cache"""
        try:
            cache_key = self._make_key(key)
            result = self.redis_client.decr(cache_key, amount)
            logger.debug(f"Cache DECR: {key} by {amount}")
            return result
            
        except Exception as e:
            logger.error(f"Cache DECR error for key {key}: {e}")
            return 0
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        try:
            cache_pattern = self._make_key(pattern)
            keys = self.redis_client.keys(cache_pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.debug(f"Cache FLUSH PATTERN: {pattern} ({result} keys deleted)")
                return result
            return 0
            
        except Exception as e:
            logger.error(f"Cache FLUSH PATTERN error for pattern {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, callable_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using callable function"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Value not in cache, compute and cache it
        try:
            value = callable_func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Cache GET_OR_SET error for key {key}: {e}")
            return None
    
    def cache_resume_data(self, resume_id: int, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache resume data"""
        return self.set(f"resume:{resume_id}", data, ttl)
    
    def get_cached_resume_data(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """Get cached resume data"""
        return self.get(f"resume:{resume_id}")
    
    def cache_job_data(self, job_id: int, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache job description data"""
        return self.set(f"job:{job_id}", data, ttl)
    
    def get_cached_job_data(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get cached job description data"""
        return self.get(f"job:{job_id}")
    
    def cache_match_result(self, resume_id: int, job_id: int, match_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache match result"""
        return self.set(f"match:{resume_id}:{job_id}", match_data, ttl)
    
    def get_cached_match_result(self, resume_id: int, job_id: int) -> Optional[Dict[str, Any]]:
        """Get cached match result"""
        return self.get(f"match:{resume_id}:{job_id}")
    
    def cache_skills_extraction(self, text_hash: str, skills: List[str], ttl: int = 7200) -> bool:
        """Cache skills extraction result"""
        return self.set(f"skills:{text_hash}", skills, ttl)
    
    def get_cached_skills_extraction(self, text_hash: str) -> Optional[List[str]]:
        """Get cached skills extraction result"""
        return self.get(f"skills:{text_hash}")
    
    def cache_similarity_score(self, text1_hash: str, text2_hash: str, score: float, ttl: int = 3600) -> bool:
        """Cache similarity score"""
        # Create deterministic key regardless of text order
        combined_hash = hashlib.md5(f"{min(text1_hash, text2_hash)}:{max(text1_hash, text2_hash)}".encode()).hexdigest()
        return self.set(f"similarity:{combined_hash}", score, ttl)
    
    def get_cached_similarity_score(self, text1_hash: str, text2_hash: str) -> Optional[float]:
        """Get cached similarity score"""
        combined_hash = hashlib.md5(f"{min(text1_hash, text2_hash)}:{max(text1_hash, text2_hash)}".encode()).hexdigest()
        return self.get(f"similarity:{combined_hash}")
    
    def cache_document_text(self, file_path: str, text: str, ttl: int = 86400) -> bool:
        """Cache extracted document text"""
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.set(f"document:{file_hash}", text, ttl)
    
    def get_cached_document_text(self, file_path: str) -> Optional[str]:
        """Get cached document text"""
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.get(f"document:{file_hash}")
    
    def cache_search_results(self, query_hash: str, results: List[Dict[str, Any]], ttl: int = 600) -> bool:
        """Cache search results"""
        return self.set(f"search:{query_hash}", results, ttl)
    
    def get_cached_search_results(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        return self.get(f"search:{query_hash}")
    
    def cache_system_stats(self, stats: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache system statistics"""
        return self.set("system:stats", stats, ttl)
    
    def get_cached_system_stats(self) -> Optional[Dict[str, Any]]:
        """Get cached system statistics"""
        return self.get("system:stats")
    
    def invalidate_resume_cache(self, resume_id: int) -> bool:
        """Invalidate all cache entries related to a resume"""
        patterns = [
            f"resume:{resume_id}",
            f"match:{resume_id}:*",
            f"match:*:{resume_id}"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.flush_pattern(pattern)
        
        logger.info(f"Invalidated {total_deleted} cache entries for resume {resume_id}")
        return total_deleted > 0
    
    def invalidate_job_cache(self, job_id: int) -> bool:
        """Invalidate all cache entries related to a job"""
        patterns = [
            f"job:{job_id}",
            f"match:*:{job_id}",
            f"match:{job_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.flush_pattern(pattern)
        
        logger.info(f"Invalidated {total_deleted} cache entries for job {job_id}")
        return total_deleted > 0
    
    def warm_cache(self) -> Dict[str, int]:
        """Warm up frequently accessed cache entries"""
        logger.info("Starting cache warming...")
        
        # This would typically be called after system startup
        # Implementation depends on your specific caching strategy
        
        warmed_entries = {
            "system_stats": 0,
            "recent_matches": 0,
            "popular_skills": 0
        }
        
        try:
            # Warm system stats
            if not self.exists("system:stats"):
                # This would call your stats service
                warmed_entries["system_stats"] = 1
            
            # Add more warming logic as needed
            
        except Exception as e:
            logger.error(f"Error during cache warming: {e}")
        
        logger.info(f"Cache warming completed: {warmed_entries}")
        return warmed_entries
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics and info"""
        try:
            info = self.redis_client.info()
            
            # Get number of keys with our prefix
            our_keys = self.redis_client.keys(f"{self.key_prefix}*")
            
            return {
                "connected": self.redis_client.ping(),
                "total_keys": len(our_keys),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0),
                "cache_hits": info.get("keyspace_hits", 0),
                "cache_misses": info.get("keyspace_misses", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {"error": str(e)}
    
    def clear_all_cache(self) -> bool:
        """Clear all cache entries (use with caution)"""
        try:
            keys = self.redis_client.keys(f"{self.key_prefix}*")
            if keys:
                result = self.redis_client.delete(*keys)
                logger.warning(f"Cleared {result} cache entries")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
