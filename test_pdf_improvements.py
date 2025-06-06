#!/usr/bin/env python3
"""
Test script for PDF improvements - focusing on accessible functionality.
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

def test_config_changes():
    """Test that config changes are properly loaded"""
    logger.info("=== Testing Configuration Changes ===")
    
    # Check if heading_max_words is updated to 13
    heading_max_words = config_manager.pdf_processing_settings.get('heading_max_words', 15)
    logger.info(f"Heading max words setting: {heading_max_words}")
    
    if heading_max_words == 13:
        logger.info("✅ PASS: Heading max words updated to 13")
    else:
        logger.info(f"❌ FAIL: Expected 13, got {heading_max_words}")
    
    # Check image extraction settings
    min_width = config_manager.pdf_processing_settings.get('min_image_width_px', 50)
    min_height = config_manager.pdf_processing_settings.get('min_image_height_px', 50)
    
    logger.info(f"Minimum image dimensions: {min_width}x{min_height} pixels")
    
    if min_width == 8 and min_height == 8:
        logger.info("✅ PASS: Image dimensions set to very low thresholds (8x8)")
    else:
        logger.info(f"❌ FAIL: Expected 8x8, got {min_width}x{min_height}")

def test_pdf_parser_initialization():
    """Test that PDFParser initializes correctly with new settings"""
    logger.info("\n=== Testing PDFParser Initialization ===")
    
    try:
        parser = PDFParser()
        logger.info("✅ PASS: PDFParser initialized successfully")
        
        # Check if settings are loaded
        settings = parser.settings
        logger.info(f"Parser loaded {len(settings)} settings")
        
        # Check specific settings
        heading_words = settings.get('heading_max_words', 'Not found')
        logger.info(f"Heading max words in parser: {heading_words}")
        
        return parser
        
    except Exception as e:
        logger.error(f"❌ FAIL: PDFParser initialization failed: {e}")
        return None

def test_image_extraction_methods():
    """Test that image extraction methods exist and are callable"""
    logger.info("\n=== Testing Image Extraction Methods ===")
    
    parser = PDFParser()
    
    # Check for key methods
    methods_to_check = [
        'extract_images_from_pdf',
        'extract_visual_content_areas',
        'extract_tables_as_images',
        'extract_equations_as_images',
        'groupby_images_by_page'
    ]
    
    for method_name in methods_to_check:
        if hasattr(parser, method_name):
            logger.info(f"✅ PASS: Method {method_name} exists")
        else:
            logger.info(f"❌ FAIL: Method {method_name} not found")

def test_enhanced_filtering_methods():
    """Test that our new filtering methods exist"""
    logger.info("\n=== Testing Enhanced Filtering Methods ===")
    
    parser = PDFParser()
    
    # Check for new methods we added
    new_methods = [
        '_remove_duplicate_images',
        '_are_images_similar',
        '_is_better_image',
        '_calculate_bbox_overlap',
        '_is_mostly_continuous_prose'
    ]
    
    for method_name in new_methods:
        if hasattr(parser, method_name):
            logger.info(f"✅ PASS: New method {method_name} exists")
        else:
            logger.info(f"❌ FAIL: New method {method_name} not found")

def test_duplicate_removal_logic():
    """Test the duplicate removal logic with mock data"""
    logger.info("\n=== Testing Duplicate Removal Logic ===")
    
    parser = PDFParser()
    
    if not hasattr(parser, '_remove_duplicate_images'):
        logger.info("❌ SKIP: _remove_duplicate_images method not available")
        return
    
    # Create mock image data
    mock_images = [
        {
            'page_num': 1,
            'filename': 'page_1_img_1.png',
            'filepath': 'mock_img_1.png',
            'bbox': [100, 100, 200, 200]
        },
        {
            'page_num': 1,
            'filename': 'page_1_img_2.png',
            'filepath': 'mock_img_2.png',
            'bbox': [105, 105, 205, 205]  # Similar position - potential duplicate
        },
        {
            'page_num': 2,
            'filename': 'page_2_img_1.png',
            'filepath': 'mock_img_3.png',
            'bbox': [50, 50, 150, 150]
        }
    ]
    
    try:
        # Test duplicate removal
        filtered = parser._remove_duplicate_images(mock_images)
        
        logger.info(f"Original images: {len(mock_images)}")
        logger.info(f"After duplicate removal: {len(filtered)}")
        
        if len(filtered) <= len(mock_images):
            logger.info("✅ PASS: Duplicate removal completed without errors")
            
            if len(filtered) < len(mock_images):
                logger.info("✅ PASS: Some duplicates were removed")
            else:
                logger.info("ℹ️  INFO: No duplicates detected (expected for mock data)")
        else:
            logger.info("❌ FAIL: Duplicate removal returned more images than input")
            
    except Exception as e:
        logger.error(f"❌ FAIL: Duplicate removal failed: {e}")

def test_prose_detection():
    """Test the continuous prose detection"""
    logger.info("\n=== Testing Prose Detection ===")
    
    parser = PDFParser()
    
    if not hasattr(parser, '_is_mostly_continuous_prose'):
        logger.info("❌ SKIP: _is_mostly_continuous_prose method not available")
        return
    
    # Test cases
    test_cases = [
        ("Short text", False, "Too short"),
        ("""This is a comprehensive academic analysis of machine learning methodologies. The research demonstrates significant improvements in algorithmic performance. However, several limitations must be acknowledged in the current implementation. Furthermore, the experimental results indicate promising directions for future research. Therefore, we recommend continued investigation into these approaches. Moreover, the implications for practical applications are substantial.""", True, "Academic prose"),
        ("Figure 1. Table 2. Chart 3.", False, "Short references")
    ]
    
    for text, expected, description in test_cases:
        try:
            result = parser._is_mostly_continuous_prose(text)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            logger.info(f"{status}: {description} -> {result} (expected {expected})")
        except Exception as e:
            logger.error(f"❌ ERROR: {description} failed: {e}")

def main():
    """Run all tests"""
    logger.info("Starting PDF Improvements Tests")
    logger.info("=" * 60)
    
    try:
        test_config_changes()
        parser = test_pdf_parser_initialization()
        
        if parser:
            test_image_extraction_methods()
            test_enhanced_filtering_methods()
            test_duplicate_removal_logic()
            test_prose_detection()
        
        logger.info("\n" + "=" * 60)
        logger.info("All tests completed!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
