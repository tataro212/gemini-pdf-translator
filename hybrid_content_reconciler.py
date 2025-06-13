# hybrid_content_reconciler.py

import logging
from typing import List, Dict, Any, Optional # Added Any, Optional for broader dict compatibility initially

# Attempt to import from structured_document_model, handle potential path issues if running standalone
try:
    from .structured_document_model import ContentBlock, ImagePlaceholder, Paragraph, Heading, ContentType
except ImportError:
    # Fallback for direct execution or if path issues occur in isolated test environments
    # This assumes structured_document_model.py is in the same directory or Python path
    from structured_document_model import ContentBlock, ImagePlaceholder, Paragraph, Heading, ContentType


logger = logging.getLogger(__name__)

class HybridContentReconciler:
    """
    Merges text-based analysis (e.g., Nougat) with visual layout analysis
    (e.g., YOLOv8, PyMuPDF) to create a single, correctly ordered document structure.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Configuration for spatial analysis, e.g., proximity thresholds
        default_config = {
            'vertical_tolerance': 50,       # Tolerance for considering elements on the same 'line'
            'horizontal_tolerance': 100,    # Tolerance for horizontal alignment/overlap
            'max_y_overlap_for_column': 0.7 # Max Y-overlap ratio to consider elements in same column band
        }
        self.config = default_config
        if config:
            self.config.update(config)
        logger.info(f"HybridContentReconciler initialized with config: {self.config}")

    def reconcile_streams(self, text_blocks: List[Dict[str, Any]], visual_elements: List[Dict[str, Any]]) -> List[ContentBlock]:
        """
        The core method. It takes two lists of detected elements, one for text and
        one for visuals, and outputs a single, sorted list of ContentBlock objects.

        Args:
            text_blocks: A list of text paragraphs/headings with their page numbers and coordinates.
                         Expected dict keys: 'type' (e.g., 'paragraph', 'heading'), 'text',
                                             'page_num', 'bbox' ([x0,y0,x1,y1]),
                                             'level' (for headings, optional).
            visual_elements: A list of detected images/tables with their page numbers and coordinates.
                             Expected dict keys: 'type' (e.g., 'image', 'table_image'), 'page_num',
                                                 'bbox' ([x0,y0,x1,y1]), 'image_path' (for images),
                                                 'ocr_text' (optional).

        Returns:
            A single list of ContentBlock objects, sorted in the correct reading order.
        """
        logger.info(f"Reconciling {len(text_blocks)} text blocks with {len(visual_elements)} visual elements.")

        # 1. Combine Inputs
        all_elements_combined: List[Dict[str, Any]] = []
        for tb in text_blocks:
            tb_copy = tb.copy()  # Work on a copy to avoid modifying original dicts
            tb_copy['source_stream'] = 'text'
            all_elements_combined.append(tb_copy)
            logger.debug(f"Added text block: {tb_copy.get('type', 'N/A')} on page {tb_copy.get('page_num', 'N/A')}")

        for ve in visual_elements:
            ve_copy = ve.copy() # Work on a copy
            ve_copy['source_stream'] = 'visual'
            all_elements_combined.append(ve_copy)
            logger.debug(f"Added visual element: {ve_copy.get('type', 'N/A')} on page {ve_copy.get('page_num', 'N/A')}")
        
        logger.debug(f"Combined {len(all_elements_combined)} elements from both streams.")

        # 2. Sort Combined Elements
        # Primary key: page_num, Secondary key: bbox[1] (y-coordinate of top).
        # Default for page_num is 0, default for bbox[1] is 0.
        all_elements_combined.sort(key=lambda el: (
            el.get('page_num', 0),
            el.get('bbox', [0, 0, 0, 0])[1] if isinstance(el.get('bbox'), (list, tuple)) and len(el.get('bbox')) > 1 else 0
        ))

        logger.info(f"Sorted {len(all_elements_combined)} combined elements.")
        if all_elements_combined:
            logger.debug("First few elements after sorting:")
            for i, el_sorted in enumerate(all_elements_combined[:3]):
                 logger.debug(f"  {i+1}. Page: {el_sorted.get('page_num', 'N/A')}, Type: {el_sorted.get('type', 'N/A')}, BBox: {el_sorted.get('bbox', 'N/A')}, Source: {el_sorted.get('source_stream', 'N/A')}")


        # 3. Convert to ContentBlocks
        final_structure: List[ContentBlock] = []
        for i, elem_data in enumerate(all_elements_combined):
            # Assign a sequential block_num. This might be adjusted later if a more semantic block_num is available.
            elem_data['block_num'] = i
            block = self._create_block_from_element(elem_data)
            if block:
                final_structure.append(block)
            # Warning for failed block creation is handled in _create_block_from_element

        logger.info(f"Reconciliation complete. Unified structure created with {len(final_structure)} blocks.")
        return final_structure

    def _create_block_from_element(self, element_data: Dict[str, Any]) -> Optional[ContentBlock]:
        """
        A helper factory function that converts a dictionary (representing a detected element)
        into the appropriate ContentBlock subclass.
        """
        elem_type = element_data.get('type', 'paragraph').lower() # Default to paragraph
        source_stream = element_data.get('source_stream')
        text = element_data.get('text', '')

        page_num = element_data.get('page_num')
        if page_num is None: # Check for None specifically, as 0 is a valid page number for some systems
            logger.warning(f"Element missing 'page_num', defaulting to 0. Element: {element_data}")
            page_num = 0

        bbox_data = element_data.get('bbox')
        if not (isinstance(bbox_data, (list, tuple)) and len(bbox_data) == 4 and all(isinstance(n, (int, float)) for n in bbox_data))):
            logger.error(f"Invalid or missing bbox for element: {element_data}. Got: {bbox_data}. Skipping block creation.")
            return None
        bbox = tuple(bbox_data) # Ensure it's a tuple

        block_num = element_data.get('block_num', 0) # Default block_num if not set prior
        
        logger.debug(f"Attempting to create ContentBlock for: type='{elem_type}', page={page_num}, bbox={bbox}, source='{source_stream}'")

        if source_stream == 'visual':
            logger.debug(f"Creating ImagePlaceholder for visual element (original type: '{elem_type}'). Path: {element_data.get('image_path', element_data.get('filepath', 'N/A'))}")
            return ImagePlaceholder(
                block_type=ContentType.IMAGE_PLACEHOLDER,
                original_text=element_data.get('ocr_text', ''),
                page_num=page_num,
                bbox=bbox,
                block_num=block_num,
                image_path=element_data.get('image_path', element_data.get('filepath', '')),
                width=element_data.get('width'),
                height=element_data.get('height'),
                ocr_text=element_data.get('ocr_text')
            )
        elif elem_type == 'heading':
            level = element_data.get('level', 1)
            logger.debug(f"Creating Heading block (L{level}) for text element. Text: '{text[:50]}...'")
            return Heading(
                block_type=ContentType.HEADING,
                original_text=text,
                page_num=page_num,
                bbox=bbox,
                block_num=block_num,
                level=level,
                content=text
            )
        elif elem_type == 'paragraph':
            logger.debug(f"Creating Paragraph block for text element. Text: '{text[:50]}...'")
            return Paragraph(
                block_type=ContentType.PARAGRAPH,
                original_text=text,
                page_num=page_num,
                bbox=bbox,
                block_num=block_num,
                content=text
            )
        # Add more text types from text_blocks if they exist (e.g., 'list_item', 'table_text')
        # elif elem_type == 'list_item': ...
        # elif elem_type == 'table': # If text_blocks can represent tables as structured text
        #     return Table(...)
        else:
            logger.warning(f"Unknown element type '{elem_type}' from source_stream '{source_stream}'. Treating as Paragraph. Element: {element_data}")
            return Paragraph(
                block_type=ContentType.PARAGRAPH,
                original_text=text if text else f"Unknown content type: {elem_type}",
                page_num=page_num,
                bbox=bbox,
                block_num=block_num,
                content=text if text else f"Unknown content type: {elem_type}"
            )

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    logging.basicConfig(level=logging.DEBUG)
    
    reconciler = HybridContentReconciler()

    # Mock data (replace with actual data from Nougat/PyMuPDF/YOLO)
    mock_text_blocks = [
        {'type': 'heading', 'text': 'Chapter 1', 'page_num': 1, 'bbox': [50, 50, 400, 70], 'level': 1},
        {'type': 'paragraph', 'text': 'This is the first paragraph.', 'page_num': 1, 'bbox': [50, 80, 550, 120]},
        {'type': 'paragraph', 'text': 'Another paragraph on page 1.', 'page_num': 1, 'bbox': [50, 500, 550, 550]}, # out of order y
    ]
    mock_visual_elements = [
        {'type': 'image', 'page_num': 1, 'bbox': [100, 150, 500, 450], 'image_path': 'path/to/image1.png', 'ocr_text': 'Image of a cat'},
        {'type': 'table_image', 'page_num': 2, 'bbox': [50, 50, 550, 200], 'image_path': 'path/to/table_img.png'},
    ]
    
    final_document_structure = reconciler.reconcile_streams(mock_text_blocks, mock_visual_elements)
    
    print("\n--- Final Document Structure ---")
    for block in final_document_structure:
        print(f"Page {block.page_num}, Type: {block.block_type.name}, BBox: {block.bbox}, Content/Path: {getattr(block, 'content', '') or getattr(block, 'image_path', 'N/A')}")
