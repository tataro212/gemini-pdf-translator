#!/usr/bin/env python3
"""
Test script specifically for figure detection debugging
"""

import os
import fitz
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_figure_detection():
    """Test figure detection on specific pages"""
    
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    pdf_path = pdf_files[0]
    logger.info(f"Testing figure detection with: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        
        # Test on pages that likely have figures (based on previous results)
        test_pages = [21, 36, 40, 68, 76, 133]  # 0-based indexing (page 22, 37, 41, 69, 77, 134)
        
        figure_patterns = [
            r'figure\s+(\d+)\.(\d+)',  # Figure 1.1, Figure 2.3, etc.
            r'figure\s+(\d+)',         # Figure 1, Figure 2, etc.
            r'fig\.\s+(\d+)\.(\d+)',   # Fig. 1.1, Fig. 2.3, etc.
            r'fig\.\s+(\d+)',          # Fig. 1, Fig. 2, etc.
        ]
        
        for page_num in test_pages:
            if page_num >= len(doc):
                continue
                
            logger.info(f"\n--- Testing Page {page_num + 1} ---")
            page = doc[page_num]
            
            # 1. Look for figure captions
            blocks = page.get_text("dict")["blocks"]
            captions_found = []
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += " "
                
                block_text = block_text.strip().lower()
                
                for pattern in figure_patterns:
                    matches = re.finditer(pattern, block_text, re.IGNORECASE)
                    for match in matches:
                        captions_found.append({
                            'text': block_text[:100] + "..." if len(block_text) > 100 else block_text,
                            'bbox': block["bbox"],
                            'match': match.group()
                        })
            
            logger.info(f"Found {len(captions_found)} figure captions:")
            for i, caption in enumerate(captions_found):
                logger.info(f"  {i+1}. {caption['match']} - {caption['text']}")
            
            # 2. Look for drawings/vector graphics
            drawings = page.get_drawings()
            logger.info(f"Found {len(drawings)} vector drawings")
            
            # 3. Look for raster images
            images = page.get_images(full=True)
            logger.info(f"Found {len(images)} raster images")
            
            # 4. Analyze text blocks for diagram patterns
            diagram_blocks = 0
            for block in blocks:
                if "lines" not in block:
                    continue
                
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += "\n"
                
                # Look for diagram-like characters
                diagram_chars = ['|', '-', '+', '/', '\\', '→', '←', '↑', '↓', '○', '●', '□', '■']
                diagram_char_count = sum(block_text.count(char) for char in diagram_chars)
                
                if diagram_char_count > 5:  # Threshold for potential diagram
                    diagram_blocks += 1
                    logger.info(f"  Potential diagram block: {diagram_char_count} special chars")
            
            logger.info(f"Found {diagram_blocks} potential diagram text blocks")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_figure_detection()
