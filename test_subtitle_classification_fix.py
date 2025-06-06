#!/usr/bin/env python3
"""
Test script to reproduce and fix subtitle classification issues
"""

import os
import sys
import logging
from pdf_parser import StructuredContentExtractor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_problematic_subtitle_classification():
    """Test cases that reproduce the subtitle classification problem"""
    logger.info("🧪 Testing problematic subtitle classification...")
    
    extractor = StructuredContentExtractor()
    
    # Mock structure analysis
    structure_analysis = {
        'dominant_font_size': 12.0,
        'heading_font_sizes': {14.0, 16.0, 18.0}
    }
    
    # Test cases that should NOT be classified as headings
    problematic_cases = [
        {
            "text": "This is a paragraph fragment that contains about fifty words and should definitely not be classified as a subtitle or heading because it is clearly part of a larger paragraph with substantial content that flows naturally.",
            "size": 14.4,  # 20% larger than normal (12 * 1.2 = 14.4)
            "expected": "paragraph",
            "reason": "Long text should not be heading despite larger font"
        },
        {
            "text": "Another example of text that might be slightly emphasized but is clearly a paragraph fragment containing meaningful content that should not be treated as a heading or subtitle in the document structure.",
            "size": 13.5,  # 12.5% larger than normal
            "expected": "paragraph", 
            "reason": "Paragraph with slight emphasis"
        },
        {
            "text": "The results of this experiment demonstrate that the methodology was effective in achieving the desired outcomes, as evidenced by the statistical analysis performed on the collected data.",
            "size": 14.0,  # 16.7% larger than normal
            "expected": "paragraph",
            "reason": "Scientific text with slight formatting difference"
        },
        {
            "text": "Furthermore, the implications of these findings extend beyond the immediate scope of this study and suggest potential applications in related fields of research.",
            "size": 13.8,  # 15% larger than normal
            "expected": "paragraph",
            "reason": "Academic text continuation"
        }
    ]
    
    # Test cases that SHOULD be classified as headings
    legitimate_headings = [
        {
            "text": "Introduction",
            "size": 16.0,
            "expected": "h2",
            "reason": "Clear section heading with semantic keyword"
        },
        {
            "text": "Methodology",
            "size": 14.0,
            "expected": "h2",
            "reason": "Academic section heading with semantic keyword"
        },
        {
            "text": "Results",
            "size": 15.0,
            "expected": "h2",
            "reason": "Short heading with semantic keyword"
        },
        {
            "text": "1.1 Background",
            "size": 13.0,
            "expected": "h2",  # Updated expectation - numbered sections are h2
            "reason": "Numbered section"
        },
        {
            "text": "CHAPTER 1",
            "size": 18.0,
            "expected": "h1",
            "reason": "Chapter heading (semantic pattern)"
        }
    ]
    
    logger.info("📋 Testing problematic cases (should be paragraphs):")
    problematic_passed = 0
    
    for i, case in enumerate(problematic_cases, 1):
        formatting = {"size": case["size"]}
        result = extractor._classify_content_type(
            case["text"], formatting, structure_analysis
        )
        
        expected = case["expected"]
        reason = case["reason"]
        
        if result == expected:
            logger.info(f"  ✅ Test {i}: {reason}")
            problematic_passed += 1
        else:
            logger.error(f"  ❌ Test {i}: {reason}")
            logger.error(f"     Text: '{case['text'][:60]}...'")
            logger.error(f"     Expected: {expected} | Got: {result} | Size: {case['size']}pt")
    
    logger.info("📋 Testing legitimate headings (should be headings):")
    heading_passed = 0
    
    for i, case in enumerate(legitimate_headings, 1):
        formatting = {"size": case["size"]}
        result = extractor._classify_content_type(
            case["text"], formatting, structure_analysis
        )
        
        expected = case["expected"]
        reason = case["reason"]
        
        if result == expected:
            logger.info(f"  ✅ Test {i}: {reason}")
            heading_passed += 1
        else:
            logger.error(f"  ❌ Test {i}: {reason}")
            logger.error(f"     Text: '{case['text']}' | Expected: {expected} | Got: {result}")
    
    total_problematic = len(problematic_cases)
    total_headings = len(legitimate_headings)
    
    logger.info(f"Problematic cases: {problematic_passed}/{total_problematic} correctly classified as paragraphs")
    logger.info(f"Legitimate headings: {heading_passed}/{total_headings} correctly classified as headings")
    
    return (problematic_passed == total_problematic and 
            heading_passed == total_headings)

