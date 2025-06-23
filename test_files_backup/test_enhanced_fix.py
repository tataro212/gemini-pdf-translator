#!/usr/bin/env python3
"""
Test script to verify the enhanced workflow fix
"""

import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_enhanced_translation_service():
    """Test that the enhanced translation service has the correct method"""
    try:
        from translation_service_enhanced import enhanced_translation_service
        
        # Check if the method exists
        if hasattr(enhanced_translation_service, 'translate_text_enhanced'):
            logger.info("SUCCESS: enhanced_translation_service.translate_text_enhanced method found")
            return True
        else:
            logger.error("FAIL: enhanced_translation_service.translate_text_enhanced method NOT found")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: Error importing enhanced_translation_service: {e}")
        return False

def test_enhanced_workflow_import():
    """Test that the enhanced workflow can be imported"""
    try:
        from main_workflow_enhanced import EnhancedPDFTranslator
        logger.info("SUCCESS: EnhancedPDFTranslator can be imported")
        return True
    except Exception as e:
        logger.error(f"FAIL: Error importing EnhancedPDFTranslator: {e}")
        return False

def test_method_signature():
    """Test that the method signature is compatible"""
    try:
        from translation_service_enhanced import enhanced_translation_service
        import inspect
        
        # Get the method signature
        method = getattr(enhanced_translation_service, 'translate_text_enhanced')
        sig = inspect.signature(method)
        
        logger.info(f"SUCCESS: Method signature: {sig}")
        
        # Check if it has the expected parameters
        params = list(sig.parameters.keys())
        expected_params = ['text', 'target_language', 'style_guide', 'prev_context', 'next_context', 'item_type']
        
        missing_params = [p for p in expected_params if p not in params]
        if missing_params:
            logger.warning(f"WARNING: Missing expected parameters: {missing_params}")
        else:
            logger.info("SUCCESS: All expected parameters found")
            
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Error checking method signature: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing Enhanced Workflow Fix...")
    
    tests = [
        ("Enhanced Translation Service Import", test_enhanced_translation_service),
        ("Enhanced Workflow Import", test_enhanced_workflow_import),
        ("Method Signature Check", test_method_signature)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        
    logger.info(f"\n=== TEST RESULTS ===")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("SUCCESS: All tests passed! The fix should work.")
        sys.exit(0)
    else:
        logger.error("FAIL: Some tests failed. There may still be issues.")
        sys.exit(1)