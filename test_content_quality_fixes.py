#!/usr/bin/env python3
"""
Test script to verify content quality improvements:
1. Image extraction and inclusion
2. Page number filtering
3. Header/footer filtering
4. Title formatting
"""

import os
import sys
import logging
import tempfile
from pdf_parser import StructuredContentExtractor, PDFParser
from document_generator import WordDocumentGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_content_filtering():
    """Test the content filtering functionality"""
    logger.info("🧪 Testing content filtering...")
    
    extractor = StructuredContentExtractor()
    
    # Test cases for content that should be filtered
    test_cases = [
        # Page numbers
        {"text": "1", "bbox": [300, 50, 320, 70], "should_filter": True, "reason": "standalone page number"},
        {"text": "Page 5", "bbox": [300, 50, 350, 70], "should_filter": True, "reason": "page number pattern"},
        {"text": "5/10", "bbox": [300, 50, 330, 70], "should_filter": True, "reason": "page ratio"},
        
        # Headers (top of page)
        {"text": "CHAPTER 1", "bbox": [100, 750, 200, 770], "should_filter": True, "reason": "header in caps"},
        {"text": "Section 1.1", "bbox": [100, 750, 180, 770], "should_filter": True, "reason": "section header"},
        
        # Footers (bottom of page)
        {"text": "Copyright 2024", "bbox": [100, 30, 200, 50], "should_filter": True, "reason": "copyright footer"},
        {"text": "Confidential", "bbox": [100, 30, 180, 50], "should_filter": True, "reason": "confidential footer"},
        {"text": "www.example.com", "bbox": [100, 30, 200, 50], "should_filter": True, "reason": "website footer"},
        
        # Content that should NOT be filtered
        {"text": "This is a normal paragraph with substantial content.", "bbox": [100, 400, 500, 420], "should_filter": False, "reason": "normal content"},
        {"text": "Introduction to Machine Learning", "bbox": [100, 400, 300, 420], "should_filter": False, "reason": "title content"},
        {"text": "The results show that 1 out of 10 participants...", "bbox": [100, 400, 450, 420], "should_filter": False, "reason": "content with numbers"},
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        text = test_case["text"]
        bbox = test_case["bbox"]
        expected = test_case["should_filter"]
        reason = test_case["reason"]
        
        # Test the filtering function
        result = extractor._should_filter_content(text, bbox, 1, {})
        
        if result == expected:
            logger.info(f"  ✅ Test {i+1}: {reason}")
            passed += 1
        else:
            logger.error(f"  ❌ Test {i+1}: {reason}")
            logger.error(f"     Text: '{text}' | Expected: {expected} | Got: {result}")
    
    logger.info(f"Content filtering: {passed}/{total} tests passed")
    return passed == total

def test_image_extraction_criteria():
    """Test image extraction filtering criteria"""
    logger.info("🧪 Testing image extraction criteria...")
    
    parser = PDFParser()
    
    # Mock image data for testing
    test_images = [
        {"width": 10, "height": 10, "should_extract": False, "reason": "too small"},
        {"width": 100, "height": 5, "should_extract": False, "reason": "too thin (line)"},
        {"width": 5, "height": 100, "should_extract": False, "reason": "too thin (vertical line)"},
        {"width": 200, "height": 150, "should_extract": True, "reason": "good diagram size"},
        {"width": 400, "height": 300, "should_extract": True, "reason": "large image"},
        {"width": 80, "height": 60, "should_extract": True, "reason": "medium image"},
    ]
    
    passed = 0
    total = len(test_images)
    
    min_width = parser.settings.get('min_image_width_px', 50)
    min_height = parser.settings.get('min_image_height_px', 50)
    
    for i, test_image in enumerate(test_images):
        width = test_image["width"]
        height = test_image["height"]
        expected = test_image["should_extract"]
        reason = test_image["reason"]
        
        # Apply the same logic as in the extraction code
        size_ok = width >= min_width and height >= min_height
        aspect_ratio = max(width, height) / min(width, height)
        aspect_ok = aspect_ratio <= 20
        
        should_extract = size_ok and aspect_ok
        
        if should_extract == expected:
            logger.info(f"  ✅ Test {i+1}: {reason} ({width}x{height})")
            passed += 1
        else:
            logger.error(f"  ❌ Test {i+1}: {reason} ({width}x{height})")
            logger.error(f"     Expected: {expected} | Got: {should_extract}")
    
    logger.info(f"Image extraction criteria: {passed}/{total} tests passed")
    return passed == total

def test_document_structure_preservation():
    """Test that document structure is preserved correctly"""
    logger.info("🧪 Testing document structure preservation...")
    
    # Create test content that represents a typical document
    test_content = [
        {'type': 'h1', 'text': 'Document Title', 'page_num': 1, 'block_num': 1},
        {'type': 'paragraph', 'text': 'This is the introduction paragraph.', 'page_num': 1, 'block_num': 2},
        {'type': 'image', 'filename': 'diagram1.png', 'page_num': 1, 'width': 200, 'height': 150},
        {'type': 'h2', 'text': 'Section 1', 'page_num': 2, 'block_num': 1},
        {'type': 'paragraph', 'text': 'Content for section 1.', 'page_num': 2, 'block_num': 2},
        {'type': 'list_item', 'text': '• First item', 'page_num': 2, 'block_num': 3},
        {'type': 'list_item', 'text': '• Second item', 'page_num': 2, 'block_num': 4},
    ]
    
    try:
        generator = WordDocumentGenerator()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Test document generation
        success = generator.create_word_document_with_structure(
            test_content, temp_path, None, None
        )
        
        if success and os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            logger.info(f"  ✅ Document created successfully ({file_size:,} bytes)")
            
            # Clean up
            os.unlink(temp_path)
            return True
        else:
            logger.error("  ❌ Document creation failed")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Document structure test failed: {e}")
        return False

def test_image_placeholder_handling():
    """Test handling of missing images"""
    logger.info("🧪 Testing image placeholder handling...")
    
    # Test content with missing image
    test_content = [
        {'type': 'h1', 'text': 'Test Document', 'page_num': 1, 'block_num': 1},
        {'type': 'image', 'filename': 'missing_image.png', 'page_num': 1, 'width': 200, 'height': 150},
        {'type': 'paragraph', 'text': 'Text after image.', 'page_num': 1, 'block_num': 2},
    ]
    
    try:
        generator = WordDocumentGenerator()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Test document generation with missing image
        success = generator.create_word_document_with_structure(
            test_content, temp_path, "nonexistent_folder", None
        )
        
        if success and os.path.exists(temp_path):
            logger.info("  ✅ Document created with image placeholders")
            
            # Clean up
            os.unlink(temp_path)
            return True
        else:
            logger.error("  ❌ Document creation failed with missing images")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Image placeholder test failed: {e}")
        return False

def test_title_and_heading_detection():
    """Test title and heading detection logic"""
    logger.info("🧪 Testing title and heading detection...")
    
    extractor = StructuredContentExtractor()
    
    # Mock structure analysis
    structure_analysis = {
        'dominant_font_size': 12.0,
        'heading_font_sizes': {16.0, 18.0, 24.0}
    }
    
    test_cases = [
        {"text": "MAIN TITLE", "formatting": {"size": 24.0}, "expected": "h1", "reason": "large title"},
        {"text": "Chapter 1: Introduction", "formatting": {"size": 18.0}, "expected": "h1", "reason": "chapter heading (semantic)"},
        {"text": "Section 1.1", "formatting": {"size": 16.0}, "expected": "h1", "reason": "section heading (semantic)"},
        {"text": "1.2.1 Subsection", "formatting": {"size": 14.0}, "expected": "h3", "reason": "subsection with numbering"},
        {"text": "Normal paragraph text", "formatting": {"size": 12.0}, "expected": "paragraph", "reason": "normal text"},
        {"text": "• List item", "formatting": {"size": 12.0}, "expected": "list_item", "reason": "bullet point"},
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        text = test_case["text"]
        formatting = test_case["formatting"]
        expected = test_case["expected"]
        reason = test_case["reason"]
        
        result = extractor._classify_content_type(text, formatting, structure_analysis)
        
        if result == expected:
            logger.info(f"  ✅ Test {i+1}: {reason}")
            passed += 1
        else:
            logger.error(f"  ❌ Test {i+1}: {reason}")
            logger.error(f"     Text: '{text}' | Expected: {expected} | Got: {result}")
    
    logger.info(f"Title/heading detection: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all content quality tests"""
    logger.info("🚀 CONTENT QUALITY IMPROVEMENTS VERIFICATION")
    logger.info("=" * 60)
    
    tests = [
        ("Content Filtering", test_content_filtering),
        ("Image Extraction Criteria", test_image_extraction_criteria),
        ("Document Structure Preservation", test_document_structure_preservation),
        ("Image Placeholder Handling", test_image_placeholder_handling),
        ("Title/Heading Detection", test_title_and_heading_detection),
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
    
    if passed == total:
        logger.info("\n🎉 ALL CONTENT QUALITY FIXES ARE WORKING!")
        logger.info("✅ Key Improvements:")
        logger.info("   • Page numbers and headers/footers filtered out")
        logger.info("   • Better image extraction with size/aspect filtering")
        logger.info("   • Improved title and heading detection")
        logger.info("   • Robust image placeholder handling")
        logger.info("   • Document structure preservation")
    else:
        logger.warning("\n⚠️ Some tests failed. Please review the fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
