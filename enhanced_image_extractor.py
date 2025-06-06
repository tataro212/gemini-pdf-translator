#!/usr/bin/env python3
"""
Enhanced image extractor that captures both raster images and vector graphics
"""

import os
import sys
import logging
import fitz  # PyMuPDF
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedImageExtractor:
    def __init__(self, min_width=30, min_height=30, min_vector_items=5):
        self.min_width = min_width
        self.min_height = min_height
        self.min_vector_items = min_vector_items
        
    def extract_raster_images(self, doc, output_dir):
        """Extract traditional raster images"""
        logger.info("🖼️ Extracting raster images...")
        
        raster_images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.width >= self.min_width and pix.height >= self.min_height:
                        filename = f"page_{page_num + 1}_raster_{img_index + 1}.png"
                        filepath = os.path.join(output_dir, filename)
                        
                        pix.save(filepath)
                        
                        raster_images.append({
                            'type': 'raster',
                            'filename': filename,
                            'page_num': page_num + 1,
                            'width': pix.width,
                            'height': pix.height,
                            'filepath': filepath
                        })
                    
                    pix = None
                except Exception as e:
                    logger.warning(f"Could not extract raster image {xref} on page {page_num + 1}: {e}")
        
        logger.info(f"   ✅ Extracted {len(raster_images)} raster images")
        return raster_images
    
    def extract_vector_graphics(self, doc, output_dir):
        """Extract vector graphics by rendering them as images"""
        logger.info("🎨 Extracting vector graphics...")
        
        vector_images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            try:
                # Get all drawings on the page
                drawings = page.get_drawings()
                
                if len(drawings) >= self.min_vector_items:
                    # Group nearby drawings together
                    drawing_groups = self._group_drawings(drawings)
                    
                    for group_index, group in enumerate(drawing_groups):
                        if len(group) >= self.min_vector_items:
                            # Calculate bounding box for the group
                            bbox = self._calculate_group_bbox(group)
                            
                            if self._is_significant_graphic(bbox):
                                # Render this area as an image
                                rendered_image = self._render_area_as_image(page, bbox, page_num, group_index, output_dir)
                                
                                if rendered_image:
                                    vector_images.append(rendered_image)
                
            except Exception as e:
                logger.warning(f"Could not extract vector graphics on page {page_num + 1}: {e}")
        
        logger.info(f"   ✅ Extracted {len(vector_images)} vector graphics")
        return vector_images
    
    def _group_drawings(self, drawings, proximity_threshold=50):
        """Group nearby drawings together"""
        if not drawings:
            return []
        
        groups = []
        used = set()
        
        for i, drawing in enumerate(drawings):
            if i in used:
                continue
            
            group = [drawing]
            used.add(i)
            
            # Find nearby drawings
            for j, other_drawing in enumerate(drawings):
                if j in used or i == j:
                    continue
                
                if self._are_drawings_close(drawing, other_drawing, proximity_threshold):
                    group.append(other_drawing)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_drawings_close(self, drawing1, drawing2, threshold):
        """Check if two drawings are close to each other"""
        try:
            # Get bounding boxes
            bbox1 = self._get_drawing_bbox(drawing1)
            bbox2 = self._get_drawing_bbox(drawing2)
            
            if not bbox1 or not bbox2:
                return False
            
            # Calculate distance between centers
            center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
            center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
            
            distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
            
            return distance <= threshold
        except:
            return False
    
    def _get_drawing_bbox(self, drawing):
        """Get bounding box of a drawing"""
        try:
            items = drawing.get('items', [])
            if not items:
                return None
            
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            
            for item in items:
                if 'rect' in item:
                    rect = item['rect']
                    min_x = min(min_x, rect[0])
                    min_y = min(min_y, rect[1])
                    max_x = max(max_x, rect[2])
                    max_y = max(max_y, rect[3])
            
            if min_x == float('inf'):
                return None
            
            return [min_x, min_y, max_x, max_y]
        except:
            return None
    
    def _calculate_group_bbox(self, group):
        """Calculate bounding box for a group of drawings"""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for drawing in group:
            bbox = self._get_drawing_bbox(drawing)
            if bbox:
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                max_x = max(max_x, bbox[2])
                max_y = max(max_y, bbox[3])
        
        if min_x == float('inf'):
            return None
        
        return [min_x, min_y, max_x, max_y]
    
    def _is_significant_graphic(self, bbox):
        """Check if a graphic is significant enough to extract"""
        if not bbox:
            return False
        
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Must be at least minimum size
        if width < self.min_width or height < self.min_height:
            return False
        
        # Must have reasonable aspect ratio (not too thin)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 10:  # Too thin, likely a line
            return False
        
        return True
    
    def _render_area_as_image(self, page, bbox, page_num, group_index, output_dir):
        """Render a specific area of the page as an image"""
        try:
            # Create a clip rectangle
            clip_rect = fitz.Rect(bbox)
            
            # Render the clipped area
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat, clip=clip_rect)
            
            if pix.width >= self.min_width and pix.height >= self.min_height:
                filename = f"page_{page_num + 1}_vector_{group_index + 1}.png"
                filepath = os.path.join(output_dir, filename)
                
                pix.save(filepath)
                
                result = {
                    'type': 'vector',
                    'filename': filename,
                    'page_num': page_num + 1,
                    'width': pix.width,
                    'height': pix.height,
                    'filepath': filepath,
                    'bbox': bbox
                }
                
                pix = None
                return result
            
            pix = None
        except Exception as e:
            logger.warning(f"Could not render vector area on page {page_num + 1}: {e}")
        
        return None
    
    def extract_all_images(self, pdf_path, output_dir):
        """Extract both raster and vector images"""
        logger.info("🚀 ENHANCED IMAGE EXTRACTION")
        logger.info("=" * 50)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Open PDF
        doc = fitz.open(pdf_path)
        
        # Extract raster images
        raster_images = self.extract_raster_images(doc, output_dir)
        
        # Extract vector graphics
        vector_images = self.extract_vector_graphics(doc, output_dir)
        
        # Combine results
        all_images = raster_images + vector_images
        
        doc.close()
        
        logger.info("=" * 50)
        logger.info(f"🎯 EXTRACTION COMPLETE")
        logger.info(f"   📊 Raster images: {len(raster_images)}")
        logger.info(f"   🎨 Vector graphics: {len(vector_images)}")
        logger.info(f"   📈 Total images: {len(all_images)}")
        
        return all_images

def test_enhanced_extraction():
    """Test the enhanced extraction on the PDF"""
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    pdf_path = pdf_files[0]
    output_dir = "enhanced_extracted_images"
    
    logger.info(f"📄 Testing enhanced extraction on: {pdf_path}")
    
    # Create extractor
    extractor = EnhancedImageExtractor(
        min_width=30,
        min_height=30,
        min_vector_items=3  # Minimum vector items to consider as a graphic
    )
    
    # Extract images
    all_images = extractor.extract_all_images(pdf_path, output_dir)
    
    # Show results
    logger.info("\n📋 EXTRACTED IMAGES:")
    for i, img in enumerate(all_images[:10]):  # Show first 10
        logger.info(f"   {i+1}. {img['filename']} ({img['type']}) - Page {img['page_num']} - {img['width']}x{img['height']}")
    
    if len(all_images) > 10:
        logger.info(f"   ... and {len(all_images) - 10} more images")
    
    logger.info(f"\n💾 Images saved to: {output_dir}")
    
    return all_images

if __name__ == "__main__":
    test_enhanced_extraction()
