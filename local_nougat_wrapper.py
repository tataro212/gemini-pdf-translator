#!/usr/bin/env python3
"""
Local Nougat Wrapper

This module provides a wrapper to use the local Nougat repository
when the pip-installed version has compatibility issues.

Usage:
    from local_nougat_wrapper import LocalNougatWrapper
    wrapper = LocalNougatWrapper()
    result = wrapper.process_pdf_pages(pdf_path, pages=[1, 2, 3])
"""

import os
import sys
import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

class LocalNougatWrapper:
    """
    Wrapper for local Nougat repository to avoid compatibility issues
    """
    
    def __init__(self):
        self.nougat_repo_path = self._find_nougat_repo()
        self.available = self._check_availability()
        
    def _find_nougat_repo(self) -> Optional[str]:
        """Find the local Nougat repository"""
        possible_paths = [
            "nougat-main/nougat-main1",
            "nougat-main",
            "../nougat-main/nougat-main1",
            "../nougat-main"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "predict.py")):
                logger.info(f"✅ Found local Nougat repository at: {path}")
                return os.path.abspath(path)
        
        logger.warning("❌ Local Nougat repository not found")
        return None
    
    def _check_availability(self) -> bool:
        """Check if local Nougat is available"""
        if not self.nougat_repo_path:
            return False
            
        predict_py = os.path.join(self.nougat_repo_path, "predict.py")
        if os.path.exists(predict_py):
            logger.info("✅ Local Nougat predict.py found")
            return True
        else:
            logger.warning("❌ Local Nougat predict.py not found")
            return False
    
    def process_pdf_pages(self, pdf_path: str, pages: List[int] = None, output_dir: str = "local_nougat_output") -> Optional[str]:
        """
        Process PDF pages using local Nougat repository
        
        Args:
            pdf_path: Path to PDF file
            pages: List of page numbers to process
            output_dir: Output directory for results
            
        Returns:
            Path to output file or None if failed
        """
        if not self.available:
            logger.error("❌ Local Nougat not available")
            return None
            
        logger.info(f"🔍 Processing PDF with local Nougat: {os.path.basename(pdf_path)}")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare command
            cmd = [sys.executable, "predict.py", pdf_path, "-o", output_dir]
            
            # Add page specification if provided
            if pages:
                page_string = ','.join(map(str, pages))
                cmd.extend(["-p", page_string])
            
            # Run from Nougat directory
            original_cwd = os.getcwd()
            os.chdir(self.nougat_repo_path)
            
            logger.info(f"   Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                # Find output file
                pdf_name = Path(pdf_path).stem
                output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
                
                if os.path.exists(output_file):
                    logger.info(f"✅ Local Nougat processing successful: {output_file}")
                    return output_file
                else:
                    logger.error(f"❌ Output file not found: {output_file}")
                    return None
            else:
                logger.error(f"❌ Local Nougat processing failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Local Nougat processing timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Error in local Nougat processing: {e}")
            return None
        finally:
            # Ensure we're back in original directory
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    def extract_toc_from_pages(self, pdf_path: str, pages: List[int]) -> Optional[Dict]:
        """
        Extract TOC from specific pages using local Nougat
        
        Args:
            pdf_path: Path to PDF file
            pages: List of page numbers containing TOC
            
        Returns:
            Dictionary with TOC analysis or None if failed
        """
        logger.info(f"📖 Extracting TOC from pages {pages} using local Nougat")
        
        output_file = self.process_pdf_pages(pdf_path, pages, "local_toc_output")
        
        if output_file and os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analyze content for TOC structure
                toc_analysis = self._analyze_local_nougat_output(content, pages)
                
                if toc_analysis:
                    logger.info(f"✅ TOC extracted: {len(toc_analysis.get('entries', []))} entries")
                    return toc_analysis
                else:
                    logger.warning("❌ No TOC structure found in output")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Error reading Nougat output: {e}")
                return None
        else:
            logger.error("❌ Failed to get Nougat output")
            return None
    
    def _analyze_local_nougat_output(self, content: str, source_pages: List[int]) -> Optional[Dict]:
        """
        Analyze local Nougat output for TOC structure
        
        Args:
            content: Raw Nougat output content
            source_pages: Pages that were processed
            
        Returns:
            TOC analysis dictionary
        """
        logger.info("📊 Analyzing local Nougat output for TOC structure...")
        
        # Check if content looks like TOC
        if not self._looks_like_toc(content):
            logger.warning("❌ Content doesn't appear to be a TOC")
            return None
        
        toc_analysis = {
            'source_pages': source_pages,
            'raw_content': content,
            'entries': [],
            'hierarchical_structure': [],
            'page_mappings': {},
            'extraction_method': 'local_nougat'
        }
        
        # Extract TOC entries
        entries = self._extract_toc_entries(content)
        toc_analysis['entries'] = entries
        
        # Create hierarchical structure
        hierarchical = self._create_hierarchical_structure(entries)
        toc_analysis['hierarchical_structure'] = hierarchical
        
        # Extract page mappings
        page_mappings = self._extract_page_mappings(entries)
        toc_analysis['page_mappings'] = page_mappings
        
        # Calculate statistics
        toc_analysis['total_entries'] = len(entries)
        toc_analysis['total_titles'] = len([e for e in entries if e.get('level', 0) <= 2])
        toc_analysis['total_subtitles'] = len([e for e in entries if e.get('level', 0) > 2])
        toc_analysis['max_level'] = max([e.get('level', 1) for e in entries], default=1)
        toc_analysis['has_page_numbers'] = bool(page_mappings)
        
        logger.info(f"📈 TOC analysis complete: {toc_analysis['total_entries']} entries")
        return toc_analysis
    
    def _looks_like_toc(self, content: str) -> bool:
        """Check if content looks like a Table of Contents"""
        content_lower = content.lower()
        
        # TOC indicators
        toc_indicators = [
            'contents', 'table of contents', 'index',
            'chapter', 'section', 'part'
        ]
        
        # Page number patterns
        page_patterns = [
            r'\.\.\.\s*\d+',  # dots followed by page numbers
            r'\s+\d+\s*$',    # page numbers at end of lines
        ]
        
        has_toc_words = any(indicator in content_lower for indicator in toc_indicators)
        has_page_numbers = any(re.search(pattern, content, re.MULTILINE) for pattern in page_patterns)
        has_structure = len(content.split('\n')) > 5  # Multiple lines
        
        return has_toc_words and (has_page_numbers or has_structure)
    
    def _extract_toc_entries(self, content: str) -> List[Dict]:
        """Extract individual TOC entries from content"""
        entries = []
        
        # Pattern for entries with page numbers
        dotted_pattern = r'^(.+?)\s*\.\.\.\s*(\d+)\s*$'
        
        # Pattern for markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for dotted entries (title ... page)
            dotted_match = re.match(dotted_pattern, line)
            if dotted_match:
                title = dotted_match.group(1).strip()
                page_num = int(dotted_match.group(2))
                level = self._determine_entry_level(line, title)
                
                entries.append({
                    'title': title,
                    'page_number': page_num,
                    'level': level,
                    'line_number': i + 1,
                    'raw_text': line,
                    'type': 'dotted_entry'
                })
                continue
            
            # Check for markdown headers
            header_match = re.match(header_pattern, line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                entries.append({
                    'title': title,
                    'page_number': None,
                    'level': level,
                    'line_number': i + 1,
                    'raw_text': line,
                    'type': 'header'
                })
                continue
            
            # Check for simple list entries
            if line and not line.startswith('#'):
                # Simple heuristic for TOC entries
                if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
                    level = self._determine_entry_level(line, line)
                    
                    entries.append({
                        'title': line,
                        'page_number': None,
                        'level': level,
                        'line_number': i + 1,
                        'raw_text': line,
                        'type': 'simple_entry'
                    })
        
        return entries
    
    def _determine_entry_level(self, line: str, title: str) -> int:
        """Determine hierarchical level of TOC entry"""
        # Count leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        
        # Keywords that indicate level
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['part', 'book']):
            return 1
        elif any(word in title_lower for word in ['chapter']):
            return 1
        elif any(word in title_lower for word in ['section']):
            return 2
        elif any(word in title_lower for word in ['subsection']):
            return 3
        elif any(word in title_lower for word in ['appendix']):
            return 2
        
        # Based on indentation
        if leading_spaces == 0:
            return 1
        elif leading_spaces <= 4:
            return 2
        elif leading_spaces <= 8:
            return 3
        else:
            return min(6, (leading_spaces // 4) + 1)
    
    def _create_hierarchical_structure(self, entries: List[Dict]) -> List[Dict]:
        """Create hierarchical structure from flat entries"""
        return sorted(entries, key=lambda x: x.get('line_number', 0))
    
    def _extract_page_mappings(self, entries: List[Dict]) -> Dict[str, int]:
        """Extract title to page number mappings"""
        mappings = {}
        
        for entry in entries:
            if entry.get('page_number'):
                mappings[entry['title']] = entry['page_number']
        
        return mappings
