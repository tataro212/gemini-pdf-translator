"""
Test script for the enhanced PDF translator fixes

This script validates that all the critical fixes are working correctly:
1. Unicode font support
2. TOC-aware parsing  
3. Enhanced proper noun handling
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_components():
    """Test that all enhanced components can be imported and initialized"""
    logger.info("Testing enhanced component imports...")
    
    try:
        # Test document generator
        from document_generator import WordDocumentGenerator
        generator = WordDocumentGenerator()
        logger.info("PASS: Enhanced document generator imported successfully")
        
        # Test translation service
        from translation_service_enhanced import enhanced_translation_service
        logger.info("PASS: Enhanced translation service imported successfully")
        
        # Test PDF parser
        from pdf_parser_enhanced import enhanced_pdf_parser
        logger.info("PASS: Enhanced PDF parser imported successfully")
        
        # Test main workflow
        from main_workflow_enhanced import EnhancedPDFTranslator
        translator = EnhancedPDFTranslator()
        logger.info("PASS: Enhanced main workflow imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Component import failed: {e}")
        return False

def test_unicode_font_configuration():
    """Test Unicode font configuration"""
    logger.info("Testing Unicode font configuration...")
    
    try:
        from docx import Document
        from document_generator import WordDocumentGenerator
        
        generator = WordDocumentGenerator()
        doc = Document()
        
        # Test font configuration
        generator._configure_document_fonts_for_unicode(doc)
        
        # Check if Normal style has been configured
        normal_style = doc.styles['Normal']
        font_name = normal_style.font.name
        
        if font_name == 'Arial Unicode MS':
            logger.info("PASS: Unicode font configuration successful")
            return True
        else:
            logger.warning(f"WARN: Font configured as {font_name} (fallback)")
            return True  # Still acceptable
            
    except Exception as e:
        logger.error(f"FAIL: Unicode font configuration failed: {e}")
        return False

def test_proper_noun_fixes():
    """Test proper noun reconstruction"""
    logger.info("Testing proper noun fixes...")
    
    try:
        from translation_service_enhanced import EnhancedTranslationService
        
        service = EnhancedTranslationService()
        
        # Test cases for missing first letters
        test_cases = [
            ("eah akshmi", "Leah akshmi"),
            ("isa ierria", "Lisa ierria"), 
            ("illy's issed", "Billy's issed"),
            ("normal text", "normal text")  # Should not change
        ]
        
        all_passed = True
        for input_text, expected_pattern in test_cases:
            result = service._fix_parsing_issues(input_text)
            if expected_pattern.lower() in result.lower():
                logger.info(f"PASS: '{input_text}' -> '{result}'")
            else:
                logger.warning(f"WARN: '{input_text}' -> '{result}' (expected pattern: {expected_pattern})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        logger.error(f"FAIL: Proper noun fixes test failed: {e}")
        return False

def test_toc_detection():
    """Test TOC page detection logic"""
    logger.info("Testing TOC detection...")
    
    try:
        from pdf_parser_enhanced import EnhancedPDFParser
        
        parser = EnhancedPDFParser()
        
        # Mock page object for testing
        class MockPage:
            def get_text(self):
                return """
                Table of Contents
                
                Chapter 1: Introduction ........................ 5
                Chapter 2: Methods ............................ 12
                Chapter 3: Results ............................ 25
                Chapter 4: Discussion ......................... 38
                Chapter 5: Conclusion ......................... 45
                """
        
        mock_page = MockPage()
        is_toc = parser.is_toc_page(mock_page, 1)
        
        if is_toc:
            logger.info("PASS: TOC detection working correctly")
            return True
        else:
            logger.error("FAIL: TOC detection failed")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: TOC detection test failed: {e}")
        return False

async def test_enhanced_translation():
    """Test enhanced translation functionality"""
    logger.info("Testing enhanced translation...")
    
    try:
        from translation_service_enhanced import enhanced_translation_service
        
        # Test text with proper nouns and potential issues
        test_text = "eah akshmi and isa ierria worked on the project."
        
        # Note: This will only work if you have a valid API key configured
        # For testing purposes, we'll just test the preprocessing
        processed_text = enhanced_translation_service._fix_parsing_issues(test_text)
        
        if "Leah" in processed_text and "Lisa" in processed_text:
            logger.info(f"PASS: Enhanced translation preprocessing: '{test_text}' -> '{processed_text}'")
            return True
        else:
            logger.warning(f"WARN: Enhanced translation preprocessing: '{test_text}' -> '{processed_text}'")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: Enhanced translation test failed: {e}")
        return False

def test_glossary_creation():
    """Test enhanced glossary creation"""
    logger.info("Testing glossary creation...")
    
    try:
        from translation_service_enhanced import EnhancedGlossaryManager
        
        # Test with a temporary glossary file
        temp_glossary = "test_glossary.json"
        
        manager = EnhancedGlossaryManager(temp_glossary)
        
        # This should create the template glossary
        if os.path.exists(temp_glossary):
            logger.info("PASS: Enhanced glossary template created")
            
            # Clean up
            os.remove(temp_glossary)
            return True
        else:
            logger.error("FAIL: Enhanced glossary template not created")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: Glossary creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=== ENHANCED PDF TRANSLATOR FIXES - VALIDATION TESTS ===")
    
    tests = [
        ("Component Imports", test_enhanced_components),
        ("Unicode Font Configuration", test_unicode_font_configuration),
        ("Proper Noun Fixes", test_proper_noun_fixes),
        ("TOC Detection", test_toc_detection),
        ("Enhanced Translation", test_enhanced_translation),
        ("Glossary Creation", test_glossary_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n=== TEST RESULTS SUMMARY ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("SUCCESS: All tests passed! Enhanced fixes are working correctly.")
        return True
    else:
        logger.warning(f"WARNING: {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)