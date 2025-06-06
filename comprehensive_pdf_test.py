#!/usr/bin/env python3
"""
Comprehensive test of the PDF image extraction system.
This script will extract images from the PDF and show detailed analysis
of what is detected, filtered, and finally kept.
"""

import os
import sys
import logging
import shutil
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_pdf_file():
    """Find the PDF file in the current directory"""
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        logger.error("❌ No PDF files found in current directory")
        return None
    
    pdf_file = pdf_files[0]
    logger.info(f"📄 Found PDF: {pdf_file}")
    return pdf_file

def create_clean_output_folder():
    """Create a clean output folder for this test"""
    output_folder = "comprehensive_test_output"
    
    # Remove existing folder if it exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        logger.info(f"🗑️ Removed existing output folder")
    
    # Create fresh folder
    os.makedirs(output_folder, exist_ok=True)
    logger.info(f"📁 Created clean output folder: {output_folder}")
    
    return output_folder

def analyze_extraction_results(extracted_images, output_folder):
    """Analyze and display detailed results of image extraction"""
    logger.info(f"\n📊 EXTRACTION ANALYSIS")
    logger.info("=" * 60)
    
    if not extracted_images:
        logger.warning("❌ No images were extracted!")
        return
    
    # Group by page
    by_page = {}
    for img in extracted_images:
        page_num = img['page_num']
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(img)
    
    # Group by type
    by_type = {}
    for img in extracted_images:
        img_type = get_image_type(img['filename'])
        if img_type not in by_type:
            by_type[img_type] = []
        by_type[img_type].append(img)
    
    # Summary statistics
    logger.info(f"📈 SUMMARY STATISTICS:")
    logger.info(f"   Total images extracted: {len(extracted_images)}")
    logger.info(f"   Pages with content: {len(by_page)}")
    logger.info(f"   Average images per page: {len(extracted_images)/len(by_page):.1f}")
    
    # Type distribution
    logger.info(f"\n🏷️ TYPE DISTRIBUTION:")
    for img_type, images in by_type.items():
        logger.info(f"   {img_type}: {len(images)} images")
    
    # Page-by-page analysis
    logger.info(f"\n📄 PAGE-BY-PAGE ANALYSIS:")
    for page_num in sorted(by_page.keys()):
        page_images = by_page[page_num]
        logger.info(f"\n   📖 Page {page_num}: {len(page_images)} images")
        
        for img in page_images:
            file_size = get_file_size(img['filepath'])
            img_type = get_image_type(img['filename'])
            logger.info(f"      • {img['filename']}")
            logger.info(f"        Type: {img_type}, Size: {file_size}")
            
            # Show additional info if available
            if 'confidence' in img:
                logger.info(f"        Confidence: {img['confidence']:.2f}")
            if 'content_type' in img:
                logger.info(f"        Content: {img['content_type']}")
    
    # File size analysis
    logger.info(f"\n💾 FILE SIZE ANALYSIS:")
    file_sizes = []
    for img in extracted_images:
        size = get_file_size_bytes(img['filepath'])
        file_sizes.append((img['filename'], size))
    
    # Sort by size
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"   🏆 Largest files (likely best quality):")
    for filename, size in file_sizes[:5]:
        logger.info(f"      • {filename}: {format_file_size(size)}")
    
    logger.info(f"   🔍 Smallest files (check if appropriate):")
    for filename, size in file_sizes[-5:]:
        logger.info(f"      • {filename}: {format_file_size(size)}")
    
    # Check for potential issues
    logger.info(f"\n⚠️ QUALITY CHECKS:")
    
    # Very small files (potential text-only)
    very_small = [img for img in extracted_images if get_file_size_bytes(img['filepath']) < 20000]
    if very_small:
        logger.info(f"   📝 {len(very_small)} very small files (<20KB) - check if text-only:")
        for img in very_small[:3]:  # Show first 3
            logger.info(f"      • {img['filename']}")
    else:
        logger.info(f"   ✅ No suspiciously small files detected")
    
    # Pages with multiple extractions
    multi_pages = [page for page, images in by_page.items() if len(images) > 1]
    if multi_pages:
        logger.info(f"   🔄 {len(multi_pages)} pages with multiple extractions:")
        for page_num in multi_pages[:5]:  # Show first 5
            count = len(by_page[page_num])
            logger.info(f"      • Page {page_num}: {count} images")
    else:
        logger.info(f"   ✅ No pages with competing extractions")

