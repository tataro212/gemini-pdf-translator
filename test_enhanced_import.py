#!/usr/bin/env python3
"""
Test script to verify enhanced workflow imports work correctly
"""

import sys
import traceback

def test_enhanced_imports():
    """Test all enhanced imports"""
    try:
        print("Testing enhanced workflow imports...")
        
        # Test 1: Enhanced PDF parser
        print("1. Testing enhanced PDF parser import...")
        from pdf_parser_enhanced import enhanced_pdf_parser
        print("   SUCCESS: Enhanced PDF parser imported successfully")
        
        # Test 2: Enhanced translation service
        print("2. Testing enhanced translation service import...")
        from translation_service_enhanced import enhanced_translation_service
        print("   SUCCESS: Enhanced translation service imported successfully")
        
        # Test 3: Enhanced document generator
        print("3. Testing enhanced document generator import...")
        from document_generator import WordDocumentGenerator
        print("   SUCCESS: Enhanced document generator imported successfully")
        
        # Test 4: Main enhanced workflow
        print("4. Testing main enhanced workflow import...")
        from main_workflow_enhanced import EnhancedPDFTranslator
        print("   SUCCESS: Enhanced workflow imported successfully")
        
        # Test 5: Create instance
        print("5. Testing enhanced translator instantiation...")
        translator = EnhancedPDFTranslator()
        print("   SUCCESS: Enhanced translator instance created successfully")
        
        print("\nAll enhanced workflow imports successful!")
        return True
        
    except Exception as e:
        print(f"\nImport test failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_imports()
    sys.exit(0 if success else 1)