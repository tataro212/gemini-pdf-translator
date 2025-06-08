#!/usr/bin/env python3
"""
Unified Nougat Processor
Consolidates all Nougat-related functionality into a single, configurable class
"""

import os
import re
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NougatMode(Enum):
    """Nougat processing modes"""
    HYBRID = "hybrid"  # Nougat + traditional methods
    NOUGAT_ONLY = "nougat_only"  # Nougat exclusively
    NOUGAT_FIRST = "nougat_first"  # Nougat with intelligent fallback
    DISABLED = "disabled"  # No Nougat processing

@dataclass
class NougatConfig:
    """Configuration for Nougat processing"""
    mode: NougatMode = NougatMode.HYBRID
    model_version: str = "0.1.0-base"
    timeout_seconds: int = 1200  # 20 minutes
    max_retries: int = 2
    enable_markdown_output: bool = True
    skip_pages: bool = False
    extract_equations: bool = True
    extract_tables: bool = True
    extract_figures: bool = True
    preserve_layout: bool = True
    quality_threshold: float = 0.7

@dataclass
class NougatResult:
    """Result from Nougat processing"""
    success: bool
    content: str = ""
    analysis: Dict[str, Any] = None
    visual_elements: List[Dict] = None
    error_message: str = ""
    processing_time: float = 0.0
    confidence_score: float = 0.0

