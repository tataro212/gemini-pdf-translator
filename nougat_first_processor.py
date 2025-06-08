"""
Nougat-First PDF Processor

Implements the strategic nougat-first approach for maximum quality and cost efficiency:
- Nougat as the primary specialist tool for complex analysis
- AI models used surgically for high-value creative tasks only
- Perfect replication of source document structure and formatting
"""

import os
import logging
import json
import re
import fitz  # PyMuPDF
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

# Import structured document model
from document_model import (
    Document, Page, ContentBlock, Heading, Paragraph, Footnote, Table,
    ListItem, MathematicalFormula, ContentType
)

logger = logging.getLogger(__name__)

class VisualElementType(Enum):
    """Visual element types determined by nougat-first analysis"""
    PHOTOGRAPH = "photograph"
    PAINTING_OR_ART = "painting_or_art"
    DECORATIVE_ELEMENT = "decorative_element"
    DATA_TABLE = "data_table"
    MATHEMATICAL_FORMULA = "mathematical_formula"
    STRUCTURED_DIAGRAM = "structured_diagram"
    COMPLEX_CHART = "complex_chart"
    UNKNOWN = "unknown"

@dataclass
class RichTextBlock:
    """Rich text block with comprehensive metadata from PyMuPDF"""
    text: str
    page_num: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_name: str
    font_size: float
    font_weight: str  # normal, bold
    font_style: str   # normal, italic
    color: int
    semantic_role: str = "unknown"  # h1, h2, body_paragraph, etc.
    placeholder_id: str = ""
    
    def __post_init__(self):
        if not self.placeholder_id:
            text_hash = hashlib.md5(self.text.encode()).hexdigest()[:8]
            self.placeholder_id = f"%%TEXT_BLOCK_{self.page_num}_{text_hash}%%"

@dataclass
class VisualElement:
    """Visual element with nougat-first analysis results"""
    element_id: str
    element_type: VisualElementType
    source_path: str
    page_num: int
    bbox: Tuple[float, float, float, float]
    nougat_output: str = ""
    nougat_confidence: float = 0.0
    translated_content: str = ""
    reconstruction_data: Dict = None
    placeholder_id: str = ""
    
    def __post_init__(self):
        if not self.placeholder_id:
            self.placeholder_id = f"%%VISUAL_ELEMENT_{self.element_id}%%"
        if self.reconstruction_data is None:
            self.reconstruction_data = {}

