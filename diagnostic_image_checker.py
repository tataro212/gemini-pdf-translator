"""
Diagnostic Image Checker for PDF Translation Pipeline

This script helps diagnose image-related issues in the translation pipeline.
"""

import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_image_issues(output_directory):
    """
    Comprehensive diagnosis of image-related issues in the translation output.
    
    Args:
        output_directory: The output directory from a recent translation
    """
    logger.info(f"🔍 Starting image diagnosis for: {output_directory}")
    
    if not os.path.exists(output_directory):
        logger.error(f"❌ Output directory not found: {output_directory}")
        return
    
    # Check for image folders
    image_folders = []
    for item in os.listdir(output_directory):
        item_path = os.path.join(output_directory, item)
        if os.path.isdir(item_path) and 'image' in item.lower():
            image_folders.append(item_path)
    
    logger.info(f"📁 Found {len(image_folders)} image folders:")
    for folder in image_folders:
        logger.info(f"   - {folder}")
    
    # Analyze each image folder
    total_images = 0
    for folder in image_folders:
        images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        total_images += len(images)
        logger.info(f"📸 {folder}: {len(images)} images")
        
        # Show first few images for debugging
        for i, img in enumerate(images[:3]):
            img_path = os.path.join(folder, img)
            size = os.path.getsize(img_path)
            logger.info(f"   {i+1}. {img} ({size:,} bytes)")
    
    # Check Word document
    word_files = [f for f in os.listdir(output_directory) if f.endswith('.docx')]
    if word_files:
        logger.info(f"📄 Found Word documents: {word_files}")
        # Could add docx inspection here
    else:
        logger.warning("⚠️ No Word documents found")
    
    # Check PDF document
    pdf_files = [f for f in os.listdir(output_directory) if f.endswith('.pdf')]
    if pdf_files:
        logger.info(f"📑 Found PDF documents: {pdf_files}")
    else:
        logger.warning("⚠️ No PDF documents found")
    
    # Generate summary
    logger.info(f"\n📊 DIAGNOSIS SUMMARY:")
    logger.info(f"   Total image folders: {len(image_folders)}")
    logger.info(f"   Total images extracted: {total_images}")
    logger.info(f"   Word documents: {len(word_files)}")
    logger.info(f"   PDF documents: {len(pdf_files)}")
    
    # Recommendations
    logger.info(f"\n💡 RECOMMENDATIONS:")
    if total_images == 0:
        logger.info("   - No images found. Check if PDF contains images.")
        logger.info("   - Verify image extraction is working in pdf_parser.py")
    elif total_images > 0 and not word_files:
        logger.info("   - Images extracted but no Word document. Check document generation.")
    elif total_images > 0 and word_files:
        logger.info("   - Images and documents found. Check image path resolution in document_generator.py")
        logger.info("   - Enable debug logging to see image processing details")
    
    return {
        'image_folders': len(image_folders),
        'total_images': total_images,
        'word_files': len(word_files),
        'pdf_files': len(pdf_files)
    }

def check_recent_translation():
    """Check the most recent translation output for image issues."""
    # Common output directories
    possible_dirs = [
        r"C:\Users\30694\Downloads\words-to-fire-press-betrayal",
        r"C:\Users\30694\Downloads\sickdays",
        r"C:\Users\30694\Downloads"
    ]
    
    recent_dirs = []
    for base_dir in possible_dirs:
        if os.path.exists(base_dir):
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    # Check if it looks like a translation output
                    contents = os.listdir(item_path)
                    if any(f.endswith('.docx') for f in contents):
                        recent_dirs.append(item_path)
    
    if not recent_dirs:
        logger.warning("⚠️ No recent translation directories found")
        logger.info("💡 Please provide the path to your most recent translation output")
        return
    
    # Sort by modification time and check the most recent
    recent_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    most_recent = recent_dirs[0]
    
    logger.info(f"🎯 Checking most recent translation: {most_recent}")
    return diagnose_image_issues(most_recent)

def suggest_fixes(diagnosis_result):
    """Suggest specific fixes based on diagnosis results."""
    logger.info(f"\n🔧 SUGGESTED FIXES:")
    
    if diagnosis_result['total_images'] == 0:
        logger.info("1. Check PDF image extraction:")
        logger.info("   - Verify pdf_parser.py extract_images_from_pdf() method")
        logger.info("   - Check if PDF actually contains images")
        logger.info("   - Enable debug logging in pdf_parser.py")
    
    elif diagnosis_result['total_images'] > 0 and diagnosis_result['word_files'] == 0:
        logger.info("1. Check document generation:")
        logger.info("   - Verify document_generator.py is working")
        logger.info("   - Check for errors in Word document creation")
        logger.info("   - Review main_workflow.py document generation step")
    
    elif diagnosis_result['total_images'] > 0 and diagnosis_result['word_files'] > 0:
        logger.info("1. Check image path resolution in document_generator.py:")
        logger.info("   - Verify _add_image_placeholder_block() method")
        logger.info("   - Check image folder path parameter")
        logger.info("   - Enable debug logging for image processing")
        
        logger.info("2. Test image insertion manually:")
        logger.info("   - Try opening Word document and inserting images manually")
        logger.info("   - Check if image files are corrupted")
        
        logger.info("3. Check image format compatibility:")
        logger.info("   - Ensure images are in supported formats (PNG, JPG, etc.)")
        logger.info("   - Check image file sizes")

if __name__ == "__main__":
    logger.info("🚀 PDF Translation Image Diagnostic Tool")
    logger.info("=" * 50)
    
    # Check recent translation
    result = check_recent_translation()
    
    if result:
        suggest_fixes(result)
    
    logger.info("\n✅ Diagnosis complete!")
    logger.info("💡 Run this script after each translation to monitor image processing")
