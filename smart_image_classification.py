#!/usr/bin/env python3
"""
Smart image classification system that treats different extraction methods differently.
Regular images (_img_) are trusted, while detected areas (_visual_, _table_, _equation_) 
need more careful evaluation.
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

def classify_extraction_methods(extracted_images):
    """Classify images by extraction method and reliability"""
    classification = {
        'regular_images': [],      # _img_ - Most reliable
        'detected_tables': [],     # _table_ - Needs validation
        'detected_equations': [],  # _equation_ - Needs validation  
        'detected_visual': [],     # _visual_ - Needs validation
        'unknown': []             # Other types
    }
    
    for img in extracted_images:
        filename = img['filename']
        
        if '_img_' in filename:
            classification['regular_images'].append(img)
        elif '_table_' in filename:
            classification['detected_tables'].append(img)
        elif '_equation_' in filename:
            classification['detected_equations'].append(img)
        elif '_visual_' in filename:
            classification['detected_visual'].append(img)
        else:
            classification['unknown'].append(img)
    
    return classification

def create_smart_placeholder_system(pdf_file):
    """Create a smart placeholder system that treats extraction methods differently"""
    logger.info(f"\n🧠 SMART IMAGE CLASSIFICATION SYSTEM")
    logger.info("=" * 60)
    logger.info("Different extraction methods are treated with appropriate confidence levels")
    
    # Create folders
    extracted_images_folder = "smart_extracted_images"
    trusted_images_folder = "trusted_images"
    detected_areas_folder = "detected_areas"
    smart_info_folder = "smart_classification_info"
    
    # Clean and create folders
    for folder in [extracted_images_folder, trusted_images_folder, detected_areas_folder, smart_info_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    logger.info(f"📁 Created folders:")
    logger.info(f"   • {extracted_images_folder} - All extracted images")
    logger.info(f"   • {trusted_images_folder} - Reliable regular images")
    logger.info(f"   • {detected_areas_folder} - Detected areas (need validation)")
    logger.info(f"   • {smart_info_folder} - Classification information")
    
    # Extract all images
    parser = PDFParser()
    extracted_images = parser.extract_images_from_pdf(pdf_file, extracted_images_folder)
    
    logger.info(f"📊 Extracted {len(extracted_images)} total images")
    
    # Classify by extraction method
    classification = classify_extraction_methods(extracted_images)
    
    # Show classification results
    logger.info(f"\n🏷️ CLASSIFICATION RESULTS:")
    logger.info(f"   🖼️ Regular Images (TRUSTED): {len(classification['regular_images'])}")
    logger.info(f"   📋 Detected Tables: {len(classification['detected_tables'])}")
    logger.info(f"   🔢 Detected Equations: {len(classification['detected_equations'])}")
    logger.info(f"   📊 Detected Visual Areas: {len(classification['detected_visual'])}")
    logger.info(f"   ❓ Unknown: {len(classification['unknown'])}")
    
    # Copy trusted images to separate folder
    trusted_count = 0
    for img in classification['regular_images']:
        src_path = img['filepath']
        dst_path = os.path.join(trusted_images_folder, img['filename'])
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            trusted_count += 1
    
    # Copy detected areas to separate folder for manual review
    detected_count = 0
    for category in ['detected_tables', 'detected_equations', 'detected_visual']:
        for img in classification[category]:
            src_path = img['filepath']
            dst_path = os.path.join(detected_areas_folder, img['filename'])
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                detected_count += 1
    
    logger.info(f"📁 Organized images:")
    logger.info(f"   ✅ {trusted_count} trusted images → {trusted_images_folder}")
    logger.info(f"   🔍 {detected_count} detected areas → {detected_areas_folder}")
    
    # Create smart recommendations
    smart_recommendations = create_smart_recommendations(classification)
    
    # Save classification data
    save_smart_classification(classification, smart_recommendations, smart_info_folder)
    
    # Create usage guide
    create_smart_usage_guide(classification, smart_recommendations, smart_info_folder)
    
    return classification, smart_recommendations

def create_smart_recommendations(classification):
    """Create smart recommendations based on extraction method reliability"""
    recommendations = {
        'auto_include': [],      # Definitely include (regular images)
        'manual_review': [],     # Review manually (detected areas)
        'likely_include': [],    # Probably good (large detected areas)
        'likely_exclude': []     # Probably not needed (small detected areas)
    }
    
    # Regular images - auto include (they're real images in the PDF)
    for img in classification['regular_images']:
        file_size = get_file_size_bytes(img['filepath'])
        recommendations['auto_include'].append({
            'image': img,
            'reason': 'Real embedded image in PDF',
            'confidence': 'HIGH',
            'size': file_size,
            'action': 'INCLUDE'
        })
    
    # Detected areas - need more careful evaluation
    for category, category_name in [
        ('detected_tables', 'Table'),
        ('detected_equations', 'Equation'), 
        ('detected_visual', 'Visual Content')
    ]:
        for img in classification[category]:
            file_size = get_file_size_bytes(img['filepath'])
            
            # Smart classification based on size and type
            if category == 'detected_visual':
                # Visual content - usually important if substantial
                if file_size > 80000:  # > 80KB
                    recommendations['likely_include'].append({
                        'image': img,
                        'reason': f'Large {category_name.lower()} area - likely contains diagrams',
                        'confidence': 'MEDIUM-HIGH',
                        'size': file_size,
                        'action': 'REVIEW_INCLUDE'
                    })
                else:
                    recommendations['manual_review'].append({
                        'image': img,
                        'reason': f'Small {category_name.lower()} area - verify content',
                        'confidence': 'MEDIUM',
                        'size': file_size,
                        'action': 'REVIEW'
                    })
            
            elif category == 'detected_tables':
                # Tables - important if they have substantial data
                if file_size > 40000:  # > 40KB
                    recommendations['likely_include'].append({
                        'image': img,
                        'reason': f'Large {category_name.lower()} - likely contains important data',
                        'confidence': 'MEDIUM-HIGH',
                        'size': file_size,
                        'action': 'REVIEW_INCLUDE'
                    })
                else:
                    recommendations['manual_review'].append({
                        'image': img,
                        'reason': f'Small {category_name.lower()} - verify if substantial',
                        'confidence': 'MEDIUM',
                        'size': file_size,
                        'action': 'REVIEW'
                    })
            
            elif category == 'detected_equations':
                # Equations - complex ones are worth including
                if file_size > 30000:  # > 30KB
                    recommendations['likely_include'].append({
                        'image': img,
                        'reason': f'Complex {category_name.lower()} - likely important',
                        'confidence': 'MEDIUM',
                        'size': file_size,
                        'action': 'REVIEW_INCLUDE'
                    })
                else:
                    recommendations['likely_exclude'].append({
                        'image': img,
                        'reason': f'Simple {category_name.lower()} - can be recreated as text',
                        'confidence': 'MEDIUM',
                        'size': file_size,
                        'action': 'REVIEW_EXCLUDE'
                    })
    
    return recommendations

def save_smart_classification(classification, recommendations, info_folder):
    """Save smart classification data"""
    # Save full classification data
    classification_file = os.path.join(info_folder, "smart_classification.json")
    
    # Convert to serializable format
    serializable_data = {
        'classification': {},
        'recommendations': recommendations,
        'summary': {
            'total_images': sum(len(images) for images in classification.values()),
            'by_method': {method: len(images) for method, images in classification.items()},
            'by_recommendation': {rec_type: len(recs) for rec_type, recs in recommendations.items()}
        }
    }
    
    # Convert image objects to serializable format
    for method, images in classification.items():
        serializable_data['classification'][method] = []
        for img in images:
            img_data = dict(img)  # Copy the image data
            img_data['file_size'] = get_file_size_bytes(img['filepath'])
            img_data['file_size_formatted'] = format_file_size(img_data['file_size'])
            serializable_data['classification'][method].append(img_data)
    
    with open(classification_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Saved smart classification: {classification_file}")

def create_smart_usage_guide(classification, recommendations, info_folder):
    """Create a smart usage guide"""
    guide_file = os.path.join(info_folder, "smart_usage_guide.md")
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write("# SMART IMAGE CLASSIFICATION GUIDE\n\n")
        f.write("This system intelligently classifies images based on their extraction method and reliability.\n\n")
        
        # Summary
        f.write("## EXTRACTION METHOD ANALYSIS\n\n")
        f.write("### 🖼️ Regular Images (MOST RELIABLE)\n")
        f.write("These are **real images embedded in the PDF**. They should almost always be included.\n\n")
        
        regular_images = classification['regular_images']
        if regular_images:
            f.write(f"**Found {len(regular_images)} regular images:**\n")
            for img in regular_images:
                size = format_file_size(get_file_size_bytes(img['filepath']))
                f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size}) ✅ **AUTO-INCLUDE**\n")
        else:
            f.write("*No regular images found.*\n")
        f.write("\n")
        
        # Detected areas
        f.write("### 📊 Detected Areas (NEED VALIDATION)\n")
        f.write("These are areas detected by algorithms. They need manual review.\n\n")
        
        for category, title, emoji in [
            ('detected_visual', 'Visual Content Areas', '📊'),
            ('detected_tables', 'Table Areas', '📋'),
            ('detected_equations', 'Equation Areas', '🔢')
        ]:
            detected_items = classification[category]
            f.write(f"#### {emoji} {title}\n")
            if detected_items:
                f.write(f"Found {len(detected_items)} detected areas:\n")
                for img in detected_items:
                    size = format_file_size(get_file_size_bytes(img['filepath']))
                    f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
            else:
                f.write("*No areas detected.*\n")
            f.write("\n")
        
        # Smart recommendations
        f.write("## SMART RECOMMENDATIONS\n\n")
        
        f.write("### ✅ AUTO-INCLUDE (Trusted)\n")
        auto_include = recommendations['auto_include']
        f.write(f"**{len(auto_include)} images** - These are real embedded images and should be included.\n\n")
        for rec in auto_include:
            img = rec['image']
            size = format_file_size(rec['size'])
            f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
            f.write(f"  - Reason: {rec['reason']}\n")
        f.write("\n")
        
        f.write("### 🟢 LIKELY INCLUDE (Review Recommended)\n")
        likely_include = recommendations['likely_include']
        f.write(f"**{len(likely_include)} images** - Large detected areas that likely contain important content.\n\n")
        for rec in likely_include:
            img = rec['image']
            size = format_file_size(rec['size'])
            f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
            f.write(f"  - Reason: {rec['reason']}\n")
        f.write("\n")
        
        f.write("### 🟡 MANUAL REVIEW (Check Content)\n")
        manual_review = recommendations['manual_review']
        f.write(f"**{len(manual_review)} images** - Medium-sized areas that need manual verification.\n\n")
        for rec in manual_review:
            img = rec['image']
            size = format_file_size(rec['size'])
            f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
            f.write(f"  - Reason: {rec['reason']}\n")
        f.write("\n")
        
        f.write("### 🔴 LIKELY EXCLUDE (Optional)\n")
        likely_exclude = recommendations['likely_exclude']
        f.write(f"**{len(likely_exclude)} images** - Small areas that can probably be omitted.\n\n")
        for rec in likely_exclude:
            img = rec['image']
            size = format_file_size(rec['size'])
            f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
            f.write(f"  - Reason: {rec['reason']}\n")
        f.write("\n")
        
        # Usage workflow
        f.write("## RECOMMENDED WORKFLOW\n\n")
        f.write("1. **Auto-Include**: Use all regular images (they're real embedded images)\n")
        f.write("2. **Review Likely Include**: Check these larger detected areas - probably good\n")
        f.write("3. **Manual Review**: Look at medium-sized areas to decide\n")
        f.write("4. **Skip Likely Exclude**: These are usually simple equations or small tables\n\n")
        
        f.write("## FOLDER ORGANIZATION\n\n")
        f.write("- **`trusted_images/`**: Regular images that should definitely be included\n")
        f.write("- **`detected_areas/`**: All detected areas for manual review\n")
        f.write("- **`smart_extracted_images/`**: All extracted images together\n\n")
        
        f.write("## KEY INSIGHT\n\n")
        f.write("**Regular images (`_img_`) are REAL images in the PDF** - they should almost always be included.\n")
        f.write("**Detected areas (`_visual_`, `_table_`, `_equation_`) are GUESSED areas** - they need validation.\n")
    
    logger.info(f"📋 Created smart usage guide: {guide_file}")

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
    """Run the smart image classification system"""
    logger.info("🧠 SMART IMAGE CLASSIFICATION SYSTEM")
    logger.info("=" * 70)
    logger.info("This system treats different extraction methods with appropriate confidence levels")
    
    try:
        # Find PDF file
        pdf_file = find_pdf_file()
        if not pdf_file:
            return
        
        # Create smart classification system
        classification, recommendations = create_smart_placeholder_system(pdf_file)
        
        # Show summary
        logger.info(f"\n📊 SMART CLASSIFICATION COMPLETE!")
        logger.info(f"   🖼️ Regular Images (TRUSTED): {len(classification['regular_images'])}")
        logger.info(f"   📊 Detected Areas (REVIEW): {len(classification['detected_visual']) + len(classification['detected_tables']) + len(classification['detected_equations'])}")
        
        logger.info(f"\n🎯 RECOMMENDATIONS:")
        logger.info(f"   ✅ Auto-Include: {len(recommendations['auto_include'])}")
        logger.info(f"   🟢 Likely Include: {len(recommendations['likely_include'])}")
        logger.info(f"   🟡 Manual Review: {len(recommendations['manual_review'])}")
        logger.info(f"   🔴 Likely Exclude: {len(recommendations['likely_exclude'])}")
        
        logger.info(f"\n📁 CHECK THESE FOLDERS:")
        logger.info(f"   • trusted_images/ - Regular images (definitely include)")
        logger.info(f"   • detected_areas/ - Detected areas (review manually)")
        logger.info(f"   • smart_classification_info/ - Detailed guides and data")
        
        logger.info(f"\n💡 KEY INSIGHT:")
        logger.info(f"   Regular images (_img_) are REAL embedded images - very reliable")
        logger.info(f"   Detected areas (_visual_, _table_, _equation_) are GUESSED - need validation")
        
    except Exception as e:
        logger.error(f"❌ Smart classification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
