#!/usr/bin/env python3
"""
Clean extraction test without equation detection.
This tests the system with equation extraction disabled to reduce false positives.
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

def test_clean_extraction(pdf_file):
    """Test extraction with equations disabled"""
    logger.info(f"\n🧹 CLEAN EXTRACTION TEST (NO EQUATIONS)")
    logger.info("=" * 60)
    logger.info("Testing extraction with equation detection disabled")
    
    # Create clean output folder
    clean_output_folder = "clean_extraction_output"
    clean_trusted_folder = "clean_trusted_images"
    clean_detected_folder = "clean_detected_areas"
    clean_info_folder = "clean_extraction_info"
    
    # Clean and create folders
    for folder in [clean_output_folder, clean_trusted_folder, clean_detected_folder, clean_info_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    logger.info(f"📁 Created clean extraction folders")
    
    # Check current settings
    settings = config_manager.pdf_processing_settings
    logger.info(f"⚙️ Current settings:")
    logger.info(f"   Extract images: {settings.get('extract_images', False)}")
    logger.info(f"   Extract tables: {settings.get('extract_tables_as_images', False)}")
    logger.info(f"   Extract equations: {settings.get('extract_equations_as_images', False)}")
    logger.info(f"   Extract figures: {settings.get('extract_figures_by_caption', False)}")
    
    # Extract images with clean settings
    parser = PDFParser()
    extracted_images = parser.extract_images_from_pdf(pdf_file, clean_output_folder)
    
    logger.info(f"📊 Clean extraction results: {len(extracted_images)} total images")
    
    # Classify by extraction method
    classification = classify_extraction_methods(extracted_images)
    
    # Show clean classification results
    logger.info(f"\n🏷️ CLEAN CLASSIFICATION RESULTS:")
    logger.info(f"   🖼️ Regular Images (TRUSTED): {len(classification['regular_images'])}")
    logger.info(f"   📋 Detected Tables: {len(classification['detected_tables'])}")
    logger.info(f"   🔢 Detected Equations: {len(classification['detected_equations'])}")
    logger.info(f"   📊 Detected Visual Areas: {len(classification['detected_visual'])}")
    logger.info(f"   ❓ Unknown: {len(classification['unknown'])}")
    
    # Copy trusted images
    trusted_count = 0
    for img in classification['regular_images']:
        src_path = img['filepath']
        dst_path = os.path.join(clean_trusted_folder, img['filename'])
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            trusted_count += 1
    
    # Copy detected areas (should be much fewer now)
    detected_count = 0
    for category in ['detected_tables', 'detected_equations', 'detected_visual']:
        for img in classification[category]:
            src_path = img['filepath']
            dst_path = os.path.join(clean_detected_folder, img['filename'])
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                detected_count += 1
    
    logger.info(f"📁 Organized clean images:")
    logger.info(f"   ✅ {trusted_count} trusted images → {clean_trusted_folder}")
    logger.info(f"   🔍 {detected_count} detected areas → {clean_detected_folder}")
    
    # Create clean recommendations
    clean_recommendations = create_clean_recommendations(classification)
    
    # Save clean analysis
    save_clean_analysis(classification, clean_recommendations, clean_info_folder)
    
    return classification, clean_recommendations

def classify_extraction_methods(extracted_images):
    """Classify images by extraction method"""
    classification = {
        'regular_images': [],      # _img_ - Most reliable
        'detected_tables': [],     # _table_ - Needs validation
        'detected_equations': [],  # _equation_ - Should be very few now
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

def create_clean_recommendations(classification):
    """Create recommendations for clean extraction"""
    recommendations = {
        'definite_include': [],    # Regular images - definitely include
        'review_include': [],      # Large detected areas - probably include
        'review_optional': [],     # Medium detected areas - optional
        'skip': []                # Small or problematic areas - skip
    }
    
    # Regular images - always include
    for img in classification['regular_images']:
        file_size = get_file_size_bytes(img['filepath'])
        recommendations['definite_include'].append({
            'image': img,
            'reason': 'Real embedded image in PDF',
            'confidence': 'VERY HIGH',
            'size': file_size,
            'action': 'INCLUDE'
        })
    
    # Visual content - usually good if substantial
    for img in classification['detected_visual']:
        file_size = get_file_size_bytes(img['filepath'])
        
        if file_size > 100000:  # > 100KB
            recommendations['review_include'].append({
                'image': img,
                'reason': 'Large visual content area - likely contains diagrams',
                'confidence': 'HIGH',
                'size': file_size,
                'action': 'REVIEW_INCLUDE'
            })
        elif file_size > 50000:  # 50-100KB
            recommendations['review_optional'].append({
                'image': img,
                'reason': 'Medium visual content area - check content',
                'confidence': 'MEDIUM',
                'size': file_size,
                'action': 'REVIEW'
            })
        else:
            recommendations['skip'].append({
                'image': img,
                'reason': 'Small visual area - likely text-only',
                'confidence': 'LOW',
                'size': file_size,
                'action': 'SKIP'
            })
    
    # Tables - important if they contain substantial data
    for img in classification['detected_tables']:
        file_size = get_file_size_bytes(img['filepath'])
        
        if file_size > 60000:  # > 60KB
            recommendations['review_include'].append({
                'image': img,
                'reason': 'Large table - likely contains important data',
                'confidence': 'HIGH',
                'size': file_size,
                'action': 'REVIEW_INCLUDE'
            })
        elif file_size > 30000:  # 30-60KB
            recommendations['review_optional'].append({
                'image': img,
                'reason': 'Medium table - verify data importance',
                'confidence': 'MEDIUM',
                'size': file_size,
                'action': 'REVIEW'
            })
        else:
            recommendations['skip'].append({
                'image': img,
                'reason': 'Small table - likely simple or header-only',
                'confidence': 'LOW',
                'size': file_size,
                'action': 'SKIP'
            })
    
    # Equations - should be very few now, but if any exist, be very strict
    for img in classification['detected_equations']:
        file_size = get_file_size_bytes(img['filepath'])
        
        if file_size > 80000:  # > 80KB - very large equation
            recommendations['review_optional'].append({
                'image': img,
                'reason': 'Very large equation area - might be complex formula',
                'confidence': 'MEDIUM',
                'size': file_size,
                'action': 'REVIEW'
            })
        else:
            recommendations['skip'].append({
                'image': img,
                'reason': 'Equation detection - likely false positive',
                'confidence': 'VERY LOW',
                'size': file_size,
                'action': 'SKIP'
            })
    
    return recommendations

def save_clean_analysis(classification, recommendations, info_folder):
    """Save clean analysis results"""
    analysis_file = os.path.join(info_folder, "clean_extraction_analysis.md")
    
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write("# CLEAN EXTRACTION ANALYSIS\n\n")
        f.write("This analysis shows results with equation detection disabled to reduce false positives.\n\n")
        
        # Summary
        total_images = sum(len(images) for images in classification.values())
        f.write(f"## SUMMARY\n\n")
        f.write(f"- **Total images extracted**: {total_images}\n")
        f.write(f"- **Regular images (trusted)**: {len(classification['regular_images'])}\n")
        f.write(f"- **Detected tables**: {len(classification['detected_tables'])}\n")
        f.write(f"- **Detected visual areas**: {len(classification['detected_visual'])}\n")
        f.write(f"- **Detected equations**: {len(classification['detected_equations'])} (should be 0 or very few)\n\n")
        
        # Recommendations summary
        f.write(f"## RECOMMENDATIONS SUMMARY\n\n")
        f.write(f"- **✅ Definite Include**: {len(recommendations['definite_include'])} images\n")
        f.write(f"- **🟢 Review Include**: {len(recommendations['review_include'])} images\n")
        f.write(f"- **🟡 Review Optional**: {len(recommendations['review_optional'])} images\n")
        f.write(f"- **🔴 Skip**: {len(recommendations['skip'])} images\n\n")
        
        # Detailed recommendations
        f.write(f"## DETAILED RECOMMENDATIONS\n\n")
        
        for rec_type, title, emoji in [
            ('definite_include', 'Definite Include', '✅'),
            ('review_include', 'Review Include', '🟢'),
            ('review_optional', 'Review Optional', '🟡'),
            ('skip', 'Skip', '🔴')
        ]:
            recs = recommendations[rec_type]
            f.write(f"### {emoji} {title} ({len(recs)} images)\n\n")
            
            if recs:
                for rec in recs:
                    img = rec['image']
                    size = format_file_size(rec['size'])
                    f.write(f"- **Page {img['page_num']}**: `{img['filename']}` ({size})\n")
                    f.write(f"  - Reason: {rec['reason']}\n")
                    f.write(f"  - Confidence: {rec['confidence']}\n")
                    f.write(f"  - Action: {rec['action']}\n\n")
            else:
                f.write("*No images in this category.*\n\n")
        
        # Benefits of clean extraction
        f.write(f"## BENEFITS OF CLEAN EXTRACTION\n\n")
        f.write(f"- **Fewer false positives**: No equation detection means less text misidentified as images\n")
        f.write(f"- **Cleaner workflow**: Focus on real images and substantial tables/visual content\n")
        f.write(f"- **Better quality**: Higher confidence in included images\n")
        f.write(f"- **Easier decisions**: Fewer marginal cases to review\n\n")
        
        # Recommended final selection
        definite = len(recommendations['definite_include'])
        review_include = len(recommendations['review_include'])
        review_optional = len(recommendations['review_optional'])
        
        f.write(f"## RECOMMENDED FINAL SELECTION\n\n")
        f.write(f"**Conservative approach**: {definite} + {review_include} = {definite + review_include} images\n")
        f.write(f"**Moderate approach**: {definite} + {review_include} + {review_optional//2} ≈ {definite + review_include + review_optional//2} images\n")
        f.write(f"**Liberal approach**: {definite} + {review_include} + {review_optional} = {definite + review_include + review_optional} images\n\n")
        
        f.write(f"**Recommended**: Start with conservative approach and add images as needed.\n")
    
    logger.info(f"📋 Saved clean analysis: {analysis_file}")

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

def compare_with_previous_results():
    """Compare clean extraction with previous results"""
    logger.info(f"\n📊 COMPARISON WITH PREVIOUS RESULTS")
    logger.info("=" * 50)
    
    # Check if previous results exist
    previous_folders = [
        "smart_extracted_images",
        "comprehensive_test_output", 
        "final_pdf_images"
    ]
    
    for folder in previous_folders:
        if os.path.exists(folder):
            previous_count = len([f for f in os.listdir(folder) if f.endswith('.png')])
            logger.info(f"   {folder}: {previous_count} images")
    
    # Current clean results
    if os.path.exists("clean_extraction_output"):
        clean_count = len([f for f in os.listdir("clean_extraction_output") if f.endswith('.png')])
        logger.info(f"   clean_extraction_output: {clean_count} images")
        
        # Show reduction
        if os.path.exists("smart_extracted_images"):
            smart_count = len([f for f in os.listdir("smart_extracted_images") if f.endswith('.png')])
            reduction = smart_count - clean_count
            percentage = (reduction / smart_count) * 100 if smart_count > 0 else 0
            logger.info(f"   📉 Reduction: {reduction} images ({percentage:.1f}% fewer)")

def main():
    """Run the clean extraction test"""
    logger.info("🧹 CLEAN EXTRACTION TEST (NO EQUATIONS)")
    logger.info("=" * 70)
    logger.info("Testing extraction with equation detection disabled to reduce false positives")
    
    try:
        # Find PDF file
        pdf_file = find_pdf_file()
        if not pdf_file:
            return
        
        # Test clean extraction
        classification, recommendations = test_clean_extraction(pdf_file)
        
        # Compare with previous results
        compare_with_previous_results()
        
        # Show final summary
        logger.info(f"\n🎉 CLEAN EXTRACTION TEST COMPLETED!")
        
        total_images = sum(len(images) for images in classification.values())
        definite = len(recommendations['definite_include'])
        review_include = len(recommendations['review_include'])
        review_optional = len(recommendations['review_optional'])
        skip = len(recommendations['skip'])
        
        logger.info(f"📊 Results:")
        logger.info(f"   Total extracted: {total_images}")
        logger.info(f"   ✅ Definite include: {definite}")
        logger.info(f"   🟢 Review include: {review_include}")
        logger.info(f"   🟡 Review optional: {review_optional}")
        logger.info(f"   🔴 Skip: {skip}")
        
        recommended_count = definite + review_include
        logger.info(f"\n🎯 RECOMMENDED FINAL COUNT: {recommended_count} images")
        logger.info(f"   (Conservative approach: definite + review include)")
        
        logger.info(f"\n📁 CHECK FOLDERS:")
        logger.info(f"   • clean_trusted_images/ - Regular images (definitely include)")
        logger.info(f"   • clean_detected_areas/ - Detected areas (much cleaner now)")
        logger.info(f"   • clean_extraction_info/ - Analysis and recommendations")
        
    except Exception as e:
        logger.error(f"❌ Clean extraction test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
