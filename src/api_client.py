import requests
from typing import Optional, Dict, Any, Callable
import time
import streamlit as st
from functools import wraps
import random

class APIClient:
    """Handles API requests with retry logic and rate limiting."""
    
    def __init__(
        self,
        base_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize the API client.
        
        Args:
            base_retries: Number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            rate_limit_delay: Delay after rate limit detection
        """
        self.base_retries = base_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
    
    def _with_retry(func: Callable) -> Callable:
        """Decorator to add retry logic to API calls."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            delay = self.base_delay
            
            for attempt in range(self.base_retries):
                try:
                    return func(self, *args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit
                        time.sleep(self.rate_limit_delay)
                    last_exception = e
                except Exception as e:
                    last_exception = e
                
                # Exponential backoff with jitter
                delay = min(delay * 2 + random.uniform(0, 1), self.max_delay)
                time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    
    @_with_retry
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Perform GET request with retry logic.
        
        Args:
            url: Request URL
            headers: Optional request headers
            params: Optional URL parameters
            
        Returns:
            Response object
        """
        # Log request details for debugging
        st.info(f"Making GET request to: {url}")
        if params:
            st.info(f"With parameters: {params}")
            
        response = self.session.get(url, headers=headers, params=params)
        
        # Log response details
        st.info(f"Response status code: {response.status_code}")
        st.info(f"Response content type: {response.headers.get('content-type', 'unknown')}")
        response.raise_for_status()
        return response
    
    @_with_retry
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Perform POST request with retry logic.
        
        Args:
            url: Request URL
            data: Request data
            headers: Optional request headers
            
        Returns:
            Response object
        """
        response = self.session.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    
    def close(self):
        """Close the session."""
        self.session.close()
