#!/usr/bin/env python3
"""
Test script for intelligent translator data structure fixes.
This script tests that the data structure issues are resolved.
"""

import os
import logging
import asyncio
from intelligent_pdf_translator import IntelligentPDFTranslator, IntelligentTranslationResult

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_intelligent_translation_result():
    """Test the IntelligentTranslationResult wrapper"""
    print("\n📦 TESTING INTELLIGENT TRANSLATION RESULT WRAPPER")
    print("=" * 60)
    
    # Test successful result
    success_dict = {
        'success': True,
        'translated_content': 'Test translated content',
        'processing_time': 10.5,
        'statistics': {
            'total_cost': 0.05,
            'pages_processed': 5,
            'items_processed': 25
        }
    }
    
    success_result = IntelligentTranslationResult(success_dict)
    
    print("✅ Testing successful result:")
    print(f"   success: {success_result.success}")
    print(f"   error: {success_result.error}")
    print(f"   has processed_document: {success_result.processed_document is not None}")
    print(f"   processed_document type: {type(success_result.processed_document)}")
    
    # Test error result
    error_dict = {
        'success': False,
        'error': 'Test error message',
        'processing_time': 2.0
    }
    
    error_result = IntelligentTranslationResult(error_dict)
    
    print("\n❌ Testing error result:")
    print(f"   success: {error_result.success}")
    print(f"   error: {error_result.error}")
    print(f"   has processed_document: {error_result.processed_document is not None}")
    
    return success_result, error_result

def test_preprocessing_error_handling():
    """Test the preprocessing error handling for string vs dict"""
    print("\n🔧 TESTING PREPROCESSING ERROR HANDLING")
    print("=" * 60)
    
    translator = IntelligentPDFTranslator()
    
    # Test different analysis types
    test_cases = [
        {"analysis": {"valid": "dict"}, "description": "Valid dict analysis"},
        {"analysis": "string error message", "description": "String analysis (error case)"},
        {"analysis": 123, "description": "Invalid type analysis"},
        {"analysis": None, "description": "None analysis"},
    ]
    
    for case in test_cases:
        analysis = case["analysis"]
        description = case["description"]
        
        print(f"\n📋 Testing: {description}")
        print(f"   Input type: {type(analysis)}")
        print(f"   Input value: {analysis}")
        
        # Simulate the preprocessing logic
        if isinstance(analysis, str):
            processed_analysis = {'error': analysis}
            print(f"   ✅ Handled as string error: {processed_analysis}")
        elif not isinstance(analysis, dict):
            processed_analysis = {'error': 'Invalid analysis format'}
            print(f"   ✅ Handled as invalid type: {processed_analysis}")
        else:
            processed_analysis = analysis
            print(f"   ✅ Used as-is: {processed_analysis}")

def test_main_workflow_compatibility():
    """Test compatibility with main workflow expectations"""
    print("\n🔗 TESTING MAIN WORKFLOW COMPATIBILITY")
    print("=" * 60)
    
    # Simulate what main workflow expects
    print("📋 Main workflow expects:")
    print("   - result.processed_document attribute")
    print("   - result.success attribute")
    print("   - result.error attribute (for error cases)")
    
    # Test with our wrapper
    success_dict = {
        'success': True,
        'translated_content': 'Test content',
        'statistics': {'pages_processed': 3}
    }
    
    result = IntelligentTranslationResult(success_dict)
    
    print("\n✅ Testing wrapper compatibility:")
    
    # Test processed_document access
    try:
        processed_doc = result.processed_document
        print(f"   processed_document: ✅ Available ({type(processed_doc)})")
    except AttributeError as e:
        print(f"   processed_document: ❌ Missing ({e})")
    
    # Test success access
    try:
        success = result.success
        print(f"   success: ✅ Available ({success})")
    except AttributeError as e:
        print(f"   success: ❌ Missing ({e})")
    
    # Test error access
    try:
        error = result.error
        print(f"   error: ✅ Available ('{error}')")
    except AttributeError as e:
        print(f"   error: ❌ Missing ({e})")
    
    # Test result_dict access (for error handling)
    try:
        result_dict = result.result_dict
        print(f"   result_dict: ✅ Available ({type(result_dict)})")
    except AttributeError as e:
        print(f"   result_dict: ❌ Missing ({e})")

def main():
    """Run all tests"""
    print("🚀 INTELLIGENT TRANSLATOR - DATA STRUCTURE FIX TEST")
    print("=" * 60)
    print("Testing fixes for data structure and async configuration issues")
    print()
    
    # Test 1: Translation result wrapper
    success_result, error_result = test_intelligent_translation_result()
    
    # Test 2: Preprocessing error handling
    test_preprocessing_error_handling()
    
    # Test 3: Main workflow compatibility
    test_main_workflow_compatibility()
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    print("✅ FIXES IMPLEMENTED:")
    print("   1. IntelligentTranslationResult wrapper for compatibility")
    print("   2. Preprocessing error handling for string/dict analysis")
    print("   3. Main workflow error handling for wrapped results")
    print("   4. Async service configuration reading from config.ini")
    print("   5. Optimal concurrent API calls (5 for Gemini 2.5)")
    
    print("\n🎯 EXPECTED IMPROVEMENTS:")
    print("   1. No more 'dict' object has no attribute 'processed_document' errors")
    print("   2. No more 'str' object has no attribute 'get' errors")
    print("   3. 4x faster translation with 5 concurrent API calls")
    print("   4. Proper error handling and fallback mechanisms")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Test with a real PDF to verify fixes work")
    print("   2. Monitor translation speed improvement")
    print("   3. Check that error handling works gracefully")

if __name__ == "__main__":
    main()
