"""
Visual Element Processor for Ultimate PDF Translator

Unified pipeline for processing all visual content including images, diagrams,
charts, tables, and mathematical formulas with AI-powered classification
and intelligent reconstruction.
"""

import os
import logging
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from config_manager import config_manager
from async_translation_service import preemptive_image_filter

logger = logging.getLogger(__name__)

class VisualElementType(Enum):
    """Types of visual elements that can be processed"""
    PHOTOGRAPH = "photograph"
    SCREENSHOT = "screenshot"
    DIAGRAM = "diagram"
    CHART = "chart"
    TABLE = "table"
    MATHEMATICAL_FORMULA = "mathematical_formula"
    DECORATIVE = "decorative"
    UNKNOWN = "unknown"

@dataclass
class VisualElement:
    """Represents a visual element with comprehensive metadata"""
    element_id: str
    element_type: VisualElementType
    source_path: str
    page_num: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    confidence: float
    extracted_text: str = ""
    translated_text: str = ""
    reconstruction_data: Dict = None
    placeholder_id: str = ""
    processing_notes: List[str] = None
    
    def __post_init__(self):
        if not self.placeholder_id:
            self.placeholder_id = f"%%VISUAL_{self.element_id}%%"
        if self.processing_notes is None:
            self.processing_notes = []
        if self.reconstruction_data is None:
            self.reconstruction_data = {}

