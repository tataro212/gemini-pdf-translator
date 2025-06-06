#!/usr/bin/env python3
"""
Test script for enhanced PDF extraction features:
- Table extraction as images
- Equation extraction as images  
- Lower image size thresholds
"""

import os
import sys
import logging
from pathlib import Path
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_extraction():
    """Test the enhanced extraction features"""
    
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("❌ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    logger.info(f"📄 Testing enhanced extraction on: {pdf_path}")
    
    # Create output directory
    output_dir = "enhanced_extraction_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize PDF parser
    parser = PDFParser()
    
    logger.info("🚀 ENHANCED PDF EXTRACTION TEST")
    logger.info("=" * 60)
    
    # Test 1: Extract all images with lower thresholds
    logger.info("🖼️  Test 1: Extracting images with lower thresholds...")
    all_images = parser.extract_images_from_pdf(pdf_path, output_dir)
    
    logger.info(f"   ✅ Extracted {len(all_images)} total images")
    
    # Categorize extracted images
    regular_images = [img for img in all_images if img.get('type', 'image') == 'image']
    table_images = [img for img in all_images if img.get('type') == 'table']
    equation_images = [img for img in all_images if img.get('type') == 'equation']
    visual_images = [img for img in all_images if img.get('type') == 'visual']

    logger.info(f"   📊 Regular images: {len(regular_images)}")
    logger.info(f"   📋 Table images: {len(table_images)}")
    logger.info(f"   🧮 Equation images: {len(equation_images)}")
    logger.info(f"   🎨 Visual content images: {len(visual_images)}")
    
    # Test 2: Show configuration settings
    logger.info("\n⚙️  Test 2: Current configuration settings...")
    settings = config_manager.pdf_processing_settings
    
    logger.info(f"   📏 Min image width: {settings.get('min_image_width_px', 'N/A')} px")
    logger.info(f"   📏 Min image height: {settings.get('min_image_height_px', 'N/A')} px")
    logger.info(f"   📋 Extract tables: {settings.get('extract_tables_as_images', 'N/A')}")
    logger.info(f"   🧮 Extract equations: {settings.get('extract_equations_as_images', 'N/A')}")
    logger.info(f"   🎨 Extract visual content: {settings.get('extract_figures_by_caption', 'N/A')}")
    logger.info(f"   📊 Min table columns: {settings.get('min_table_columns', 'N/A')}")
    logger.info(f"   📊 Min table rows: {settings.get('min_table_rows', 'N/A')}")
    
    # Test 3: Analyze extracted content
    logger.info("\n🔍 Test 3: Analyzing extracted content...")
    
    if table_images:
        logger.info("   📋 Table images found:")
        for i, img in enumerate(table_images[:5]):  # Show first 5
            logger.info(f"      {i+1}. {img['filename']} - Page {img['page_num']} - {img['width']}x{img['height']}")
        if len(table_images) > 5:
            logger.info(f"      ... and {len(table_images) - 5} more table images")
    else:
        logger.info("   📋 No table images extracted")
    
    if equation_images:
        logger.info("   🧮 Equation images found:")
        for i, img in enumerate(equation_images[:5]):  # Show first 5
            logger.info(f"      {i+1}. {img['filename']} - Page {img['page_num']} - {img['width']}x{img['height']}")
        if len(equation_images) > 5:
            logger.info(f"      ... and {len(equation_images) - 5} more equation images")
    else:
        logger.info("   🧮 No equation images extracted")

    if visual_images:
        logger.info("   🎨 Visual content images found:")
        for i, img in enumerate(visual_images[:5]):  # Show first 5
            content_type = img.get('content_type', 'unknown')
            logger.info(f"      {i+1}. {img['filename']} - Page {img['page_num']} - {img['width']}x{img['height']} - Type: {content_type}")
        if len(visual_images) > 5:
            logger.info(f"      ... and {len(visual_images) - 5} more visual content images")
    else:
        logger.info("   🎨 No visual content images extracted")
    
    # Test 4: Size distribution analysis
    logger.info("\n📊 Test 4: Image size distribution analysis...")
    
    if all_images:
        sizes = [(img['width'], img['height']) for img in all_images]
        widths = [s[0] for s in sizes]
        heights = [s[1] for s in sizes]
        
        logger.info(f"   📏 Width range: {min(widths)} - {max(widths)} px")
        logger.info(f"   📏 Height range: {min(heights)} - {max(heights)} px")
        logger.info(f"   📏 Average size: {sum(widths)//len(widths)}x{sum(heights)//len(heights)} px")
        
        # Count very small images (that wouldn't be captured with higher thresholds)
        very_small = [img for img in all_images if img['width'] <= 10 or img['height'] <= 10]
        small = [img for img in all_images if 10 < img['width'] <= 50 or 10 < img['height'] <= 50]
        medium = [img for img in all_images if 50 < img['width'] <= 200 or 50 < img['height'] <= 200]
        large = [img for img in all_images if img['width'] > 200 and img['height'] > 200]
        
        logger.info(f"   🔍 Very small (≤10px): {len(very_small)} images")
        logger.info(f"   🔍 Small (11-50px): {len(small)} images")
        logger.info(f"   🔍 Medium (51-200px): {len(medium)} images")
        logger.info(f"   🔍 Large (>200px): {len(large)} images")
    
    # Test 5: File output summary
    logger.info("\n💾 Test 5: Output summary...")
    
    output_files = list(Path(output_dir).glob("*.png"))
    logger.info(f"   📁 Output directory: {output_dir}")
    logger.info(f"   📄 Total files created: {len(output_files)}")
    
    # Group by type
    regular_files = [f for f in output_files if not any(t in f.name for t in ['table', 'equation', 'visual'])]
    table_files = [f for f in output_files if 'table' in f.name]
    equation_files = [f for f in output_files if 'equation' in f.name]
    visual_files = [f for f in output_files if 'visual' in f.name]

    logger.info(f"   🖼️  Regular image files: {len(regular_files)}")
    logger.info(f"   📋 Table image files: {len(table_files)}")
    logger.info(f"   🧮 Equation image files: {len(equation_files)}")
    logger.info(f"   🎨 Visual content files: {len(visual_files)}")
    
    # Calculate total file size
    total_size = sum(f.stat().st_size for f in output_files)
    logger.info(f"   💾 Total output size: {total_size / 1024 / 1024:.2f} MB")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 ENHANCED EXTRACTION TEST COMPLETE")
    logger.info(f"✅ Successfully extracted {len(all_images)} images with enhanced features")
    logger.info(f"📁 Results saved to: {output_dir}")
    
    return all_images

def show_configuration_help():
    """Show help for configuration options"""
    logger.info("⚙️  CONFIGURATION HELP")
    logger.info("=" * 50)
    logger.info("📝 To customize extraction behavior, edit config.ini:")
    logger.info("")
    logger.info("🖼️  Image Extraction:")
    logger.info("   min_image_width_px = 5    # Lower = more images")
    logger.info("   min_image_height_px = 5   # Lower = more images")
    logger.info("")
    logger.info("📋 Table Extraction:")
    logger.info("   extract_tables_as_images = True")
    logger.info("   min_table_columns = 2")
    logger.info("   min_table_rows = 2")
    logger.info("   min_table_width_points = 100")
    logger.info("   min_table_height_points = 50")
    logger.info("")
    logger.info("🧮 Equation Extraction:")
    logger.info("   extract_equations_as_images = True")
    logger.info("   min_equation_width_points = 30")
    logger.info("   min_equation_height_points = 15")
    logger.info("   detect_math_symbols = True")
    logger.info("")
    logger.info("🖼️  Figure Extraction:")
    logger.info("   extract_figures_by_caption = True")
    logger.info("   min_figure_width_points = 50")
    logger.info("   min_figure_height_points = 50")
    logger.info("   max_caption_to_figure_distance_points = 100")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_configuration_help()
    else:
        test_enhanced_extraction()
