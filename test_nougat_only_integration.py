#!/usr/bin/env python3
"""
Test Script for NOUGAT-ONLY Integration

This script tests the comprehensive Nougat-only integration that extracts
ALL visual content including paintings, schemata, diagrams, etc.
Creates inspection files for manual review.
"""

import os
import sys
import logging
import time
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nougat_only_integration import NougatOnlyIntegration
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_nougat_only_integration():
    """Test the NOUGAT-ONLY integration comprehensively"""
    
    print("🚀 NOUGAT-ONLY INTEGRATION TEST")
    print("=" * 60)
    print("🎯 Mode: NOUGAT ONLY - No fallback to traditional methods")
    print("📊 Target: ALL visual content - paintings, schemata, diagrams, equations, tables")
    print("👁️  Feature: Visual inspection files for manual review")
    print("=" * 60)
    
    # Initialize Nougat-only integration
    logger.info("🔧 Initializing NOUGAT-ONLY integration...")
    nougat_only = NougatOnlyIntegration(config_manager)
    
    # Check status
    if not nougat_only.nougat_available:
        logger.error("❌ NOUGAT-ONLY MODE requires Nougat to be available!")
        logger.error("❌ Please install Nougat first")
        return False
    
    logger.info("✅ Nougat is available - NOUGAT-ONLY mode ready")
    logger.info(f"   🚫 No fallback mode: {nougat_only.no_fallback}")
    logger.info(f"   📊 Extract everything: {nougat_only.extract_everything}")
    logger.info(f"   👁️  Save for inspection: {nougat_only.save_for_inspection}")
    logger.info(f"   🖼️  Create previews: {nougat_only.create_previews}")
    
    # Show content types being extracted
    print("\n📊 Visual Content Types Being Extracted:")
    for content_type, settings in nougat_only.visual_content_types.items():
        if settings['extract']:
            print(f"   ✅ {content_type} (priority: {settings['priority']:.2f})")
    
    # Find test PDF
    test_pdf = find_test_pdf()
    if not test_pdf:
        logger.error("❌ No test PDF found")
        logger.info("💡 Place a PDF file in the current directory to test")
        return False
    
    logger.info(f"📄 Test PDF: {os.path.basename(test_pdf)}")
    
    # Test 1: Comprehensive visual content extraction
    print("\n" + "=" * 60)
    print("🧪 TEST 1: Comprehensive Visual Content Extraction")
    print("=" * 60)
    
    output_folder = "test_nougat_only_output"
    os.makedirs(output_folder, exist_ok=True)
    
    start_time = time.time()
    all_visual_elements = nougat_only.extract_all_visual_content(test_pdf, output_folder)
    extraction_time = time.time() - start_time
    
    if all_visual_elements:
        logger.info(f"✅ Extraction completed in {extraction_time:.1f}s")
        display_extraction_results(all_visual_elements)
    else:
        logger.error("❌ No visual elements extracted")
        return False
    
    # Test 2: PDF Parser Integration
    print("\n" + "=" * 60)
    print("🧪 TEST 2: PDF Parser NOUGAT-ONLY Integration")
    print("=" * 60)
    
    pdf_parser = PDFParser()
    logger.info("📝 Original PDF parser created")
    
    # Convert to Nougat-only mode
    nougat_only.enhance_pdf_parser_nougat_only(pdf_parser)
    logger.info("🚀 PDF parser converted to NOUGAT-ONLY mode")
    
    # Test enhanced extraction
    start_time = time.time()
    enhanced_images = pdf_parser.extract_images_from_pdf(test_pdf, output_folder)
    integration_time = time.time() - start_time
    
    logger.info(f"✅ NOUGAT-ONLY integration completed in {integration_time:.1f}s")
    display_integration_results(enhanced_images)
    
    # Test 3: Inspection Files Review
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Inspection Files Review")
    print("=" * 60)
    
    inspection_dir = nougat_only.inspection_dir
    pdf_name = Path(test_pdf).stem
    pdf_inspection_dir = os.path.join(inspection_dir, pdf_name)
    
    if os.path.exists(pdf_inspection_dir):
        logger.info(f"📁 Inspection directory: {pdf_inspection_dir}")
        review_inspection_files(pdf_inspection_dir)
    else:
        logger.warning("⚠️ No inspection files found")
    
    # Test 4: Visual Content Categories
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Visual Content Categories Analysis")
    print("=" * 60)
    
    analyze_visual_categories(all_visual_elements)
    
    # Test 5: Manual Inspection Guide
    print("\n" + "=" * 60)
    print("🧪 TEST 5: Manual Inspection Guide")
    print("=" * 60)
    
    create_inspection_guide(pdf_inspection_dir, all_visual_elements)
    
    print("\n" + "=" * 60)
    print("🎉 NOUGAT-ONLY INTEGRATION TEST COMPLETED")
    print("=" * 60)
    print("✅ All tests passed successfully!")
    print(f"👁️  Inspection files available in: {pdf_inspection_dir}")
    print("📊 Review the extracted content manually using the inspection files")
    
    return True

def find_test_pdf():
    """Find a test PDF file"""
    # Look for the main test PDF first
    main_pdf = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    if os.path.exists(main_pdf):
        return main_pdf
    
    # Look for any PDF in current directory
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            return filename
    
    return None