class VisualElementProcessor:
    """
    Unified processor for all visual content with AI-powered classification,
    text extraction, translation, and intelligent reconstruction.
    """
    
    def __init__(self):
        self.settings = config_manager.get_config_section('VisualProcessing', {
            'enable_ai_classification': True,
            'enable_text_extraction': True,
            'enable_reconstruction': True,
            'min_confidence_threshold': 0.7,
            'use_placeholder_workflow': True
        })
        
        # Processing settings
        self.enable_ai_classification = self.settings.get('enable_ai_classification', True)
        self.enable_text_extraction = self.settings.get('enable_text_extraction', True)
        self.enable_reconstruction = self.settings.get('enable_reconstruction', True)
        self.min_confidence_threshold = self.settings.get('min_confidence_threshold', 0.7)
        self.use_placeholder_workflow = self.settings.get('use_placeholder_workflow', True)
        
        # Initialize components
        self.image_filter = preemptive_image_filter
        self.processed_elements = {}
        self.placeholder_map = {}
        
        logger.info(f"🎨 VisualElementProcessor initialized:")
        logger.info(f"   • AI classification: {self.enable_ai_classification}")
        logger.info(f"   • Text extraction: {self.enable_text_extraction}")
        logger.info(f"   • Reconstruction: {self.enable_reconstruction}")
        logger.info(f"   • Placeholder workflow: {self.use_placeholder_workflow}")
    
    def process_visual_elements(self, image_items: List[Dict], output_dir: str) -> Tuple[List[VisualElement], Dict[str, str]]:
        """
        Main processing pipeline for visual elements.
        Returns (processed_elements, placeholder_map)
        """
        logger.info(f"🔄 Processing {len(image_items)} visual elements...")
        
        # Step 1: Pre-filter images
        filtered_items = self._prefilter_images(image_items)
        
        # Step 2: Classify visual elements
        classified_elements = self._classify_visual_elements(filtered_items)
        
        # Step 3: Extract text from relevant elements
        if self.enable_text_extraction:
            classified_elements = self._extract_text_from_elements(classified_elements)
        
        # Step 4: Generate placeholders for workflow
        placeholder_map = {}
        if self.use_placeholder_workflow:
            placeholder_map = self._generate_placeholders(classified_elements)
        
        # Step 5: Store processing results
        self.processed_elements = {elem.element_id: elem for elem in classified_elements}
        self.placeholder_map = placeholder_map
        
        # Step 6: Save processing metadata
        self._save_processing_metadata(classified_elements, output_dir)
        
        logger.info(f"✅ Visual element processing completed:")
        logger.info(f"   • Processed: {len(classified_elements)} elements")
        logger.info(f"   • Placeholders: {len(placeholder_map)}")
        
        return classified_elements, placeholder_map
    
    def _prefilter_images(self, image_items: List[Dict]) -> List[Dict]:
        """Apply preemptive filtering to remove obviously decorative images"""
        if not hasattr(self.image_filter, 'filter_image_list'):
            return image_items
        
        image_paths = [item.get('filepath', '') for item in image_items if item.get('filepath')]
        analyze_paths, skip_paths = self.image_filter.filter_image_list(image_paths)
        
        # Filter items based on analysis results
        filtered_items = []
        for item in image_items:
            filepath = item.get('filepath', '')
            if filepath in analyze_paths or not filepath:
                filtered_items.append(item)
            else:
                logger.debug(f"Prefiltered: {filepath}")
        
        logger.info(f"📊 Prefiltering results: {len(filtered_items)}/{len(image_items)} images retained")
        return filtered_items
    
    def _classify_visual_elements(self, image_items: List[Dict]) -> List[VisualElement]:
        """Classify visual elements using AI-powered analysis"""
        elements = []
        
        for i, item in enumerate(image_items):
            element_id = f"elem_{i:04d}"
            
            # Basic element creation
            element = VisualElement(
                element_id=element_id,
                element_type=VisualElementType.UNKNOWN,
                source_path=item.get('filepath', ''),
                page_num=item.get('page_num', 1),
                bbox=item.get('bbox', (0, 0, 100, 100)),
                confidence=0.5
            )
            
            # Classify using filename patterns first (fast)
            element.element_type, element.confidence = self._classify_by_filename(item.get('filename', ''))
            
            # AI-powered classification if enabled and confidence is low
            if self.enable_ai_classification and element.confidence < self.min_confidence_threshold:
                ai_type, ai_confidence = self._classify_with_ai(element.source_path)
                if ai_confidence > element.confidence:
                    element.element_type = ai_type
                    element.confidence = ai_confidence
                    element.processing_notes.append("AI classification applied")
            
            elements.append(element)
            logger.debug(f"Classified {element.element_id}: {element.element_type.value} (confidence: {element.confidence:.2f})")
        
        return elements
    
    def _classify_by_filename(self, filename: str) -> Tuple[VisualElementType, float]:
        """Quick classification based on filename patterns"""
        filename_lower = filename.lower()
        
        # High confidence classifications
        if '_img_' in filename_lower:
            return VisualElementType.PHOTOGRAPH, 0.9
        elif '_table_' in filename_lower:
            return VisualElementType.TABLE, 0.8
        elif '_equation_' in filename_lower:
            return VisualElementType.MATHEMATICAL_FORMULA, 0.8
        elif '_visual_' in filename_lower:
            return VisualElementType.DIAGRAM, 0.7
        
        # Pattern-based classification
        if any(word in filename_lower for word in ['chart', 'graph', 'plot']):
            return VisualElementType.CHART, 0.7
        elif any(word in filename_lower for word in ['diagram', 'schema', 'flow']):
            return VisualElementType.DIAGRAM, 0.7
        elif any(word in filename_lower for word in ['photo', 'image', 'picture']):
            return VisualElementType.PHOTOGRAPH, 0.6
        elif any(word in filename_lower for word in ['screen', 'capture', 'shot']):
            return VisualElementType.SCREENSHOT, 0.6
        
        return VisualElementType.UNKNOWN, 0.3
    
    def _classify_with_ai(self, image_path: str) -> Tuple[VisualElementType, float]:
        """AI-powered visual element classification"""
        try:
            # This would integrate with Gemini Vision API
            # For now, return a placeholder implementation
            logger.debug(f"AI classification requested for: {image_path}")
            
            # TODO: Implement actual AI classification
            # This would send the image to Gemini Vision with a classification prompt
            
            return VisualElementType.UNKNOWN, 0.5
            
        except Exception as e:
            logger.warning(f"AI classification failed for {image_path}: {e}")
            return VisualElementType.UNKNOWN, 0.3
    
    def _extract_text_from_elements(self, elements: List[VisualElement]) -> List[VisualElement]:
        """Extract text from visual elements that likely contain text"""
        text_bearing_types = {
            VisualElementType.TABLE,
            VisualElementType.DIAGRAM,
            VisualElementType.CHART,
            VisualElementType.SCREENSHOT,
            VisualElementType.MATHEMATICAL_FORMULA
        }
        
        for element in elements:
            if element.element_type in text_bearing_types:
                extracted_text = self._extract_text_from_image(element.source_path)
                if extracted_text:
                    element.extracted_text = extracted_text
                    element.processing_notes.append("Text extracted")
                    logger.debug(f"Extracted text from {element.element_id}: {len(extracted_text)} chars")
        
        return elements
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR"""
        try:
            # Try using nougat first if available
            if hasattr(self, '_extract_with_nougat'):
                result = self._extract_with_nougat(image_path)
                if result:
                    return result
            
            # Fallback to pytesseract
            try:
                import pytesseract
                from PIL import Image
                
                with Image.open(image_path) as img:
                    text = pytesseract.image_to_string(img)
                    return text.strip()
                    
            except ImportError:
                logger.warning("pytesseract not available for text extraction")
                return ""
                
        except Exception as e:
            logger.warning(f"Text extraction failed for {image_path}: {e}")
            return ""
    
    def _generate_placeholders(self, elements: List[VisualElement]) -> Dict[str, str]:
        """Generate placeholder map for workflow integration"""
        placeholder_map = {}
        
        for element in elements:
            placeholder_map[element.placeholder_id] = element.element_id
            logger.debug(f"Generated placeholder: {element.placeholder_id} -> {element.element_id}")
        
        return placeholder_map
    
    def translate_visual_text(self, elements: List[VisualElement], target_language: str) -> List[VisualElement]:
        """Translate extracted text from visual elements"""
        from async_translation_service import async_translation_service, TranslationTask
        import asyncio
        
        # Create translation tasks for elements with extracted text
        tasks = []
        element_map = {}
        
        for element in elements:
            if element.extracted_text.strip():
                task = TranslationTask(
                    text=element.extracted_text,
                    target_language=target_language,
                    item_type=f"visual_{element.element_type.value}",
                    priority=2  # Medium priority for visual text
                )
                tasks.append(task)
                element_map[task.task_id] = element
        
        if not tasks:
            logger.info("No visual text to translate")
            return elements
        
        logger.info(f"🌐 Translating text from {len(tasks)} visual elements...")
        
        # Execute translations
        try:
            translated_texts = asyncio.run(async_translation_service.translate_batch_concurrent(tasks))
            
            # Update elements with translated text
            for task, translated_text in zip(tasks, translated_texts):
                element = element_map[task.task_id]
                element.translated_text = translated_text
                element.processing_notes.append("Text translated")
                logger.debug(f"Translated text for {element.element_id}")
            
        except Exception as e:
            logger.error(f"Visual text translation failed: {e}")
        
        return elements
    
    def reconstruct_visual_elements(self, elements: List[VisualElement], output_dir: str) -> List[VisualElement]:
        """Intelligently reconstruct visual elements for final document"""
        if not self.enable_reconstruction:
            return elements
        
        logger.info(f"🔧 Reconstructing {len(elements)} visual elements...")
        
        for element in elements:
            reconstruction_method = self._get_reconstruction_method(element)
            
            if reconstruction_method == "recreate_programmatically":
                self._recreate_element_programmatically(element, output_dir)
            elif reconstruction_method == "overlay_translation":
                self._overlay_translation_on_image(element, output_dir)
            elif reconstruction_method == "convert_to_html_table":
                self._convert_to_html_table(element)
            else:
                # Keep original image
                element.reconstruction_data = {"method": "keep_original"}
        
        return elements
    
    def _get_reconstruction_method(self, element: VisualElement) -> str:
        """Determine the best reconstruction method for an element"""
        if element.element_type == VisualElementType.TABLE and element.translated_text:
            return "convert_to_html_table"
        elif element.element_type == VisualElementType.CHART and element.confidence > 0.8:
            return "recreate_programmatically"
        elif element.element_type == VisualElementType.DIAGRAM and element.confidence > 0.8:
            return "recreate_programmatically"
        elif element.translated_text and element.element_type != VisualElementType.PHOTOGRAPH:
            return "overlay_translation"
        else:
            return "keep_original"
    
    def _recreate_element_programmatically(self, element: VisualElement, output_dir: str):
        """Recreate element using code (Mermaid, Chart.js, etc.)"""
        # TODO: Implement programmatic recreation
        element.reconstruction_data = {
            "method": "programmatic",
            "status": "not_implemented",
            "note": "Would generate Mermaid/Chart.js code here"
        }
        element.processing_notes.append("Programmatic recreation planned")
    
    def _overlay_translation_on_image(self, element: VisualElement, output_dir: str):
        """Overlay translated text on the original image"""
        # TODO: Implement text overlay
        element.reconstruction_data = {
            "method": "text_overlay",
            "status": "not_implemented",
            "note": "Would overlay translated text on image"
        }
        element.processing_notes.append("Text overlay planned")
    
    def _convert_to_html_table(self, element: VisualElement):
        """Convert table image to HTML table using extracted/translated text"""
        # TODO: Implement table conversion
        element.reconstruction_data = {
            "method": "html_table",
            "status": "not_implemented",
            "note": "Would convert to HTML table structure"
        }
        element.processing_notes.append("HTML table conversion planned")
    
    def _save_processing_metadata(self, elements: List[VisualElement], output_dir: str):
        """Save comprehensive processing metadata"""
        metadata = {
            "processing_summary": {
                "total_elements": len(elements),
                "by_type": {},
                "with_extracted_text": 0,
                "with_translated_text": 0
            },
            "elements": []
        }
        
        # Collect statistics
        for element in elements:
            element_type = element.element_type.value
            metadata["processing_summary"]["by_type"][element_type] = \
                metadata["processing_summary"]["by_type"].get(element_type, 0) + 1
            
            if element.extracted_text:
                metadata["processing_summary"]["with_extracted_text"] += 1
            if element.translated_text:
                metadata["processing_summary"]["with_translated_text"] += 1
            
            # Add element details
            metadata["elements"].append({
                "element_id": element.element_id,
                "type": element.element_type.value,
                "confidence": element.confidence,
                "source_path": element.source_path,
                "page_num": element.page_num,
                "has_extracted_text": bool(element.extracted_text),
                "has_translated_text": bool(element.translated_text),
                "reconstruction_method": element.reconstruction_data.get("method", "none"),
                "processing_notes": element.processing_notes
            })
        
        # Save metadata
        metadata_path = os.path.join(output_dir, "visual_processing_metadata.json")
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved visual processing metadata: {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")

# Global visual element processor instance
visual_element_processor = VisualElementProcessor()
