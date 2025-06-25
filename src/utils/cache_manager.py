"""
Cache management utility for the EPV Research Platform
"""
import pickle
import json
import os
import time
from typing import Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import logging

class CacheManager:
    """
    File-based cache manager with expiration support
    """
    
    def __init__(self, cache_dir: str = "data/cache", default_expiry_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_expiry_hours = default_expiry_hours
        self.logger = logging.getLogger(__name__)
        
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key"""
        # Create a hash of the key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _get_metadata_path(self, key: str) -> Path:
        """Generate metadata file path from key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.meta"
    
    def set(self, key: str, value: Any, expiry_hours: Optional[int] = None) -> bool:
        """
        Store value in cache with optional expiration
        
        Args:
            key: Cache key
            value: Value to cache
            expiry_hours: Hours until expiration (default: 24)
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            expiry_hours = expiry_hours or self.default_expiry_hours
            expiry_time = datetime.now() + timedelta(hours=expiry_hours)
            
            # Store the data
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Store metadata
            metadata = {
                'key': key,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiry_time.isoformat(),
                'size_bytes': os.path.getsize(cache_path)
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            self.logger.debug(f"Cached data for key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching data for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            # Check if cache files exist
            if not cache_path.exists() or not metadata_path.exists():
                return None
            
            # Check if cache has expired
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                self.logger.debug(f"Cache expired for key: {key}")
                self._delete_cache_files(key)
                return None
            
            # Load and return cached data
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            self.logger.debug(f"Cache hit for key: {key}")
            return value
            
        except Exception as e:
            self.logger.error(f"Error retrieving cache for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete cached value
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            return self._delete_cache_files(key)
        except Exception as e:
            self.logger.error(f"Error deleting cache for key {key}: {e}")
            return False
    
    def _delete_cache_files(self, key: str) -> bool:
        """Delete cache and metadata files"""
        cache_path = self._get_cache_path(key)
        metadata_path = self._get_metadata_path(key)
        
        deleted = False
        
        if cache_path.exists():
            cache_path.unlink()
            deleted = True
            
        if metadata_path.exists():
            metadata_path.unlink()
            deleted = True
            
        return deleted
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        try:
            for metadata_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    expires_at = datetime.fromisoformat(metadata['expires_at'])
                    if datetime.now() > expires_at:
                        key = metadata['key']
                        if self._delete_cache_files(key):
                            cleared_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Error processing metadata file {metadata_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {e}")
        
        if cleared_count > 0:
            self.logger.info(f"Cleared {cleared_count} expired cache entries")
            
        return cleared_count
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        stats = {
            'total_entries': 0,
            'total_size_bytes': 0,
            'expired_entries': 0,
            'oldest_entry': None,
            'newest_entry': None
        }
        
        try:
            metadata_files = list(self.cache_dir.glob("*.meta"))
            stats['total_entries'] = len(metadata_files)
            
            entry_dates = []
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Check size
                    if 'size_bytes' in metadata:
                        stats['total_size_bytes'] += metadata['size_bytes']
                    
                    # Check expiration
                    expires_at = datetime.fromisoformat(metadata['expires_at'])
                    if datetime.now() > expires_at:
                        stats['expired_entries'] += 1
                    
                    # Track dates
                    created_at = datetime.fromisoformat(metadata['created_at'])
                    entry_dates.append(created_at)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing metadata file {metadata_file}: {e}")
            
            if entry_dates:
                stats['oldest_entry'] = min(entry_dates).isoformat()
                stats['newest_entry'] = max(entry_dates).isoformat()
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
        
        return stats
    
    def clear_all(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        try:
            # Clear cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
                cleared_count += 1
            
            # Clear metadata files
            for metadata_file in self.cache_dir.glob("*.meta"):
                metadata_file.unlink()
                
        except Exception as e:
            self.logger.error(f"Error clearing all cache: {e}")
        
        if cleared_count > 0:
            self.logger.info(f"Cleared all cache ({cleared_count} entries)")
            
        return cleared_count