class NougatFirstProcessor:
    """
    Strategic processor implementing the nougat-first methodology for
    maximum quality and cost efficiency in PDF translation.
    """
    
    def __init__(self):
        self.nougat_available = self._check_nougat_availability()
        self.processed_elements = {}
        self.placeholder_map = {}
        
        # Cost tracking
        self.cost_stats = {
            'nougat_calls': 0,
            'ai_calls': 0,
            'pymupdf_operations': 0,
            'total_cost_saved': 0.0
        }
        
        logger.info("🎯 NougatFirstProcessor initialized")
        logger.info(f"   • Nougat available: {self.nougat_available}")
        logger.info("   • Strategy: Quality and Fidelity First")
        logger.info("   • Principle: Nougat-First for complex analysis")
    
    def _check_nougat_availability(self) -> bool:
        """Check if nougat is available for processing"""
        try:
            # Try to import nougat components
            from nougat_integration import NougatIntegration
            nougat_integration = NougatIntegration()
            return nougat_integration.nougat_available
        except ImportError:
            logger.warning("⚠️ Nougat not available - falling back to alternative methods")
            return False
    
    def process_document_nougat_first(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Main processing pipeline implementing the nougat-first strategy.
        
        Part 1: Nougat-Driven Structure and ToC Analysis
        Part 2: Nougat-First Visual Element Pipeline  
        Part 3: High-Fidelity Document Assembly
        """
        logger.info(f"🚀 Starting nougat-first processing: {os.path.basename(pdf_path)}")
        
        results = {
            'text_blocks': [],
            'visual_elements': [],
            'toc_structure': {},
            'document_metadata': {},
            'cost_analysis': {}
        }
        
        try:
            # Part 1: Initial Data Extraction and Structure Analysis
            logger.info("📖 Part 1: Nougat-Driven Structure and ToC Analysis")
            
            # 1.1 Initial Data Extraction with PyMuPDF
            text_blocks, visual_elements = self._extract_initial_data_pymupdf(pdf_path, output_dir)
            self.cost_stats['pymupdf_operations'] += 1
            
            # 1.2 High-Fidelity ToC Replication
            toc_structure = self._extract_toc_nougat_first(pdf_path)
            
            # 1.3 Efficient Semantic Role Classification
            text_blocks = self._classify_semantic_roles_efficiently(text_blocks, toc_structure)
            
            # Part 2: Nougat-First Visual Element Pipeline
            logger.info("🖼️ Part 2: Nougat-First Visual Element Pipeline")
            visual_elements = self._process_visual_elements_nougat_first(visual_elements, output_dir)
            
            # Store results
            results['text_blocks'] = text_blocks
            results['visual_elements'] = visual_elements
            results['toc_structure'] = toc_structure
            results['cost_analysis'] = self.cost_stats
            
            logger.info("✅ Nougat-first processing completed successfully")
            logger.info(f"   • Text blocks: {len(text_blocks)}")
            logger.info(f"   • Visual elements: {len(visual_elements)}")
            logger.info(f"   • Nougat calls: {self.cost_stats['nougat_calls']}")
            logger.info(f"   • AI calls: {self.cost_stats['ai_calls']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Nougat-first processing failed: {e}")
            raise

    def process_document_structured(self, pdf_path: str, output_dir: str) -> Document:
        """
        NEW STRUCTURED APPROACH: Process document and return structured Document object.

        This method implements the structured document model, parsing nougat output
        into proper ContentBlock objects that preserve document structure.
        """
        logger.info(f"🏗️ Starting structured document processing: {os.path.basename(pdf_path)}")

        try:
            # Extract initial data using existing methods
            text_blocks, visual_elements = self._extract_initial_data_pymupdf(pdf_path, output_dir)
            toc_structure = self._extract_toc_nougat_first(pdf_path)
            text_blocks = self._classify_semantic_roles_efficiently(text_blocks, toc_structure)

            # Convert to structured document
            document = self._convert_to_structured_document(text_blocks, toc_structure, pdf_path)

            # Process visual elements and associate with document
            processed_visual_elements = self._process_visual_elements_nougat_first(visual_elements, output_dir)
            document.document_metadata['visual_elements'] = processed_visual_elements

            logger.info(f"✅ Structured document created:")
            logger.info(f"   • Pages: {len(document.pages)}")
            logger.info(f"   • Total blocks: {len(document.get_all_content_blocks())}")
            logger.info(f"   • Headings: {len(document.get_all_headings())}")
            logger.info(f"   • Footnotes: {len(document.get_all_footnotes())}")

            return document

        except Exception as e:
            logger.error(f"❌ Structured document processing failed: {e}")
            raise

    def _convert_to_structured_document(self, text_blocks: List[RichTextBlock],
                                      toc_structure: Dict, pdf_path: str) -> Document:
        """
        Convert RichTextBlocks to structured Document with proper ContentBlock types.

        This method implements the core parsing logic that classifies text into
        headings, paragraphs, footnotes, tables, etc.
        """
        # Create document with title from filename
        title = os.path.splitext(os.path.basename(pdf_path))[0]
        document = Document(title=title)

        # Group blocks by page
        pages_dict = {}
        for block in text_blocks:
            page_num = block.page_num
            if page_num not in pages_dict:
                pages_dict[page_num] = Page(page_number=page_num)

        # Process blocks and convert to structured content
        current_paragraph_blocks = []

        for block in text_blocks:
            page = pages_dict[block.page_num]

            # Convert RichTextBlock to appropriate ContentBlock
            content_block = self._parse_text_block_to_content_block(block, toc_structure)

            if content_block:
                # Handle paragraph grouping
                if isinstance(content_block, Paragraph):
                    current_paragraph_blocks.append(content_block)
                else:
                    # Flush accumulated paragraphs
                    if current_paragraph_blocks:
                        merged_paragraph = self._merge_paragraph_blocks(current_paragraph_blocks)
                        page.add_block(merged_paragraph)
                        current_paragraph_blocks = []

                    # Add the non-paragraph block
                    page.add_block(content_block)

        # Flush any remaining paragraphs
        if current_paragraph_blocks:
            last_page = pages_dict[current_paragraph_blocks[-1].page_num]
            merged_paragraph = self._merge_paragraph_blocks(current_paragraph_blocks)
            last_page.add_block(merged_paragraph)

        # Add pages to document in order
        for page_num in sorted(pages_dict.keys()):
            document.add_page(pages_dict[page_num])

        # Set document metadata
        document.document_metadata.update({
            'toc_structure': toc_structure,
            'processing_method': 'nougat_first_structured',
            'total_text_blocks': len(text_blocks)
        })

        return document

    def _parse_text_block_to_content_block(self, block: RichTextBlock,
                                         toc_structure: Dict) -> Optional[ContentBlock]:
        """
        Parse a RichTextBlock into the appropriate ContentBlock type.

        This method implements the core classification logic using semantic roles,
        font analysis, and content patterns to determine block types.
        """
        text = block.text.strip()
        if not text:
            return None

        semantic_role = block.semantic_role.lower()

        # Common fields for all content blocks
        common_fields = {
            'content': text,
            'page_num': block.page_num,
            'bbox': block.bbox,
            'font_info': {
                'font_name': block.font_name,
                'font_size': block.font_size,
                'font_weight': block.font_weight,
                'font_style': block.font_style,
                'color': block.color
            }
        }

        # Heading detection
        if semantic_role.startswith('h') and semantic_role[1:].isdigit():
            level = int(semantic_role[1:])
            return Heading(level=min(level, 6), **common_fields)

        # Footnote detection
        if self._is_footnote_text(text):
            reference_id = self._extract_footnote_reference_id(text)
            return Footnote(reference_id=reference_id, **common_fields)

        # Table detection
        if self._is_table_content(text):
            return Table(**common_fields)

        # List item detection
        if semantic_role == 'list_item' or self._is_list_item(text):
            list_level, is_ordered, item_number = self._parse_list_item(text)
            return ListItem(
                list_level=list_level,
                is_ordered=is_ordered,
                item_number=item_number,
                **common_fields
            )

        # Mathematical formula detection
        if self._is_mathematical_formula(text):
            latex_repr = self._extract_latex_representation(text)
            return MathematicalFormula(
                formula_type='block' if len(text) > 50 else 'inline',
                latex_representation=latex_repr,
                **common_fields
            )

        # Default to paragraph
        return Paragraph(**common_fields)

    def _merge_paragraph_blocks(self, paragraph_blocks: List[Paragraph]) -> Paragraph:
        """
        Merge consecutive paragraph blocks into a single paragraph.

        This addresses the paragraph break issue by properly combining
        text blocks that belong to the same logical paragraph.
        """
        if not paragraph_blocks:
            return None

        if len(paragraph_blocks) == 1:
            return paragraph_blocks[0]

        # Combine content with paragraph breaks
        combined_content = []
        for i, para in enumerate(paragraph_blocks):
            combined_content.append(para.content)
            # Add paragraph break marker except for the last paragraph
            if i < len(paragraph_blocks) - 1:
                combined_content.append('[PARAGRAPH_BREAK]')

        # Use properties from the first paragraph
        first_para = paragraph_blocks[0]
        merged_paragraph = Paragraph(
            content=' '.join(combined_content),
            page_num=first_para.page_num,
            bbox=first_para.bbox,
            font_info=first_para.font_info
        )

        return merged_paragraph

    def _is_footnote_text(self, text: str) -> bool:
        """Check if text appears to be a footnote"""
        # Look for footnote patterns at the beginning
        footnote_patterns = [
            r'^\s*\[\d+\]',  # [1]
            r'^\s*\(\d+\)',  # (1)
            r'^\s*\d+\.',    # 1.
            r'^\s*[¹²³⁴⁵⁶⁷⁸⁹⁰]+',  # Superscript numbers
            r'^\s*\*+',      # Asterisks
        ]

        for pattern in footnote_patterns:
            if re.match(pattern, text):
                return True

        # Check if text is at bottom of page and short
        return len(text) < 300 and any(word in text.lower() for word in ['note:', 'see', 'cf.', 'ibid'])

    def _extract_footnote_reference_id(self, text: str) -> str:
        """Extract footnote reference ID from text"""
        patterns = [
            r'^\s*\[(\d+)\]',  # [1]
            r'^\s*\((\d+)\)',  # (1)
            r'^\s*(\d+)\.',    # 1.
            r'^\s*([¹²³⁴⁵⁶⁷⁸⁹⁰]+)',  # Superscript numbers
            r'^\s*(\*+)',      # Asterisks
        ]

        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _is_table_content(self, text: str) -> bool:
        """Check if text appears to be table content"""
        # Look for table indicators
        table_indicators = [
            '|',  # Markdown table separator
            '\t',  # Tab-separated values
            '  +',  # Multiple spaces (column alignment)
        ]

        # Check for multiple table indicators
        indicator_count = sum(1 for indicator in table_indicators if indicator in text)

        # Also check for structured data patterns
        lines = text.split('\n')
        if len(lines) > 1:
            # Check if multiple lines have similar structure
            structured_lines = [line for line in lines if any(ind in line for ind in table_indicators)]
            return len(structured_lines) >= 2

        return indicator_count >= 2

    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item"""
        list_patterns = [
            r'^\s*[•\-\*]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-zA-Z][\.\)]\s+',  # Lettered lists
            r'^\s*[ivxlcdm]+[\.\)]\s+',  # Roman numerals
        ]

        for pattern in list_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        return False

    def _parse_list_item(self, text: str) -> Tuple[int, bool, Optional[int]]:
        """Parse list item to extract level, type, and number"""
        # Count leading whitespace for level
        leading_spaces = len(text) - len(text.lstrip())
        list_level = max(1, leading_spaces // 4 + 1)  # Assume 4 spaces per level

        # Check if ordered list
        ordered_patterns = [
            r'^\s*(\d+)[\.\)]\s+',  # Numbered
            r'^\s*([a-zA-Z])[\.\)]\s+',  # Lettered
            r'^\s*([ivxlcdm]+)[\.\)]\s+',  # Roman numerals
        ]

        for pattern in ordered_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                try:
                    item_number = int(match.group(1))
                    return list_level, True, item_number
                except ValueError:
                    return list_level, True, None

        # Default to unordered list
        return list_level, False, None

    def _is_mathematical_formula(self, text: str) -> bool:
        """Check if text contains mathematical formulas"""
        math_indicators = [
            r'\$.*\$',  # LaTeX math mode
            r'\\[a-zA-Z]+',  # LaTeX commands
            r'[∑∫∏∆∇]',  # Mathematical symbols
            r'[αβγδεζηθικλμνξοπρστυφχψω]',  # Greek letters
            r'[≤≥≠≈∞±]',  # Mathematical operators
        ]

        for pattern in math_indicators:
            if re.search(pattern, text):
                return True

        return False

    def _extract_latex_representation(self, text: str) -> str:
        """Extract LaTeX representation from mathematical text"""
        # Look for existing LaTeX delimiters
        latex_patterns = [
            r'\$\$(.*?)\$\$',  # Display math
            r'\$(.*?)\$',      # Inline math
        ]

        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return matches[0].strip()

        # If no delimiters, return the text if it looks like LaTeX
        if any(cmd in text for cmd in ['\\frac', '\\sum', '\\int', '\\alpha']):
            return text.strip()

        return ""
    
    def _extract_initial_data_pymupdf(self, pdf_path: str, output_dir: str) -> Tuple[List[RichTextBlock], List[VisualElement]]:
        """
        1.1 Initial Data Extraction: Fast pass with PyMuPDF to extract:
        - All basic, selectable text blocks with rich metadata
        - All visual elements with unique placeholders
        """
        logger.info("📄 Extracting initial data with PyMuPDF...")
        
        text_blocks = []
        visual_elements = []
        
        doc = fitz.open(pdf_path)
        
        # Create images directory
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract rich text blocks
            page_text_blocks = self._extract_rich_text_blocks_page(page, page_num + 1)
            text_blocks.extend(page_text_blocks)
            
            # Extract visual elements and replace with placeholders
            page_visual_elements = self._extract_visual_elements_page(page, page_num + 1, images_dir)
            visual_elements.extend(page_visual_elements)
        
        doc.close()
        
        logger.info(f"   ✅ Extracted {len(text_blocks)} text blocks and {len(visual_elements)} visual elements")
        return text_blocks, visual_elements
    
    def _extract_rich_text_blocks_page(self, page: fitz.Page, page_num: int) -> List[RichTextBlock]:
        """Extract rich text blocks with comprehensive metadata from a page"""
        text_blocks = []
        
        # Get text with detailed formatting
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue  # Skip image blocks
            
            for line in block["lines"]:
                line_text = ""
                primary_span = None
                
                for span in line["spans"]:
                    span_text = span.get("text", "").strip()
                    if span_text:
                        line_text += span_text + " "
                        if primary_span is None or len(span_text) > len(primary_span.get("text", "")):
                            primary_span = span
                
                line_text = line_text.strip()
                if not line_text or not primary_span:
                    continue
                
                # Extract rich formatting metadata
                font_flags = primary_span.get("flags", 0)
                font_weight = "bold" if (font_flags & 2**4) else "normal"
                font_style = "italic" if (font_flags & 2**1) else "normal"
                
                text_block = RichTextBlock(
                    text=line_text,
                    page_num=page_num,
                    bbox=tuple(line["bbox"]),
                    font_name=primary_span.get("font", ""),
                    font_size=primary_span.get("size", 12.0),
                    font_weight=font_weight,
                    font_style=font_style,
                    color=primary_span.get("color", 0)
                )
                
                text_blocks.append(text_block)
        
        return text_blocks
    
    def _extract_visual_elements_page(self, page: fitz.Page, page_num: int, images_dir: str) -> List[VisualElement]:
        """Extract visual elements and save them with unique identifiers"""
        visual_elements = []
        
        # Extract raster images
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    element_id = f"page_{page_num}_img_{img_index + 1}"
                    img_filename = f"{element_id}.png"
                    img_path = os.path.join(images_dir, img_filename)
                    
                    pix.save(img_path)
                    
                    # Get image rectangle (approximate)
                    img_rect = page.get_image_rects(xref)
                    bbox = img_rect[0] if img_rect else (0, 0, 100, 100)
                    
                    visual_element = VisualElement(
                        element_id=element_id,
                        element_type=VisualElementType.UNKNOWN,
                        source_path=img_path,
                        page_num=page_num,
                        bbox=bbox
                    )
                    
                    visual_elements.append(visual_element)
                
                pix = None
                
            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
        
        # Extract vector drawings (simplified)
        drawings = page.get_drawings()
        for draw_index, drawing in enumerate(drawings):
            try:
                element_id = f"page_{page_num}_drawing_{draw_index + 1}"
                
                # Get bounding box
                bbox = drawing.get("rect", (0, 0, 100, 100))
                
                visual_element = VisualElement(
                    element_id=element_id,
                    element_type=VisualElementType.UNKNOWN,
                    source_path="",  # Vector drawing, no file
                    page_num=page_num,
                    bbox=bbox
                )
                
                visual_elements.append(visual_element)
                
            except Exception as e:
                logger.warning(f"Failed to extract drawing {draw_index} from page {page_num}: {e}")
        
        return visual_elements
    
    def _extract_toc_nougat_first(self, pdf_path: str) -> Dict[str, Any]:
        """
        1.2 High-Fidelity ToC Replication using nougat-first strategy
        """
        logger.info("📑 Extracting Table of Contents with nougat-first approach...")
        
        toc_structure = {
            'method_used': 'none',
            'entries': [],
            'confidence': 0.0,
            'raw_data': {}
        }
        
        try:
            # Default Path: PyMuPDF built-in ToC
            doc = fitz.open(pdf_path)
            pymupdf_toc = doc.get_toc()
            doc.close()
            
            if pymupdf_toc and len(pymupdf_toc) > 2:  # Reasonable ToC found
                logger.info("   ✅ Using PyMuPDF built-in ToC (fast and free)")
                toc_structure['method_used'] = 'pymupdf_builtin'
                toc_structure['entries'] = self._format_pymupdf_toc(pymupdf_toc)
                toc_structure['confidence'] = 0.9
                toc_structure['raw_data'] = {'pymupdf_toc': pymupdf_toc}
                return toc_structure
            
            # Nougat as Advanced Path
            if self.nougat_available:
                logger.info("   🔄 PyMuPDF ToC insufficient, using nougat for advanced analysis...")
                nougat_toc = self._extract_toc_with_nougat(pdf_path)
                self.cost_stats['nougat_calls'] += 1
                
                if nougat_toc['confidence'] > 0.7:
                    toc_structure = nougat_toc
                    return toc_structure
            
            # AI Refinement (rare case)
            if toc_structure['confidence'] < 0.7:
                logger.info("   🤖 Using AI for ToC refinement (rare case)...")
                ai_refined_toc = self._refine_toc_with_ai(toc_structure)
                self.cost_stats['ai_calls'] += 1
                toc_structure = ai_refined_toc
            
        except Exception as e:
            logger.warning(f"ToC extraction failed: {e}")
        
        return toc_structure
    
    def _format_pymupdf_toc(self, pymupdf_toc: List) -> List[Dict]:
        """Format PyMuPDF ToC into structured entries"""
        formatted_entries = []
        
        for level, title, page_num in pymupdf_toc:
            entry = {
                'level': level,
                'title': title.strip(),
                'page_num': page_num,
                'confidence': 0.9
            }
            formatted_entries.append(entry)
        
        return formatted_entries
    
    def _extract_toc_with_nougat(self, pdf_path: str) -> Dict[str, Any]:
        """Extract ToC using nougat's advanced analysis"""
        if not self.nougat_available:
            return {'method_used': 'none', 'entries': [], 'confidence': 0.0}
        
        try:
            # Use nougat integration to analyze ToC pages
            from nougat_integration import NougatIntegration
            nougat_integration = NougatIntegration()
            
            # Analyze first few pages for ToC
            nougat_result = nougat_integration.analyze_toc_pages(pdf_path, max_pages=5)
            
            if nougat_result and nougat_result.get('toc_entries'):
                return {
                    'method_used': 'nougat_advanced',
                    'entries': nougat_result['toc_entries'],
                    'confidence': nougat_result.get('confidence', 0.8),
                    'raw_data': nougat_result
                }
        
        except Exception as e:
            logger.warning(f"Nougat ToC extraction failed: {e}")
        
        return {'method_used': 'nougat_failed', 'entries': [], 'confidence': 0.0}
    
    def _refine_toc_with_ai(self, toc_structure: Dict) -> Dict:
        """AI refinement for ambiguous ToC (rare case)"""
        # This would be implemented with a strategic AI call
        # For now, return the original structure
        logger.info("   🤖 AI ToC refinement not yet implemented")
        self.cost_stats['total_cost_saved'] += 0.05  # Estimated cost saved
        return toc_structure
    
    def _classify_semantic_roles_efficiently(self, text_blocks: List[RichTextBlock], 
                                           toc_structure: Dict) -> List[RichTextBlock]:
        """
        1.3 Efficient Semantic Role Classification using font analysis and nougat structure
        """
        logger.info("🏷️ Classifying semantic roles efficiently...")
        
        if not text_blocks:
            return text_blocks
        
        # Analyze font patterns
        font_analysis = self._analyze_font_patterns(text_blocks)
        
        # Apply semantic classification
        for block in text_blocks:
            block.semantic_role = self._determine_semantic_role(block, font_analysis, toc_structure)
        
        # Count classifications
        role_counts = {}
        for block in text_blocks:
            role = block.semantic_role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        logger.info(f"   ✅ Semantic role classification completed:")
        for role, count in role_counts.items():
            logger.info(f"      • {role}: {count}")
        
        return text_blocks
    
    def _analyze_font_patterns(self, text_blocks: List[RichTextBlock]) -> Dict[str, Any]:
        """Analyze font patterns to determine document structure"""
        font_sizes = [block.font_size for block in text_blocks]
        
        if not font_sizes:
            return {'body_size': 12.0, 'heading_thresholds': []}
        
        # Calculate statistics
        avg_size = sum(font_sizes) / len(font_sizes)
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Determine heading thresholds
        heading_thresholds = []
        for size in unique_sizes:
            if size > avg_size * 1.2:  # 20% larger than average
                heading_thresholds.append(size)
        
        return {
            'body_size': avg_size,
            'heading_thresholds': heading_thresholds,
            'unique_sizes': unique_sizes
        }
    
    def _determine_semantic_role(self, block: RichTextBlock, font_analysis: Dict, 
                                toc_structure: Dict) -> str:
        """Determine semantic role for a text block"""
        text = block.text.strip()
        font_size = block.font_size
        
        # Check against ToC entries
        toc_entries = toc_structure.get('entries', [])
        for entry in toc_entries:
            if text.lower() in entry.get('title', '').lower() or entry.get('title', '').lower() in text.lower():
                level = entry.get('level', 1)
                return f"h{min(level, 6)}"
        
        # Font-based classification
        heading_thresholds = font_analysis.get('heading_thresholds', [])
        body_size = font_analysis.get('body_size', 12.0)
        
        if font_size in heading_thresholds:
            # Determine heading level based on size
            threshold_index = heading_thresholds.index(font_size)
            return f"h{min(threshold_index + 1, 6)}"
        
        # Check for list items
        if re.match(r'^\s*[•\-\*]\s+', text) or re.match(r'^\s*\d+[\.\)]\s+', text):
            return "list_item"
        
        # Check for captions (small text)
        if font_size < body_size * 0.9 and len(text) < 200:
            return "caption"
        
        # Default to paragraph
        return "body_paragraph"

    def _process_visual_elements_nougat_first(self, visual_elements: List[VisualElement],
                                            output_dir: str) -> List[VisualElement]:
        """
        Part 2: Nougat-First Visual Element Pipeline
        Process each visual element with nougat first, then targeted AI only when needed
        """
        logger.info("🔍 Processing visual elements with nougat-first strategy...")

        processed_elements = []

        for element in visual_elements:
            try:
                # 2.1 Initial Analysis with nougat
                element = self._analyze_element_with_nougat(element)

                # 2.2 Targeted Processing and Reconstruction
                element = self._process_element_based_on_nougat_analysis(element, output_dir)

                processed_elements.append(element)

            except Exception as e:
                logger.warning(f"Failed to process visual element {element.element_id}: {e}")
                processed_elements.append(element)  # Keep original

        logger.info(f"   ✅ Processed {len(processed_elements)} visual elements")

        # Show processing statistics
        type_counts = {}
        for element in processed_elements:
            element_type = element.element_type.value
            type_counts[element_type] = type_counts.get(element_type, 0) + 1

        logger.info("   📊 Element type distribution:")
        for element_type, count in type_counts.items():
            logger.info(f"      • {element_type}: {count}")

        return processed_elements

    def _analyze_element_with_nougat(self, element: VisualElement) -> VisualElement:
        """
        2.1 Initial Analysis with nougat
        Analyze visual element with nougat to get structured output for classification
        """
        if not self.nougat_available or not element.source_path or not os.path.exists(element.source_path):
            return element

        try:
            from nougat_integration import NougatIntegration
            nougat_integration = NougatIntegration()

            # Analyze with nougat
            nougat_result = nougat_integration.analyze_visual_element(element.source_path)
            self.cost_stats['nougat_calls'] += 1

            if nougat_result:
                element.nougat_output = nougat_result.get('text', '')
                element.nougat_confidence = nougat_result.get('confidence', 0.0)

                # Classify based on nougat output
                element.element_type = self._classify_from_nougat_output(element.nougat_output)

                logger.debug(f"Nougat analysis for {element.element_id}: {element.element_type.value}")

        except Exception as e:
            logger.warning(f"Nougat analysis failed for {element.element_id}: {e}")

        return element

    def _classify_from_nougat_output(self, nougat_output: str) -> VisualElementType:
        """
        Classify visual element based on nougat's output analysis
        """
        if not nougat_output or len(nougat_output.strip()) < 10:
            # Very little or no coherent text
            return VisualElementType.PHOTOGRAPH  # Likely photo, art, or decorative

        # Check for structured content patterns
        if self._contains_table_structure(nougat_output):
            return VisualElementType.DATA_TABLE

        if self._contains_mathematical_content(nougat_output):
            return VisualElementType.MATHEMATICAL_FORMULA

        if self._contains_diagram_structure(nougat_output):
            return VisualElementType.STRUCTURED_DIAGRAM

        if self._contains_chart_indicators(nougat_output):
            return VisualElementType.COMPLEX_CHART

        # If substantial text but no clear structure
        if len(nougat_output.strip()) > 50:
            return VisualElementType.STRUCTURED_DIAGRAM

        return VisualElementType.UNKNOWN

    def _contains_table_structure(self, text: str) -> bool:
        """Check if nougat output contains table structure"""
        # Look for markdown table patterns
        table_patterns = [
            r'\|.*\|.*\|',  # Markdown table rows
            r'\+[-=]+\+',   # ASCII table borders
            r'\\begin{tabular}',  # LaTeX tables
            r'\\begin{table}',
        ]

        for pattern in table_patterns:
            if re.search(pattern, text):
                return True

        # Check for multiple rows with similar structure
        lines = text.split('\n')
        structured_lines = [line for line in lines if '|' in line or '\t' in line]
        return len(structured_lines) >= 3

    def _contains_mathematical_content(self, text: str) -> bool:
        """Check if nougat output contains mathematical formulas"""
        math_patterns = [
            r'\$.*\$',  # LaTeX math mode
            r'\\begin{equation}',
            r'\\begin{align}',
            r'\\frac{',
            r'\\sum',
            r'\\int',
            r'\\alpha|\\beta|\\gamma',  # Greek letters
            r'\\mathbf|\\mathrm',
        ]

        for pattern in math_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _contains_diagram_structure(self, text: str) -> bool:
        """Check if nougat output indicates a structured diagram"""
        diagram_indicators = [
            'flow', 'diagram', 'chart', 'process', 'step',
            'arrow', 'box', 'node', 'connection', 'link',
            'input', 'output', 'decision', 'start', 'end'
        ]

        text_lower = text.lower()
        indicator_count = sum(1 for indicator in diagram_indicators if indicator in text_lower)

        return indicator_count >= 2

    def _contains_chart_indicators(self, text: str) -> bool:
        """Check if nougat output indicates a chart or graph"""
        chart_indicators = [
            'axis', 'x-axis', 'y-axis', 'legend', 'data',
            'graph', 'plot', 'chart', 'bar', 'line',
            'pie', 'scatter', 'histogram', 'trend'
        ]

        text_lower = text.lower()
        indicator_count = sum(1 for indicator in chart_indicators if indicator in text_lower)

        return indicator_count >= 2

    def _process_element_based_on_nougat_analysis(self, element: VisualElement,
                                                 output_dir: str) -> VisualElement:
        """
        2.2 Targeted Processing and Reconstruction based on nougat analysis
        """
        element_type = element.element_type

        if element_type in [VisualElementType.PHOTOGRAPH, VisualElementType.PAINTING_OR_ART,
                           VisualElementType.DECORATIVE_ELEMENT]:
            # Preserve as-is, no AI calls needed
            element.reconstruction_data = {
                'method': 'preserve_original',
                'html': f'<img src="{os.path.basename(element.source_path)}" alt="Visual element" />'
            }
            logger.debug(f"Preserving {element.element_id} as-is")

        elif element_type == VisualElementType.DATA_TABLE:
            # Process table with nougat output
            element = self._process_data_table(element)

        elif element_type == VisualElementType.MATHEMATICAL_FORMULA:
            # Process mathematical content
            element = self._process_mathematical_formula(element)

        elif element_type in [VisualElementType.STRUCTURED_DIAGRAM, VisualElementType.COMPLEX_CHART]:
            # High-value AI step for reconstruction
            element = self._process_complex_visual_with_ai(element, output_dir)

        else:
            # Unknown or unprocessed
            element.reconstruction_data = {
                'method': 'preserve_original',
                'html': f'<img src="{os.path.basename(element.source_path)}" alt="Visual element" />'
            }

        return element

    def _process_data_table(self, element: VisualElement) -> VisualElement:
        """Process data table using nougat's extracted structure"""
        logger.debug(f"Processing data table: {element.element_id}")

        try:
            # Parse table structure from nougat output
            table_html = self._convert_nougat_table_to_html(element.nougat_output)

            element.reconstruction_data = {
                'method': 'html_table',
                'html': table_html,
                'source': 'nougat_extraction'
            }

        except Exception as e:
            logger.warning(f"Table processing failed for {element.element_id}: {e}")
            element.reconstruction_data = {
                'method': 'preserve_original',
                'html': f'<img src="{os.path.basename(element.source_path)}" alt="Table" />'
            }

        return element

    def _convert_nougat_table_to_html(self, nougat_output: str) -> str:
        """Convert nougat table output to clean HTML table"""
        # Simple markdown table to HTML conversion
        lines = nougat_output.strip().split('\n')
        table_lines = [line for line in lines if '|' in line]

        if len(table_lines) < 2:
            return f'<div class="table-container">{nougat_output}</div>'

        html_rows = []
        for i, line in enumerate(table_lines):
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]

            if i == 0:
                # Header row
                cell_tags = ['th'] * len(cells)
            else:
                # Data row
                cell_tags = ['td'] * len(cells)

            row_html = '<tr>'
            for cell, tag in zip(cells, cell_tags):
                row_html += f'<{tag}>{cell}</{tag}>'
            row_html += '</tr>'

            html_rows.append(row_html)

        table_html = f'''
        <table class="extracted-table">
            <thead>{html_rows[0]}</thead>
            <tbody>{"".join(html_rows[1:])}</tbody>
        </table>
        '''

        return table_html

    def _process_mathematical_formula(self, element: VisualElement) -> VisualElement:
        """Process mathematical formula using nougat's LaTeX output"""
        logger.debug(f"Processing mathematical formula: {element.element_id}")

        try:
            # Extract LaTeX from nougat output
            latex_content = self._extract_latex_from_nougat(element.nougat_output)

            if latex_content:
                # Create MathJax-compatible HTML
                mathjax_html = f'''
                <div class="math-formula">
                    <script type="math/tex; mode=display">
                    {latex_content}
                    </script>
                </div>
                '''

                element.reconstruction_data = {
                    'method': 'mathjax_latex',
                    'html': mathjax_html,
                    'latex': latex_content
                }
            else:
                # Fallback to original image
                element.reconstruction_data = {
                    'method': 'preserve_original',
                    'html': f'<img src="{os.path.basename(element.source_path)}" alt="Mathematical formula" />'
                }

        except Exception as e:
            logger.warning(f"Mathematical formula processing failed for {element.element_id}: {e}")
            element.reconstruction_data = {
                'method': 'preserve_original',
                'html': f'<img src="{os.path.basename(element.source_path)}" alt="Mathematical formula" />'
            }

        return element

    def _extract_latex_from_nougat(self, nougat_output: str) -> str:
        """Extract LaTeX content from nougat output"""
        # Look for LaTeX patterns
        latex_patterns = [
            r'\$\$(.*?)\$\$',  # Display math
            r'\$(.*?)\$',      # Inline math
            r'\\begin{equation}(.*?)\\end{equation}',
            r'\\begin{align}(.*?)\\end{align}',
        ]

        for pattern in latex_patterns:
            matches = re.findall(pattern, nougat_output, re.DOTALL)
            if matches:
                return matches[0].strip()

        # If no specific LaTeX delimiters, return the whole output if it looks like LaTeX
        if any(cmd in nougat_output for cmd in ['\\frac', '\\sum', '\\int', '\\alpha', '\\beta']):
            return nougat_output.strip()

        return ""

    def _process_complex_visual_with_ai(self, element: VisualElement, output_dir: str) -> VisualElement:
        """
        High-value AI step for complex diagrams and charts
        This is the strategic, surgical use of expensive AI models
        """
        logger.debug(f"Processing complex visual with AI: {element.element_id}")

        try:
            # This is where we make our strategic, high-value AI call
            # First translate the nougat-extracted text
            translated_text = self._translate_nougat_text(element.nougat_output)
            element.translated_content = translated_text

            # Then use AI for intelligent reconstruction
            reconstruction_result = self._ai_reconstruct_visual_element(element, translated_text)
            self.cost_stats['ai_calls'] += 1

            element.reconstruction_data = reconstruction_result

        except Exception as e:
            logger.warning(f"AI processing failed for {element.element_id}: {e}")
            element.reconstruction_data = {
                'method': 'preserve_original',
                'html': f'<img src="{os.path.basename(element.source_path)}" alt="Complex visual element" />'
            }

        return element

    def _translate_nougat_text(self, nougat_text: str) -> str:
        """Translate nougat-extracted text (placeholder implementation)"""
        # This would integrate with the translation service
        # For now, return the original text
        return nougat_text

    def _ai_reconstruct_visual_element(self, element: VisualElement, translated_text: str) -> Dict:
        """
        Strategic AI call for visual element reconstruction
        This is the high-value creative task that only AI can perform
        """
        # This would implement the strategic AI prompt for reconstruction
        # For now, return a placeholder structure

        if element.element_type == VisualElementType.COMPLEX_CHART:
            return {
                'method': 'mermaid_chart',
                'html': f'<div class="mermaid-chart" data-chart-type="complex">{translated_text}</div>',
                'mermaid_code': f'graph TD\n    A[{translated_text[:50]}...]',
                'note': 'AI reconstruction would generate Mermaid.js code here'
            }
        else:
            return {
                'method': 'structured_diagram',
                'html': f'<div class="structured-diagram">{translated_text}</div>',
                'note': 'AI reconstruction would generate diagram code here'
            }

# Global nougat-first processor instance
nougat_first_processor = NougatFirstProcessor()
