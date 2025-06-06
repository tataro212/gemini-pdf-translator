#!/usr/bin/env python3
"""
Debug script for PDF extraction issues
"""

import os
import fitz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_pdf_extraction():
    """Debug PDF extraction step by step"""
    
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    pdf_path = pdf_files[0]
    logger.info(f"Testing with: {pdf_path}")
    
    try:
        # Test 1: Basic PDF opening
        logger.info("Test 1: Opening PDF...")
        doc = fitz.open(pdf_path)
        logger.info(f"✅ PDF opened successfully. Pages: {len(doc)}")
        
        # Test 2: Basic image extraction
        logger.info("Test 2: Basic image extraction...")
        total_images = 0
        for page_num in range(min(3, len(doc))):  # Test first 3 pages
            page = doc[page_num]
            image_list = page.get_images(full=True)
            logger.info(f"Page {page_num + 1}: {len(image_list)} images found")
            total_images += len(image_list)
        
        logger.info(f"✅ Total images in first 3 pages: {total_images}")
        
        # Test 3: Table detection
        logger.info("Test 3: Table detection...")
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if "lines" in b]
        logger.info(f"✅ Found {len(text_blocks)} text blocks on page 1")
        
        # Test 4: Equation detection
        logger.info("Test 4: Equation detection...")
        page_text = page.get_text()
        math_symbols = ['=', '+', '-', '*', '/', '^', '_']
        found_symbols = [s for s in math_symbols if s in page_text]
        logger.info(f"✅ Found math symbols: {found_symbols}")
        
        # Test 5: Document closing
        logger.info("Test 5: Closing document...")
        doc.close()
        logger.info("✅ Document closed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_extraction()
