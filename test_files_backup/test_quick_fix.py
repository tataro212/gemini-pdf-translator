#!/usr/bin/env python3
"""
Quick test to verify the enhanced workflow fix
"""

import logging
import asyncio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_enhanced_translation():
    """Test the enhanced translation service with a simple text"""
    try:
        logger.info("Testing enhanced translation service...")
        
        # Import the enhanced translation service
        from translation_service_enhanced import enhanced_translation_service
        
        # Test with a simple text
        test_text = "Hello, this is a test."
        target_language = "Greek"
        
        logger.info(f"Testing translation of: '{test_text}'")
        logger.info(f"Target language: {target_language}")
        
        # Call the method that was fixed
        result = await enhanced_translation_service.translate_text_enhanced(
            text=test_text,
            target_language=target_language,
            prev_context="",
            next_context="",
            item_type="text"
        )
        
        logger.info(f"Translation result: '{result}'")
        
        if result and result != test_text:
            logger.info("SUCCESS: Translation appears to be working!")
            return True
        else:
            logger.warning("WARNING: Translation returned original text - may indicate an issue")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: Error during translation test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_workflow_import():
    """Test that the enhanced workflow can be imported and initialized"""
    try:
        logger.info("Testing enhanced workflow import...")
        
        from main_workflow_enhanced import EnhancedPDFTranslator
        
        # Try to create an instance
        translator = EnhancedPDFTranslator()
        
        logger.info("SUCCESS: Enhanced workflow imported and initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Error importing enhanced workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    logger.info("=== TESTING ENHANCED WORKFLOW FIX ===")
    
    tests = [
        ("Enhanced Workflow Import", test_enhanced_workflow_import),
        ("Enhanced Translation", test_enhanced_translation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if await test_func():
                passed += 1
                logger.info(f"PASS: {test_name}")
            else:
                logger.error(f"FAIL: {test_name}")
        except Exception as e:
            logger.error(f"ERROR in {test_name}: {e}")
    
    logger.info(f"\n=== TEST RESULTS ===")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("SUCCESS: All tests passed! The enhanced workflow should work now.")
        return True
    else:
        logger.error("FAIL: Some tests failed. There may still be issues.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)