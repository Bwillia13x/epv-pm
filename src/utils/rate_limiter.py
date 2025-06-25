"""
Rate limiting utility for API calls
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
from collections import deque
import logging

class RateLimiter:
    """
    Rate limiter to control API request frequency
    """
    
    def __init__(self, requests_per_minute: int = 30, requests_per_day: int = 500):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Track requests with timestamps
        self.minute_requests: deque = deque()
        self.daily_requests: deque = deque()
        
        # Thread safety
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
    def wait_if_needed(self) -> None:
        """
        Wait if necessary to respect rate limits
        """
        with self.lock:
            now = datetime.now()
            
            # Clean old requests
            self._clean_old_requests(now)
            
            # Check daily limit
            if len(self.daily_requests) >= self.requests_per_day:
                oldest_daily = self.daily_requests[0]
                wait_until = oldest_daily + timedelta(days=1)
                wait_seconds = (wait_until - now).total_seconds()
                
                if wait_seconds > 0:
                    self.logger.warning(f"Daily rate limit reached. Waiting {wait_seconds:.1f} seconds")
                    time.sleep(wait_seconds)
                    return
            
            # Check minute limit
            if len(self.minute_requests) >= self.requests_per_minute:
                oldest_minute = self.minute_requests[0]
                wait_until = oldest_minute + timedelta(minutes=1)
                wait_seconds = (wait_until - now).total_seconds()
                
                if wait_seconds > 0:
                    self.logger.debug(f"Minute rate limit reached. Waiting {wait_seconds:.1f} seconds")
                    time.sleep(wait_seconds)
            
            # Record this request
            now = datetime.now()  # Update time after potential wait
            self.minute_requests.append(now)
            self.daily_requests.append(now)
    
    def _clean_old_requests(self, now: datetime) -> None:
        """Remove requests older than the tracking window"""
        
        # Remove requests older than 1 minute
        minute_cutoff = now - timedelta(minutes=1)
        while self.minute_requests and self.minute_requests[0] < minute_cutoff:
            self.minute_requests.popleft()
        
        # Remove requests older than 1 day
        daily_cutoff = now - timedelta(days=1)
        while self.daily_requests and self.daily_requests[0] < daily_cutoff:
            self.daily_requests.popleft()
    
    def get_stats(self) -> Dict:
        """Get current rate limiting statistics"""
        with self.lock:
            now = datetime.now()
            self._clean_old_requests(now)
            
            return {
                'requests_this_minute': len(self.minute_requests),
                'requests_this_day': len(self.daily_requests),
                'minute_limit': self.requests_per_minute,
                'daily_limit': self.requests_per_day,
                'minute_remaining': self.requests_per_minute - len(self.minute_requests),
                'daily_remaining': self.requests_per_day - len(self.daily_requests)
            }
    
    def reset(self) -> None:
        """Reset all rate limiting counters"""
        with self.lock:
            self.minute_requests.clear()
            self.daily_requests.clear()
            self.logger.info("Rate limiter reset")
