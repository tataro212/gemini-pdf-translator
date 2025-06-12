#!/usr/bin/env python3
"""
Test script for async translation service configuration.
This script tests that the async API calls are properly configured.
"""

import os
import logging
import asyncio
from config_manager import config_manager
from async_translation_service import AsyncTranslationService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_reading():
    """Test that config values are being read correctly"""
    print("\n📋 TESTING CONFIG READING")
    print("=" * 60)
    
    # Test config manager access
    print("🔧 Config Manager attributes:")
    if hasattr(config_manager, 'translation_enhancement_settings'):
        settings = config_manager.translation_enhancement_settings
        print(f"   translation_enhancement_settings: {type(settings)}")
        if isinstance(settings, dict):
            max_concurrent_tasks = settings.get('max_concurrent_tasks', 'NOT_FOUND')
            print(f"   max_concurrent_tasks: {max_concurrent_tasks}")
        else:
            print(f"   translation_enhancement_settings is not a dict: {settings}")
    else:
        print("   translation_enhancement_settings: NOT_FOUND")
    
    if hasattr(config_manager, 'gemini_api_settings'):
        settings = config_manager.gemini_api_settings
        print(f"   gemini_api_settings: {type(settings)}")
        if isinstance(settings, dict):
            max_concurrent_api = settings.get('max_concurrent_api_calls', 'NOT_FOUND')
            print(f"   max_concurrent_api_calls: {max_concurrent_api}")
        else:
            print(f"   gemini_api_settings is not a dict: {settings}")
    else:
        print("   gemini_api_settings: NOT_FOUND")
    
    # Test direct config access
    if hasattr(config_manager, 'get_config_value'):
        try:
            max_concurrent_tasks = config_manager.get_config_value('TranslationEnhancement', 'max_concurrent_tasks', 'DEFAULT', int)
            max_concurrent_api = config_manager.get_config_value('GeminiAPI', 'max_concurrent_api_calls', 'DEFAULT', int)
            print(f"   Direct access - max_concurrent_tasks: {max_concurrent_tasks}")
            print(f"   Direct access - max_concurrent_api_calls: {max_concurrent_api}")
        except Exception as e:
            print(f"   Direct access failed: {e}")

def test_async_service_initialization():
    """Test async translation service initialization"""
    print("\n🚀 TESTING ASYNC SERVICE INITIALIZATION")
    print("=" * 60)
    
    try:
        # Initialize async service
        async_service = AsyncTranslationService()
        
        print(f"✅ AsyncTranslationService initialized successfully")
        print(f"   Max concurrent: {async_service.max_concurrent}")
        print(f"   Request delay: {async_service.request_delay * 1000:.0f}ms")
        print(f"   Semaphore value: {async_service.semaphore._value}")
        
        # Check if values are reasonable for Gemini 2.5
        if async_service.max_concurrent >= 5:
            print("✅ Concurrent limit is appropriate for Gemini 2.5")
        else:
            print(f"⚠️ Concurrent limit ({async_service.max_concurrent}) may be too low for Gemini 2.5")
        
        if async_service.request_delay <= 0.1:
            print("✅ Request delay is appropriate for fast processing")
        else:
            print(f"⚠️ Request delay ({async_service.request_delay}s) may be too high")
        
        return async_service
        
    except Exception as e:
        print(f"❌ Failed to initialize AsyncTranslationService: {e}")
        return None

async def test_concurrent_processing_simulation():
    """Test concurrent processing simulation"""
    print("\n⚡ TESTING CONCURRENT PROCESSING SIMULATION")
    print("=" * 60)
    
    async_service = AsyncTranslationService()
    
    # Create mock translation tasks
    from async_translation_service import TranslationTask
    
    tasks = []
    for i in range(10):
        task = TranslationTask(
            task_id=f"test_task_{i}",
            text=f"Test text {i} for translation",
            target_language="Greek",
            priority=1,
            item_type="paragraph"
        )
        tasks.append(task)
    
    print(f"📦 Created {len(tasks)} mock translation tasks")
    print(f"🚀 Max concurrent workers: {async_service.max_concurrent}")
    print(f"⏱️ Request delay: {async_service.request_delay * 1000:.0f}ms")
    
    # Simulate concurrent processing timing
    import time
    start_time = time.time()
    
    # Calculate expected time
    sequential_time = len(tasks) * 1.0  # Assume 1 second per task
    concurrent_time = (len(tasks) / async_service.max_concurrent) * 1.0 + (len(tasks) * async_service.request_delay)
    
    print(f"\n📊 Performance estimation:")
    print(f"   Sequential processing: ~{sequential_time:.1f} seconds")
    print(f"   Concurrent processing: ~{concurrent_time:.1f} seconds")
    print(f"   Expected speedup: {sequential_time / concurrent_time:.1f}x")
    
    if concurrent_time < sequential_time * 0.5:
        print("✅ Significant speedup expected from concurrent processing")
    else:
        print("⚠️ Limited speedup - consider increasing concurrent limit")

def main():
    """Run all tests"""
    print("🚀 ASYNC TRANSLATION SERVICE - CONFIGURATION TEST")
    print("=" * 60)
    print("Testing async API call configuration and concurrent processing")
    print()
    
    # Test 1: Config reading
    test_config_reading()
    
    # Test 2: Async service initialization
    async_service = test_async_service_initialization()
    
    # Test 3: Concurrent processing simulation
    if async_service:
        asyncio.run(test_concurrent_processing_simulation())
    
    # Summary and recommendations
    print("\n📊 SUMMARY AND RECOMMENDATIONS")
    print("=" * 60)
    
    if async_service:
        concurrent_limit = async_service.max_concurrent
        
        if concurrent_limit >= 5:
            print("✅ ASYNC CONFIGURATION: OPTIMAL")
            print(f"   Concurrent limit: {concurrent_limit} (good for Gemini 2.5)")
            print("   Expected performance: Fast concurrent processing")
        elif concurrent_limit >= 3:
            print("⚠️ ASYNC CONFIGURATION: MODERATE")
            print(f"   Concurrent limit: {concurrent_limit} (could be higher)")
            print("   Recommendation: Consider increasing to 5 for Gemini 2.5")
        else:
            print("❌ ASYNC CONFIGURATION: SUBOPTIMAL")
            print(f"   Concurrent limit: {concurrent_limit} (too low)")
            print("   Recommendation: Increase to 5 for optimal Gemini 2.5 performance")
    else:
        print("❌ ASYNC CONFIGURATION: FAILED")
        print("   Could not initialize async service")
    
    print("\n🔧 CONFIGURATION TIPS:")
    print("   1. For Gemini 2.5: Use 5 concurrent API calls")
    print("   2. For Gemini 1.5: Use 10 concurrent API calls")
    print("   3. Set request_delay to 50ms for fast processing")
    print("   4. Monitor API rate limits and adjust accordingly")
    print("   5. Check config.ini for max_concurrent_api_calls and max_concurrent_tasks")

if __name__ == "__main__":
    main()
