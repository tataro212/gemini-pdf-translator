"""
YOLOv8 Visual Content Detector

This module implements state-of-the-art visual content detection using YOLOv8
fine-tuned on document layout analysis datasets (PubLayNet). It replaces heuristic
visual extraction with deep learning-powered precision.

Key Features:
- YOLOv8 model fine-tuned on PubLayNet dataset
- Supreme accuracy in detecting figures, tables, headers, footnotes
- Rich classification with confidence scores
- Robust performance across diverse document layouts
- FastAPI microservice architecture for scalability
"""

import os
import logging
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import io
import base64

# Import image processing
try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import PyMuPDF for page rendering
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class YOLODetection:
    """Represents a visual element detected by YOLOv8"""
    label: str  # 'figure', 'table', 'text', 'title', 'list'
    confidence: float
    bounding_box: Tuple[float, float, float, float]  # (x1, y1, x2, y2)
    page_num: int
    detection_id: str
    
    def get_area(self) -> float:
        """Calculate bounding box area"""
        x1, y1, x2, y2 = self.bounding_box
        return (x2 - x1) * (y2 - y1)
    
    def get_center(self) -> Tuple[float, float]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = self.bounding_box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

class YOLOv8VisualDetector:
    """
    State-of-the-art visual content detector using YOLOv8.
    
    This class integrates with a YOLOv8 microservice to provide supreme accuracy
    in detecting and classifying visual elements in PDF documents.
    """
    
    def __init__(self, service_url: str = "http://127.0.0.1:8000"):
        self.logger = logging.getLogger(__name__)
        self.service_url = service_url
        
        # Detection configuration
        self.config = {
            'confidence_threshold': 0.5,  # Minimum confidence for detections
            'nms_threshold': 0.4,  # Non-maximum suppression threshold
            'max_detections': 100,  # Maximum detections per page
            'target_dpi': 300,  # DPI for page rendering
            'supported_classes': ['figure', 'table', 'text', 'title', 'list'],
            'service_timeout': 30  # Timeout for API calls
        }
        
        # Performance tracking
        self.stats = {
            'pages_processed': 0,
            'detections_found': 0,
            'api_calls': 0,
            'errors': 0
        }
        
        # Check dependencies
        if not PIL_AVAILABLE:
            raise Exception("PIL/Pillow not available for image processing")
        if not PYMUPDF_AVAILABLE:
            raise Exception("PyMuPDF not available for PDF rendering")
    
    async def detect_visual_elements_in_pdf(self, pdf_path: str, output_dir: str) -> List[YOLODetection]:
        """
        Detect visual elements in entire PDF using YOLOv8.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for saving extracted images
            
        Returns:
            List of YOLODetection objects with supreme accuracy
        """
        self.logger.info(f"🔍 Starting YOLOv8 visual detection: {os.path.basename(pdf_path)}")
        
        # Check if YOLOv8 service is available
        if not await self._check_service_availability():
            self.logger.error("❌ YOLOv8 service not available - falling back to heuristic detection")
            return await self._fallback_heuristic_detection(pdf_path, output_dir)
        
        all_detections = []
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Create output directory for cropped images
            images_dir = os.path.join(output_dir, "yolo_detected_images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                self.logger.info(f"   📄 Processing page {page_num + 1}/{len(doc)}")
                
                # Render page to high-resolution image
                page_image = self._render_page_to_image(page, self.config['target_dpi'])
                
                # Detect visual elements using YOLOv8
                page_detections = await self._detect_elements_in_page_image(
                    page_image, page_num + 1
                )
                
                # Crop and save detected visual elements
                for detection in page_detections:
                    if detection.label in ['figure', 'table']:  # Only save visual content
                        cropped_image_path = await self._crop_and_save_detection(
                            page_image, detection, images_dir, page_num + 1
                        )
                        # Update detection with saved image path
                        detection.detection_id = cropped_image_path
                
                all_detections.extend(page_detections)
                self.stats['pages_processed'] += 1
            
            doc.close()
            
            # Filter and validate detections
            filtered_detections = self._filter_and_validate_detections(all_detections)
            
            self.stats['detections_found'] = len(filtered_detections)
            
            self.logger.info(f"✅ YOLOv8 detection completed:")
            self.logger.info(f"   📊 Pages processed: {self.stats['pages_processed']}")
            self.logger.info(f"   🎯 Visual elements detected: {len(filtered_detections)}")
            self.logger.info(f"   📈 Average detections per page: {len(filtered_detections) / max(1, self.stats['pages_processed']):.1f}")
            
            return filtered_detections
            
        except Exception as e:
            self.logger.error(f"❌ YOLOv8 detection failed: {e}")
            self.stats['errors'] += 1
            # Fallback to heuristic detection
            return await self._fallback_heuristic_detection(pdf_path, output_dir)
    
    def _render_page_to_image(self, page, dpi: int = 300) -> Image.Image:
        """Render PDF page to high-resolution PIL Image"""
        try:
            # Create high-resolution pixmap
            mat = fitz.Matrix(dpi / 72, dpi / 72)  # Scale factor for DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            image = Image.open(io.BytesIO(img_data))
            
            pix = None  # Free memory
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to render page to image: {e}")
            # Create blank image as fallback
            return Image.new('RGB', (1000, 1000), 'white')
    
    async def _detect_elements_in_page_image(self, page_image: Image.Image, 
                                           page_num: int) -> List[YOLODetection]:
        """Send page image to YOLOv8 service for detection"""
        try:
            # Convert PIL Image to bytes
            img_buffer = io.BytesIO()
            page_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file', img_bytes, filename=f'page_{page_num}.png', 
                          content_type='image/png')
            
            # Make API call to YOLOv8 service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.service_url}/predict/layout",
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=self.config['service_timeout'])
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        detections = self._parse_yolo_response(result, page_num)
                        self.stats['api_calls'] += 1
                        return detections
                    else:
                        self.logger.error(f"YOLOv8 service error: {response.status}")
                        return []
                        
        except asyncio.TimeoutError:
            self.logger.error(f"YOLOv8 service timeout for page {page_num}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to detect elements in page {page_num}: {e}")
            return []
    
    def _parse_yolo_response(self, response: Dict[str, Any], page_num: int) -> List[YOLODetection]:
        """Parse YOLOv8 service response into YOLODetection objects"""
        detections = []
        
        try:
            for i, detection_data in enumerate(response.get('detections', [])):
                label = detection_data.get('label', 'unknown')
                confidence = detection_data.get('confidence', 0.0)
                bbox = detection_data.get('bounding_box', [0, 0, 0, 0])
                
                # Filter by confidence threshold
                if confidence >= self.config['confidence_threshold']:
                    detection = YOLODetection(
                        label=label,
                        confidence=confidence,
                        bounding_box=tuple(bbox),
                        page_num=page_num,
                        detection_id=f"page_{page_num}_detection_{i}"
                    )
                    detections.append(detection)
            
            self.logger.debug(f"   🎯 Page {page_num}: {len(detections)} detections above threshold")
            return detections
            
        except Exception as e:
            self.logger.error(f"Failed to parse YOLOv8 response: {e}")
            return []
    
    async def _crop_and_save_detection(self, page_image: Image.Image, 
                                     detection: YOLODetection, 
                                     images_dir: str, page_num: int) -> str:
        """Crop detected visual element and save as image file"""
        try:
            x1, y1, x2, y2 = detection.bounding_box
            
            # Ensure coordinates are within image bounds
            width, height = page_image.size
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(x1, min(x2, width))
            y2 = max(y1, min(y2, height))
            
            # Crop the image
            cropped_image = page_image.crop((x1, y1, x2, y2))
            
            # Generate filename
            filename = f"page_{page_num}_{detection.label}_{detection.detection_id.split('_')[-1]}.png"
            filepath = os.path.join(images_dir, filename)
            
            # Save cropped image
            cropped_image.save(filepath, 'PNG')
            
            self.logger.debug(f"   💾 Saved {detection.label}: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to crop and save detection: {e}")
            return ""

    def _filter_and_validate_detections(self, detections: List[YOLODetection]) -> List[YOLODetection]:
        """Filter and validate detections for quality and relevance"""
        filtered = []

        for detection in detections:
            # Filter by supported classes
            if detection.label not in self.config['supported_classes']:
                continue

            # Filter by minimum area (avoid tiny detections)
            if detection.get_area() < 100:  # Minimum 100 square pixels
                continue

            # Filter by confidence
            if detection.confidence < self.config['confidence_threshold']:
                continue

            filtered.append(detection)

        # Sort by confidence (highest first)
        filtered.sort(key=lambda x: x.confidence, reverse=True)

        # Limit maximum detections
        if len(filtered) > self.config['max_detections']:
            filtered = filtered[:self.config['max_detections']]

        return filtered

    async def _check_service_availability(self) -> bool:
        """Check if YOLOv8 service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.service_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False

    def _filter_and_validate_detections(self, detections: List[YOLODetection]) -> List[YOLODetection]:
        """Filter and validate detections for quality and relevance"""
        filtered = []

        for detection in detections:
            # Filter by supported classes
            if detection.label not in self.config['supported_classes']:
                continue

            # Filter by minimum area (avoid tiny detections)
            if detection.get_area() < 100:  # Minimum 100 square pixels
                continue

            # Filter by confidence
            if detection.confidence < self.config['confidence_threshold']:
                continue

            filtered.append(detection)

        # Sort by confidence (highest first)
        filtered.sort(key=lambda x: x.confidence, reverse=True)

        # Limit maximum detections
        if len(filtered) > self.config['max_detections']:
            filtered = filtered[:self.config['max_detections']]

        return filtered

    async def _check_service_availability(self) -> bool:
        """Check if YOLOv8 service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.service_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False

    async def _fallback_heuristic_detection(self, pdf_path: str, output_dir: str) -> List[YOLODetection]:
        """Fallback to heuristic detection if YOLOv8 service unavailable"""
        self.logger.warning("🔄 Using fallback heuristic detection...")

        detections = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Simple heuristic: detect images using PyMuPDF
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        # Get image rectangle
                        img_rects = page.get_image_rects(xref)
                        if img_rects:
                            bbox = img_rects[0]
                            detection = YOLODetection(
                                label='figure',
                                confidence=0.8,  # Heuristic confidence
                                bounding_box=bbox,
                                page_num=page_num + 1,
                                detection_id=f"heuristic_page_{page_num + 1}_img_{img_index}"
                            )
                            detections.append(detection)
                    except:
                        continue

            doc.close()

        except Exception as e:
            self.logger.error(f"Fallback detection failed: {e}")

        return detections

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection performance statistics"""
        return {
            'pages_processed': self.stats['pages_processed'],
            'detections_found': self.stats['detections_found'],
            'api_calls_made': self.stats['api_calls'],
            'errors_encountered': self.stats['errors'],
            'average_detections_per_page': self.stats['detections_found'] / max(1, self.stats['pages_processed']),
            'service_url': self.service_url,
            'configuration': self.config.copy()
        }

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection performance statistics"""
        return {
            'pages_processed': self.stats['pages_processed'],
            'detections_found': self.stats['detections_found'],
            'api_calls_made': self.stats['api_calls'],
            'errors_encountered': self.stats['errors'],
            'average_detections_per_page': self.stats['detections_found'] / max(1, self.stats['pages_processed']),
            'service_url': self.service_url,
            'configuration': self.config.copy()
        }
