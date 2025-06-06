#!/usr/bin/env python3
"""
Test script for image handling and ToC subtitle merging improvements
"""

import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translation_strategy_manager import translation_strategy_manager, ImportanceLevel
from document_generator import WordDocumentGenerator
from config_manager import config_manager

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_image_importance_analysis():
    """Test that images are properly preserved based on extraction settings"""
    print("=" * 60)
    print("TEST 1: Image Importance Analysis")
    print("=" * 60)

    # Check config first
    extract_images = config_manager.pdf_processing_settings.get('extract_images', True)
    print(f"Image extraction enabled in config: {extract_images}")

    # Use the global strategy manager instance
    
    # Test cases for different image scenarios
    test_cases = [
        {
            'name': 'Image with substantial OCR text',
            'item': {
                'type': 'image',
                'filename': 'figure_3_1.png',
                'ocr_text': 'This is a detailed diagram showing the relationship between various components',
                'page_num': 5
            },
            'expected': ImportanceLevel.MEDIUM
        },
        {
            'name': 'Image without OCR text (diagram/figure)',
            'item': {
                'type': 'image', 
                'filename': 'diagram_complex.png',
                'ocr_text': '',
                'page_num': 10
            },
            'expected': ImportanceLevel.LOW
        },
        {
            'name': 'Image with minimal OCR text',
            'item': {
                'type': 'image',
                'filename': 'chart_simple.png', 
                'ocr_text': 'Fig 3.1',
                'page_num': 8
            },
            'expected': ImportanceLevel.LOW
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"  Item: {test_case['item']}")

        importance = translation_strategy_manager.analyze_content_importance(test_case['item'])
        strategy = translation_strategy_manager.get_translation_strategy(test_case['item'])

        print(f"  Expected: {test_case['expected'].value}")
        print(f"  Got importance: {importance.value}")
        print(f"  Should translate: {strategy.get('should_translate', False)}")
        print(f"  Strategy: {strategy}")

        success = importance == test_case['expected']
        results.append(success)
        print(f"  Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    overall_success = all(results)
    print(f"\nTest 1 Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    return overall_success

def test_toc_heading_merging():
    """Test that split ToC headings are properly merged"""
    print("\n" + "=" * 60)
    print("TEST 2: ToC Heading Merging")
    print("=" * 60)
    
    doc_generator = WordDocumentGenerator()
    
    # Test case: headings that should be merged
    test_headings = [
        {
            'text': 'Chapter 3: Advanced Concepts in Quantum',
            'level': 1,
            'estimated_page': 45,
            'original_page': 45,
            'bbox': [100, 200, 400, 220]
        },
        {
            'text': 'Mechanics and Their Applications',
            'level': 1,
            'estimated_page': 45,
            'original_page': 45,
            'bbox': [100, 225, 350, 245]
        },
        {
            'text': '3.1 Introduction to Wave Functions',
            'level': 2,
            'estimated_page': 46,
            'original_page': 46,
            'bbox': [120, 300, 380, 320]
        },
        {
            'text': 'and Probability Distributions',
            'level': 2,
            'estimated_page': 46,
            'original_page': 46,
            'bbox': [120, 325, 320, 345]
        },
        {
            'text': 'Conclusion',
            'level': 1,
            'estimated_page': 50,
            'original_page': 50,
            'bbox': [100, 400, 200, 420]
        }
    ]
    
    # Test the merging logic
    merged_headings = doc_generator._merge_split_headings(test_headings)
    
    print(f"Original headings: {len(test_headings)}")
    print(f"Merged headings: {len(merged_headings)}")
    
    expected_merged = [
        'Chapter 3: Advanced Concepts in Quantum Mechanics and Their Applications',
        '3.1 Introduction to Wave Functions and Probability Distributions', 
        'Conclusion'
    ]
    
    success = True
    if len(merged_headings) != len(expected_merged):
        success = False
        print(f"❌ Expected {len(expected_merged)} merged headings, got {len(merged_headings)}")
    else:
        for i, (merged, expected) in enumerate(zip(merged_headings, expected_merged)):
            if merged['text'] != expected:
                success = False
                print(f"❌ Heading {i+1} mismatch:")
                print(f"   Expected: '{expected}'")
                print(f"   Got: '{merged['text']}'")
            else:
                print(f"✅ Heading {i+1}: '{merged['text']}'")
    
    print(f"\nTest 2 Result: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

def test_heading_merge_logic():
    """Test the individual heading merge decision logic"""
    print("\n" + "=" * 60)
    print("TEST 3: Heading Merge Decision Logic")
    print("=" * 60)
    
    doc_generator = WordDocumentGenerator()
    
    test_cases = [
        {
            'name': 'Should merge: continuation with lowercase',
            'preceding': [{'text': 'Advanced Concepts in', 'level': 1, 'original_page': 5}],
            'candidate': {'text': 'quantum Mechanics', 'level': 1, 'original_page': 5},
            'expected': True
        },
        {
            'name': 'Should merge: no ending punctuation',
            'preceding': [{'text': 'Introduction to Wave Functions', 'level': 2, 'original_page': 10}],
            'candidate': {'text': 'and Probability Theory', 'level': 2, 'original_page': 10},
            'expected': True
        },
        {
            'name': 'Should NOT merge: different levels',
            'preceding': [{'text': 'Chapter 1', 'level': 1, 'original_page': 5}],
            'candidate': {'text': 'Introduction', 'level': 2, 'original_page': 5},
            'expected': False
        },
        {
            'name': 'Should NOT merge: ends with period',
            'preceding': [{'text': 'Complete Analysis.', 'level': 1, 'original_page': 5}],
            'candidate': {'text': 'Next Topic', 'level': 1, 'original_page': 5},
            'expected': False
        },
        {
            'name': 'Should NOT merge: too far apart (pages)',
            'preceding': [{'text': 'Chapter Title', 'level': 1, 'original_page': 5}],
            'candidate': {'text': 'continuation', 'level': 1, 'original_page': 8},
            'expected': False
        }
    ]
    
    results = []
    for test_case in test_cases:
        result = doc_generator._should_merge_headings(
            test_case['preceding'], 
            test_case['candidate']
        )
        success = result == test_case['expected']
        results.append(success)
        
        print(f"\n{test_case['name']}:")
        print(f"  Expected: {test_case['expected']}")
        print(f"  Got: {result}")
        print(f"  Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    overall_success = all(results)
    print(f"\nTest 3 Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    return overall_success

def test_image_strategy_decisions():
    """Test complete translation strategy decisions for images"""
    print("\n" + "=" * 60)
    print("TEST 4: Image Translation Strategy Decisions")
    print("=" * 60)
    
    test_images = [
        {
            'name': 'Complex diagram (should be preserved)',
            'item': {
                'type': 'image',
                'filename': 'complex_diagram.png',
                'ocr_text': '',
                'page_num': 15
            }
        },
        {
            'name': 'Image with caption (should be preserved)',
            'item': {
                'type': 'image',
                'filename': 'figure_with_text.png',
                'ocr_text': 'Figure 3.1: Detailed analysis of quantum state transitions in complex systems',
                'page_num': 20
            }
        }
    ]
    
    results = []
    for test_case in test_images:
        strategy = translation_strategy_manager.get_translation_strategy(test_case['item'])
        
        # Images should not be skipped when extraction is enabled
        should_translate = strategy.get('should_translate', False)
        importance = strategy.get('importance', 'skip')
        
        # For our purposes, images should be preserved (not skipped)
        success = importance != 'skip'
        results.append(success)
        
        print(f"\n{test_case['name']}:")
        print(f"  Should translate: {should_translate}")
        print(f"  Importance: {importance}")
        print(f"  Result: {'✅ PRESERVED' if success else '❌ SKIPPED'}")
    
    overall_success = all(results)
    print(f"\nTest 4 Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    return overall_success

def main():
    """Run all tests"""
    print("🧪 TESTING IMAGE AND TOC IMPROVEMENTS")
    print("=" * 60)
    
    tests = [
        test_image_importance_analysis,
        test_toc_heading_merging,
        test_heading_merge_logic,
        test_image_strategy_decisions
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The image and ToC improvements are working correctly.")
        print("\n💡 Key improvements:")
        print("   • Images are now preserved regardless of OCR content")
        print("   • Split ToC headings are intelligently merged")
        print("   • Enhanced logging helps debug missing images")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
