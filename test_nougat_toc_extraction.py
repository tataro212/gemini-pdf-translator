#!/usr/bin/env python3
"""
Test script for Nougat TOC (Table of Contents) extraction functionality

This script demonstrates how to use the enhanced Nougat integration to:
1. Fix Nougat installation issues
2. Extract TOC from content pages
3. Analyze title and subtitle structure
4. Generate formatted TOC for translation

Usage:
    python test_nougat_toc_extraction.py
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nougat_integration import NougatIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_nougat_installation():
    """Test and fix Nougat installation"""
    logger.info("🔧 Testing Nougat installation...")
    
    nougat = NougatIntegration()
    
    if nougat.nougat_available:
        logger.info("✅ Nougat is already installed and working")
        return True
    else:
        logger.info("❌ Nougat not available, attempting installation...")
        success = nougat.install_nougat()
        if success:
            logger.info("✅ Nougat installation successful")
            return True
        else:
            logger.error("❌ Nougat installation failed")
            return False

def test_toc_extraction(pdf_path: str):
    """Test TOC extraction from a PDF"""
    logger.info(f"📖 Testing TOC extraction from: {os.path.basename(pdf_path)}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return None
    
    nougat = NougatIntegration()
    
    # Test auto-detection of TOC pages
    logger.info("🔍 Testing auto-detection of TOC pages...")
    toc_data = nougat.scan_content_pages_and_extract_toc(pdf_path, auto_detect=True)
    
    if toc_data:
        logger.info("✅ TOC extraction successful!")
        return toc_data
    else:
        logger.warning("❌ No TOC detected with auto-detection")
        
        # Try specific pages (common TOC locations)
        logger.info("🔍 Trying specific pages for TOC...")
        for page_range in [[1, 2], [2, 3], [1, 2, 3]]:
            logger.info(f"   Testing pages: {page_range}")
            toc_data = nougat.scan_content_pages_and_extract_toc(
                pdf_path, auto_detect=False, specific_pages=page_range
            )
            if toc_data:
                logger.info(f"✅ TOC found on pages: {page_range}")
                return toc_data
        
        logger.error("❌ No TOC found in common locations")
        return None

def analyze_toc_results(toc_data: Dict):
    """Analyze and display TOC extraction results"""
    if not toc_data:
        logger.error("❌ No TOC data to analyze")
        return
    
    logger.info("📊 Analyzing TOC extraction results...")
    
    # Display basic statistics
    total_titles = toc_data.get('total_titles', 0)
    total_subtitles = toc_data.get('total_subtitles', 0)
    max_level = toc_data.get('max_level', 0)
    has_page_numbers = toc_data.get('has_page_numbers', False)
    
    logger.info(f"📈 TOC Statistics:")
    logger.info(f"   • Total titles: {total_titles}")
    logger.info(f"   • Total subtitles: {total_subtitles}")
    logger.info(f"   • Maximum depth level: {max_level}")
    logger.info(f"   • Has page numbers: {has_page_numbers}")
    
    # Display hierarchical structure
    logger.info("🏗️ Hierarchical Structure:")
    for entry in toc_data.get('hierarchical_structure', [])[:10]:  # Show first 10
        indent = "  " * (entry['level'] - 1)
        page_info = f" (page {entry['page_number']})" if entry.get('page_number') else ""
        logger.info(f"   {indent}Level {entry['level']}: {entry['title']}{page_info}")
    
    if len(toc_data.get('hierarchical_structure', [])) > 10:
        logger.info(f"   ... and {len(toc_data['hierarchical_structure']) - 10} more entries")
    
    # Display title-subtitle relationships
    logger.info("🔗 Title-Subtitle Relationships:")
    title_mapping = toc_data.get('title_subtitle_mapping', {})
    for title, info in list(title_mapping.items())[:5]:  # Show first 5
        subtitle_count = len(info.get('subtitles', []))
        logger.info(f"   • '{title}' has {subtitle_count} subtitles")
        for subtitle in info.get('subtitles', [])[:3]:  # Show first 3 subtitles
            logger.info(f"     - {subtitle['title']}")
    
    # Display formatting patterns
    logger.info("🎨 Formatting Patterns:")
    patterns = toc_data.get('formatting_patterns', {})
    for pattern, value in patterns.items():
        logger.info(f"   • {pattern}: {value}")

def test_translation_preparation(toc_data: Dict):
    """Test preparation of TOC for translation"""
    if not toc_data:
        logger.error("❌ No TOC data for translation preparation")
        return None
    
    logger.info("📝 Testing TOC preparation for translation...")
    
    nougat = NougatIntegration()
    translation_toc = nougat.create_toc_for_translation(toc_data, target_language="Spanish")
    
    if translation_toc:
        logger.info("✅ TOC prepared for translation successfully")
        
        # Display translation information
        logger.info("🌐 Translation Preparation Results:")
        logger.info(f"   • Preservation rules: {translation_toc.get('preservation_rules', {})}")
        logger.info(f"   • Formatting template: {translation_toc.get('formatting_template', 'unknown')}")
        logger.info(f"   • Number of placeholders: {len(translation_toc.get('translation_placeholders', []))}")
        
        # Show formatted TOC
        formatted_toc = translation_toc.get('formatted_toc_text', '')
        if formatted_toc:
            logger.info("📄 Formatted TOC (first 500 characters):")
            logger.info(f"   {formatted_toc[:500]}{'...' if len(formatted_toc) > 500 else ''}")
        
        return translation_toc
    else:
        logger.error("❌ Failed to prepare TOC for translation")
        return None

def save_results(toc_data: Dict, translation_toc: Dict, output_dir: str = "toc_extraction_results"):
    """Save extraction results to files"""
    logger.info(f"💾 Saving results to: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw TOC data
    if toc_data:
        toc_file = os.path.join(output_dir, "toc_extraction_results.json")
        with open(toc_file, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        logger.info(f"   ✅ TOC data saved to: {toc_file}")
    
    # Save translation-ready TOC
    if translation_toc:
        translation_file = os.path.join(output_dir, "translation_ready_toc.json")
        with open(translation_file, 'w', encoding='utf-8') as f:
            json.dump(translation_toc, f, indent=2, ensure_ascii=False)
        logger.info(f"   ✅ Translation TOC saved to: {translation_file}")
        
        # Save formatted TOC as text
        formatted_toc = translation_toc.get('formatted_toc_text', '')
        if formatted_toc:
            text_file = os.path.join(output_dir, "formatted_toc.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(formatted_toc)
            logger.info(f"   ✅ Formatted TOC saved to: {text_file}")

def main():
    """Main test function"""
    logger.info("🚀 Starting Nougat TOC Extraction Test")
    
    # Step 1: Test Nougat installation
    if not test_nougat_installation():
        logger.error("❌ Cannot proceed without working Nougat installation")
        return
    
    # Step 2: Find a PDF to test with
    test_pdf = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    
    if not os.path.exists(test_pdf):
        logger.error(f"❌ Test PDF not found: {test_pdf}")
        logger.info("   Please ensure you have a PDF file in the current directory")
        return
    
    # Step 3: Extract TOC
    toc_data = test_toc_extraction(test_pdf)
    
    # Step 4: Analyze results
    analyze_toc_results(toc_data)
    
    # Step 5: Test translation preparation
    translation_toc = test_translation_preparation(toc_data)
    
    # Step 6: Save results
    save_results(toc_data, translation_toc)
    
    logger.info("🎉 Nougat TOC Extraction Test completed!")
    
    if toc_data:
        logger.info("✅ Test PASSED: TOC extraction successful")
    else:
        logger.warning("⚠️ Test PARTIAL: TOC extraction failed, but Nougat is working")

if __name__ == "__main__":
    main()
