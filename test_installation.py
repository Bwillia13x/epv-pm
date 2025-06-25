#!/usr/bin/env python3
"""
Test script to verify EPV Research Platform installation
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test configuration
        from config.config import config, setup_directories
        print("✓ Configuration module imported")
        
        # Test data models
        from models.financial_models import CompanyProfile, EPVCalculation
        print("✓ Financial models imported")
        
        # Test utilities
        from utils.cache_manager import CacheManager
        from utils.rate_limiter import RateLimiter
        print("✓ Utility modules imported")
        
        # Test data collection
        from data.data_collector import DataCollector
        print("✓ Data collector imported")
        
        # Test analysis modules
        from analysis.epv_calculator import EPVCalculator
        from analysis.research_generator import ResearchGenerator
        print("✓ Analysis modules imported")
        
        print("\n✓ All modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_directories():
    """Test directory creation"""
    try:
        print("\nTesting directory creation...")
        from config.config import setup_directories
        setup_directories()
        
        # Check if directories exist
        required_dirs = [
            "data/raw",
            "data/processed", 
            "data/cache",
            "logs",
            "exports"
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"✓ {directory} created")
            else:
                print(f"✗ {directory} not found")
                return False
        
        print("✓ All directories created successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Directory creation error: {e}")
        return False

def test_basic_functionality():
    """Test basic platform functionality"""
    try:
        print("\nTesting basic functionality...")
        
        # Test cache manager
        from utils.cache_manager import CacheManager
        cache = CacheManager()
        cache.set("test_key", "test_value", 1)
        value = cache.get("test_key")
        assert value == "test_value"
        print("✓ Cache manager working")
        
        # Test rate limiter
        from utils.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=60)
        stats = limiter.get_stats()
        assert 'requests_this_minute' in stats
        print("✓ Rate limiter working")
        
        # Test EPV calculator initialization
        from analysis.epv_calculator import EPVCalculator
        calculator = EPVCalculator()
        print("✓ EPV calculator initialized")
        
        print("✓ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests"""
    print("EPV Research Platform Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_directories,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ Installation successful! You can now use the EPV Research Platform.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run quick test: python3 src/main.py quick --symbol AAPL")
        print("3. Start web interface: python3 src/main.py web")
    else:
        print("✗ Installation issues detected. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
