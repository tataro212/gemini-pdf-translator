#!/usr/bin/env python3
"""
Analyze vector drawings to understand what they contain
"""

import os
import sys
import logging
import fitz  # PyMuPDF
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_drawings_on_page(page, page_num, max_drawings=10):
    """Analyze drawings on a specific page"""
    try:
        drawings = page.get_drawings()
        
        if not drawings:
            return []
        
        logger.info(f"📄 Page {page_num}: {len(drawings)} drawings")
        
        analyzed = []
        
        for i, drawing in enumerate(drawings[:max_drawings]):
            try:
                analysis = {
                    'page': page_num,
                    'drawing_index': i,
                    'items': len(drawing.get('items', [])),
                    'bbox': None,
                    'area': 0,
                    'types': set()
                }
                
                # Analyze items in the drawing
                items = drawing.get('items', [])
                
                if items:
                    min_x = min_y = float('inf')
                    max_x = max_y = float('-inf')
                    
                    for item in items:
                        # Track item types
                        if 'type' in item:
                            analysis['types'].add(item['type'])
                        
                        # Calculate bounding box
                        if 'rect' in item:
                            rect = item['rect']
                            min_x = min(min_x, rect[0])
                            min_y = min(min_y, rect[1])
                            max_x = max(max_x, rect[2])
                            max_y = max(max_y, rect[3])
                    
                    if min_x != float('inf'):
                        analysis['bbox'] = [min_x, min_y, max_x, max_y]
                        width = max_x - min_x
                        height = max_y - min_y
                        analysis['area'] = width * height
                        analysis['width'] = width
                        analysis['height'] = height
                
                analysis['types'] = list(analysis['types'])
                analyzed.append(analysis)
                
            except Exception as e:
                logger.warning(f"Could not analyze drawing {i} on page {page_num}: {e}")
        
        return analyzed
        
    except Exception as e:
        logger.warning(f"Could not get drawings on page {page_num}: {e}")
        return []

def find_significant_graphics(pdf_path, min_area=1000, min_items=5):
    """Find drawings that might be significant graphics"""
    logger.info("🔍 ANALYZING VECTOR DRAWINGS FOR SIGNIFICANT GRAPHICS")
    logger.info("=" * 60)
    
    doc = fitz.open(pdf_path)
    significant_graphics = []
    
    # Analyze first 20 pages to get a sample
    pages_to_check = min(20, len(doc))
    
    for page_num in range(pages_to_check):
        page = doc[page_num]
        drawings = analyze_drawings_on_page(page, page_num + 1)
        
        for drawing in drawings:
            # Check if this might be a significant graphic
            if (drawing['area'] >= min_area and 
                drawing['items'] >= min_items and
                drawing['width'] >= 50 and 
                drawing['height'] >= 50):
                
                significant_graphics.append(drawing)
    
    doc.close()
    
    logger.info(f"📊 Found {len(significant_graphics)} potentially significant graphics")
    
    # Sort by area (largest first)
    significant_graphics.sort(key=lambda x: x['area'], reverse=True)
    
    # Show top candidates
    logger.info("\n🎯 TOP CANDIDATES FOR GRAPHICS:")
    for i, graphic in enumerate(significant_graphics[:10]):
        logger.info(f"   {i+1}. Page {graphic['page']}: {graphic['width']:.0f}x{graphic['height']:.0f} "
                   f"({graphic['items']} items, area: {graphic['area']:.0f})")
        logger.info(f"      Types: {graphic['types']}")
    
    return significant_graphics

def sample_drawing_content(pdf_path, num_pages=5):
    """Sample drawing content to understand structure"""
    logger.info(f"\n🔬 SAMPLING DRAWING CONTENT (first {num_pages} pages)")
    logger.info("=" * 60)
    
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(num_pages, len(doc))):
        page = doc[page_num]
        
        try:
            drawings = page.get_drawings()
            
            if drawings:
                logger.info(f"\n📄 Page {page_num + 1}: {len(drawings)} drawings")
                
                # Sample first few drawings
                for i, drawing in enumerate(drawings[:3]):
                    logger.info(f"   Drawing {i+1}:")
                    
                    items = drawing.get('items', [])
                    logger.info(f"     Items: {len(items)}")
                    
                    if items:
                        # Show first item structure
                        first_item = items[0]
                        logger.info(f"     First item keys: {list(first_item.keys())}")
                        
                        if 'type' in first_item:
                            logger.info(f"     Type: {first_item['type']}")
                        
                        if 'rect' in first_item:
                            rect = first_item['rect']
                            width = rect[2] - rect[0]
                            height = rect[3] - rect[1]
                            logger.info(f"     Size: {width:.1f}x{height:.1f}")
        
        except Exception as e:
            logger.warning(f"Could not sample page {page_num + 1}: {e}")
    
    doc.close()

def render_sample_graphics(pdf_path, significant_graphics, output_dir, max_samples=5):
    """Render sample graphics to see what they look like"""
    logger.info(f"\n🖼️ RENDERING SAMPLE GRAPHICS")
    logger.info("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    rendered = []
    
    for i, graphic in enumerate(significant_graphics[:max_samples]):
        try:
            page_num = graphic['page'] - 1  # Convert to 0-based
            page = doc[page_num]
            
            bbox = graphic['bbox']
            if bbox:
                # Add some padding
                padding = 10
                clip_rect = fitz.Rect(
                    bbox[0] - padding,
                    bbox[1] - padding, 
                    bbox[2] + padding,
                    bbox[3] + padding
                )
                
                # Render at high resolution
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom
                pix = page.get_pixmap(matrix=mat, clip=clip_rect)
                
                filename = f"sample_graphic_{i+1}_page_{graphic['page']}.png"
                filepath = os.path.join(output_dir, filename)
                
                pix.save(filepath)
                
                rendered.append({
                    'filename': filename,
                    'page': graphic['page'],
                    'size': f"{graphic['width']:.0f}x{graphic['height']:.0f}",
                    'items': graphic['items']
                })
                
                logger.info(f"   ✅ Rendered: {filename}")
                
                pix = None
        
        except Exception as e:
            logger.warning(f"Could not render graphic {i+1}: {e}")
    
    doc.close()
    
    logger.info(f"💾 Sample graphics saved to: {output_dir}")
    return rendered

def main():
    """Main analysis function"""
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    pdf_path = pdf_files[0]
    logger.info(f"📄 Analyzing: {pdf_path}")
    
    # Sample drawing content structure
    sample_drawing_content(pdf_path)
    
    # Find significant graphics
    significant_graphics = find_significant_graphics(pdf_path)
    
    # Render samples
    if significant_graphics:
        output_dir = "sample_vector_graphics"
        rendered = render_sample_graphics(pdf_path, significant_graphics, output_dir)
        
        logger.info(f"\n🎯 ANALYSIS COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📊 Total significant graphics found: {len(significant_graphics)}")
        logger.info(f"🖼️ Sample graphics rendered: {len(rendered)}")
        logger.info(f"💡 Check the '{output_dir}' folder to see what was extracted")
        
        if len(significant_graphics) > 10:
            logger.info("\n✅ SUCCESS: Found many potential graphics!")
            logger.info("   This suggests the PDF has diagrams/schemas that can be extracted")
            logger.info("   Consider updating the main extraction logic to capture these")
        else:
            logger.info("\n⚠️ Limited graphics found")
            logger.info("   The vector drawings might be decorative elements or text formatting")
    else:
        logger.info("\n❌ No significant graphics found")
        logger.info("   The 2097 vector drawings are likely decorative elements or text formatting")

if __name__ == "__main__":
    main()
