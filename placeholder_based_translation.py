#!/usr/bin/env python3
"""
Placeholder-based translation system.
Instead of embedding all images, this creates placeholders in the text
that can be manually replaced with selected images.
"""

import os
import sys
import logging
import shutil
import json
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

def create_placeholder_system(pdf_file):
    """Create a placeholder-based system for image management"""
    logger.info(f"\n🎯 CREATING PLACEHOLDER-BASED TRANSLATION SYSTEM")
    logger.info("=" * 60)
    
    # Create folders
    extracted_images_folder = "extracted_images_all"
    placeholder_info_folder = "placeholder_info"
    
    # Clean and create folders
    for folder in [extracted_images_folder, placeholder_info_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    logger.info(f"📁 Created folders:")
    logger.info(f"   • {extracted_images_folder} - All extracted images")
    logger.info(f"   • {placeholder_info_folder} - Placeholder information")
    
    # Extract all images
    parser = PDFParser()
    extracted_images = parser.extract_images_from_pdf(pdf_file, extracted_images_folder)
    
    logger.info(f"📊 Extracted {len(extracted_images)} total images")
    
    # Group images by page
    images_by_page = {}
    for img in extracted_images:
        page_num = img['page_num']
        if page_num not in images_by_page:
            images_by_page[page_num] = []
        images_by_page[page_num].append(img)
    
    # Create placeholder information
    placeholder_data = create_placeholder_data(images_by_page)
    
    # Save placeholder information
    save_placeholder_info(placeholder_data, placeholder_info_folder)
    
    # Create placeholder text file
    create_placeholder_text_file(placeholder_data, placeholder_info_folder)
    
    # Create image selection guide
    create_image_selection_guide(placeholder_data, placeholder_info_folder)
    
    return placeholder_data, extracted_images_folder, placeholder_info_folder

def create_placeholder_data(images_by_page):
    """Create structured data for placeholders"""
    placeholder_data = {
        'pages': {},
        'summary': {
            'total_pages_with_images': len(images_by_page),
            'total_images': sum(len(images) for images in images_by_page.values()),
            'by_type': {}
        }
    }
    
    type_counts = {}
    
    for page_num in sorted(images_by_page.keys()):
        page_images = images_by_page[page_num]
        
        page_data = {
            'page_number': page_num,
            'image_count': len(page_images),
            'images': []
        }
        
        for i, img in enumerate(page_images, 1):
            img_type = get_image_type(img['filename'])
            file_size = get_file_size_bytes(img['filepath'])
            
            # Count by type
            if img_type not in type_counts:
                type_counts[img_type] = 0
            type_counts[img_type] += 1
            
            # Create placeholder ID
            placeholder_id = f"PAGE_{page_num}_IMG_{i}"
            
            image_data = {
                'placeholder_id': placeholder_id,
                'filename': img['filename'],
                'type': img_type,
                'size_bytes': file_size,
                'size_formatted': format_file_size(file_size),
                'confidence': img.get('confidence', 'N/A'),
                'content_type': img.get('content_type', 'unknown'),
                'recommended_include': recommend_inclusion(img_type, file_size),
                'placeholder_text': f"[IMAGE_PLACEHOLDER_{placeholder_id}]"
            }
            
            page_data['images'].append(image_data)
        
        placeholder_data['pages'][page_num] = page_data
    
    placeholder_data['summary']['by_type'] = type_counts
    
    return placeholder_data

def recommend_inclusion(img_type, file_size):
    """Recommend whether to include this image based on type and size"""
    if img_type == 'Visual Content':
        return "HIGH" if file_size > 50000 else "MEDIUM"
    elif img_type == 'Table':
        return "HIGH" if file_size > 30000 else "MEDIUM"
    elif img_type == 'Equation':
        return "MEDIUM" if file_size > 20000 else "LOW"
    elif img_type == 'Regular Image':
        return "HIGH" if file_size > 200000 else "MEDIUM"
    else:
        return "LOW"

def save_placeholder_info(placeholder_data, info_folder):
    """Save placeholder information as JSON"""
    json_file = os.path.join(info_folder, "placeholder_data.json")
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(placeholder_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Saved placeholder data: {json_file}")

def create_placeholder_text_file(placeholder_data, info_folder):
    """Create a text file showing all placeholders for translation"""
    text_file = os.path.join(info_folder, "translation_placeholders.txt")
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("# TRANSLATION PLACEHOLDERS\n")
        f.write("# Use these placeholders in your translated text where images should appear\n")
        f.write("# After translation, you can manually select which images to include\n\n")
        
        for page_num in sorted(placeholder_data['pages'].keys()):
            page_data = placeholder_data['pages'][page_num]
            
            f.write(f"## PAGE {page_num} ({page_data['image_count']} images)\n\n")
            
            for img_data in page_data['images']:
                f.write(f"**{img_data['placeholder_text']}**\n")
                f.write(f"   Type: {img_data['type']}\n")
                f.write(f"   Size: {img_data['size_formatted']}\n")
                f.write(f"   File: {img_data['filename']}\n")
                f.write(f"   Recommendation: {img_data['recommended_include']}\n")
                f.write(f"   Description: {get_image_description(img_data)}\n\n")
            
            f.write("---\n\n")
    
    logger.info(f"📝 Created placeholder text file: {text_file}")

def create_image_selection_guide(placeholder_data, info_folder):
    """Create a guide for manually selecting images"""
    guide_file = os.path.join(info_folder, "image_selection_guide.md")
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write("# IMAGE SELECTION GUIDE\n\n")
        f.write("This guide helps you manually select which images to include in the final PDF.\n\n")
        
        # Summary
        f.write("## SUMMARY\n\n")
        summary = placeholder_data['summary']
        f.write(f"- **Total pages with images**: {summary['total_pages_with_images']}\n")
        f.write(f"- **Total images extracted**: {summary['total_images']}\n\n")
        
        f.write("### By Type:\n")
        for img_type, count in summary['by_type'].items():
            f.write(f"- **{img_type}**: {count} images\n")
        f.write("\n")
        
        # Recommendations by priority
        f.write("## RECOMMENDATIONS BY PRIORITY\n\n")
        
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for page_num in sorted(placeholder_data['pages'].keys()):
            page_data = placeholder_data['pages'][page_num]
            for img_data in page_data['images']:
                if img_data['recommended_include'] == 'HIGH':
                    high_priority.append((page_num, img_data))
                elif img_data['recommended_include'] == 'MEDIUM':
                    medium_priority.append((page_num, img_data))
                else:
                    low_priority.append((page_num, img_data))
        
        f.write(f"### 🔴 HIGH PRIORITY ({len(high_priority)} images)\n")
        f.write("**Strongly recommended to include**\n\n")
        for page_num, img_data in high_priority:
            f.write(f"- **Page {page_num}**: `{img_data['filename']}` ({img_data['type']}, {img_data['size_formatted']})\n")
            f.write(f"  - Placeholder: `{img_data['placeholder_text']}`\n")
        f.write("\n")
        
        f.write(f"### 🟡 MEDIUM PRIORITY ({len(medium_priority)} images)\n")
        f.write("**Consider including based on content importance**\n\n")
        for page_num, img_data in medium_priority:
            f.write(f"- **Page {page_num}**: `{img_data['filename']}` ({img_data['type']}, {img_data['size_formatted']})\n")
            f.write(f"  - Placeholder: `{img_data['placeholder_text']}`\n")
        f.write("\n")
        
        f.write(f"### ⚪ LOW PRIORITY ({len(low_priority)} images)\n")
        f.write("**Optional - can be omitted to reduce file size**\n\n")
        for page_num, img_data in low_priority:
            f.write(f"- **Page {page_num}**: `{img_data['filename']}` ({img_data['type']}, {img_data['size_formatted']})\n")
            f.write(f"  - Placeholder: `{img_data['placeholder_text']}`\n")
        f.write("\n")
        
        # Usage instructions
        f.write("## HOW TO USE\n\n")
        f.write("1. **During Translation**: Use the placeholders from `translation_placeholders.txt` in your translated text\n")
        f.write("2. **After Translation**: Review this guide and select which images to include\n")
        f.write("3. **Final PDF**: Replace selected placeholders with actual images, leave others as text indicators\n\n")
        
        f.write("### Example Workflow:\n")
        f.write("```\n")
        f.write("Original: [IMAGE_PLACEHOLDER_PAGE_22_IMG_1] shows the data distribution.\n")
        f.write("If including: <insert page_22_visual_visual_1.png here>\n")
        f.write("If not including: [Figure 22.1 - Data distribution diagram - see original PDF]\n")
        f.write("```\n\n")
        
        f.write("## BENEFITS OF THIS APPROACH\n\n")
        f.write("- ✅ **Full control** over which images to include\n")
        f.write("- ✅ **Reduced file size** by excluding unnecessary images\n")
        f.write("- ✅ **Clear indicators** where images should be in the text\n")
        f.write("- ✅ **Manual quality control** - you decide what's important\n")
        f.write("- ✅ **Flexible workflow** - can change decisions later\n")
    
    logger.info(f"📋 Created image selection guide: {guide_file}")

def get_image_description(img_data):
    """Get a description of what the image likely contains"""
    img_type = img_data['type']
    size = img_data['size_bytes']
    
    if img_type == 'Visual Content':
        if size > 100000:
            return "Large diagram or figure with detailed visual content"
        else:
            return "Diagram or figure with visual elements"
    elif img_type == 'Table':
        if size > 50000:
            return "Large data table with multiple rows/columns"
        else:
            return "Simple data table"
    elif img_type == 'Equation':
        if size > 30000:
            return "Complex mathematical equation or formula"
        else:
            return "Simple mathematical expression"
    elif img_type == 'Regular Image':
        if size > 500000:
            return "High-resolution photograph or detailed image"
        else:
            return "Standard image or photograph"
    else:
        return "Unknown content type"

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

def main():
    """Run the placeholder-based translation system"""
    logger.info("🎯 PLACEHOLDER-BASED TRANSLATION SYSTEM")
    logger.info("=" * 70)
    logger.info("This system extracts all images but uses placeholders instead of embedding them")
    logger.info("You can manually select which images to include in the final PDF")
    
    try:
        # Find PDF file
        pdf_file = find_pdf_file()
        if not pdf_file:
            return
        
        # Create placeholder system
        placeholder_data, images_folder, info_folder = create_placeholder_system(pdf_file)
        
        # Show summary
        summary = placeholder_data['summary']
        logger.info(f"\n📊 SYSTEM CREATED SUCCESSFULLY!")
        logger.info(f"   📁 All images extracted to: {images_folder}")
        logger.info(f"   📋 Placeholder info in: {info_folder}")
        logger.info(f"   🖼️ Total images: {summary['total_images']}")
        logger.info(f"   📄 Pages with images: {summary['total_pages_with_images']}")
        
        logger.info(f"\n📝 NEXT STEPS:")
        logger.info(f"   1. Check '{info_folder}/translation_placeholders.txt' for placeholders to use during translation")
        logger.info(f"   2. Review '{info_folder}/image_selection_guide.md' for recommendations")
        logger.info(f"   3. After translation, manually select which images to include")
        logger.info(f"   4. Replace placeholders with selected images or descriptive text")
        
        logger.info(f"\n✅ BENEFITS:")
        logger.info(f"   • Full control over image inclusion")
        logger.info(f"   • Reduced final PDF size")
        logger.info(f"   • Clear workflow for manual selection")
        logger.info(f"   • No risk of including unnecessary images")
        
    except Exception as e:
        logger.error(f"❌ System creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
