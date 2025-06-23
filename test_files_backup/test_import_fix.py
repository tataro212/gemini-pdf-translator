#!/usr/bin/env python3
"""
Test script to verify that the import fixes are working correctly
"""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all the critical imports"""
    
    try:
        # Test 1: Main workflow imports
        logger.info("Testing main workflow imports...")
        from document_generator import document_generator, convert_word_to_pdf, WordDocumentGenerator
        logger.info("SUCCESS: document_generator imports successful")
        
        # Test 2: Enhanced workflow imports  
        logger.info("Testing enhanced workflow imports...")
        from main_workflow_enhanced import EnhancedPDFTranslator
        logger.info("SUCCESS: Enhanced workflow imports successful")
        
        # Test 3: Verify the objects are properly instantiated
        logger.info("Testing object instantiation...")
        generator = WordDocumentGenerator()
        logger.info("SUCCESS: WordDocumentGenerator instantiated successfully")
        
        translator = EnhancedPDFTranslator()
        logger.info("SUCCESS: EnhancedPDFTranslator instantiated successfully")
        
        logger.info("All import tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\nAll imports are working correctly!")
        sys.exit(0)
    else:
        print("\nImport issues detected!")
        sys.exit(1)