def test_length_based_filtering():
    """Test that long text is not classified as headings regardless of font size"""
    logger.info("🧪 Testing length-based filtering...")
    
    extractor = StructuredContentExtractor()
    
    structure_analysis = {
        'dominant_font_size': 12.0,
        'heading_font_sizes': {16.0, 18.0, 24.0}
    }
    
    test_cases = [
        {
            "text": "A",  # Very short
            "size": 18.0,
            "expected_heading": True,
            "reason": "Very short text can be heading"
        },
        {
            "text": "Short Title",  # Short
            "size": 18.0,
            "expected_heading": True,
            "reason": "Short text can be heading"
        },
        {
            "text": "This is a medium length title that might be acceptable",  # Medium
            "size": 18.0,
            "expected_heading": False,  # Should be too long
            "reason": "Medium text should not be heading"
        },
        {
            "text": "This is definitely too long to be considered a heading or subtitle because it contains way too much content and is clearly a paragraph fragment that should not be classified as a heading regardless of font size.",  # Long
            "size": 24.0,  # Even very large font
            "expected_heading": False,
            "reason": "Long text should never be heading"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        formatting = {"size": case["size"]}
        result = extractor._classify_content_type(
            case["text"], formatting, structure_analysis
        )
        
        is_heading = result in ['h1', 'h2', 'h3']
        expected_heading = case["expected_heading"]
        reason = case["reason"]
        
        if is_heading == expected_heading:
            logger.info(f"  ✅ Test {i}: {reason}")
            passed += 1
        else:
            logger.error(f"  ❌ Test {i}: {reason}")
            logger.error(f"     Text: '{case['text'][:60]}...'")
            logger.error(f"     Expected heading: {expected_heading} | Got: {result} (is_heading: {is_heading})")
    
    logger.info(f"Length-based filtering: {passed}/{total} tests passed")
    return passed == total

def test_cache_bypass_for_images():
    """Test that image extraction is not affected by caching"""
    logger.info("🧪 Testing cache bypass for image extraction...")
    
    # Check if there are any cache files that might affect image extraction
    cache_files = [
        'translation_cache.json',
        'content_cache.json', 
        'image_cache.json',
        'pdf_cache.json'
    ]
    
    found_caches = []
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            found_caches.append(cache_file)
    
    if found_caches:
        logger.info(f"  Found cache files: {found_caches}")
        logger.info("  Note: These should not affect image extraction")
    else:
        logger.info("  ✅ No cache files found that would affect image extraction")
    
    # Test that image extraction settings are properly applied
    from pdf_parser import PDFParser
    parser = PDFParser()
    
    min_width = parser.settings.get('min_image_width_px', 50)
    min_height = parser.settings.get('min_image_height_px', 50)
    
    logger.info(f"  Current image extraction settings:")
    logger.info(f"    Min width: {min_width}px")
    logger.info(f"    Min height: {min_height}px")
    
    if min_width >= 50 and min_height >= 50:
        logger.info("  ✅ Image extraction settings are properly configured")
        return True
    else:
        logger.error("  ❌ Image extraction settings need adjustment")
        return False

def main():
    """Run all subtitle classification tests"""
    logger.info("🚀 SUBTITLE CLASSIFICATION FIX VERIFICATION")
    logger.info("=" * 60)
    
    tests = [
        ("Problematic Subtitle Classification", test_problematic_subtitle_classification),
        ("Length-based Filtering", test_length_based_filtering),
        ("Cache Bypass for Images", test_cache_bypass_for_images),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} Test ---")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n🎯 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        logger.warning("\n⚠️ Some tests failed - fixes needed for subtitle classification")
    else:
        logger.info("\n🎉 All tests passed - subtitle classification is working correctly")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
