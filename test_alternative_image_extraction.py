#!/usr/bin/env python3
"""
Test alternative image extraction methods to find more images
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

def extract_images_method1_standard(pdf_path):
    """Standard method - current implementation"""
    logger.info("🔍 Method 1: Standard PyMuPDF image extraction")
    
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            if pix.width >= 10 and pix.height >= 10:  # Very low threshold
                images.append({
                    'page': page_num + 1,
                    'width': pix.width,
                    'height': pix.height,
                    'method': 'standard'
                })
            
            pix = None
    
    doc.close()
    logger.info(f"   Found {len(images)} images")
    return images

def extract_images_method2_all_objects(pdf_path):
    """Method 2: Extract all image objects regardless of size"""
    logger.info("🔍 Method 2: All image objects (no size filtering)")
    
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)  # Get full image info
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                images.append({
                    'page': page_num + 1,
                    'width': pix.width,
                    'height': pix.height,
                    'method': 'all_objects',
                    'colorspace': pix.colorspace.name if pix.colorspace else 'unknown',
                    'alpha': pix.alpha
                })
                pix = None
            except Exception as e:
                logger.warning(f"   Could not process image {xref} on page {page_num + 1}: {e}")
    
    doc.close()
    logger.info(f"   Found {len(images)} images")
    return images

def extract_images_method3_drawings(pdf_path):
    """Method 3: Look for vector drawings and paths"""
    logger.info("🔍 Method 3: Vector drawings and paths")
    
    doc = fitz.open(pdf_path)
    drawings = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get drawing commands
        try:
            drawings_on_page = page.get_drawings()
            for drawing in drawings_on_page:
                drawings.append({
                    'page': page_num + 1,
                    'type': 'vector_drawing',
                    'method': 'drawings',
                    'items': len(drawing.get('items', []))
                })
        except Exception as e:
            logger.warning(f"   Could not get drawings on page {page_num + 1}: {e}")
    
    doc.close()
    logger.info(f"   Found {len(drawings)} vector drawings")
    return drawings

def extract_images_method4_text_blocks(pdf_path):
    """Method 4: Look for image blocks in text extraction"""
    logger.info("🔍 Method 4: Image blocks from text extraction")
    
    doc = fitz.open(pdf_path)
    image_blocks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text blocks with images
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "image" in block:
                image_blocks.append({
                    'page': page_num + 1,
                    'method': 'text_blocks',
                    'bbox': block.get('bbox', []),
                    'width': block.get('width', 0),
                    'height': block.get('height', 0)
                })
    
    doc.close()
    logger.info(f"   Found {len(image_blocks)} image blocks")
    return image_blocks

def analyze_pdf_structure(pdf_path):
    """Analyze the overall PDF structure"""
    logger.info("🔍 PDF Structure Analysis")
    
    doc = fitz.open(pdf_path)
    
    logger.info(f"   📄 Total pages: {len(doc)}")
    logger.info(f"   🔒 Encrypted: {doc.is_encrypted}")
    logger.info(f"   📊 Metadata: {doc.metadata}")
    
    # Count different object types
    total_objects = 0
    image_objects = 0
    
    for page_num in range(min(5, len(doc))):  # Check first 5 pages
        page = doc[page_num]
        
        # Count objects on page
        try:
            page_objects = len(page.get_images(full=True))
            total_objects += page_objects
            
            # Count actual image objects
            for img in page.get_images():
                image_objects += 1
                
        except Exception as e:
            logger.warning(f"   Could not analyze page {page_num + 1}: {e}")
    
    logger.info(f"   🖼️ Image objects in first 5 pages: {image_objects}")
    logger.info(f"   📦 Total objects in first 5 pages: {total_objects}")
    
    doc.close()

def test_all_methods(pdf_path):
    """Test all extraction methods on the PDF"""
    logger.info("🧪 TESTING ALL IMAGE EXTRACTION METHODS")
    logger.info("=" * 60)
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    # Analyze PDF structure first
    analyze_pdf_structure(pdf_path)
    
    logger.info("\n" + "=" * 60)
    
    # Test all methods
    results = {}
    
    try:
        results['standard'] = extract_images_method1_standard(pdf_path)
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")
        results['standard'] = []
    
    try:
        results['all_objects'] = extract_images_method2_all_objects(pdf_path)
    except Exception as e:
        logger.error(f"Method 2 failed: {e}")
        results['all_objects'] = []
    
    try:
        results['drawings'] = extract_images_method3_drawings(pdf_path)
    except Exception as e:
        logger.error(f"Method 3 failed: {e}")
        results['drawings'] = []
    
    try:
        results['text_blocks'] = extract_images_method4_text_blocks(pdf_path)
    except Exception as e:
        logger.error(f"Method 4 failed: {e}")
        results['text_blocks'] = []
    
    # Summary
    logger.info("\n🎯 EXTRACTION RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for method, items in results.items():
        logger.info(f"📊 {method.upper()}: {len(items)} items found")
        
        if items and len(items) > 0:
            # Show first few examples
            logger.info(f"   Examples:")
            for i, item in enumerate(items[:3]):
                if 'width' in item and 'height' in item:
                    logger.info(f"     {i+1}. Page {item['page']}: {item['width']}x{item['height']}")
                else:
                    logger.info(f"     {i+1}. Page {item['page']}: {item.get('type', 'unknown')}")
    
    # Find the method with most results
    best_method = max(results.keys(), key=lambda k: len(results[k]))
    best_count = len(results[best_method])
    
    logger.info(f"\n🏆 BEST METHOD: {best_method.upper()} with {best_count} items")
    
    if best_count > 3:
        logger.info("💡 This method found more images than the current implementation!")
        logger.info("   Consider updating the image extraction logic to use this approach.")
    elif best_count == 3:
        logger.info("ℹ️ This matches the current extraction count.")
        logger.info("   The PDF might genuinely have only 3 raster images.")
        logger.info("   Other content might be vector graphics or embedded differently.")
    else:
        logger.info("⚠️ All methods found few images.")
        logger.info("   This PDF might use vector graphics instead of raster images.")
    
    return results

def main():
    """Main function"""
    # Look for PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found in current directory")
        return
    
    # Use the first PDF file
    test_pdf = pdf_files[0]
    logger.info(f"📄 Testing with: {test_pdf}")
    
    results = test_all_methods(test_pdf)
    
    logger.info("\n🎯 RECOMMENDATIONS")
    logger.info("=" * 60)
    
    total_found = sum(len(items) for items in results.values())
    
    if total_found > 10:
        logger.info("✅ Multiple methods found many images!")
        logger.info("   • Update the extraction logic to use the best method")
        logger.info("   • Consider combining multiple methods")
    elif total_found > 3:
        logger.info("📈 Some methods found more images than current implementation")
        logger.info("   • Try the method with most results")
        logger.info("   • Verify the additional images are meaningful")
    else:
        logger.info("📊 This PDF appears to have limited raster images")
        logger.info("   • Content might be primarily vector graphics")
        logger.info("   • Consider if vector graphics extraction is needed")
        logger.info("   • Current extraction might be working correctly")

if __name__ == "__main__":
    main()
