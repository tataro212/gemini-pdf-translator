"""
Hybrid Content Reconciler for Final Document Assembly

This module implements the comprehensive strategy for reconciling Nougat and PyMuPDF outputs
into a unified StructuredDocument that ensures TOC and visual elements are correctly placed
in the final translated document.

Key Features:
- Parallel processing of Nougat (text/structure) and PyMuPDF (visual assets)
- Intelligent correlation of image placeholders with actual visual elements
- Unified ContentBlock generation with proper ordering
- Visual content bypass for translation (images go directly to output)
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import structured document model
try:
    from structured_document_model import (
        Document as StructuredDocument, ContentBlock, ContentType,
        Heading, Paragraph, ImagePlaceholder, Table, CodeBlock, 
        ListItem, Caption, Equation, create_content_block_from_dict
    )
    STRUCTURED_MODEL_AVAILABLE = True
except ImportError:
    STRUCTURED_MODEL_AVAILABLE = False
    StructuredDocument = None

logger = logging.getLogger(__name__)

@dataclass
class VisualElement:
    """Represents a visual element extracted by PyMuPDF"""
    element_id: str
    element_type: str  # 'image', 'drawing', 'chart', 'diagram'
    source_path: str
    page_num: int
    bbox: Tuple[float, float, float, float]
    width: Optional[int] = None
    height: Optional[int] = None
    classification: Optional[str] = None  # 'photograph', 'schema', 'diagram'

@dataclass
class NougatBlock:
    """Represents a content block from Nougat output"""
    content_type: str  # 'heading', 'paragraph', 'table', 'image_placeholder'
    content: str
    page_num: int
    line_number: int
    level: Optional[int] = None  # For headings
    image_reference: Optional[str] = None  # For image placeholders

class HybridContentReconciler:
    """
    Reconciles Nougat and PyMuPDF outputs into unified StructuredDocument.
    
    This class implements the hybrid parsing strategy that treats Nougat and PyMuPDF
    as complementary tools, merging their outputs into a single, definitive document
    structure with all visual elements correctly positioned.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration for image correlation
        self.correlation_config = {
            'vertical_tolerance': 50,  # pixels
            'horizontal_tolerance': 100,  # pixels
            'confidence_threshold': 0.7
        }
        
        # Image bypass configuration - these images skip translation entirely
        self.image_bypass_config = {
            'bypass_all_images': True,  # USER REQUIREMENT: No images for translation
            'preserve_in_output': True,  # Keep images in final document
            'classification_whitelist': ['photograph', 'schema', 'diagram', 'chart']
        }
    
    def reconcile_content(self, nougat_output: str, visual_elements: List[VisualElement], 
                         pdf_path: str, output_dir: str) -> StructuredDocument:
        """
        Main reconciliation method that merges Nougat and PyMuPDF outputs.
        
        Args:
            nougat_output: Markdown content from Nougat
            visual_elements: List of visual elements from PyMuPDF
            pdf_path: Path to source PDF
            output_dir: Output directory for processed files
            
        Returns:
            Unified StructuredDocument with all content properly ordered
        """
        if not STRUCTURED_MODEL_AVAILABLE:
            raise Exception("Structured document model not available")
            
        self.logger.info("🔄 Starting hybrid content reconciliation...")
        self.logger.info(f"   • Nougat content length: {len(nougat_output)} characters")
        self.logger.info(f"   • Visual elements: {len(visual_elements)}")
        
        # Step 1: Parse Nougat output into structured blocks
        nougat_blocks = self._parse_nougat_output(nougat_output)
        self.logger.info(f"   • Parsed Nougat blocks: {len(nougat_blocks)}")
        
        # Step 2: Correlate visual elements with Nougat placeholders
        correlated_content = self._correlate_visual_elements(nougat_blocks, visual_elements)
        self.logger.info(f"   • Correlated content blocks: {len(correlated_content)}")
        
        # Step 3: Create unified ContentBlock objects
        content_blocks = self._create_unified_content_blocks(correlated_content, output_dir)
        self.logger.info(f"   • Generated content blocks: {len(content_blocks)}")
        
        # Step 4: Create StructuredDocument
        document = StructuredDocument(
            title=self._extract_document_title(nougat_blocks),
            content_blocks=content_blocks,
            source_filepath=pdf_path,
            total_pages=self._estimate_total_pages(visual_elements),
            metadata={
                'processing_method': 'hybrid_reconciliation',
                'nougat_blocks': len(nougat_blocks),
                'visual_elements': len(visual_elements),
                'image_bypass_enabled': self.image_bypass_config['bypass_all_images']
            }
        )
        
        self.logger.info(f"✅ Hybrid reconciliation completed: {document.get_statistics()}")
        return document
    
    def _parse_nougat_output(self, nougat_content: str) -> List[NougatBlock]:
        """Parse Nougat Markdown output into structured blocks"""
        blocks = []
        lines = nougat_content.split('\n')
        current_page = 1
        
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
                
            # Detect page breaks
            if re.match(r'\[MISSING_PAGE_.*?\]', line_stripped):
                current_page += 1
                continue
            
            # Detect headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                blocks.append(NougatBlock(
                    content_type='heading',
                    content=content,
                    page_num=current_page,
                    line_number=line_num,
                    level=level
                ))
                continue
            
            # Detect image placeholders
            image_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line_stripped)
            if image_match:
                alt_text = image_match.group(1)
                image_ref = image_match.group(2)
                blocks.append(NougatBlock(
                    content_type='image_placeholder',
                    content=alt_text,
                    page_num=current_page,
                    line_number=line_num,
                    image_reference=image_ref
                ))
                continue
            
            # Detect tables (simplified)
            if '|' in line_stripped and line_stripped.count('|') >= 2:
                blocks.append(NougatBlock(
                    content_type='table',
                    content=line_stripped,
                    page_num=current_page,
                    line_number=line_num
                ))
                continue
            
            # Regular paragraphs
            if line_stripped:
                blocks.append(NougatBlock(
                    content_type='paragraph',
                    content=line_stripped,
                    page_num=current_page,
                    line_number=line_num
                ))
        
        return blocks
    
    def _correlate_visual_elements(self, nougat_blocks: List[NougatBlock], 
                                 visual_elements: List[VisualElement]) -> List[Dict[str, Any]]:
        """Correlate visual elements with Nougat placeholders"""
        correlated_content = []
        visual_elements_by_page = {}
        
        # Group visual elements by page
        for element in visual_elements:
            page = element.page_num
            if page not in visual_elements_by_page:
                visual_elements_by_page[page] = []
            visual_elements_by_page[page].append(element)
        
        # Process each Nougat block
        for block in nougat_blocks:
            if block.content_type == 'image_placeholder':
                # Find matching visual element
                page_visuals = visual_elements_by_page.get(block.page_num, [])
                matched_element = self._find_best_visual_match(block, page_visuals)
                
                if matched_element:
                    correlated_content.append({
                        'type': 'image_with_visual',
                        'nougat_block': block,
                        'visual_element': matched_element,
                        'bypass_translation': self.image_bypass_config['bypass_all_images']
                    })
                else:
                    # No visual match found, keep as text placeholder
                    correlated_content.append({
                        'type': 'image_placeholder_only',
                        'nougat_block': block,
                        'bypass_translation': True
                    })
            else:
                # Regular content block
                correlated_content.append({
                    'type': 'text_content',
                    'nougat_block': block,
                    'bypass_translation': False
                })
        
        return correlated_content
    
    def _find_best_visual_match(self, nougat_block: NougatBlock, 
                               page_visuals: List[VisualElement]) -> Optional[VisualElement]:
        """Find the best visual element match for a Nougat image placeholder"""
        if not page_visuals:
            return None
        
        # For now, return the first visual element on the page
        # TODO: Implement spatial correlation based on line numbers and bounding boxes
        return page_visuals[0] if page_visuals else None
    
    def _create_unified_content_blocks(self, correlated_content: List[Dict[str, Any]], 
                                     output_dir: str) -> List[ContentBlock]:
        """Create unified ContentBlock objects from correlated content"""
        content_blocks = []
        block_counter = 0
        
        for item in correlated_content:
            block_counter += 1
            nougat_block = item['nougat_block']
            
            if item['type'] == 'image_with_visual':
                # Create ImagePlaceholder with actual visual data
                visual_element = item['visual_element']
                
                image_block = ImagePlaceholder(
                    block_type=ContentType.IMAGE_PLACEHOLDER,
                    original_text=nougat_block.content,
                    page_num=nougat_block.page_num,
                    bbox=visual_element.bbox,
                    block_num=block_counter,
                    image_path=visual_element.source_path,
                    width=visual_element.width,
                    height=visual_element.height,
                    translation_needed=False,  # USER REQUIREMENT: No image translation
                    caption=nougat_block.content
                )
                content_blocks.append(image_block)
                
            elif item['type'] == 'text_content':
                # Create appropriate text content block
                if nougat_block.content_type == 'heading':
                    heading_block = Heading(
                        block_type=ContentType.HEADING,
                        original_text=nougat_block.content,
                        page_num=nougat_block.page_num,
                        bbox=(0, 0, 100, 20),  # Placeholder bbox
                        block_num=block_counter,
                        content=nougat_block.content,
                        level=nougat_block.level or 1
                    )
                    content_blocks.append(heading_block)
                    
                elif nougat_block.content_type == 'paragraph':
                    paragraph_block = Paragraph(
                        block_type=ContentType.PARAGRAPH,
                        original_text=nougat_block.content,
                        page_num=nougat_block.page_num,
                        bbox=(0, 0, 100, 20),  # Placeholder bbox
                        block_num=block_counter,
                        content=nougat_block.content
                    )
                    content_blocks.append(paragraph_block)
        
        return content_blocks
    
    def _extract_document_title(self, nougat_blocks: List[NougatBlock]) -> str:
        """Extract document title from Nougat blocks"""
        for block in nougat_blocks:
            if block.content_type == 'heading' and block.level == 1:
                return block.content
        return "Untitled Document"
    
    def _estimate_total_pages(self, visual_elements: List[VisualElement]) -> int:
        """Estimate total pages from visual elements"""
        if not visual_elements:
            return 1
        return max(element.page_num for element in visual_elements)
