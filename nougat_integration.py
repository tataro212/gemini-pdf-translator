"""
Nougat Integration Module for Ultimate PDF Translator

This module integrates Nougat (Neural Optical Understanding for Academic Documents)
to enhance PDF parsing, especially for academic documents with complex layouts,
mathematical equations, and structured content.
"""

import os
import logging
import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class NougatIntegration:
    """
    Integrates Nougat for enhanced academic document parsing
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.nougat_available = self._check_nougat_availability()
        self.temp_dir = "nougat_temp"
        self.use_alternative = False

        # Try to load alternative if Nougat not available
        if not self.nougat_available:
            self.use_alternative = self._try_load_alternative()
        
    def _check_nougat_availability(self) -> bool:
        """Check if Nougat is installed and available"""
        try:
            result = subprocess.run(['nougat', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Nougat is available and ready to use")
                return True
            else:
                logger.warning("❌ Nougat command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.warning(f"❌ Nougat not available: {e}")
            return False
    
    def install_nougat(self) -> bool:
        """Install Nougat if not available"""
        if self.nougat_available:
            return True
            
        logger.info("Installing Nougat...")
        try:
            # Install nougat-ocr
            result = subprocess.run(['pip', 'install', 'nougat-ocr'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Nougat installed successfully")
                self.nougat_available = self._check_nougat_availability()
                return self.nougat_available
            else:
                logger.error(f"❌ Failed to install Nougat: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing Nougat: {e}")
            return False
    
    def parse_pdf_with_nougat(self, pdf_path: str, output_dir: str = None) -> Optional[Dict]:
        """
        Parse PDF using Nougat and return structured content
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save Nougat output (optional)
            
        Returns:
            Dictionary containing parsed content structure
        """
        if not self.nougat_available:
            logger.warning("Nougat not available, attempting to install...")
            if not self.install_nougat():
                logger.error("Cannot proceed without Nougat")
                return None
        
        if output_dir is None:
            output_dir = self.temp_dir
            
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            logger.info(f"🔍 Parsing PDF with Nougat: {os.path.basename(pdf_path)}")
            
            # Run Nougat on the PDF
            cmd = [
                'nougat', 
                pdf_path,
                '-o', output_dir,
                '--markdown'  # Ensure markdown output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Nougat parsing failed: {result.stderr}")
                return None
            
            # Find the output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
            
            if not os.path.exists(output_file):
                logger.error(f"Nougat output file not found: {output_file}")
                return None
            
            # Parse the Nougat output
            with open(output_file, 'r', encoding='utf-8') as f:
                nougat_content = f.read()
            
            # Analyze and structure the content
            structured_content = self._analyze_nougat_output(nougat_content, pdf_path)
            
            logger.info(f"✅ Nougat parsing completed successfully")
            return structured_content
            
        except subprocess.TimeoutExpired:
            logger.error("Nougat parsing timed out")
            return None
        except Exception as e:
            logger.error(f"Error during Nougat parsing: {e}")
            return None
    
    def _analyze_nougat_output(self, content: str, pdf_path: str) -> Dict:
        """
        Analyze Nougat output and extract structured information
        
        Args:
            content: Raw Nougat markdown output
            pdf_path: Original PDF path for reference
            
        Returns:
            Structured content dictionary
        """
        logger.info("📊 Analyzing Nougat output structure...")
        
        analysis = {
            'source_pdf': pdf_path,
            'raw_content': content,
            'mathematical_equations': self._extract_math_equations(content),
            'tables': self._extract_tables(content),
            'sections': self._extract_sections(content),
            'figures_references': self._extract_figure_references(content),
            'text_blocks': self._extract_text_blocks(content),
            'metadata': self._extract_metadata(content)
        }
        
        logger.info(f"📈 Analysis complete: {len(analysis['mathematical_equations'])} equations, "
                   f"{len(analysis['tables'])} tables, {len(analysis['sections'])} sections")
        
        return analysis
    
    def _extract_math_equations(self, content: str) -> List[Dict]:
        """Extract mathematical equations from Nougat output"""
        equations = []
        
        # Nougat outputs LaTeX math in various formats
        patterns = [
            r'\$\$([^$]+)\$\$',  # Display math
            r'\$([^$]+)\$',      # Inline math
            r'\\begin\{equation\}(.*?)\\end\{equation\}',  # Equation environment
            r'\\begin\{align\}(.*?)\\end\{align\}',        # Align environment
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                equations.append({
                    'type': ['display', 'inline', 'equation', 'align'][i],
                    'latex': match.group(1).strip(),
                    'position': match.span(),
                    'raw_match': match.group(0)
                })
        
        logger.debug(f"Extracted {len(equations)} mathematical equations")
        return equations
    
    def _extract_tables(self, content: str) -> List[Dict]:
        """Extract table structures from Nougat output"""
        tables = []
        
        # Nougat outputs tables in markdown format
        table_pattern = r'(\|[^\n]*\|\n(?:\|[^\n]*\|\n)*)'
        
        matches = re.finditer(table_pattern, content, re.MULTILINE)
        for i, match in enumerate(matches):
            table_text = match.group(1)
            rows = [row.strip() for row in table_text.split('\n') if row.strip()]
            
            tables.append({
                'id': f'table_{i+1}',
                'markdown': table_text,
                'rows': rows,
                'position': match.span(),
                'row_count': len(rows),
                'estimated_columns': len(rows[0].split('|')) - 2 if rows else 0
            })
        
        logger.debug(f"Extracted {len(tables)} tables")
        return tables
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract section structure from Nougat output"""
        sections = []
        
        # Look for markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        
        matches = re.finditer(header_pattern, content, re.MULTILINE)
        for match in matches:
            level = len(match.group(1))
            title = match.group(2).strip()
            
            sections.append({
                'level': level,
                'title': title,
                'position': match.span(),
                'raw_header': match.group(0)
            })
        
        logger.debug(f"Extracted {len(sections)} sections")
        return sections
    
    def _extract_figure_references(self, content: str) -> List[Dict]:
        """Extract figure references from Nougat output"""
        references = []
        
        # Common figure reference patterns
        patterns = [
            r'Figure\s+(\d+)',
            r'Fig\.\s*(\d+)',
            r'figure\s+(\d+)',
            r'see\s+Figure\s+(\d+)',
            r'shown\s+in\s+Figure\s+(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                references.append({
                    'figure_number': match.group(1),
                    'reference_text': match.group(0),
                    'position': match.span()
                })
        
        logger.debug(f"Extracted {len(references)} figure references")
        return references
    
    def _extract_text_blocks(self, content: str) -> List[Dict]:
        """Extract and classify text blocks"""
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        text_blocks = []
        for i, paragraph in enumerate(paragraphs):
            text_blocks.append({
                'id': f'block_{i+1}',
                'text': paragraph,
                'word_count': len(paragraph.split()),
                'type': self._classify_text_block(paragraph)
            })
        
        return text_blocks
    
    def _classify_text_block(self, text: str) -> str:
        """Classify a text block by type"""
        text_lower = text.lower()
        
        if text.startswith('#'):
            return 'header'
        elif '|' in text and text.count('|') > 2:
            return 'table'
        elif '$' in text or '\\' in text:
            return 'math'
        elif any(word in text_lower for word in ['figure', 'table', 'equation']):
            return 'reference'
        elif len(text.split()) < 10:
            return 'short'
        else:
            return 'paragraph'
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract document metadata from Nougat output"""
        metadata = {
            'total_length': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'has_math': '$' in content or '\\begin{' in content,
            'has_tables': '|' in content,
            'has_figures': 'figure' in content.lower()
        }
        
        return metadata

    def create_hybrid_content(self, nougat_analysis: Dict, extracted_images: List[Dict]) -> Dict:
        """
        Create hybrid content combining Nougat's structured analysis with our image extraction

        Args:
            nougat_analysis: Structured content from Nougat
            extracted_images: Images extracted by our visual detection system

        Returns:
            Hybrid content structure optimized for translation
        """
        logger.info("🔄 Creating hybrid content structure...")

        hybrid_content = {
            'text_for_translation': self._prepare_translation_text(nougat_analysis),
            'mathematical_content': nougat_analysis['mathematical_equations'],
            'table_content': nougat_analysis['tables'],
            'visual_content': self._merge_visual_content(nougat_analysis, extracted_images),
            'document_structure': nougat_analysis['sections'],
            'translation_strategy': self._determine_translation_strategy(nougat_analysis)
        }

        logger.info(f"✅ Hybrid content created with {len(hybrid_content['visual_content'])} visual elements")
        return hybrid_content

    def _prepare_translation_text(self, nougat_analysis: Dict) -> str:
        """
        Prepare clean text for translation, removing math and table content
        that should be handled separately
        """
        content = nougat_analysis['raw_content']

        # Remove mathematical equations (they'll be handled separately)
        for eq in nougat_analysis['mathematical_equations']:
            content = content.replace(eq['raw_match'], f"[MATH_EQUATION_{eq.get('type', 'unknown')}]")

        # Mark table locations (they'll be handled as images)
        for i, table in enumerate(nougat_analysis['tables']):
            content = content.replace(table['markdown'], f"[TABLE_{i+1}]")

        # Clean up the content for better translation
        content = self._clean_content_for_translation(content)

        return content

    def _clean_content_for_translation(self, content: str) -> str:
        """Clean content to improve translation quality"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Fix common Nougat artifacts
        content = re.sub(r'\[MISSING_PAGE.*?\]', '', content)
        content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', content)  # Remove LaTeX commands

        # Normalize spacing
        content = re.sub(r' +', ' ', content)

        return content.strip()

    def _merge_visual_content(self, nougat_analysis: Dict, extracted_images: List[Dict]) -> List[Dict]:
        """
        Intelligently merge Nougat's content analysis with our visual extraction
        """
        visual_content = []

        # Add our extracted images (these are actual visual content)
        for img in extracted_images:
            visual_content.append({
                'type': 'extracted_image',
                'source': 'visual_detection',
                'data': img,
                'confidence': img.get('confidence', 0.8)
            })

        # Add table content as potential images (if configured)
        for table in nougat_analysis['tables']:
            visual_content.append({
                'type': 'table',
                'source': 'nougat',
                'data': table,
                'confidence': 0.9
            })

        # Add mathematical equations as potential images (if complex)
        for eq in nougat_analysis['mathematical_equations']:
            if eq['type'] in ['display', 'equation', 'align']:  # Complex equations
                visual_content.append({
                    'type': 'equation',
                    'source': 'nougat',
                    'data': eq,
                    'confidence': 0.95
                })

        return visual_content

    def _determine_translation_strategy(self, nougat_analysis: Dict) -> Dict:
        """
        Determine optimal translation strategy based on document analysis
        """
        metadata = nougat_analysis['metadata']

        strategy = {
            'approach': 'academic',  # Default for Nougat-processed documents
            'preserve_math': metadata['has_math'],
            'preserve_tables': metadata['has_tables'],
            'chunk_size': 'medium',  # Academic documents benefit from medium chunks
            'quality_level': 'high',  # Academic content needs high quality
            'special_handling': []
        }

        # Adjust strategy based on content
        if len(nougat_analysis['mathematical_equations']) > 10:
            strategy['special_handling'].append('math_heavy')
            strategy['chunk_size'] = 'small'  # Smaller chunks for math-heavy content

        if len(nougat_analysis['tables']) > 5:
            strategy['special_handling'].append('table_heavy')

        if len(nougat_analysis['sections']) > 20:
            strategy['special_handling'].append('long_document')
            strategy['chunk_size'] = 'large'  # Larger chunks for very long documents

        return strategy

    def enhance_pdf_parser_with_nougat(self, pdf_parser_instance):
        """
        Enhance an existing PDF parser instance with Nougat capabilities

        Args:
            pdf_parser_instance: Instance of PDFParser to enhance
        """
        logger.info("🚀 Enhancing PDF parser with Nougat capabilities...")

        # Store original methods
        original_extract_images = pdf_parser_instance.extract_images_from_pdf

        def enhanced_extract_images(pdf_filepath, output_image_folder):
            """Enhanced image extraction using both Nougat and visual detection"""
            logger.info("🔍 Using hybrid Nougat + Visual detection approach...")

            # Step 1: Run Nougat analysis
            nougat_analysis = self.parse_pdf_with_nougat(pdf_filepath)

            # Step 2: Run original visual detection
            visual_images = original_extract_images(pdf_filepath, output_image_folder)

            # Step 3: Create hybrid content
            if nougat_analysis:
                hybrid_content = self.create_hybrid_content(nougat_analysis, visual_images)

                # Store Nougat analysis for later use
                pdf_parser_instance._nougat_analysis = nougat_analysis
                pdf_parser_instance._hybrid_content = hybrid_content

                # Return enhanced image list
                return self._create_enhanced_image_list(hybrid_content, output_image_folder)
            else:
                logger.warning("Nougat analysis failed, falling back to visual detection only")
                return visual_images

        # Replace the method
        pdf_parser_instance.extract_images_from_pdf = enhanced_extract_images

        logger.info("✅ PDF parser enhanced with Nougat capabilities")

    def _create_enhanced_image_list(self, hybrid_content: Dict, output_folder: str) -> List[Dict]:
        """
        Create an enhanced image list from hybrid content
        """
        enhanced_images = []

        # Add visual images (actual diagrams/figures)
        for visual in hybrid_content['visual_content']:
            if visual['type'] == 'extracted_image':
                enhanced_images.append(visual['data'])
            elif visual['type'] in ['table', 'equation'] and visual['confidence'] > 0.8:
                # For high-confidence tables/equations, create placeholder entries
                enhanced_images.append({
                    'filename': f"nougat_{visual['type']}_{len(enhanced_images)+1}.placeholder",
                    'filepath': os.path.join(output_folder, f"nougat_{visual['type']}_{len(enhanced_images)+1}.placeholder"),
                    'page_num': 1,  # Will be determined later
                    'type': visual['type'],
                    'source': 'nougat',
                    'data': visual['data'],
                    'confidence': visual['confidence']
                })

        return enhanced_images

    def _try_load_alternative(self) -> bool:
        """Try to load Nougat alternative implementation"""
        try:
            # Check if alternative exists
            if os.path.exists('nougat_alternative.py'):
                import nougat_alternative
                self.alternative = nougat_alternative.nougat_alternative
                logger.info("✅ Loaded Nougat alternative implementation")
                return True
            else:
                logger.warning("❌ Nougat alternative not found")
                return False
        except Exception as e:
            logger.warning(f"❌ Failed to load Nougat alternative: {e}")
            return False

    def parse_pdf_with_alternative(self, pdf_path: str) -> Optional[Dict]:
        """Parse PDF using alternative implementation when Nougat unavailable"""
        if not self.use_alternative:
            return None

        try:
            logger.info(f"🔄 Using alternative PDF parsing for: {os.path.basename(pdf_path)}")
            analysis = self.alternative.parse_pdf_basic(pdf_path)

            if analysis:
                logger.info("✅ Alternative parsing completed")
                return analysis
            else:
                logger.error("❌ Alternative parsing failed")
                return None

        except Exception as e:
            logger.error(f"❌ Error in alternative parsing: {e}")
            return None

    def parse_pdf_with_fallback(self, pdf_path: str, output_dir: str = None) -> Optional[Dict]:
        """
        Parse PDF with automatic fallback to alternative if Nougat unavailable
        """
        # Try Nougat first
        if self.nougat_available:
            result = self.parse_pdf_with_nougat(pdf_path, output_dir)
            if result:
                return result

        # Fallback to alternative
        if self.use_alternative:
            logger.info("🔄 Falling back to alternative implementation...")
            return self.parse_pdf_with_alternative(pdf_path)

        # No options available
        logger.error("❌ No PDF parsing options available")
        return None

    def extract_toc_with_fallback(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """
        Extract TOC using multiple fallback methods when Nougat fails

        Args:
            pdf_path: Path to PDF file
            pages: Specific pages to extract (if known)

        Returns:
            TOC analysis dictionary or None
        """
        logger.info(f"🔍 Extracting TOC with fallback methods: {os.path.basename(pdf_path)}")

        # Method 1: Try Nougat if available
        if self.nougat_available:
            logger.info("   Trying Nougat method...")
            try:
                toc_data = self._extract_toc_with_nougat_command(pdf_path, pages)
                if toc_data and toc_data.get('total_entries', 0) > 0:
                    logger.info("✅ Nougat method successful")
                    return toc_data
            except Exception as e:
                logger.warning(f"   Nougat method failed: {e}")

        # Method 2: Try PyPDF2 text extraction
        logger.info("   Trying PyPDF2 text extraction...")
        try:
            toc_data = self._extract_toc_with_pypdf(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ PyPDF2 method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   PyPDF2 method failed: {e}")

        # Method 3: Try pdfplumber
        logger.info("   Trying pdfplumber extraction...")
        try:
            toc_data = self._extract_toc_with_pdfplumber(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ pdfplumber method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   pdfplumber method failed: {e}")

        # Method 4: Manual pattern extraction
        logger.info("   Trying manual pattern extraction...")
        try:
            toc_data = self._extract_toc_manual_patterns(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ Manual pattern method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   Manual pattern method failed: {e}")

        logger.warning("❌ All TOC extraction methods failed")
        return None

    def _extract_toc_with_nougat_command(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using Nougat command line (bypassing Python import issues)"""
        try:
            if pages is None:
                pages = [1, 2, 3]  # Default pages

            output_dir = "nougat_toc_temp"
            os.makedirs(output_dir, exist_ok=True)

            # Run nougat command
            cmd = ['nougat', pdf_path, '-o', output_dir, '--markdown']
            page_string = ','.join(map(str, pages))
            cmd.extend(['-p', page_string])

            # Use a longer timeout and capture any output
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check if output file was created (even if command had warnings)
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")

            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if self._looks_like_toc_content(content):
                    return self._analyze_text_for_toc(content, pages, "nougat_command")

        except Exception as e:
            logger.debug(f"Nougat command extraction failed: {e}")

        return None

    def _extract_toc_with_pypdf(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using PyPDF2 text extraction"""
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if pages is None:
                    pages = [1, 2, 3]  # Default to first 3 pages

                text_content = ""
                for page_num in pages:
                    if page_num <= len(pdf_reader.pages):
                        page = pdf_reader.pages[page_num - 1]  # 0-indexed
                        text_content += page.extract_text() + "\n"

                if self._looks_like_toc_content(text_content):
                    return self._analyze_text_for_toc(text_content, pages, "pypdf2")

        except ImportError:
            logger.warning("PyPDF2 not available")
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        return None

    def _extract_toc_with_pdfplumber(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using pdfplumber"""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                if pages is None:
                    pages = [1, 2, 3]  # Default to first 3 pages

                text_content = ""
                for page_num in pages:
                    if page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]  # 0-indexed
                        text_content += page.extract_text() + "\n"

                if self._looks_like_toc_content(text_content):
                    return self._analyze_text_for_toc(text_content, pages, "pdfplumber")

        except ImportError:
            logger.warning("pdfplumber not available")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        return None

    def _extract_toc_manual_patterns(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using manual pattern recognition on any available text"""
        try:
            # Try to get text using any available method
            text_content = self._get_text_any_method(pdf_path, pages)

            if text_content and self._looks_like_toc_content(text_content):
                return self._analyze_text_for_toc(text_content, pages or [1, 2, 3], "manual_patterns")

        except Exception as e:
            logger.warning(f"Manual pattern extraction failed: {e}")

        return None

    def _get_text_any_method(self, pdf_path: str, pages: List[int] = None) -> str:
        """Get text using any available method"""
        if pages is None:
            pages = [1, 2, 3]

        # Try multiple libraries
        for method_name, method in [
            ("PyPDF2", self._try_pypdf2_text),
            ("pdfplumber", self._try_pdfplumber_text),
            ("pymupdf", self._try_pymupdf_text)
        ]:
            try:
                text = method(pdf_path, pages)
                if text and len(text.strip()) > 50:
                    logger.info(f"   Got text using {method_name}")
                    return text
            except:
                continue

        return ""

    def _try_pypdf2_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with PyPDF2"""
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in pages:
                if page_num <= len(pdf_reader.pages):
                    text += pdf_reader.pages[page_num - 1].extract_text() + "\n"
            return text

    def _try_pdfplumber_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with pdfplumber"""
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num in pages:
                if page_num <= len(pdf.pages):
                    text += pdf.pages[page_num - 1].extract_text() + "\n"
            return text

    def _try_pymupdf_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with PyMuPDF"""
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in pages:
            if page_num <= len(doc):
                page = doc[page_num - 1]  # 0-indexed
                text += page.get_text() + "\n"
        doc.close()
        return text

    def _looks_like_toc_content(self, text: str) -> bool:
        """Check if text looks like Table of Contents"""
        if not text or len(text.strip()) < 50:
            return False

        text_lower = text.lower()

        # Strong indicators
        strong_indicators = ['table of contents', 'contents', 'index']
        has_strong = any(indicator in text_lower for indicator in strong_indicators)

        # Weak indicators
        weak_indicators = ['chapter', 'section', 'part', 'appendix']
        weak_count = sum(1 for indicator in weak_indicators if indicator in text_lower)

        # Structure indicators
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        has_structure = len(lines) >= 3
        has_numbers = bool(re.search(r'\d+', text))
        has_dots = '...' in text or '..' in text

        # Scoring
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

    def _analyze_text_for_toc(self, text: str, pages: List[int], method: str) -> Dict:
        """Analyze extracted text for TOC structure"""
        entries = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) > 200:
                continue

            # Pattern 1: Dotted entries (Title ... Page)
            dotted_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
            if dotted_match:
                title = dotted_match.group(1).strip()
                page = int(dotted_match.group(2))
                level = self._determine_toc_level_from_text(title, line)
                entries.append({
                    'title': title,
                    'page': page,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'dotted',
                    'raw_line': line
                })
                continue

            # Pattern 2: Numbered entries
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

            # Pattern 3: Keyword-based entries
            if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
                level = self._determine_toc_level_from_text(line, line)
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

        return {
            'source_pages': pages,
            'extraction_method': method,
            'total_entries': len(entries),
            'total_titles': len(titles),
            'total_subtitles': len(subtitles),
            'max_level': max([e.get('level', 1) for e in entries], default=1),
            'has_page_numbers': any(e.get('page') for e in entries),
            'entries': entries,
            'hierarchical_structure': sorted(entries, key=lambda x: x.get('line_number', 0)),
            'raw_content': text[:1000] + '...' if len(text) > 1000 else text,
            'formatted_toc': self._generate_formatted_toc_from_entries(entries)
        }

    def _determine_toc_level_from_text(self, title: str, full_line: str) -> int:
        """Determine TOC entry level from text analysis"""
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

    def _generate_formatted_toc_from_entries(self, entries: List[Dict]) -> str:
        """Generate formatted TOC string from entries"""
        formatted_lines = []

        for entry in entries:
            level = entry.get('level', 1)
            title = entry['title']
            page = entry.get('page')

            # Create indentation
            indent = "  " * (level - 1)

            # Format entry
            if page:
                line = f"{indent}{title} ... {page}"
            else:
                line = f"{indent}{title}"

            formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    def scan_content_pages_and_extract_toc(self, pdf_path: str, auto_detect: bool = True,
                                         specific_pages: List[int] = None) -> Optional[Dict]:
        """
        Main method to scan content pages and extract TOC information

        Args:
            pdf_path: Path to the PDF file
            auto_detect: Whether to automatically detect TOC pages
            specific_pages: Specific page numbers to scan (overrides auto_detect)

        Returns:
            Complete TOC analysis with formatting and structure information
        """
        logger.info(f"🔍 Starting content page scan for: {os.path.basename(pdf_path)}")

        try:
            if specific_pages:
                logger.info(f"📖 Scanning specific pages: {specific_pages}")
                toc_data = self.extract_toc_with_fallback(pdf_path, specific_pages)
            elif auto_detect:
                logger.info("🔍 Auto-detecting TOC pages...")
                # Try different page combinations
                page_combinations = [
                    [1, 2], [1, 2, 3], [2, 3], [1], [2], [3], [4, 5]
                ]

                best_result = None
                best_score = 0

                for pages in page_combinations:
                    toc_data = self.extract_toc_with_fallback(pdf_path, pages)
                    if toc_data:
                        score = toc_data.get('total_entries', 0)
                        if score > best_score:
                            best_score = score
                            best_result = toc_data

                toc_data = best_result
            else:
                logger.warning("❌ No pages specified and auto-detect disabled")
                return None

            if toc_data:
                # Add metadata about the extraction
                toc_data['extraction_metadata'] = {
                    'pdf_source': pdf_path,
                    'extraction_method': toc_data.get('extraction_method', 'fallback'),
                    'auto_detected': auto_detect and not specific_pages,
                    'extraction_timestamp': self._get_timestamp()
                }

                # Generate summary for logging
                summary = self._generate_toc_summary(toc_data)
                logger.info(f"✅ TOC extraction completed: {summary}")

                return toc_data
            else:
                logger.warning("❌ No TOC data extracted")
                return None

        except Exception as e:
            logger.error(f"❌ Error during content page scanning: {e}")
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _generate_toc_summary(self, toc_data: Dict) -> str:
        """Generate a summary string of TOC extraction results"""
        total_titles = toc_data.get('total_titles', 0)
        total_subtitles = toc_data.get('total_subtitles', 0)
        max_level = toc_data.get('max_level', 0)
        has_pages = toc_data.get('has_page_numbers', False)
        method = toc_data.get('extraction_method', 'unknown')

        summary_parts = [
            f"{total_titles} titles",
            f"{total_subtitles} subtitles",
            f"max depth {max_level}",
            f"method: {method}"
        ]

        if has_pages:
            summary_parts.append("with page numbers")

        return ", ".join(summary_parts)