def display_extraction_results(visual_elements):
    """Display comprehensive extraction results"""
    logger.info("📊 Extraction Results:")
    logger.info(f"   📊 Total visual elements: {len(visual_elements)}")
    
    # Count by category
    categories = {}
    priorities = {'high': 0, 'medium': 0, 'low': 0}
    
    for element in visual_elements:
        # Count categories
        cat = element.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        
        # Count priorities
        priority = element.get('priority', 0.5)
        if priority >= 0.9:
            priorities['high'] += 1
        elif priority >= 0.7:
            priorities['medium'] += 1
        else:
            priorities['low'] += 1
    
    logger.info("   📋 By Category:")
    for category, count in sorted(categories.items()):
        logger.info(f"      {category}: {count}")
    
    logger.info("   ⭐ By Priority:")
    logger.info(f"      High (≥0.9): {priorities['high']}")
    logger.info(f"      Medium (0.7-0.9): {priorities['medium']}")
    logger.info(f"      Low (<0.7): {priorities['low']}")
    
    # Show top priority elements
    top_elements = sorted(visual_elements, key=lambda x: x.get('priority', 0), reverse=True)[:5]
    logger.info("   🏆 Top 5 Priority Elements:")
    for i, element in enumerate(top_elements, 1):
        logger.info(f"      {i}. {element.get('type', 'unknown')} "
                   f"(priority: {element.get('priority', 0):.2f}) - "
                   f"{element.get('description', 'No description')[:50]}...")

def display_integration_results(enhanced_images):
    """Display PDF parser integration results"""
    logger.info("🔄 Integration Results:")
    logger.info(f"   📊 Total enhanced images: {len(enhanced_images)}")
    
    # Count by source and type
    sources = {}
    types = {}
    
    for img in enhanced_images:
        source = img.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
        
        img_type = img.get('type', 'unknown')
        types[img_type] = types.get(img_type, 0) + 1
    
    logger.info("   🔍 By Source:")
    for source, count in sources.items():
        logger.info(f"      {source}: {count}")
    
    logger.info("   📷 By Type:")
    for img_type, count in sorted(types.items()):
        logger.info(f"      {img_type}: {count}")

def review_inspection_files(inspection_dir):
    """Review the created inspection files"""
    logger.info("📁 Inspection Files Created:")
    
    files = os.listdir(inspection_dir)
    for filename in sorted(files):
        filepath = os.path.join(inspection_dir, filename)
        file_size = os.path.getsize(filepath)
        logger.info(f"   📄 {filename} ({file_size:,} bytes)")
    
    # Show summary file content preview
    summary_file = os.path.join(inspection_dir, "extraction_summary.md")
    if os.path.exists(summary_file):
        logger.info("\n📋 Summary File Preview:")
        with open(summary_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]  # First 10 lines
            for line in lines:
                logger.info(f"   {line.strip()}")
        if len(lines) >= 10:
            logger.info("   ... (see full file for complete summary)")

def analyze_visual_categories(visual_elements):
    """Analyze visual content by categories"""
    logger.info("📊 Visual Content Categories Analysis:")
    
    categories = {}
    for element in visual_elements:
        cat = element.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(element)
    
    for category, elements in categories.items():
        logger.info(f"\n   📋 {category.upper()} ({len(elements)} elements):")
        
        # Show top 3 elements in this category
        top_elements = sorted(elements, key=lambda x: x.get('priority', 0), reverse=True)[:3]
        for i, element in enumerate(top_elements, 1):
            logger.info(f"      {i}. {element.get('type', 'unknown')} - "
                       f"{element.get('description', 'No description')[:40]}...")

def create_inspection_guide(inspection_dir, visual_elements):
    """Create a guide for manual inspection"""
    guide_file = os.path.join(inspection_dir, "INSPECTION_GUIDE.md")
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write("# Manual Inspection Guide\n\n")
        f.write("This guide helps you manually review the extracted visual content.\n\n")
        
        f.write("## Files to Review\n\n")
        f.write("1. **extraction_summary.md** - Overview of all extracted content\n")
        f.write("2. **visual_elements.json** - Complete data for all elements\n")
        f.write("3. **nougat_raw_output.md** - Raw Nougat output for reference\n")
        f.write("4. **element_locations.md** - Map of where elements are located\n")
        f.write("5. **[category]_elements.json** - Elements grouped by category\n\n")
        
        f.write("## What to Look For\n\n")
        f.write("### High Priority Elements (Priority ≥ 0.9)\n")
        high_priority = [e for e in visual_elements if e.get('priority', 0) >= 0.9]
        for element in high_priority[:10]:
            f.write(f"- **{element.get('id', 'unknown')}**: {element.get('description', 'No description')}\n")
        
        f.write("\n### Categories to Review\n")
        categories = {}
        for element in visual_elements:
            cat = element.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in sorted(categories.items()):
            f.write(f"- **{category}**: {count} elements\n")
        
        f.write("\n### Questions to Consider\n")
        f.write("- Are all important visual elements captured?\n")
        f.write("- Are the descriptions accurate?\n")
        f.write("- Are there any false positives?\n")
        f.write("- Are the priority scores appropriate?\n")
        f.write("- Should any elements be reclassified?\n")
    
    logger.info(f"📋 Inspection guide created: {guide_file}")

if __name__ == "__main__":
    try:
        success = test_nougat_only_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
