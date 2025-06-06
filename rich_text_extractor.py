"""
Rich Text Extractor for Ultimate PDF Translator

Extracts text with comprehensive formatting metadata including fonts, positions,
colors, and styling information for faithful document reconstruction.
"""

import fitz  # PyMuPDF
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from config_manager import config_manager

logger = logging.getLogger(__name__)

@dataclass
class TextBlock:
    """Rich text block with comprehensive formatting metadata"""
    text: str
    page_num: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_name: str
    font_size: float
    font_flags: int  # Bold, italic, etc.
    color: int  # RGB color as integer
    line_height: float
    char_spacing: float
    word_spacing: float
    text_matrix: Tuple[float, ...]  # Transformation matrix
    block_type: str  # 'heading', 'paragraph', 'list', 'caption', etc.
    confidence: float  # Confidence in block type classification
    
    def is_bold(self) -> bool:
        """Check if text is bold"""
        return bool(self.font_flags & 2**4)
    
    def is_italic(self) -> bool:
        """Check if text is italic"""
        return bool(self.font_flags & 2**1)
    
    def get_rgb_color(self) -> Tuple[int, int, int]:
        """Convert color integer to RGB tuple"""
        return (
            (self.color >> 16) & 255,  # Red
            (self.color >> 8) & 255,   # Green
            self.color & 255           # Blue
        )
    
    def get_css_color(self) -> str:
        """Get CSS color string"""
        r, g, b = self.get_rgb_color()
        return f"rgb({r}, {g}, {b})"
    
    def get_relative_position(self, page_width: float, page_height: float) -> Dict[str, float]:
        """Get position as percentages of page dimensions"""
        return {
            'left_percent': (self.bbox[0] / page_width) * 100,
            'top_percent': (self.bbox[1] / page_height) * 100,
            'width_percent': ((self.bbox[2] - self.bbox[0]) / page_width) * 100,
            'height_percent': ((self.bbox[3] - self.bbox[1]) / page_height) * 100
        }

