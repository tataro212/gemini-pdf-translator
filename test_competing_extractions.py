#!/usr/bin/env python3
"""
Test script for the enhanced competing extraction detection.
This tests the new logic that handles multiple extractions from the same page
where one is good (diagram + explanation) and one is poor (text only).
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

def test_competing_extraction_logic():
    """Test the new competing extraction detection logic"""
    logger.info("=== Testing Competing Extraction Logic ===")
    
    parser = PDFParser()
    
    # Create mock competing extractions from the same page
    mock_competing_images = [
        {
            'page_num': 22,
            'filename': 'page_22_visual_visual_1.png',
            'filepath': 'mock_good_visual.png',
            'bbox': [100, 100, 400, 300],  # Large area
            'confidence': 0.8,
            'content_type': 'page_with_drawings'
        },
        {
            'page_num': 22,
            'filename': 'page_22_visual_visual_2.png', 
            'filepath': 'mock_poor_visual.png',
            'bbox': [120, 120, 200, 180],  # Smaller overlapping area
            'confidence': 0.4,
            'content_type': 'text_only'
        },
        {
            'page_num': 54,
            'filename': 'page_54_visual_visual_1.png',
            'filepath': 'mock_good_54.png',
            'bbox': [50, 50, 350, 250],
            'confidence': 0.9,
            'content_type': 'diagram'
        },
        {
            'page_num': 54,
            'filename': 'page_54_table_table_1.png',
            'filepath': 'mock_table_54.png',
            'bbox': [60, 260, 340, 320],  # Different area - should keep both
            'confidence': 0.7,
            'content_type': 'table'
        }
    ]
    
    # Create mock files with different sizes to simulate quality differences
    mock_file_sizes = {
        'mock_good_visual.png': 500000,  # 500KB - good quality
        'mock_poor_visual.png': 25000,   # 25KB - poor quality (text only)
        'mock_good_54.png': 800000,      # 800KB - very good quality
        'mock_table_54.png': 150000      # 150KB - decent table
    }
    
    # Mock the file size checking
    original_getsize = os.path.getsize
    def mock_getsize(filepath):
        filename = os.path.basename(filepath)
        return mock_file_sizes.get(filename, 100000)  # Default 100KB
    
    # Mock file existence
    original_exists = os.path.exists
    def mock_exists(filepath):
        filename = os.path.basename(filepath)
        return filename in mock_file_sizes
    
    # Apply mocks
    os.path.getsize = mock_getsize
    os.path.exists = mock_exists
    
    try:
        # Test the competing extraction removal
        logger.info(f"Input: {len(mock_competing_images)} images")
        for img in mock_competing_images:
            logger.info(f"  Page {img['page_num']}: {img['filename']} ({mock_file_sizes.get(os.path.basename(img['filepath']), 'unknown')} bytes)")
        
        filtered_images = parser._remove_duplicate_images(mock_competing_images)
        
        logger.info(f"\nOutput: {len(filtered_images)} images")
        for img in filtered_images:
            logger.info(f"  Page {img['page_num']}: {img['filename']} ({mock_file_sizes.get(os.path.basename(img['filepath']), 'unknown')} bytes)")
        
        # Analyze results
        page_22_results = [img for img in filtered_images if img['page_num'] == 22]
        page_54_results = [img for img in filtered_images if img['page_num'] == 54]
        
        logger.info(f"\nPage 22 results: {len(page_22_results)} images")
        if len(page_22_results) == 1:
            kept_img = page_22_results[0]
            if 'good' in kept_img['filepath']:
                logger.info("✅ PASS: Kept the good visual extraction from page 22")
            else:
                logger.info("❌ FAIL: Kept the poor visual extraction from page 22")
        else:
            logger.info(f"❌ FAIL: Expected 1 image from page 22, got {len(page_22_results)}")
        
        logger.info(f"\nPage 54 results: {len(page_54_results)} images")
        if len(page_54_results) == 2:
            logger.info("✅ PASS: Kept both visual and table from page 54 (different types)")
        else:
            logger.info(f"❌ FAIL: Expected 2 images from page 54, got {len(page_54_results)}")
        
    finally:
        # Restore original functions
        os.path.getsize = original_getsize
        os.path.exists = original_exists

def test_quality_scoring():
    """Test the image quality scoring system"""
    logger.info("\n=== Testing Quality Scoring System ===")
    
    parser = PDFParser()
    
    # Test images with different characteristics
    test_images = [
        {
            'filename': 'large_diagram.png',
            'filepath': 'large_file.png',
            'bbox': [0, 0, 500, 400],  # Large area
            'confidence': 0.9,
            'content_type': 'diagram'
        },
        {
            'filename': 'small_text.png',
            'filepath': 'small_file.png', 
            'bbox': [0, 0, 100, 50],   # Small area
            'confidence': 0.3,
            'content_type': 'text_only'
        },
        {
            'filename': 'medium_visual.png',
            'filepath': 'medium_file.png',
            'bbox': [0, 0, 300, 200],  # Medium area
            'confidence': 0.7,
            'content_type': 'visual'
        }
    ]
    
    # Mock file sizes
    mock_sizes = {
        'large_file.png': 1000000,  # 1MB
        'small_file.png': 20000,    # 20KB
        'medium_file.png': 300000   # 300KB
    }
    
    original_getsize = os.path.getsize
    original_exists = os.path.exists
    
    def mock_getsize(filepath):
        filename = os.path.basename(filepath)
        return mock_sizes.get(filename, 100000)
    
    def mock_exists(filepath):
        filename = os.path.basename(filepath)
        return filename in mock_sizes
    
    os.path.getsize = mock_getsize
    os.path.exists = mock_exists
    
    try:
        scores = []
        for img in test_images:
            score = parser._calculate_image_quality_score(img)
            scores.append((score, img['filename']))
            logger.info(f"{img['filename']}: Score {score:.2f}")
        
        # Sort by score
        scores.sort(reverse=True)
        
        logger.info(f"\nRanking (best to worst):")
        for i, (score, filename) in enumerate(scores, 1):
            logger.info(f"  {i}. {filename} (score: {score:.2f})")
        
        # Check if ranking makes sense
        if scores[0][1] == 'large_diagram.png' and scores[-1][1] == 'small_text.png':
            logger.info("✅ PASS: Quality scoring ranks images correctly")
        else:
            logger.info("❌ FAIL: Quality scoring ranking is incorrect")
            
    finally:
        os.path.getsize = original_getsize
        os.path.exists = original_exists

def test_extraction_type_detection():
    """Test extraction type detection from filenames"""
    logger.info("\n=== Testing Extraction Type Detection ===")
    
    parser = PDFParser()
    
    test_cases = [
        ('page_22_visual_visual_1.png', 'visual'),
        ('page_54_table_table_1.png', 'table'),
        ('page_36_equation_equation_1.png', 'equation'),
        ('page_1_img_1.png', 'image'),
        ('some_other_file.png', 'unknown')
    ]
    
    for filename, expected_type in test_cases:
        detected_type = parser._get_extraction_type(filename)
        status = "✅ PASS" if detected_type == expected_type else "❌ FAIL"
        logger.info(f"{status}: {filename} -> {detected_type} (expected: {expected_type})")

def main():
    """Run all competing extraction tests"""
    logger.info("Starting Competing Extraction Detection Tests")
    logger.info("=" * 60)
    
    try:
        test_competing_extraction_logic()
        test_quality_scoring()
        test_extraction_type_detection()
        
        logger.info("\n" + "=" * 60)
        logger.info("All competing extraction tests completed!")
        logger.info("The system should now better handle pages with multiple extractions,")
        logger.info("keeping the best quality version and filtering out text-only extractions.")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
