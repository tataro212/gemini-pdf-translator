#!/usr/bin/env python3
"""
Test the improvements with the actual PDF file to see real-world performance.
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

def test_with_real_pdf():
    """Test improvements with the actual PDF file"""
    logger.info("=== Testing Improvements with Real PDF ===")
    
    # Find the PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found in current directory")
        return
    
    pdf_file = pdf_files[0]  # Use the first PDF found
    logger.info(f"Testing with PDF: {pdf_file}")
    
    # Create output folder for test
    output_folder = "test_improvements_output"
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        parser = PDFParser()
        
        # Test image extraction with improvements
        logger.info("Extracting images with enhanced filtering...")
        extracted_images = parser.extract_images_from_pdf(pdf_file, output_folder)
        
        logger.info(f"Total images extracted: {len(extracted_images)}")
        
        # Group by page to see distribution
        images_by_page = parser.groupby_images_by_page(extracted_images)
        
        logger.info(f"Images distributed across {len(images_by_page)} pages")
        
        # Show some statistics
        pages_with_multiple_images = sum(1 for page_images in images_by_page.values() if len(page_images) > 1)
        logger.info(f"Pages with multiple images: {pages_with_multiple_images}")
        
        # Show first few pages with images
        for page_num in sorted(list(images_by_page.keys())[:5]):
            page_images = images_by_page[page_num]
            logger.info(f"Page {page_num}: {len(page_images)} images")
            for img in page_images:
                logger.info(f"  - {img['filename']}")
        
        # Test visual content extraction specifically
        logger.info("\nTesting visual content extraction...")
        
        import fitz
        doc = fitz.open(pdf_file)
        visual_images = parser.extract_visual_content_areas(doc, output_folder)
        doc.close()
        
        logger.info(f"Visual content images: {len(visual_images)}")
        
        # Show visual content by page
        visual_by_page = {}
        for img in visual_images:
            page_num = img['page_num']
            if page_num not in visual_by_page:
                visual_by_page[page_num] = []
            visual_by_page[page_num].append(img)
        
        logger.info(f"Visual content on {len(visual_by_page)} pages")
        
        for page_num in sorted(list(visual_by_page.keys())[:5]):
            page_visuals = visual_by_page[page_num]
            logger.info(f"Page {page_num}: {len(page_visuals)} visual items")
            for img in page_visuals:
                content_type = img.get('content_type', 'unknown')
                confidence = img.get('confidence', 0)
                logger.info(f"  - {img['filename']} ({content_type}, confidence: {confidence:.2f})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing with real PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_extraction_quality():
    """Analyze the quality of extractions"""
    logger.info("\n=== Analyzing Extraction Quality ===")
    
    output_folder = "test_improvements_output"
    
    if not os.path.exists(output_folder):
        logger.warning("No output folder found. Run test_with_real_pdf() first.")
        return
    
    # Count different types of extractions
    image_files = [f for f in os.listdir(output_folder) if f.endswith('.png')]
    
    extraction_types = {
        'img': 0,
        'visual': 0,
        'table': 0,
        'equation': 0,
        'raster': 0
    }
    
    for filename in image_files:
        for ext_type in extraction_types.keys():
            if ext_type in filename:
                extraction_types[ext_type] += 1
                break
    
    logger.info("Extraction type distribution:")
    for ext_type, count in extraction_types.items():
        logger.info(f"  {ext_type}: {count} files")
    
    # Analyze file sizes (indicator of quality)
    file_sizes = []
    for filename in image_files:
        filepath = os.path.join(output_folder, filename)
        size = os.path.getsize(filepath)
        file_sizes.append((filename, size))
    
    # Sort by size
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"\nLargest extracted images (likely good quality):")
    for filename, size in file_sizes[:5]:
        logger.info(f"  {filename}: {size:,} bytes")
    
    logger.info(f"\nSmallest extracted images (possibly text-only):")
    for filename, size in file_sizes[-5:]:
        logger.info(f"  {filename}: {size:,} bytes")
    
    # Check for potential duplicates based on size
    size_groups = {}
    for filename, size in file_sizes:
        if size not in size_groups:
            size_groups[size] = []
        size_groups[size].append(filename)
    
    potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
    
    if potential_duplicates:
        logger.info(f"\nPotential duplicates (same file size):")
        for size, files in potential_duplicates.items():
            logger.info(f"  Size {size:,} bytes: {len(files)} files")
            for filename in files:
                logger.info(f"    - {filename}")
    else:
        logger.info("\n✅ No obvious duplicates detected based on file size")

def main():
    """Run the real PDF tests"""
    logger.info("Starting Real PDF Improvements Test")
    logger.info("=" * 60)
    
    try:
        success = test_with_real_pdf()
        
        if success:
            analyze_extraction_quality()
            
            logger.info("\n" + "=" * 60)
            logger.info("Real PDF test completed successfully!")
            logger.info("Check the 'test_improvements_output' folder to see extracted images.")
            logger.info("Compare with previous extractions to see improvement in quality.")
        else:
            logger.error("Real PDF test failed")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
