#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for enhanced capabilities
"""

import sys
import os

def test_basic_import():
    """Test basic import functionality"""
    print("Testing basic import...")
    try:
        import ultimate_pdf_translator as upt
        print("✓ Import successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_detection():
    """Test document type detection"""
    print("\nTesting document type detection...")
    try:
        import ultimate_pdf_translator as upt
        
        detector = upt.DocumentTypeDetector()
        test_text = "This study presents a comprehensive analysis of the methodology."
        
        result = detector.detect_document_type(test_text)
        print(f"✓ Detection result: {result[0]} (confidence: {result[1]:.2f})")
        return True
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_generation():
    """Test enhanced prompt generation"""
    print("\nTesting prompt generation...")
    try:
        import ultimate_pdf_translator as upt
        
        prompt_gen = upt.EnhancedTranslationPromptGenerator()
        prompt = prompt_gen.generate_enhanced_prompt(
            "Test text",
            "Greek",
            "Academic document sample",
            "formal style"
        )
        
        print(f"✓ Prompt generated: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing():
    """Test coherent batch processing"""
    print("\nTesting batch processing...")
    try:
        import ultimate_pdf_translator as upt
        
        processor = upt.CoherentBatchProcessor(max_batch_size=100)
        test_text = "This is a test. " * 50  # Create longer text
        
        batches = processor.create_coherent_batches(test_text)
        print(f"✓ Created {len(batches)} batches")
        return True
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== ENHANCED CAPABILITIES TEST ===")
    
    tests = [
        test_basic_import,
        test_document_detection,
        test_prompt_generation,
        test_batch_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n=== RESULTS: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
