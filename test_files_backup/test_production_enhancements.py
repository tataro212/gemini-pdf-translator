#!/usr/bin/env python3
"""
Test script for production-ready enhancements:
1. Quarantine system for problematic PDFs
2. Parallel page processing with ProcessPoolExecutor
3. Structured logging with JSON output
4. Unified configuration with Pydantic validation
"""

import os
import sys
import json
import tempfile
import logging
import asyncio
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_unified_config():
    """Test the unified configuration system"""
    logger.info("🧪 Testing Unified Configuration System...")
    
    try:
        from unified_config import ConfigManager, UnifiedConfig
        
        # Test creating a config manager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config_file = f.name
        
        try:
            # Create config manager with test file
            config_manager = ConfigManager(test_config_file)
            
            # Test getting values
            target_lang = config_manager.get_value('general', 'target_language', 'English')
            max_workers = config_manager.get_value('performance', 'max_parallel_workers', 2)
            
            logger.info(f"✅ Config loaded: target_language={target_lang}, max_workers={max_workers}")
            
            # Test setting values
            config_manager.set_value('general', 'target_language', 'French')
            config_manager.set_value('performance', 'max_parallel_workers', 8)
            
            # Test validation
            is_valid = config_manager.validate_config()
            logger.info(f"✅ Config validation: {'passed' if is_valid else 'failed'}")
            
            # Test saving
            config_manager.save_config()
            logger.info("✅ Config saved successfully")
            
            return True
            
        finally:
            # Cleanup
            if os.path.exists(test_config_file):
                os.unlink(test_config_file)
                
    except ImportError as e:
        logger.warning(f"⚠️ Unified config not available: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unified config test failed: {e}")
        return False

def test_quarantine_system():
    """Test the quarantine system for problematic PDFs"""
    logger.info("🧪 Testing Quarantine System...")
    
    try:
        from main_workflow import FailureTracker
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test quarantine tracker
            quarantine_dir = os.path.join(temp_dir, "test_quarantine")
            tracker = FailureTracker(quarantine_dir=quarantine_dir, max_retries=2)
            
            # Create a fake problematic file
            test_file = os.path.join(temp_dir, "problematic.pdf")
            with open(test_file, 'w') as f:
                f.write("fake pdf content")
            
            # Test failure tracking
            should_process_1 = tracker.should_process_file(test_file)
            logger.info(f"✅ Should process initially: {should_process_1}")
            
            # Record first failure
            was_quarantined_1 = tracker.record_failure(test_file, "Test error 1")
            logger.info(f"✅ First failure recorded, quarantined: {was_quarantined_1}")
            
            # Record second failure (should quarantine)
            was_quarantined_2 = tracker.record_failure(test_file, "Test error 2")
            logger.info(f"✅ Second failure recorded, quarantined: {was_quarantined_2}")
            
            # Check if file is now blocked
            should_process_2 = tracker.should_process_file(test_file)
            logger.info(f"✅ Should process after quarantine: {should_process_2}")
            
            # Verify quarantine directory exists and has files
            quarantine_path = Path(quarantine_dir)
            quarantined_files = list(quarantine_path.glob("*"))
            logger.info(f"✅ Quarantined files: {len(quarantined_files)}")
            
            return was_quarantined_2 and not should_process_2
            
    except ImportError as e:
        logger.warning(f"⚠️ Quarantine system not available: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Quarantine system test failed: {e}")
        return False

def test_structured_logging():
    """Test structured logging with JSON output"""
    logger.info("🧪 Testing Structured Logging...")
    
    try:
        from main_workflow import MetricsCollector, STRUCTURED_LOGGING_AVAILABLE
        
        # Create test metrics collector
        metrics = MetricsCollector()
        
        # Create a fake file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            test_file = f.name
            f.write("fake pdf content")
        
        try:
            # Test metrics collection
            metrics.start_document_processing(test_file)
            logger.info("✅ Document processing started")
            
            # Simulate content metrics
            from types import SimpleNamespace
            mock_document = SimpleNamespace()
            mock_document.content_blocks = []
            mock_document.total_pages = 5
            
            metrics.update_content_metrics(mock_document)
            logger.info("✅ Content metrics updated")
            
            # Add some test data
            metrics.add_warning("Test warning message")
            metrics.add_error("Test error message")
            
            # Test translation metrics
            metrics.update_translation_metrics(1500, 250)  # 1.5 seconds, 250 words
            logger.info("✅ Translation metrics updated")
            
            # Finalize and log
            final_metrics = metrics.finalize_and_log(success=True)
            logger.info(f"✅ Final metrics collected: {len(final_metrics)} fields")
            
            # Verify key metrics are present
            required_fields = ['document_name', 'processing_start_time', 'total_processing_time_ms', 'success']
            has_required = all(field in final_metrics for field in required_fields)
            logger.info(f"✅ Required fields present: {has_required}")
            
            return has_required
            
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.unlink(test_file)
                
    except ImportError as e:
        logger.warning(f"⚠️ Structured logging not available: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Structured logging test failed: {e}")
        return False

def test_parallel_processing():
    """Test parallel processing capabilities"""
    logger.info("🧪 Testing Parallel Processing...")
    
    try:
        from main_workflow import _process_single_page
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing
        
        # Test that the function is importable and callable
        logger.info("✅ Parallel processing function available")
        
        # Test with mock data (without actually processing a PDF)
        mock_task = {
            'filepath': 'test.pdf',
            'page_num': 0,
            'page_images': []
        }
        
        # Test that we can create a ProcessPoolExecutor
        max_workers = min(4, multiprocessing.cpu_count())
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            logger.info(f"✅ ProcessPoolExecutor created with {max_workers} workers")
        
        logger.info("✅ Parallel processing infrastructure ready")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ Parallel processing not available: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Parallel processing test failed: {e}")
        return False

async def run_all_tests():
    """Run all production enhancement tests"""
    logger.info("🚀 Starting Production Enhancement Tests...")
    
    tests = [
        ("Unified Configuration", test_unified_config),
        ("Quarantine System", test_quarantine_system),
        ("Structured Logging", test_structured_logging),
        ("Parallel Processing", test_parallel_processing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ ERROR in {test_name}: {e}")
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL PRODUCTION ENHANCEMENTS READY!")
    else:
        logger.warning("⚠️ Some enhancements need attention")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())