class RichTextExtractor:
    """
    Advanced text extractor that captures comprehensive formatting information
    for faithful document reconstruction in HTML/CSS.
    """
    
    def __init__(self):
        self.settings = config_manager.pdf_processing_settings
        
        # Font size thresholds for content classification
        self.heading_size_threshold = config_manager.get_config_value(
            'RichTextExtraction', 'heading_size_threshold', 14.0, float
        )
        self.body_text_size_range = (
            config_manager.get_config_value('RichTextExtraction', 'min_body_size', 9.0, float),
            config_manager.get_config_value('RichTextExtraction', 'max_body_size', 13.0, float)
        )
        self.caption_size_threshold = config_manager.get_config_value(
            'RichTextExtraction', 'caption_size_threshold', 10.0, float
        )
        
        # Layout analysis settings
        self.column_detection_enabled = config_manager.get_config_value(
            'RichTextExtraction', 'enable_column_detection', True, bool
        )
        self.preserve_text_positioning = config_manager.get_config_value(
            'RichTextExtraction', 'preserve_text_positioning', True, bool
        )
        
        logger.info(f"🎨 RichTextExtractor initialized:")
        logger.info(f"   • Heading threshold: {self.heading_size_threshold}pt")
        logger.info(f"   • Body text range: {self.body_text_size_range[0]}-{self.body_text_size_range[1]}pt")
        logger.info(f"   • Column detection: {self.column_detection_enabled}")
    
    def extract_rich_text_from_pdf(self, pdf_path: str) -> List[TextBlock]:
        """
        Extract all text from PDF with comprehensive formatting metadata.
        """
        logger.info(f"📖 Extracting rich text from: {pdf_path}")
        
        text_blocks = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_blocks = self._extract_page_rich_text(page, page_num + 1)
                text_blocks.extend(page_blocks)
                
                logger.debug(f"Page {page_num + 1}: extracted {len(page_blocks)} text blocks")
            
            doc.close()
            
            # Post-process blocks for better classification
            text_blocks = self._classify_text_blocks(text_blocks)
            
            logger.info(f"✅ Rich text extraction completed: {len(text_blocks)} blocks")
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error extracting rich text: {e}")
            return []
    
    def _extract_page_rich_text(self, page: fitz.Page, page_num: int) -> List[TextBlock]:
        """Extract rich text from a single page"""
        blocks = []
        
        # Get text with detailed formatting information
        text_dict = page.get_text("dict")
        page_rect = page.rect
        
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue  # Skip image blocks
            
            block_bbox = block["bbox"]
            
            for line in block["lines"]:
                line_text = ""
                line_spans = []
                
                for span in line["spans"]:
                    span_text = span.get("text", "")
                    if span_text.strip():
                        line_text += span_text
                        line_spans.append(span)
                
                if not line_text.strip():
                    continue
                
                # Create text block from the most representative span
                if line_spans:
                    # Use the span with the most text or the first one
                    primary_span = max(line_spans, key=lambda s: len(s.get("text", "")))
                    
                    text_block = TextBlock(
                        text=line_text.strip(),
                        page_num=page_num,
                        bbox=tuple(line["bbox"]),
                        font_name=primary_span.get("font", ""),
                        font_size=primary_span.get("size", 12.0),
                        font_flags=primary_span.get("flags", 0),
                        color=primary_span.get("color", 0),
                        line_height=line["bbox"][3] - line["bbox"][1],
                        char_spacing=0.0,  # PyMuPDF doesn't provide this directly
                        word_spacing=0.0,  # PyMuPDF doesn't provide this directly
                        text_matrix=tuple(primary_span.get("transform", (1, 0, 0, 1, 0, 0))),
                        block_type="unknown",  # Will be classified later
                        confidence=0.0
                    )
                    
                    blocks.append(text_block)
        
        return blocks
    
    def _classify_text_blocks(self, text_blocks: List[TextBlock]) -> List[TextBlock]:
        """Classify text blocks by type (heading, paragraph, caption, etc.)"""
        if not text_blocks:
            return text_blocks
        
        # Analyze font sizes to determine document structure
        font_sizes = [block.font_size for block in text_blocks]
        avg_font_size = sum(font_sizes) / len(font_sizes)
        
        logger.debug(f"Font size analysis: avg={avg_font_size:.1f}, range={min(font_sizes):.1f}-{max(font_sizes):.1f}")
        
        for block in text_blocks:
            block.block_type, block.confidence = self._classify_single_block(block, avg_font_size)
        
        return text_blocks
    
    def _classify_single_block(self, block: TextBlock, avg_font_size: float) -> Tuple[str, float]:
        """Classify a single text block"""
        text = block.text.strip()
        font_size = block.font_size
        
        # Heading detection
        if font_size > self.heading_size_threshold or font_size > avg_font_size * 1.2:
            if block.is_bold() or len(text) < 100:
                if font_size > avg_font_size * 1.5:
                    return "h1", 0.9
                elif font_size > avg_font_size * 1.3:
                    return "h2", 0.8
                else:
                    return "h3", 0.7
        
        # Caption detection (small text near images or tables)
        if font_size < self.caption_size_threshold or font_size < avg_font_size * 0.8:
            if len(text) < 200:
                return "caption", 0.7
        
        # List item detection
        if self._is_list_item(text):
            return "list_item", 0.8
        
        # Table cell detection (based on position and size)
        if self._is_table_cell(block):
            return "table_cell", 0.6
        
        # Default to paragraph
        return "paragraph", 0.5
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text appears to be a list item"""
        import re
        
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
    
    def _is_table_cell(self, block: TextBlock) -> bool:
        """Check if block appears to be a table cell based on layout"""
        # Simple heuristic: short text with specific positioning
        text_length = len(block.text.strip())
        
        # Table cells are usually short and positioned in grid-like patterns
        if text_length < 50:
            # Check if the block is relatively small
            width = block.bbox[2] - block.bbox[0]
            height = block.bbox[3] - block.bbox[1]
            
            if width < 200 and height < 30:
                return True
        
        return False
    
    def get_document_structure_analysis(self, text_blocks: List[TextBlock]) -> Dict:
        """Analyze document structure for layout reconstruction"""
        if not text_blocks:
            return {}
        
        # Group blocks by page
        pages = {}
        for block in text_blocks:
            if block.page_num not in pages:
                pages[block.page_num] = []
            pages[block.page_num].append(block)
        
        # Analyze each page
        page_analyses = {}
        for page_num, page_blocks in pages.items():
            page_analyses[page_num] = self._analyze_page_layout(page_blocks)
        
        # Overall document analysis
        font_usage = {}
        for block in text_blocks:
            font_key = f"{block.font_name}_{block.font_size}"
            font_usage[font_key] = font_usage.get(font_key, 0) + 1
        
        # Find dominant fonts
        dominant_fonts = sorted(font_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_blocks': len(text_blocks),
            'total_pages': len(pages),
            'page_analyses': page_analyses,
            'dominant_fonts': dominant_fonts,
            'block_type_distribution': self._get_block_type_distribution(text_blocks),
            'color_usage': self._get_color_usage(text_blocks)
        }
    
    def _analyze_page_layout(self, page_blocks: List[TextBlock]) -> Dict:
        """Analyze layout of a single page"""
        if not page_blocks:
            return {}
        
        # Get page dimensions from first block
        # Note: This is approximate - we'd need the actual page object for exact dimensions
        min_x = min(block.bbox[0] for block in page_blocks)
        max_x = max(block.bbox[2] for block in page_blocks)
        min_y = min(block.bbox[1] for block in page_blocks)
        max_y = max(block.bbox[3] for block in page_blocks)
        
        page_width = max_x - min_x
        page_height = max_y - min_y
        
        # Detect columns by analyzing x-positions
        x_positions = [block.bbox[0] for block in page_blocks]
        columns = self._detect_columns(x_positions) if self.column_detection_enabled else 1
        
        return {
            'block_count': len(page_blocks),
            'estimated_page_width': page_width,
            'estimated_page_height': page_height,
            'detected_columns': columns,
            'text_density': len(page_blocks) / (page_width * page_height) if page_width * page_height > 0 else 0
        }
    
    def _detect_columns(self, x_positions: List[float]) -> int:
        """Simple column detection based on x-position clustering"""
        if len(x_positions) < 10:
            return 1
        
        # Use a simple clustering approach
        sorted_x = sorted(set(x_positions))
        
        # Look for gaps that might indicate column boundaries
        gaps = []
        for i in range(1, len(sorted_x)):
            gap = sorted_x[i] - sorted_x[i-1]
            gaps.append(gap)
        
        if not gaps:
            return 1
        
        # If there's a significant gap, we might have multiple columns
        avg_gap = sum(gaps) / len(gaps)
        large_gaps = [gap for gap in gaps if gap > avg_gap * 3]
        
        return min(len(large_gaps) + 1, 3)  # Cap at 3 columns for sanity
    
    def _get_block_type_distribution(self, text_blocks: List[TextBlock]) -> Dict[str, int]:
        """Get distribution of block types"""
        distribution = {}
        for block in text_blocks:
            block_type = block.block_type
            distribution[block_type] = distribution.get(block_type, 0) + 1
        return distribution
    
    def _get_color_usage(self, text_blocks: List[TextBlock]) -> Dict[str, int]:
        """Get distribution of text colors"""
        color_usage = {}
        for block in text_blocks:
            color_str = block.get_css_color()
            color_usage[color_str] = color_usage.get(color_str, 0) + 1
        return color_usage

# Global rich text extractor instance
rich_text_extractor = RichTextExtractor()
