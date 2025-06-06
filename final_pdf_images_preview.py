#!/usr/bin/env python3
"""
Preview of images that will be included in the final translated PDF.
This script simulates the translation workflow and shows which images
will actually be embedded in the final document.
"""

import os
import sys
import logging
import shutil
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_pdf_file():
    """Find the PDF file in the current directory"""
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        logger.error("❌ No PDF files found in current directory")
        return None
    
    pdf_file = pdf_files[0]
    logger.info(f"📄 Found PDF: {pdf_file}")
    return pdf_file

def create_final_images_folder():
    """Create folder for images that will go in the final PDF"""
    output_folder = "final_pdf_images"
    
    # Remove existing folder if it exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        logger.info(f"🗑️ Removed existing final images folder")
    
    # Create fresh folder
    os.makedirs(output_folder, exist_ok=True)
    logger.info(f"📁 Created final PDF images folder: {output_folder}")
    
    return output_folder

def simulate_translation_workflow(pdf_file, final_images_folder):
    """Simulate the translation workflow and determine which images will be in final PDF"""
    logger.info(f"\n🔄 SIMULATING TRANSLATION WORKFLOW")
    logger.info("=" * 50)
    
    # Step 1: Extract all images (as we just did)
    temp_extraction_folder = "temp_extraction"
    os.makedirs(temp_extraction_folder, exist_ok=True)
    
    parser = PDFParser()
    extracted_images = parser.extract_images_from_pdf(pdf_file, temp_extraction_folder)
    
    logger.info(f"📊 Extracted {len(extracted_images)} total images")
    
    # Step 2: Group images by page for translation workflow
    images_by_page = {}
    for img in extracted_images:
        page_num = img['page_num']
        if page_num not in images_by_page:
            images_by_page[page_num] = []
        images_by_page[page_num].append(img)
    
    # Step 3: Determine which images will be included in final PDF
    final_images = []
    
    for page_num in sorted(images_by_page.keys()):
        page_images = images_by_page[page_num]
        
        logger.info(f"\n📖 Processing Page {page_num}:")
        logger.info(f"   Available images: {len(page_images)}")
        
        # Simulate translation logic - which images get included
        page_final_images = select_images_for_final_pdf(page_images, page_num)
        
        for img in page_final_images:
            # Copy to final images folder
            src_path = img['filepath']
            dst_path = os.path.join(final_images_folder, img['filename'])
            
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                img['final_path'] = dst_path
                final_images.append(img)
                
                img_type = get_image_type(img['filename'])
                file_size = get_file_size(dst_path)
                logger.info(f"   ✅ INCLUDED: {img['filename']} ({img_type}, {file_size})")
            else:
                logger.warning(f"   ❌ MISSING: {img['filename']} (file not found)")
    
    # Clean up temp folder
    if os.path.exists(temp_extraction_folder):
        shutil.rmtree(temp_extraction_folder)
    
    return final_images

def select_images_for_final_pdf(page_images, page_num):
    """Determine which images from a page will be included in the final PDF"""
    final_images = []
    
    # Translation workflow logic:
    # 1. Visual content images are always included (diagrams, figures)
    # 2. Tables are included if they contain structured data
    # 3. Equations are included to preserve mathematical content
    # 4. Regular images are included if they're significant
    
    for img in page_images:
        img_type = get_image_type(img['filename'])
        include_in_final = False
        reason = ""
        
        if img_type == 'Visual Content':
            # Visual content (diagrams, figures) - always include
            include_in_final = True
            reason = "Contains diagrams/visual elements"
            
        elif img_type == 'Table':
            # Tables - include if they're substantial
            file_size = get_file_size_bytes(img['filepath'])
            if file_size > 10000:  # > 10KB
                include_in_final = True
                reason = "Substantial table data"
            else:
                reason = "Table too small/simple"
                
        elif img_type == 'Equation':
            # Equations - include if they're complex
            file_size = get_file_size_bytes(img['filepath'])
            if file_size > 8000:  # > 8KB
                include_in_final = True
                reason = "Complex mathematical content"
            else:
                reason = "Simple equation (can be recreated as text)"
                
        elif img_type == 'Regular Image':
            # Regular images - include if they're significant
            file_size = get_file_size_bytes(img['filepath'])
            if file_size > 100000:  # > 100KB
                include_in_final = True
                reason = "Significant image content"
            else:
                reason = "Small decorative image"
        
        if include_in_final:
            final_images.append(img)
            logger.info(f"      ✅ {img['filename']} - {reason}")
        else:
            logger.info(f"      ❌ {img['filename']} - {reason}")
    
    return final_images

