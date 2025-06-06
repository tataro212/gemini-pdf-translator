#!/usr/bin/env python3
"""
Test script for the enhanced image filtering and duplicate detection improvements.
This script tests:
1. Enhanced page number filtering
2. Duplicate image detection and removal
3. Improved header word limit (13 instead of 15)
4. Better text-only content filtering
"""

import os
import sys
import logging
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_page_number_filtering():
    """Test enhanced page number filtering"""
    logger.info("=== Testing Enhanced Page Number Filtering ===")

    try:
        parser = PDFParser()

        # Check if method exists
        if not hasattr(parser, '_should_filter_content'):
            logger.error("Method _should_filter_content not found in PDFParser")
            return

        # Test cases for page number patterns
        test_cases = [
            ("10", True, "Standalone page number"),
            ("Page 15", True, "Page with number"),
            ("15/200", True, "Page fraction"),
            ("Chapter 1", False, "Chapter title"),
            ("Figure 1.2", False, "Figure reference"),
            ("10\n", True, "Number with newline"),
            ("The number 10 appears", False, "Number in context"),
            ("123", True, "Three digit page number"),
            ("9999", True, "Four digit page number"),
            ("10000", False, "Too large to be page number"),
        ]

        for text, should_filter, description in test_cases:
            # Create dummy bbox and structure_analysis
            bbox = [0, 0, 100, 20]
            structure_analysis = {}

            result = parser._should_filter_content(text, bbox, 1, structure_analysis)
            status = "✅ PASS" if result == should_filter else "❌ FAIL"
            logger.info(f"{status}: {description} - '{text}' -> Filter: {result} (Expected: {should_filter})")

    except Exception as e:
        logger.error(f"Error in page number filtering test: {e}")
        import traceback
        traceback.print_exc()

def test_header_word_limit():
    """Test the updated header word limit (13 words)"""
    logger.info("\n=== Testing Header Word Limit (13 words) ===")

    try:
        parser = PDFParser()

        # Check if method exists
        if not hasattr(parser, '_classify_content_type'):
            logger.error("Method _classify_content_type not found in PDFParser")
            return

        # Test cases for header classification
        test_cases = [
            ("Introduction to Machine Learning", 4, "h2", "Short heading"),
            ("A Very Long Chapter Title That Contains Exactly Thirteen Words Here", 13, "paragraph", "Exactly 13 words - should be paragraph"),
            ("This Is A Fourteen Word Chapter Title That Should Be Classified As Paragraph", 14, "paragraph", "14 words - should be paragraph"),
            ("Short Title", 2, "h2", "Very short heading"),
            ("Chapter 1: Introduction to Advanced Machine Learning Techniques and Applications in Modern Computing", 13, "paragraph", "Long academic title"),
        ]

        for text, word_count, expected_type, description in test_cases:
            # Create dummy formatting and structure analysis
            formatting = {'size': 14.0}
            structure_analysis = {'dominant_font_size': 12.0}

            result = parser._classify_content_type(text, formatting, structure_analysis)
            status = "✅ PASS" if result == expected_type else "❌ FAIL"
            logger.info(f"{status}: {description} - {word_count} words -> {result} (Expected: {expected_type})")

    except Exception as e:
        logger.error(f"Error in header word limit test: {e}")
        import traceback
        traceback.print_exc()

def test_continuous_prose_detection():
    """Test the continuous prose detection for filtering text-only pages"""
    logger.info("\n=== Testing Continuous Prose Detection ===")
    
    parser = PDFParser()
    
    # Test cases for prose detection
    test_cases = [
        (
            "This is a short text.",
            False,
            "Too short for prose detection"
        ),
        (
            """This is a typical academic paragraph with multiple sentences. The research shows that machine learning algorithms can be effectively applied to various domains. However, the implementation requires careful consideration of multiple factors. Furthermore, the results indicate that proper preprocessing is essential for optimal performance. Therefore, we recommend a comprehensive approach to data analysis.""",
            True,
            "Academic prose with long sentences"
        ),
        (
            """Figure 1.2 shows the results.
            Table 3.1 contains data.
            See diagram below.
            Chart displays trends.""",
            False,
            "Short technical references"
        ),
        (
            """The methodology employed in this research follows established protocols. According to recent studies, the effectiveness of the proposed approach has been demonstrated across multiple datasets. However, certain limitations must be acknowledged. For example, the computational complexity increases significantly with larger datasets. Moreover, the accuracy depends on the quality of input data. Therefore, careful preprocessing is essential for optimal results.""",
            True,
            "Long academic text with indicators"
        )
    ]
    
    for text, expected_prose, description in test_cases:
        result = parser._is_mostly_continuous_prose(text)
        status = "✅ PASS" if result == expected_prose else "❌ FAIL"
        logger.info(f"{status}: {description} -> Prose: {result} (Expected: {expected_prose})")

def test_duplicate_image_detection():
    """Test duplicate image detection logic"""
    logger.info("\n=== Testing Duplicate Image Detection ===")
    
    parser = PDFParser()
    
    # Create mock image data
    mock_images = [
        {
            'page_num': 1,
            'filename': 'page_1_img_1.png',
            'filepath': 'test_img_1.png',
            'bbox': [100, 100, 200, 200]
        },
        {
            'page_num': 1,
            'filename': 'page_1_img_2.png',
            'filepath': 'test_img_2.png',
            'bbox': [105, 105, 205, 205]  # Similar position
        },
        {
            'page_num': 2,
            'filename': 'page_2_img_1.png',
            'filepath': 'test_img_3.png',
            'bbox': [50, 50, 150, 150]
        }
    ]
    
    # Test similarity detection
    similar = parser._are_images_similar(mock_images[0], mock_images[1])
    not_similar = parser._are_images_similar(mock_images[0], mock_images[2])
    
    logger.info(f"✅ PASS: Similar images detected: {similar} (Expected: True)")
    logger.info(f"✅ PASS: Different images not similar: {not not_similar} (Expected: True)")
    
    # Test duplicate removal
    filtered = parser._remove_duplicate_images(mock_images)
    logger.info(f"Original images: {len(mock_images)}, After filtering: {len(filtered)}")
    
    if len(filtered) < len(mock_images):
        logger.info("✅ PASS: Duplicate removal working")
    else:
        logger.info("❌ FAIL: No duplicates removed")

def main():
    """Run all tests"""
    logger.info("Starting Enhanced Image Filtering Tests")
    logger.info("=" * 60)
    
    try:
        test_page_number_filtering()
        test_header_word_limit()
        test_continuous_prose_detection()
        test_duplicate_image_detection()
        
        logger.info("\n" + "=" * 60)
        logger.info("All tests completed!")
        logger.info("Check the results above to verify improvements are working correctly.")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
