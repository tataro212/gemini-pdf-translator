#!/usr/bin/env python3
"""
Comprehensive TOC Extraction Test

This script demonstrates the enhanced Nougat integration with fallback methods
for extracting Table of Contents from PDFs. It handles Nougat compatibility issues
by using multiple extraction methods.

Features:
- Nougat integration with fallback methods
- PyPDF2, pdfplumber, and manual pattern extraction
- Automatic TOC page detection
- Title/subtitle classification
- Translation-ready formatting

Usage:
    python comprehensive_toc_test.py
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nougat_integration import NougatIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_nougat_availability():
    """Test Nougat availability and fallback methods"""
    logger.info("🔧 Testing Nougat availability and fallback methods...")
    
    nougat = NougatIntegration()
    
    logger.info(f"   Nougat available: {nougat.nougat_available}")
    logger.info(f"   Alternative available: {nougat.use_alternative}")
    
    return nougat

def test_toc_extraction_comprehensive(pdf_path: str):
    """Test comprehensive TOC extraction with all methods"""
    logger.info(f"📖 Testing comprehensive TOC extraction: {os.path.basename(pdf_path)}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return None
    
    nougat = NougatIntegration()
    
    # Test auto-detection
    logger.info("🔍 Testing auto-detection...")
    toc_data = nougat.scan_content_pages_and_extract_toc(pdf_path, auto_detect=True)
    
    if toc_data:
        logger.info("✅ Auto-detection successful!")
        return toc_data
    else:
        logger.warning("❌ Auto-detection failed")
        
        # Test specific pages
        logger.info("🔍 Testing specific page ranges...")
        for pages in [[1, 2], [2, 3], [1, 2, 3], [1], [2], [3]]:
            logger.info(f"   Trying pages: {pages}")
            toc_data = nougat.scan_content_pages_and_extract_toc(
                pdf_path, auto_detect=False, specific_pages=pages
            )
            if toc_data:
                logger.info(f"✅ TOC found on pages: {pages}")
                return toc_data
        
        logger.error("❌ No TOC found with any method")
        return None

def analyze_toc_results(toc_data: dict):
    """Analyze and display comprehensive TOC results"""
    if not toc_data:
        logger.error("❌ No TOC data to analyze")
        return
    
    logger.info("📊 Analyzing comprehensive TOC results...")
    
    # Display basic statistics
    logger.info(f"📈 TOC Statistics:")
    logger.info(f"   • Source pages: {toc_data.get('source_pages', [])}")
    logger.info(f"   • Extraction method: {toc_data.get('extraction_method', 'unknown')}")
    logger.info(f"   • Total entries: {toc_data.get('total_entries', 0)}")
    logger.info(f"   • Main titles: {toc_data.get('total_titles', 0)}")
    logger.info(f"   • Subtitles: {toc_data.get('total_subtitles', 0)}")
    logger.info(f"   • Maximum depth: {toc_data.get('max_level', 0)}")
    logger.info(f"   • Has page numbers: {toc_data.get('has_page_numbers', False)}")
    
    # Display hierarchical structure
    logger.info("🏗️ Hierarchical Structure (first 15 entries):")
    entries = toc_data.get('hierarchical_structure', [])
    for entry in entries[:15]:
        indent = "  " * (entry.get('level', 1) - 1)
        title = entry.get('title', '')
        page_info = f" (page {entry['page']})" if entry.get('page') else ""
        entry_type = entry.get('type', 'unknown')
        logger.info(f"   {indent}• {title}{page_info} [{entry_type}]")
    
    if len(entries) > 15:
        logger.info(f"   ... and {len(entries) - 15} more entries")
    
    # Display extraction metadata
    metadata = toc_data.get('extraction_metadata', {})
    if metadata:
        logger.info("🔍 Extraction Metadata:")
        for key, value in metadata.items():
            logger.info(f"   • {key}: {value}")

def test_fallback_methods(pdf_path: str):
    """Test individual fallback methods"""
    logger.info("🔄 Testing individual fallback methods...")
    
    nougat = NougatIntegration()
    pages = [1, 2, 3]
    
    # Test each method individually
    methods = [
        ("Nougat command", nougat._extract_toc_with_nougat_command),
        ("PyPDF2", nougat._extract_toc_with_pypdf),
        ("pdfplumber", nougat._extract_toc_with_pdfplumber),
        ("Manual patterns", nougat._extract_toc_manual_patterns)
    ]
    
    results = {}
    
    for method_name, method_func in methods:
        logger.info(f"   Testing {method_name}...")
        try:
            result = method_func(pdf_path, pages)
            if result and result.get('total_entries', 0) > 0:
                logger.info(f"   ✅ {method_name}: {result['total_entries']} entries")
                results[method_name] = result
            else:
                logger.info(f"   ❌ {method_name}: No results")
                results[method_name] = None
        except Exception as e:
            logger.info(f"   ❌ {method_name}: Error - {e}")
            results[method_name] = None
    
    return results

def save_comprehensive_results(toc_data: dict, fallback_results: dict, output_dir: str = "comprehensive_toc_results"):
    """Save comprehensive test results"""
    logger.info(f"💾 Saving comprehensive results to: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main TOC data
    if toc_data:
        main_file = os.path.join(output_dir, "main_toc_results.json")
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        logger.info(f"   ✅ Main results saved: {main_file}")
        
        # Save formatted TOC
        formatted_toc = toc_data.get('formatted_toc', '')
        if formatted_toc:
            toc_file = os.path.join(output_dir, "formatted_toc.txt")
            with open(toc_file, 'w', encoding='utf-8') as f:
                f.write(formatted_toc)
            logger.info(f"   ✅ Formatted TOC saved: {toc_file}")
    
    # Save fallback method results
    if fallback_results:
        fallback_file = os.path.join(output_dir, "fallback_method_results.json")
        with open(fallback_file, 'w', encoding='utf-8') as f:
            json.dump(fallback_results, f, indent=2, ensure_ascii=False)
        logger.info(f"   ✅ Fallback results saved: {fallback_file}")
    
    # Create summary report
    summary_file = os.path.join(output_dir, "extraction_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("Comprehensive TOC Extraction Summary\n")
        f.write("=" * 40 + "\n\n")
        
        if toc_data:
            f.write(f"Main Extraction Results:\n")
            f.write(f"  Method: {toc_data.get('extraction_method', 'unknown')}\n")
            f.write(f"  Pages: {toc_data.get('source_pages', [])}\n")
            f.write(f"  Entries: {toc_data.get('total_entries', 0)}\n")
            f.write(f"  Titles: {toc_data.get('total_titles', 0)}\n")
            f.write(f"  Subtitles: {toc_data.get('total_subtitles', 0)}\n\n")
        
        f.write("Fallback Method Results:\n")
        for method, result in fallback_results.items():
            if result:
                f.write(f"  {method}: {result.get('total_entries', 0)} entries\n")
            else:
                f.write(f"  {method}: Failed\n")
    
    logger.info(f"   ✅ Summary saved: {summary_file}")

def display_usage_instructions():
    """Display usage instructions for the enhanced TOC extraction"""
    logger.info("📋 Usage Instructions for Enhanced TOC Extraction:")
    logger.info("")
    logger.info("1. **Basic Usage:**")
    logger.info("   from nougat_integration import NougatIntegration")
    logger.info("   nougat = NougatIntegration()")
    logger.info("   toc_data = nougat.scan_content_pages_and_extract_toc('document.pdf')")
    logger.info("")
    logger.info("2. **Specific Pages:**")
    logger.info("   toc_data = nougat.scan_content_pages_and_extract_toc('document.pdf', specific_pages=[1, 2, 3])")
    logger.info("")
    logger.info("3. **Manual Fallback:**")
    logger.info("   toc_data = nougat.extract_toc_with_fallback('document.pdf', pages=[1, 2])")
    logger.info("")
    logger.info("4. **The system automatically tries:**")
    logger.info("   • Nougat command line (if available)")
    logger.info("   • PyPDF2 text extraction")
    logger.info("   • pdfplumber extraction")
    logger.info("   • Manual pattern recognition")
    logger.info("")
    logger.info("5. **Results include:**")
    logger.info("   • Hierarchical structure with levels")
    logger.info("   • Title/subtitle classification")
    logger.info("   • Page number mapping (if available)")
    logger.info("   • Formatted TOC for translation")

def main():
    """Main comprehensive test function"""
    logger.info("🚀 Starting Comprehensive TOC Extraction Test")
    
    # Step 1: Test Nougat availability
    nougat = test_nougat_availability()
    
    # Step 2: Find test PDF
    test_pdf = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    
    if not os.path.exists(test_pdf):
        logger.error(f"❌ Test PDF not found: {test_pdf}")
        logger.info("   Please ensure you have a PDF file in the current directory")
        return
    
    # Step 3: Test comprehensive extraction
    toc_data = test_toc_extraction_comprehensive(test_pdf)
    
    # Step 4: Test individual fallback methods
    fallback_results = test_fallback_methods(test_pdf)
    
    # Step 5: Analyze results
    analyze_toc_results(toc_data)
    
    # Step 6: Save results
    save_comprehensive_results(toc_data, fallback_results)
    
    # Step 7: Display usage instructions
    display_usage_instructions()
    
    # Final summary
    if toc_data:
        logger.info("🎉 Comprehensive TOC extraction test completed successfully!")
        logger.info(f"✅ Found {toc_data.get('total_entries', 0)} TOC entries using {toc_data.get('extraction_method', 'unknown')} method")
        logger.info(f"   • {toc_data.get('total_titles', 0)} main titles")
        logger.info(f"   • {toc_data.get('total_subtitles', 0)} subtitles")
        logger.info(f"   • Results saved to 'comprehensive_toc_results' directory")
    else:
        logger.warning("⚠️ No TOC found, but fallback methods are available")
        logger.info("   Check 'comprehensive_toc_results' for individual method results")

if __name__ == "__main__":
    main()