def get_image_type(filename):
    """Determine image type from filename"""
    if '_visual_' in filename:
        return 'Visual Content'
    elif '_table_' in filename:
        return 'Table'
    elif '_equation_' in filename:
        return 'Equation'
    elif '_img_' in filename:
        return 'Regular Image'
    else:
        return 'Unknown'

def get_file_size(filepath):
    """Get formatted file size"""
    try:
        size = os.path.getsize(filepath)
        return format_file_size(size)
    except:
        return "Unknown"

def get_file_size_bytes(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def test_specific_pages(pdf_file, output_folder):
    """Test extraction on specific pages that were mentioned as problematic"""
    logger.info(f"\n🎯 TESTING SPECIFIC PAGES")
    logger.info("=" * 40)
    
    # Pages that were mentioned as having good results
    good_pages = [22, 36, 38, 41, 54, 58, 71, 76, 79, 86, 91, 134]
    
    # Pages that were mentioned as having issues
    problem_pages = [70, 72]  # These were mentioned as having good results later
    
    parser = PDFParser()
    
    try:
        import fitz
        doc = fitz.open(pdf_file)
        
        logger.info(f"📋 Testing extraction on key pages...")
        
        # Test visual content extraction specifically
        visual_images = parser.extract_visual_content_areas(doc, output_folder)
        
        # Check results for specific pages
        visual_by_page = {}
        for img in visual_images:
            page_num = img['page_num']
            if page_num not in visual_by_page:
                visual_by_page[page_num] = []
            visual_by_page[page_num].append(img)
        
        logger.info(f"\n✅ GOOD PAGES RESULTS:")
        for page_num in good_pages:
            if page_num in visual_by_page:
                images = visual_by_page[page_num]
                logger.info(f"   Page {page_num}: {len(images)} visual extractions ✅")
                for img in images:
                    size = get_file_size(img['filepath'])
                    confidence = img.get('confidence', 'N/A')
                    logger.info(f"      • {img['filename']} ({size}, conf: {confidence})")
            else:
                logger.info(f"   Page {page_num}: No visual extractions ❌")
        
        logger.info(f"\n🔍 PREVIOUSLY PROBLEMATIC PAGES:")
        for page_num in problem_pages:
            if page_num in visual_by_page:
                images = visual_by_page[page_num]
                logger.info(f"   Page {page_num}: {len(images)} visual extractions ✅ (Fixed!)")
                for img in images:
                    size = get_file_size(img['filepath'])
                    confidence = img.get('confidence', 'N/A')
                    logger.info(f"      • {img['filename']} ({size}, conf: {confidence})")
            else:
                logger.info(f"   Page {page_num}: No visual extractions ❌")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Error testing specific pages: {e}")

def main():
    """Run comprehensive PDF test"""
    logger.info("🚀 COMPREHENSIVE PDF IMAGE EXTRACTION TEST")
    logger.info("=" * 70)
    
    try:
        # Find PDF file
        pdf_file = find_pdf_file()
        if not pdf_file:
            return
        
        # Create clean output folder
        output_folder = create_clean_output_folder()
        
        # Show current configuration
        logger.info(f"\n⚙️ CURRENT CONFIGURATION:")
        settings = config_manager.pdf_processing_settings
        logger.info(f"   Header max words: {settings.get('heading_max_words', 'Not set')}")
        logger.info(f"   Min image size: {settings.get('min_image_width_px')}x{settings.get('min_image_height_px')} px")
        logger.info(f"   Extract images: {settings.get('extract_images', False)}")
        logger.info(f"   Extract tables: {settings.get('extract_tables_as_images', False)}")
        logger.info(f"   Extract equations: {settings.get('extract_equations_as_images', False)}")
        logger.info(f"   Extract figures: {settings.get('extract_figures_by_caption', False)}")
        
        # Run full extraction
        logger.info(f"\n🔄 RUNNING FULL EXTRACTION...")
        parser = PDFParser()
        extracted_images = parser.extract_images_from_pdf(pdf_file, output_folder)
        
        # Analyze results
        analyze_extraction_results(extracted_images, output_folder)
        
        # Test specific pages
        test_specific_pages(pdf_file, output_folder)
        
        # Final summary
        logger.info(f"\n🎉 TEST COMPLETED!")
        logger.info(f"📁 Check the '{output_folder}' folder to see all extracted images")
        logger.info(f"📊 Total extractions: {len(extracted_images)}")
        logger.info(f"🔍 Review the analysis above to verify quality")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
