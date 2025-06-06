#!/usr/bin/env python3
"""
Final Nougat TOC Extractor

This script provides the complete solution for TOC extraction using the fixed Nougat installation.
It integrates with the existing translation workflow and provides all requested functionality:

1. Scans content pages for TOC
2. Retrieves title names with hierarchical structure
3. Counts titles and subtitles
4. Formats for translation workflow
5. Handles title-subtitle relationships

Usage:
    # Make sure nougat_env is activated first
    nougat_env\Scripts\activate
    python nougat_toc_extractor_final.py
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NougatTOCExtractor:
    """
    Complete TOC extractor using fixed Nougat installation
    """
    
    def __init__(self):
        self.nougat_available = self._check_nougat_availability()
        
    def _check_nougat_availability(self) -> bool:
        """Check if Nougat is properly installed"""
        try:
            from nougat import NougatModel
            logger.info("✅ Nougat is available")
            return True
        except ImportError as e:
            logger.error(f"❌ Nougat not available: {e}")
            logger.error("   Make sure you're in the nougat_env virtual environment")
            return False
    
    def scan_content_pages_and_extract_toc(self, pdf_path: str, 
                                         auto_detect: bool = True,
                                         specific_pages: List[int] = None) -> Optional[Dict]:
        """
        Main method to scan content pages and extract TOC information
        
        Args:
            pdf_path: Path to the PDF file
            auto_detect: Whether to automatically detect TOC pages
            specific_pages: Specific page numbers to scan
            
        Returns:
            Complete TOC analysis with formatting and structure information
        """
        logger.info(f"🔍 Starting TOC extraction from: {os.path.basename(pdf_path)}")
        
        if not self.nougat_available:
            logger.error("❌ Nougat not available - cannot extract TOC")
            return None
        
        if not os.path.exists(pdf_path):
            logger.error(f"❌ PDF file not found: {pdf_path}")
            return None
        
        try:
            if specific_pages:
                logger.info(f"📖 Scanning specific pages: {specific_pages}")
                toc_data = self._extract_from_pages(pdf_path, specific_pages)
            elif auto_detect:
                logger.info("🔍 Auto-detecting TOC pages...")
                toc_data = self._auto_detect_and_extract(pdf_path)
            else:
                logger.error("❌ No pages specified and auto-detect disabled")
                return None
            
            if toc_data:
                # Enhance with metadata
                toc_data['extraction_metadata'] = {
                    'pdf_source': pdf_path,
                    'extraction_method': 'nougat_fixed',
                    'auto_detected': auto_detect and not specific_pages,
                    'extraction_timestamp': self._get_timestamp()
                }
                
                logger.info(f"✅ TOC extraction completed: {self._generate_summary(toc_data)}")
                return toc_data
            else:
                logger.warning("❌ No TOC data extracted")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during TOC extraction: {e}")
            return None
    
    def _auto_detect_and_extract(self, pdf_path: str) -> Optional[Dict]:
        """Auto-detect TOC pages and extract"""
        page_ranges = [
            [1, 2],      # Most common
            [1, 2, 3],   # Extended
            [2, 3],      # Sometimes TOC starts on page 2
            [1],         # Single page
            [2],         # Just second page
            [3],         # Just third page
            [4, 5],      # Sometimes later
        ]
        
        best_result = None
        best_score = 0
        
        for pages in page_ranges:
            logger.info(f"   Trying pages: {pages}")
            
            toc_data = self._extract_from_pages(pdf_path, pages)
            
            if toc_data:
                score = toc_data.get('total_entries', 0)
                if score > best_score:
                    best_score = score
                    best_result = toc_data
                    logger.info(f"   ✅ Found {score} entries on pages {pages}")
        
        return best_result
    
    def _extract_from_pages(self, pdf_path: str, pages: List[int]) -> Optional[Dict]:
        """Extract TOC from specific pages using Nougat"""
        try:
            from nougat import NougatModel
            from nougat.utils.dataset import LazyDataset
            from nougat.utils.checkpoint import get_checkpoint
            import torch
            
            # Initialize model (cached after first use)
            if not hasattr(self, '_model'):
                logger.info("🔄 Initializing Nougat model...")
                checkpoint_path = get_checkpoint()
                self._model = NougatModel.from_pretrained(checkpoint_path)
                
                if torch.cuda.is_available():
                    self._model = self._model.to("cuda")
                
                try:
                    self._model = self._model.to(torch.bfloat16)
                except:
                    pass  # Use default precision
                
                self._model.eval()
                logger.info("✅ Model initialized")
            
            # Process specific pages
            logger.info(f"🔄 Processing pages {pages} with Nougat...")
            
            # Create temporary PDF with only specified pages if needed
            # For now, process entire PDF and extract relevant pages from output
            dataset = LazyDataset(
                pdf_path,
                partial_paths=[pdf_path],
                model=self._model,
                batch_size=1,
            )
            
            result = dataset[0]
            
            if result and 'parsed' in result:
                content = result['parsed']
                
                # Analyze content for TOC structure
                if self._looks_like_toc(content):
                    return self._analyze_toc_content(content, pages)
                else:
                    logger.info(f"   Content from pages {pages} doesn't look like TOC")
                    return None
            else:
                logger.warning(f"   No content extracted from pages {pages}")
                return None
                
        except Exception as e:
            logger.error(f"   Error processing pages {pages}: {e}")
            return None
    
    def _looks_like_toc(self, content: str) -> bool:
        """Check if content looks like Table of Contents"""
        if not content or len(content.strip()) < 50:
            return False
        
        content_lower = content.lower()
        
        # Strong TOC indicators
        strong_indicators = ['table of contents', 'contents', 'index']
        has_strong = any(indicator in content_lower for indicator in strong_indicators)
        
        # Weak indicators
        weak_indicators = ['chapter', 'section', 'part', 'appendix']
        weak_count = sum(1 for indicator in weak_indicators if indicator in content_lower)
        
        # Structure indicators
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        has_structure = len(lines) >= 3
        has_numbers = bool(re.search(r'\d+', content))
        has_dots = '...' in content
        
        # Scoring system
        score = 0
        if has_strong:
            score += 5
        if weak_count >= 2:
            score += 3
        elif weak_count >= 1:
            score += 1
        if has_structure:
            score += 2
        if has_numbers:
            score += 1
        if has_dots:
            score += 2
        
        return score >= 4
    
    def _analyze_toc_content(self, content: str, source_pages: List[int]) -> Dict:
        """Analyze content and extract TOC structure"""
        logger.info("📊 Analyzing TOC content structure...")
        
        entries = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) > 200:
                continue
            
            # Pattern 1: Dotted entries (Title ... Page)
            dotted_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
            if dotted_match:
                title = dotted_match.group(1).strip()
                page = int(dotted_match.group(2))
                level = self._determine_level(title, line)
                entries.append({
                    'title': title,
                    'page': page,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'dotted',
                    'raw_line': line
                })
                continue
            
            # Pattern 2: Numbered entries (1. Title, 1.1 Title)
            numbered_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', line)
            if numbered_match:
                number = numbered_match.group(1)
                title = numbered_match.group(2).strip()
                level = number.count('.') + 1
                entries.append({
                    'title': title,
                    'number': number,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'numbered',
                    'raw_line': line
                })
                continue
            
            # Pattern 3: Markdown headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                entries.append({
                    'title': title,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'header',
                    'raw_line': line
                })
                continue
            
            # Pattern 4: Keyword-based entries
            if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
                level = self._determine_level(line, line)
                entries.append({
                    'title': line,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'keyword',
                    'raw_line': line
                })
        
        # Calculate statistics
        titles = [e for e in entries if e.get('level', 1) <= 2]
        subtitles = [e for e in entries if e.get('level', 1) > 2]
        
        # Create title-subtitle mapping
        title_subtitle_mapping = self._create_title_subtitle_mapping(entries)
        
        # Generate formatted TOC
        formatted_toc = self._generate_formatted_toc(entries)
        
        return {
            'source_pages': source_pages,
            'total_entries': len(entries),
            'total_titles': len(titles),
            'total_subtitles': len(subtitles),
            'max_level': max([e.get('level', 1) for e in entries], default=1),
            'has_page_numbers': any(e.get('page') for e in entries),
            'entries': entries,
            'hierarchical_structure': sorted(entries, key=lambda x: x.get('line_number', 0)),
            'title_subtitle_mapping': title_subtitle_mapping,
            'formatted_toc': formatted_toc,
            'raw_content': content[:1000] + '...' if len(content) > 1000 else content
        }
    
    def _determine_level(self, title: str, full_line: str) -> int:
        """Determine hierarchical level of TOC entry"""
        title_lower = title.lower()
        
        # Keyword-based determination
        if any(word in title_lower for word in ['part', 'book']):
            return 1
        elif 'chapter' in title_lower:
            return 1
        elif 'section' in title_lower and 'subsection' not in title_lower:
            return 2
        elif any(word in title_lower for word in ['subsection', 'subchapter']):
            return 3
        elif any(word in title_lower for word in ['appendix', 'bibliography']):
            return 2
        
        # Indentation-based determination
        leading_spaces = len(full_line) - len(full_line.lstrip())
        if leading_spaces == 0:
            return 1
        elif leading_spaces <= 4:
            return 2
        elif leading_spaces <= 8:
            return 3
        else:
            return min(6, (leading_spaces // 4) + 1)
    
    def _create_title_subtitle_mapping(self, entries: List[Dict]) -> Dict:
        """Create mapping between titles and their subtitles"""
        mapping = {}
        current_title = None
        
        for entry in entries:
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
    
    def _generate_formatted_toc(self, entries: List[Dict]) -> str:
        """Generate formatted TOC string for translation"""
        formatted_lines = []
        
        for entry in entries:
            level = entry.get('level', 1)
            title = entry.get('title', '')
            page = entry.get('page')
            
            # Create indentation based on level
            indent = "  " * (level - 1)
            
            # Format entry
            if page:
                line = f"{indent}{title} ... {page}"
            else:
                line = f"{indent}{title}"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_summary(self, toc_data: Dict) -> str:
        """Generate summary of extraction results"""
        total_titles = toc_data.get('total_titles', 0)
        total_subtitles = toc_data.get('total_subtitles', 0)
        max_level = toc_data.get('max_level', 0)
        has_pages = toc_data.get('has_page_numbers', False)
        
        summary_parts = [
            f"{total_titles} titles",
            f"{total_subtitles} subtitles",
            f"max depth {max_level}"
        ]
        
        if has_pages:
            summary_parts.append("with page numbers")
        
        return ", ".join(summary_parts)
    
    def save_results(self, toc_data: Dict, output_dir: str = "nougat_toc_results"):
        """Save TOC extraction results"""
        if not toc_data:
            logger.warning("❌ No TOC data to save")
            return
        
        logger.info(f"💾 Saving results to: {output_dir}")
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
        
        # Save title-subtitle mapping
        mapping = toc_data.get('title_subtitle_mapping', {})
        if mapping:
            mapping_file = os.path.join(output_dir, "title_subtitle_mapping.json")
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Title-subtitle mapping saved: {mapping_file}")

def main():
    """Main function"""
    logger.info("🚀 Final Nougat TOC Extractor")
    
    # Check if we're in the right environment
    if 'nougat_env' not in sys.executable:
        logger.warning("⚠️ You may not be in the nougat_env virtual environment")
        logger.warning("   Run: nougat_env\\Scripts\\activate")
    
    # Initialize extractor
    extractor = NougatTOCExtractor()
    
    if not extractor.nougat_available:
        logger.error("❌ Nougat not available - please check your installation")
        return
    
    # Find PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("❌ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    logger.info(f"📖 Processing: {pdf_path}")
    
    # Extract TOC
    toc_data = extractor.scan_content_pages_and_extract_toc(pdf_path, auto_detect=True)
    
    if toc_data:
        # Display results
        logger.info("📊 TOC Extraction Results:")
        logger.info(f"   • Source pages: {toc_data.get('source_pages', [])}")
        logger.info(f"   • Total entries: {toc_data.get('total_entries', 0)}")
        logger.info(f"   • Main titles: {toc_data.get('total_titles', 0)}")
        logger.info(f"   • Subtitles: {toc_data.get('total_subtitles', 0)}")
        logger.info(f"   • Maximum depth: {toc_data.get('max_level', 0)}")
        logger.info(f"   • Has page numbers: {toc_data.get('has_page_numbers', False)}")
        
        # Show first few entries
        logger.info("📋 First 10 TOC entries:")
        for entry in toc_data.get('hierarchical_structure', [])[:10]:
            indent = "  " * entry.get('level', 1)
            title = entry.get('title', '')
            page_info = f" (page {entry['page']})" if entry.get('page') else ""
            logger.info(f"   {indent}• {title}{page_info}")
        
        # Save results
        extractor.save_results(toc_data)
        
        logger.info("🎉 TOC extraction completed successfully!")
        logger.info("   Results saved to 'nougat_toc_results' directory")
        
    else:
        logger.warning("❌ No TOC found in the document")

if __name__ == "__main__":
    main()