def get_image_type(filename):
    """Determine image type from filename"""
    if '_visual_' in filename:
        return 'Visual Content'
    elif '_table_' in filename:
        return 'Table'
    elif '_equation_' in filename:
        return 'Equation'
    elif '_img_' in filename:
        return 'Regular Image'
    else:
        return 'Unknown'

def get_file_size(filepath):
    """Get formatted file size"""
    try:
        size = os.path.getsize(filepath)
        return format_file_size(size)
    except:
        return "Unknown"

def get_file_size_bytes(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def analyze_final_pdf_content(final_images):
    """Analyze what will be in the final PDF"""
    logger.info(f"\n📋 FINAL PDF CONTENT ANALYSIS")
    logger.info("=" * 50)
    
    if not final_images:
        logger.warning("❌ No images will be included in the final PDF!")
        return
    
    # Group by type
    by_type = {}
    for img in final_images:
        img_type = get_image_type(img['filename'])
        if img_type not in by_type:
            by_type[img_type] = []
        by_type[img_type].append(img)
    
    # Group by page
    by_page = {}
    for img in final_images:
        page_num = img['page_num']
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(img)
    
    # Summary
    logger.info(f"📊 FINAL PDF STATISTICS:")
    logger.info(f"   Total images in final PDF: {len(final_images)}")
    logger.info(f"   Pages with images: {len(by_page)}")
    logger.info(f"   Average images per page: {len(final_images)/len(by_page):.1f}")
    
    # Type distribution
    logger.info(f"\n🏷️ CONTENT TYPE DISTRIBUTION:")
    total_size = 0
    for img_type, images in by_type.items():
        type_size = sum(get_file_size_bytes(img['final_path']) for img in images)
        total_size += type_size
        logger.info(f"   {img_type}: {len(images)} images ({format_file_size(type_size)})")
    
    logger.info(f"   Total size: {format_file_size(total_size)}")
    
    # Page distribution
    logger.info(f"\n📄 PAGES WITH IMAGES IN FINAL PDF:")
    for page_num in sorted(by_page.keys()):
        page_images = by_page[page_num]
        page_size = sum(get_file_size_bytes(img['final_path']) for img in page_images)
        logger.info(f"   Page {page_num}: {len(page_images)} images ({format_file_size(page_size)})")
        
        for img in page_images:
            img_type = get_image_type(img['filename'])
            size = get_file_size(img['final_path'])
            logger.info(f"      • {img['filename']} ({img_type}, {size})")
    
    # Quality indicators
    logger.info(f"\n🏆 QUALITY INDICATORS:")
    
    # Largest images (likely most important)
    file_sizes = [(img, get_file_size_bytes(img['final_path'])) for img in final_images]
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"   🥇 Largest images (most important content):")
    for img, size in file_sizes[:5]:
        img_type = get_image_type(img['filename'])
        logger.info(f"      • Page {img['page_num']}: {img['filename']} ({img_type}, {format_file_size(size)})")
    
    # Coverage analysis
    visual_content = len(by_type.get('Visual Content', []))
    tables = len(by_type.get('Table', []))
    equations = len(by_type.get('Equation', []))
    
    logger.info(f"\n📈 CONTENT COVERAGE:")
    logger.info(f"   📊 Visual diagrams/figures: {visual_content}")
    logger.info(f"   📋 Data tables: {tables}")
    logger.info(f"   🔢 Mathematical equations: {equations}")
    
    if visual_content > 0:
        logger.info(f"   ✅ Good visual content preservation")
    if tables > 0:
        logger.info(f"   ✅ Structured data preserved")
    if equations > 0:
        logger.info(f"   ✅ Mathematical content preserved")

def main():
    """Run the final PDF images preview"""
    logger.info("🎯 FINAL PDF IMAGES PREVIEW")
    logger.info("=" * 70)
    logger.info("This shows which images will actually be included in the translated PDF")
    
    try:
        # Find PDF file
        pdf_file = find_pdf_file()
        if not pdf_file:
            return
        
        # Create final images folder
        final_images_folder = create_final_images_folder()
        
        # Simulate translation workflow
        final_images = simulate_translation_workflow(pdf_file, final_images_folder)
        
        # Analyze final content
        analyze_final_pdf_content(final_images)
        
        # Final summary
        logger.info(f"\n🎉 PREVIEW COMPLETED!")
        logger.info(f"📁 Check the '{final_images_folder}' folder to see images that will be in the final PDF")
        logger.info(f"📊 {len(final_images)} images will be included in the translated document")
        logger.info(f"🔍 These are the images that readers will see in the final PDF")
        
    except Exception as e:
        logger.error(f"❌ Preview failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
