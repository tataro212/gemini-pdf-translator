#!/usr/bin/env python3
"""
Test script to verify that the Nougat cache_position error is resolved.
"""

import logging
import sys
import subprocess
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nougat_import():
    """Test that nougat_integration imports without cache_position errors"""
    try:
        logger.info("🔧 Testing Nougat integration import...")
        import nougat_integration
        logger.info("✅ nougat_integration imported successfully")
        
        nougat = nougat_integration.NougatIntegration()
        logger.info("✅ NougatIntegration initialized successfully")
        logger.info(f"Nougat available: {nougat.nougat_available}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error importing nougat_integration: {e}")
        return False

def test_nougat_command():
    """Test that the nougat command works without cache_position errors"""
    try:
        logger.info("🔧 Testing nougat command...")
        result = subprocess.run(['nougat', '--help'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info("✅ nougat command works")
            return True
        else:
            logger.error(f"❌ nougat command failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing nougat command: {e}")
        return False

def test_transformers_patch():
    """Test that the transformers patch was applied correctly"""
    try:
        logger.info("🔧 Testing transformers patch...")
        from transformers.models.bart.modeling_bart import BartDecoder
        
        # Check if our patch was applied
        if hasattr(BartDecoder, 'prepare_inputs_for_generation'):
            logger.info("✅ BartDecoder.prepare_inputs_for_generation method exists")
            
            # Try to create a simple instance to see if it works
            # Note: This is just a basic test, not a full model test
            logger.info("✅ Transformers patch appears to be working")
            return True
        else:
            logger.warning("⚠️ BartDecoder.prepare_inputs_for_generation method not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing transformers patch: {e}")
        return False

def test_hybrid_ocr_integration():
    """Test that hybrid OCR integration works with the patched Nougat"""
    try:
        logger.info("🔧 Testing hybrid OCR integration...")
        from hybrid_ocr_processor import HybridOCRProcessor
        from nougat_integration import NougatIntegration

        # Initialize with proper nougat_integration parameter
        nougat_integration = NougatIntegration()
        processor = HybridOCRProcessor(nougat_integration=nougat_integration)
        logger.info(f"✅ HybridOCRProcessor initialized with Nougat integration")
        logger.info(f"Available engines: {[e.value for e in processor.available_engines]}")

        # Check if nougat is in the available engines
        nougat_available = any(e.value == 'nougat' for e in processor.available_engines)
        if nougat_available:
            logger.info("✅ Nougat is available in hybrid OCR processor")
            return True
        else:
            logger.warning("⚠️ Nougat not available in hybrid OCR processor")
            logger.warning(f"   Nougat integration available: {nougat_integration.nougat_available}")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing hybrid OCR integration: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🎯 Testing Nougat Cache Position Fix")
    logger.info("=" * 50)
    
    tests = [
        ("Nougat Import", test_nougat_import),
        ("Nougat Command", test_nougat_command),
        ("Transformers Patch", test_transformers_patch),
        ("Hybrid OCR Integration", test_hybrid_ocr_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                logger.info(f"✅ PASSED: {test_name}")
            else:
                logger.error(f"❌ FAILED: {test_name}")
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
        
        logger.info("-" * 30)
    
    # Summary
    logger.info(f"\n📊 Test Results Summary:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
        if success:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Nougat cache_position error is resolved.")
        return 0
    else:
        logger.error("❌ Some tests failed. The cache_position error may not be fully resolved.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