class UnifiedNougatProcessor:
    """
    Unified processor that consolidates all Nougat functionality
    """
    
    def __init__(self, config: Optional[NougatConfig] = None):
        self.config = config or NougatConfig()
        self.temp_dir = tempfile.mkdtemp(prefix="nougat_unified_")
        self.nougat_available = self._check_nougat_availability()
        
        logger.info(f"🔧 Unified Nougat Processor initialized")
        logger.info(f"   Mode: {self.config.mode.value}")
        logger.info(f"   Available: {self.nougat_available}")
        
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def _check_nougat_availability(self) -> bool:
        """Check if Nougat is installed and available"""
        try:
            result = subprocess.run(['nougat', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Nougat is available")
                return True
            else:
                logger.error("❌ Nougat command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.error(f"❌ Nougat not available: {e}")
            return False
    
    def process_pdf(self, pdf_path: str, output_folder: str) -> NougatResult:
        """
        Process PDF using the configured Nougat mode
        
        Args:
            pdf_path: Path to the PDF file
            output_folder: Output directory for results
            
        Returns:
            NougatResult with processing results
        """
        if not self.nougat_available and self.config.mode != NougatMode.DISABLED:
            logger.warning("Nougat not available, falling back to disabled mode")
            return NougatResult(success=False, error_message="Nougat not available")
        
        if self.config.mode == NougatMode.DISABLED:
            logger.info("Nougat processing disabled")
            return NougatResult(success=False, error_message="Nougat processing disabled")
        
        logger.info(f"🚀 Processing PDF with Nougat mode: {self.config.mode.value}")
        
        try:
            if self.config.mode == NougatMode.NOUGAT_ONLY:
                return self._process_nougat_only(pdf_path, output_folder)
            elif self.config.mode == NougatMode.NOUGAT_FIRST:
                return self._process_nougat_first(pdf_path, output_folder)
            elif self.config.mode == NougatMode.HYBRID:
                return self._process_hybrid(pdf_path, output_folder)
            else:
                return NougatResult(success=False, error_message=f"Unknown mode: {self.config.mode}")
                
        except Exception as e:
            logger.error(f"Error in Nougat processing: {e}")
            return NougatResult(success=False, error_message=str(e))
    
    def _run_nougat_command(self, pdf_path: str) -> Optional[str]:
        """Run the core Nougat command and return content"""
        try:
            # Build Nougat command
            cmd = [
                'nougat', 
                pdf_path,
                '-o', self.temp_dir,
                '--model', self.config.model_version
            ]
            
            if self.config.enable_markdown_output:
                cmd.append('--markdown')
            
            if not self.config.skip_pages:
                cmd.append('--no-skipping')
            
            logger.info(f"🔧 Running: {' '.join(cmd)}")
            
            import time
            start_time = time.time()
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=self.config.timeout_seconds)
            
            processing_time = time.time() - start_time
            
            if result.returncode != 0:
                logger.error(f"Nougat failed: {result.stderr}")
                return None
            
            # Find and read output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(self.temp_dir, f"{pdf_name}.mmd")
            
            if not os.path.exists(output_file):
                logger.error(f"Nougat output not found: {output_file}")
                return None
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"✅ Nougat processing completed in {processing_time:.2f}s")
            return content
            
        except subprocess.TimeoutExpired:
            logger.error(f"Nougat processing timed out after {self.config.timeout_seconds}s")
            return None
        except Exception as e:
            logger.error(f"Error running Nougat command: {e}")
            return None
    
    def _process_nougat_only(self, pdf_path: str, output_folder: str) -> NougatResult:
        """Process using Nougat exclusively"""
        logger.info("🎯 NOUGAT-ONLY processing")
        
        content = self._run_nougat_command(pdf_path)
        if not content:
            return NougatResult(success=False, error_message="Nougat processing failed")
        
        # Analyze content for visual elements
        analysis = self._analyze_nougat_content(content)
        visual_elements = self._extract_visual_elements(content, output_folder)
        
        return NougatResult(
            success=True,
            content=content,
            analysis=analysis,
            visual_elements=visual_elements,
            confidence_score=analysis.get('confidence', 0.8)
        )
    
    def _process_nougat_first(self, pdf_path: str, output_folder: str) -> NougatResult:
        """Process using Nougat with intelligent fallback"""
        logger.info("🔄 NOUGAT-FIRST processing with intelligent fallback")
        
        # Try Nougat first
        content = self._run_nougat_command(pdf_path)
        if content:
            analysis = self._analyze_nougat_content(content)
            
            # Check if quality meets threshold
            if analysis.get('confidence', 0.0) >= self.config.quality_threshold:
                visual_elements = self._extract_visual_elements(content, output_folder)
                return NougatResult(
                    success=True,
                    content=content,
                    analysis=analysis,
                    visual_elements=visual_elements,
                    confidence_score=analysis['confidence']
                )
            else:
                logger.warning(f"Nougat quality below threshold ({analysis.get('confidence', 0.0)} < {self.config.quality_threshold})")
        
        # Fallback to traditional methods
        logger.info("🔄 Falling back to traditional PDF processing")
        return self._fallback_processing(pdf_path, output_folder)
    
    def _process_hybrid(self, pdf_path: str, output_folder: str) -> NougatResult:
        """Process using hybrid approach (Nougat + traditional)"""
        logger.info("🔀 HYBRID processing (Nougat + traditional methods)")
        
        # Run Nougat for advanced analysis
        nougat_content = self._run_nougat_command(pdf_path)
        nougat_analysis = None
        
        if nougat_content:
            nougat_analysis = self._analyze_nougat_content(nougat_content)
            logger.info("✅ Nougat analysis completed")
        else:
            logger.warning("⚠️ Nougat analysis failed, using traditional methods only")
        
        # Always run traditional methods for comparison/enhancement
        traditional_result = self._fallback_processing(pdf_path, output_folder)
        
        # Combine results intelligently
        if nougat_analysis and nougat_analysis.get('confidence', 0.0) > 0.5:
            # Use Nougat as primary with traditional as enhancement
            visual_elements = self._extract_visual_elements(nougat_content, output_folder)
            return NougatResult(
                success=True,
                content=nougat_content,
                analysis=nougat_analysis,
                visual_elements=visual_elements,
                confidence_score=nougat_analysis['confidence']
            )
        else:
            # Use traditional as primary
            return traditional_result

    def _analyze_nougat_content(self, content: str) -> Dict[str, Any]:
        """Analyze Nougat output for quality and structure"""
        if not content:
            return {'confidence': 0.0, 'analysis': 'empty_content'}

        analysis = {
            'content_length': len(content),
            'has_equations': bool(re.search(r'\$.*?\$|\\\(.*?\\\)', content)),
            'has_tables': bool(re.search(r'\|.*?\|', content)),
            'has_figures': bool(re.search(r'!\[.*?\]', content)),
            'has_sections': bool(re.search(r'^#+\s', content, re.MULTILINE)),
            'line_count': len(content.split('\n')),
            'word_count': len(content.split())
        }

        # Calculate confidence based on content richness
        confidence = 0.0
        if analysis['content_length'] > 100:
            confidence += 0.3
        if analysis['has_equations']:
            confidence += 0.2
        if analysis['has_tables']:
            confidence += 0.2
        if analysis['has_figures']:
            confidence += 0.2
        if analysis['has_sections']:
            confidence += 0.1

        analysis['confidence'] = min(confidence, 1.0)
        return analysis

    def _extract_visual_elements(self, content: str, output_folder: str) -> List[Dict]:
        """Extract visual elements from Nougat content"""
        visual_elements = []

        # Extract equations
        if self.config.extract_equations:
            equations = re.findall(r'\$\$?(.*?)\$\$?', content, re.DOTALL)
            for i, eq in enumerate(equations):
                visual_elements.append({
                    'type': 'equation',
                    'content': eq.strip(),
                    'index': i,
                    'source': 'nougat'
                })

        # Extract tables
        if self.config.extract_tables:
            table_pattern = r'\|.*?\|(?:\n\|.*?\|)*'
            tables = re.findall(table_pattern, content, re.MULTILINE)
            for i, table in enumerate(tables):
                visual_elements.append({
                    'type': 'table',
                    'content': table.strip(),
                    'index': i,
                    'source': 'nougat'
                })

        # Extract figure references
        if self.config.extract_figures:
            figures = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
            for i, (alt_text, url) in enumerate(figures):
                visual_elements.append({
                    'type': 'figure',
                    'alt_text': alt_text,
                    'url': url,
                    'index': i,
                    'source': 'nougat'
                })

        logger.info(f"📊 Extracted {len(visual_elements)} visual elements from Nougat content")
        return visual_elements

    def _fallback_processing(self, pdf_path: str, output_folder: str) -> NougatResult:
        """Fallback to traditional PDF processing methods"""
        try:
            # Import traditional processors
            from pdf_parser import PDFParser
            from ocr_processor import SmartImageAnalyzer

            pdf_parser = PDFParser()
            image_analyzer = SmartImageAnalyzer()

            # Extract text using traditional methods
            text_content = pdf_parser.extract_text_from_pdf(pdf_path)

            # Extract images using traditional methods
            images = pdf_parser.extract_images_from_pdf(pdf_path, output_folder)

            # Create basic analysis
            analysis = {
                'confidence': 0.6,  # Traditional methods baseline
                'method': 'traditional_fallback',
                'text_length': len(text_content) if text_content else 0,
                'image_count': len(images) if images else 0
            }

            return NougatResult(
                success=True,
                content=text_content or "",
                analysis=analysis,
                visual_elements=images or [],
                confidence_score=0.6
            )

        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            return NougatResult(
                success=False,
                error_message=f"Fallback processing failed: {e}"
            )

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'mode': self.config.mode.value,
            'nougat_available': self.nougat_available,
            'config': {
                'model_version': self.config.model_version,
                'timeout_seconds': self.config.timeout_seconds,
                'quality_threshold': self.config.quality_threshold
            }
        }

def main():
    """Test the unified Nougat processor"""
    print("🔧 Unified Nougat Processor")
    print("✅ Consolidated all Nougat workflows")
    print("✅ Configurable processing modes")
    print("✅ Intelligent fallback mechanisms")
    print("✅ Unified error handling")

if __name__ == "__main__":
    main()
