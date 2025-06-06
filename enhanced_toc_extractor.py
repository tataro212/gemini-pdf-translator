#!/usr/bin/env python3
"""
Enhanced TOC Extractor using Local Nougat

This script provides comprehensive TOC extraction functionality using
the local Nougat repository to avoid compatibility issues.

Features:
- Automatic TOC page detection
- Manual page specification
- Hierarchical structure analysis
- Title/subtitle classification
- Translation-ready formatting

Usage:
    python enhanced_toc_extractor.py
"""

import os
import sys
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_nougat_wrapper import LocalNougatWrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedTOCExtractor:
    """
    Enhanced TOC extractor using local Nougat wrapper
    """
    
    def __init__(self):
        self.nougat_wrapper = LocalNougatWrapper()
        self.available = self.nougat_wrapper.available
        
    def scan_content_pages(self, pdf_path: str, auto_detect: bool = True, 
                          specific_pages: List[int] = None) -> Optional[Dict]:
        """
        Scan content pages and extract TOC
        
        Args:
            pdf_path: Path to PDF file
            auto_detect: Whether to auto-detect TOC pages
            specific_pages: Specific pages to scan
            
        Returns:
            Complete TOC analysis
        """
        if not self.available:
            logger.error("❌ Local Nougat wrapper not available")
            return None
            
        logger.info(f"🔍 Starting TOC extraction from: {os.path.basename(pdf_path)}")
        
        if specific_pages:
            logger.info(f"📖 Scanning specific pages: {specific_pages}")
            return self._extract_from_specific_pages(pdf_path, specific_pages)
        elif auto_detect:
            logger.info("🔍 Auto-detecting TOC pages...")
            return self._auto_detect_and_extract(pdf_path)
        else:
            logger.error("❌ No pages specified and auto-detect disabled")
            return None
    
    def _extract_from_specific_pages(self, pdf_path: str, pages: List[int]) -> Optional[Dict]:
        """Extract TOC from specific pages"""
        toc_data = self.nougat_wrapper.extract_toc_from_pages(pdf_path, pages)
        
        if toc_data:
            # Enhance with additional analysis
            enhanced_toc = self._enhance_toc_analysis(toc_data)
            return enhanced_toc
        else:
            return None
    
    def _auto_detect_and_extract(self, pdf_path: str) -> Optional[Dict]:
        """Auto-detect TOC pages and extract"""
        # Try common TOC page ranges
        page_ranges = [
            [1, 2],      # First two pages
            [2, 3],      # Pages 2-3
            [1, 2, 3],   # First three pages
            [3, 4],      # Pages 3-4
            [1],         # Just first page
            [2],         # Just second page
            [3]          # Just third page
        ]
        
        for pages in page_ranges:
            logger.info(f"   Trying pages: {pages}")
            
            toc_data = self.nougat_wrapper.extract_toc_from_pages(pdf_path, pages)
            
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info(f"✅ TOC found on pages: {pages}")
                enhanced_toc = self._enhance_toc_analysis(toc_data)
                return enhanced_toc
        
        logger.warning("❌ No TOC detected in common page locations")
        return None
    
    def _enhance_toc_analysis(self, toc_data: Dict) -> Dict:
        """Enhance TOC analysis with additional information"""
        logger.info("✨ Enhancing TOC analysis...")
        
        enhanced = toc_data.copy()
        
        # Add title-subtitle mapping
        enhanced['title_subtitle_mapping'] = self._create_title_subtitle_mapping(
            toc_data.get('hierarchical_structure', [])
        )
        
        # Generate formatted TOC
        enhanced['formatted_toc'] = self._generate_formatted_toc(
            toc_data.get('hierarchical_structure', [])
        )
        
        # Add formatting patterns
        enhanced['formatting_patterns'] = self._analyze_formatting_patterns(
            toc_data.get('entries', [])
        )
        
        # Add translation preparation
        enhanced['translation_ready'] = self._prepare_for_translation(enhanced)
        
        return enhanced
    
    def _create_title_subtitle_mapping(self, hierarchical_structure: List[Dict]) -> Dict:
        """Create mapping between titles and their subtitles"""
        mapping = {}
        current_title = None
        
        for entry in hierarchical_structure:
            level = entry.get('level', 1)
            title = entry.get('title', '')
            
            if level <= 2:  # This is a main title
                current_title = title
                mapping[current_title] = {
                    'entry': entry,
                    'subtitles': []
                }
            elif current_title and level > 2:  # This is a subtitle
                mapping[current_title]['subtitles'].append(entry)
        
        return mapping
    
    def _generate_formatted_toc(self, hierarchical_structure: List[Dict]) -> str:
        """Generate formatted TOC string"""
        formatted_lines = []
        
        for entry in hierarchical_structure:
            level = entry.get('level', 1)
            title = entry.get('title', '')
            page_num = entry.get('page_number')
            
            # Create indentation
            indent = "  " * (level - 1)
            
            # Format entry
            if page_num:
                line = f"{indent}{title} ... {page_num}"
            else:
                line = f"{indent}{title}"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _analyze_formatting_patterns(self, entries: List[Dict]) -> Dict:
        """Analyze formatting patterns in TOC entries"""
        patterns = {
            'has_page_numbers': False,
            'uses_dots': False,
            'uses_headers': False,
            'consistent_indentation': True,
            'entry_types': set()
        }
        
        for entry in entries:
            # Check for page numbers
            if entry.get('page_number'):
                patterns['has_page_numbers'] = True
            
            # Check for dots
            if '...' in entry.get('raw_text', ''):
                patterns['uses_dots'] = True
            
            # Check for headers
            if entry.get('type') == 'header':
                patterns['uses_headers'] = True
            
            # Collect entry types
            patterns['entry_types'].add(entry.get('type', 'unknown'))
        
        # Convert set to list for JSON serialization
        patterns['entry_types'] = list(patterns['entry_types'])
        
        return patterns
    
    def _prepare_for_translation(self, toc_data: Dict) -> Dict:
        """Prepare TOC data for translation workflow"""
        translation_data = {
            'preserve_hierarchy': True,
            'preserve_page_numbers': toc_data.get('has_page_numbers', False),
            'preserve_formatting': True,
            'placeholders': []
        }
        
        # Create placeholders for each entry
        for i, entry in enumerate(toc_data.get('hierarchical_structure', [])):
            placeholder = {
                'id': f"TOC_ENTRY_{i+1}",
                'original_title': entry.get('title', ''),
                'level': entry.get('level', 1),
                'page_number': entry.get('page_number'),
                'placeholder_text': f"[TOC_ENTRY_{i+1}]"
            }
            translation_data['placeholders'].append(placeholder)
        
        return translation_data
    
    def save_results(self, toc_data: Dict, output_dir: str = "toc_extraction_results"):
        """Save TOC extraction results"""
        if not toc_data:
            logger.warning("❌ No TOC data to save")
            return
            
        logger.info(f"💾 Saving TOC results to: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save complete analysis
        analysis_file = os.path.join(output_dir, "toc_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        logger.info(f"   ✅ Analysis saved: {analysis_file}")
        
        # Save formatted TOC
        formatted_toc = toc_data.get('formatted_toc', '')
        if formatted_toc:
            toc_file = os.path.join(output_dir, "formatted_toc.txt")
            with open(toc_file, 'w', encoding='utf-8') as f:
                f.write(formatted_toc)
            logger.info(f"   ✅ Formatted TOC saved: {toc_file}")
        
        # Save translation-ready data
        translation_data = toc_data.get('translation_ready', {})
        if translation_data:
            translation_file = os.path.join(output_dir, "translation_ready.json")
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(translation_data, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Translation data saved: {translation_file}")
    
    def display_results(self, toc_data: Dict):
        """Display TOC extraction results"""
        if not toc_data:
            logger.error("❌ No TOC data to display")
            return
            
        logger.info("📊 TOC Extraction Results:")
        logger.info(f"   • Total entries: {toc_data.get('total_entries', 0)}")
        logger.info(f"   • Main titles: {toc_data.get('total_titles', 0)}")
        logger.info(f"   • Subtitles: {toc_data.get('total_subtitles', 0)}")
        logger.info(f"   • Maximum depth: {toc_data.get('max_level', 0)}")
        logger.info(f"   • Has page numbers: {toc_data.get('has_page_numbers', False)}")
        
        # Display first few entries
        logger.info("📋 First 10 TOC entries:")
        for i, entry in enumerate(toc_data.get('hierarchical_structure', [])[:10]):
            indent = "  " * entry.get('level', 1)
            title = entry.get('title', '')
            page_info = f" (page {entry.get('page_number')})" if entry.get('page_number') else ""
            logger.info(f"   {indent}• {title}{page_info}")
        
        if len(toc_data.get('hierarchical_structure', [])) > 10:
            remaining = len(toc_data['hierarchical_structure']) - 10
            logger.info(f"   ... and {remaining} more entries")

def main():
    """Main function"""
    logger.info("🚀 Starting Enhanced TOC Extraction")
    
    # Initialize extractor
    extractor = EnhancedTOCExtractor()
    
    if not extractor.available:
        logger.error("❌ Local Nougat wrapper not available")
        logger.error("   Please ensure the nougat-main directory exists")
        return
    
    # Find test PDF
    test_pdf = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    
    if not os.path.exists(test_pdf):
        logger.error(f"❌ Test PDF not found: {test_pdf}")
        logger.info("   Please ensure you have a PDF file in the current directory")
        return
    
    # Extract TOC
    logger.info("🔍 Extracting TOC with auto-detection...")
    toc_data = extractor.scan_content_pages(test_pdf, auto_detect=True)
    
    if toc_data:
        # Display results
        extractor.display_results(toc_data)
        
        # Save results
        extractor.save_results(toc_data)
        
        logger.info("🎉 TOC extraction completed successfully!")
        logger.info(f"✅ Found {toc_data.get('total_entries', 0)} TOC entries")
        logger.info(f"   • {toc_data.get('total_titles', 0)} main titles")
        logger.info(f"   • {toc_data.get('total_subtitles', 0)} subtitles")
        
    else:
        logger.warning("⚠️ No TOC found in the document")
        logger.info("   You can try specifying specific pages manually")

if __name__ == "__main__":
    main()
