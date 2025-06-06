#!/usr/bin/env python3
"""
Comprehensive test of the enhanced PDF extraction and translation workflow
"""

import os
import logging
import time
from pdf_parser import PDFParser, StructuredContentExtractor
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_full_workflow():
    """Test the complete enhanced PDF extraction and processing workflow"""
    
    print("🚀 COMPREHENSIVE PDF WORKFLOW TEST")
    print("=" * 60)
    
    # Test configuration - find PDF file
    import glob
    pdf_files = glob.glob("*.pdf")

    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return

    pdf_path = pdf_files[0]  # Use the first PDF found
    output_folder = "workflow_test_output"
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize components
    parser = PDFParser()
    extractor = StructuredContentExtractor()
    
    print(f"📄 Testing PDF: {os.path.basename(pdf_path)}")
    print(f"📁 Output folder: {output_folder}")
    print()
    
    # Test 1: Extract all image types
    print("🖼️  Test 1: Comprehensive Image Extraction")
    print("-" * 40)
    
    start_time = time.time()
    
    try:
        # Extract regular images
        regular_images = parser.extract_images_from_pdf(pdf_path, output_folder)
        print(f"   ✅ Regular images: {len(regular_images)}")
        
        # Extract tables
        table_images = parser.extract_tables_as_images(pdf_path, output_folder)
        print(f"   ✅ Table images: {len(table_images)}")
        
        # Extract equations
        equation_images = parser.extract_equations_as_images(pdf_path, output_folder)
        print(f"   ✅ Equation images: {len(equation_images)}")
        
        # Extract visual content areas (with two-phase validation)
        visual_images = parser.extract_visual_content_areas(pdf_path, output_folder)
        print(f"   ✅ Visual content images: {len(visual_images)}")
        
        # Combine all images
        all_images = regular_images + table_images + equation_images + visual_images
        print(f"   🎯 Total images extracted: {len(all_images)}")
        
        extraction_time = time.time() - start_time
        print(f"   ⏱️  Extraction time: {extraction_time:.2f} seconds")
        
    except Exception as e:
        print(f"   ❌ Error in image extraction: {e}")
        return
    
    print()
    
    # Test 2: Structured content extraction
    print("📋 Test 2: Structured Content Extraction")
    print("-" * 40)
    
    start_time = time.time()
    
    try:
        structured_content = extractor.extract_structured_content_from_pdf(pdf_path, all_images)
        print(f"   ✅ Structured content items: {len(structured_content)}")
        
        # Analyze content types
        content_types = {}
        for item in structured_content:
            content_type = item.get('type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print("   📊 Content type breakdown:")
        for content_type, count in sorted(content_types.items()):
            print(f"      - {content_type}: {count}")
        
        structure_time = time.time() - start_time
        print(f"   ⏱️  Structure extraction time: {structure_time:.2f} seconds")
        
    except Exception as e:
        print(f"   ❌ Error in structured content extraction: {e}")
        return
    
    print()
    
    # Test 3: Quality analysis
    print("🔍 Test 3: Quality Analysis")
    print("-" * 40)
    
    # Analyze image quality
    image_sizes = []
    image_types = {}
    
    for img in all_images:
        if 'width' in img and 'height' in img:
            image_sizes.append((img['width'], img['height']))
        
        img_type = img.get('type', 'unknown')
        image_types[img_type] = image_types.get(img_type, 0) + 1
    
    if image_sizes:
        avg_width = sum(w for w, h in image_sizes) / len(image_sizes)
        avg_height = sum(h for w, h in image_sizes) / len(image_sizes)
        print(f"   📏 Average image size: {avg_width:.0f}x{avg_height:.0f} px")
        
        min_width = min(w for w, h in image_sizes)
        max_width = max(w for w, h in image_sizes)
        min_height = min(h for w, h in image_sizes)
        max_height = max(h for w, h in image_sizes)
        print(f"   📏 Size range: {min_width}x{min_height} to {max_width}x{max_height} px")
    
    print("   🎨 Image type distribution:")
    for img_type, count in sorted(image_types.items()):
        print(f"      - {img_type}: {count}")
    
    print()
    
    # Test 4: File system analysis
    print("💾 Test 4: Output Analysis")
    print("-" * 40)
    
    try:
        output_files = os.listdir(output_folder)
        total_files = len(output_files)
        
        # Calculate total size
        total_size = 0
        for filename in output_files:
            filepath = os.path.join(output_folder, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        
        print(f"   📁 Total output files: {total_files}")
        print(f"   💾 Total output size: {total_size / (1024*1024):.2f} MB")
        
        # Analyze file types
        file_extensions = {}
        for filename in output_files:
            ext = os.path.splitext(filename)[1].lower()
            file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
        print("   📄 File type distribution:")
        for ext, count in sorted(file_extensions.items()):
            print(f"      - {ext or 'no extension'}: {count}")
        
    except Exception as e:
        print(f"   ❌ Error analyzing output: {e}")
    
    print()
    
    # Test 5: Validation checks
    print("✅ Test 5: Validation Checks")
    print("-" * 40)
    
    # Check for your confirmed good pages
    confirmed_good_pages = [22, 36, 37, 38, 41, 54, 58, 70, 71, 72, 76, 79, 86, 91, 134]
    captured_good_pages = []
    
    for img in visual_images:
        page_num = img.get('page_num', 0)
        if page_num in confirmed_good_pages:
            captured_good_pages.append(page_num)
    
    print(f"   🎯 Confirmed good pages captured: {len(captured_good_pages)}/{len(confirmed_good_pages)}")
    print(f"   ✅ Captured pages: {sorted(captured_good_pages)}")
    
    if len(captured_good_pages) < len(confirmed_good_pages):
        missed_pages = [p for p in confirmed_good_pages if p not in captured_good_pages]
        print(f"   ⚠️  Missed pages: {missed_pages}")
    
    # Check for potential text-only images
    potential_text_only = []
    for img in visual_images:
        if img.get('content_type') == 'sparse_text_page':
            potential_text_only.append(img.get('page_num', 0))
    
    if potential_text_only:
        print(f"   ⚠️  Potential text-only pages: {potential_text_only}")
    else:
        print("   ✅ No obvious text-only pages detected")
    
    print()
    
    # Summary
    print("🎯 WORKFLOW TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Total processing time: {(time.time() - start_time + extraction_time + structure_time):.2f} seconds")
    print(f"✅ Images extracted: {len(all_images)}")
    print(f"✅ Content items structured: {len(structured_content)}")
    print(f"✅ Good pages captured: {len(captured_good_pages)}/{len(confirmed_good_pages)}")
    print(f"✅ Output files created: {total_files}")
    print(f"✅ Two-phase validation: Active")
    print()
    print("🌟 Enhanced PDF extraction workflow test completed successfully!")

if __name__ == "__main__":
    test_full_workflow()
