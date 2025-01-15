from typing import Optional, Any, Dict
import json
import os
from datetime import datetime, timedelta
import streamlit as st

class CacheManager:
    """Manages caching of API responses and analysis results."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize the cache manager."""
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate a safe filename for the cache key."""
        return os.path.join(self.cache_dir, f"{key.replace('/', '_')}.json")
    
    def get(self, key: str, max_age: Optional[timedelta] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache if it exists and is not expired.
        
        Args:
            key: Cache key
            max_age: Maximum age of cached data
            
        Returns:
            Cached data if valid, None otherwise
        """
        try:
            cache_file = self._get_cache_key(key)
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                
            # Check if data is expired
            if max_age:
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time > max_age:
                    return None
                    
            return cached_data['data']
            
        except Exception as e:
            st.warning(f"Cache retrieval failed: {str(e)}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]):
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        try:
            cache_file = self._get_cache_key(key)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            st.warning(f"Cache storage failed: {str(e)}")
    
    def invalidate(self, key: str):
        """
        Remove item from cache.
        
        Args:
            key: Cache key to invalidate
        """
        try:
            cache_file = self._get_cache_key(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        except Exception as e:
            st.warning(f"Cache invalidation failed: {str(e)}")
    
    def clear(self):
        """Clear all cached data."""
        try:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            st.warning(f"Cache clear failed: {str(e)}")
