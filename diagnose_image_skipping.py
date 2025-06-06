#!/usr/bin/env python3
"""
Diagnostic tool to trace what happens to images during translation strategy optimization
"""

import os
import sys
import logging
from translation_strategy_manager import TranslationStrategyManager
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_content_with_images():
    """Create test content that includes various types of images"""
    test_content = [
        # Text content
        {
            'type': 'h1',
            'text': 'Chapter 1: Introduction',
            'page_num': 1,
            'block_num': 1
        },
        {
            'type': 'paragraph',
            'text': 'This is an introduction paragraph with substantial content.',
            'page_num': 1,
            'block_num': 2
        },
        
        # Images with different characteristics
        {
            'type': 'image',
            'filename': 'diagram1.png',
            'page_num': 1,
            'width': 200,
            'height': 150,
            'ocr_text': '',  # No OCR text (pure diagram)
            'block_num': 3
        },
        {
            'type': 'image',
            'filename': 'chart_with_text.png',
            'page_num': 2,
            'width': 300,
            'height': 200,
            'ocr_text': 'Figure 1: Sales Performance Chart showing quarterly results',  # Has OCR text
            'block_num': 1
        },
        {
            'type': 'image',
            'filename': 'schema.png',
            'page_num': 2,
            'width': 400,
            'height': 300,
            'ocr_text': 'Database Schema',  # Minimal OCR text
            'block_num': 2
        },
        {
            'type': 'image',
            'filename': 'flowchart.png',
            'page_num': 3,
            'width': 350,
            'height': 250,
            'ocr_text': '',  # No OCR text
            'block_num': 1
        },
        
        # More text content
        {
            'type': 'paragraph',
            'text': 'This paragraph follows the images and should be translated.',
            'page_num': 3,
            'block_num': 2
        }
    ]
    
    return test_content

def analyze_strategy_decisions():
    """Analyze how the strategy manager handles different content types"""
    logger.info("🔍 DIAGNOSING IMAGE SKIPPING IN TRANSLATION STRATEGY")
    logger.info("=" * 60)
    
    # Create strategy manager
    strategy_manager = TranslationStrategyManager()
    
    # Create test content
    test_content = create_test_content_with_images()
    
    logger.info(f"📋 Created test content with {len(test_content)} items:")
    image_count = sum(1 for item in test_content if item['type'] == 'image')
    text_count = len(test_content) - image_count
    logger.info(f"   • {text_count} text items")
    logger.info(f"   • {image_count} image items")
    
    # Check configuration
    logger.info(f"\n⚙️ Configuration check:")
    extract_images = config_manager.pdf_processing_settings.get('extract_images', True)
    logger.info(f"   • extract_images: {extract_images}")
    
    # Analyze each item individually
    logger.info(f"\n🔍 Individual item analysis:")
    
    for i, item in enumerate(test_content, 1):
        item_type = item.get('type', 'unknown')
        
        if item_type == 'image':
            filename = item.get('filename', 'unknown')
            ocr_text = item.get('ocr_text', '')
            ocr_word_count = len(ocr_text.split()) if ocr_text else 0
            
            logger.info(f"\n   📷 Image {i}: {filename}")
            logger.info(f"      • OCR text: '{ocr_text}' ({ocr_word_count} words)")
            
            # Analyze importance
            importance = strategy_manager.analyze_content_importance(item)
            logger.info(f"      • Importance: {importance.value}")
            
            # Get full strategy
            strategy = strategy_manager.get_translation_strategy(item)
            should_translate = strategy['should_translate']
            reason = strategy.get('reason', 'No reason provided')
            
            logger.info(f"      • Should translate: {should_translate}")
            logger.info(f"      • Reason: {reason}")
            
            if not should_translate:
                logger.warning(f"      ⚠️ IMAGE WILL BE SKIPPED!")
        else:
            text = item.get('text', '')[:50] + "..." if len(item.get('text', '')) > 50 else item.get('text', '')
            logger.info(f"\n   📝 {item_type.upper()} {i}: {text}")
            
            importance = strategy_manager.analyze_content_importance(item)
            strategy = strategy_manager.get_translation_strategy(item)
            
            logger.info(f"      • Importance: {importance.value}")
            logger.info(f"      • Should translate: {strategy['should_translate']}")

def test_full_optimization():
    """Test the full optimization process"""
    logger.info(f"\n🚀 TESTING FULL OPTIMIZATION PROCESS")
    logger.info("=" * 60)
    
    strategy_manager = TranslationStrategyManager()
    test_content = create_test_content_with_images()
    
    logger.info(f"📋 Before optimization: {len(test_content)} items")
    
    # Run the full optimization
    optimized_items, stats = strategy_manager.optimize_content_for_strategy(test_content)
    
    logger.info(f"📋 After optimization: {len(optimized_items)} items")
    logger.info(f"📊 Optimization stats:")
    for key, value in stats.items():
        logger.info(f"   • {key}: {value}")
    
    # Check what happened to images
    original_images = [item for item in test_content if item['type'] == 'image']
    optimized_images = [item for item in optimized_items if item['type'] == 'image']
    
    logger.info(f"\n🖼️ Image analysis:")
    logger.info(f"   • Original images: {len(original_images)}")
    logger.info(f"   • Optimized images: {len(optimized_images)}")
    logger.info(f"   • Images skipped: {len(original_images) - len(optimized_images)}")
    
    if len(original_images) != len(optimized_images):
        logger.warning("⚠️ SOME IMAGES WERE SKIPPED!")
        
        skipped_images = []
        optimized_filenames = {item.get('filename') for item in optimized_images}
        
        for img in original_images:
            if img.get('filename') not in optimized_filenames:
                skipped_images.append(img)
        
        logger.warning(f"Skipped images:")
        for img in skipped_images:
            logger.warning(f"   • {img.get('filename')} (OCR: '{img.get('ocr_text', '')}' - {len(img.get('ocr_text', '').split())} words)")
    else:
        logger.info("✅ All images preserved!")

def check_config_issues():
    """Check for configuration issues that might affect image processing"""
    logger.info(f"\n⚙️ CONFIGURATION DIAGNOSTICS")
    logger.info("=" * 60)
    
    # Check PDF processing settings
    pdf_settings = config_manager.pdf_processing_settings
    
    important_settings = [
        'extract_images',
        'perform_ocr_on_images', 
        'min_image_width_px',
        'min_image_height_px',
        'min_ocr_words_for_translation'
    ]
    
    logger.info("📋 PDF Processing Settings:")
    for setting in important_settings:
        value = pdf_settings.get(setting, 'NOT SET')
        logger.info(f"   • {setting}: {value}")
    
    # Check for potential issues
    issues = []
    
    if not pdf_settings.get('extract_images', True):
        issues.append("extract_images is disabled")
    
    min_ocr_words = pdf_settings.get('min_ocr_words_for_translation', 3)
    if min_ocr_words > 5:
        issues.append(f"min_ocr_words_for_translation is high ({min_ocr_words}) - might skip images with little text")
    
    if issues:
        logger.warning("⚠️ Potential configuration issues:")
        for issue in issues:
            logger.warning(f"   • {issue}")
    else:
        logger.info("✅ Configuration looks good for image processing")

def main():
    """Run all diagnostic tests"""
    logger.info("🔍 IMAGE SKIPPING DIAGNOSTIC TOOL")
    logger.info("This tool will help identify why images are being skipped during translation")
    
    try:
        # Run diagnostics
        analyze_strategy_decisions()
        test_full_optimization()
        check_config_issues()
        
        logger.info(f"\n🎯 SUMMARY")
        logger.info("=" * 60)
        logger.info("✅ Diagnostic complete!")
        logger.info("💡 Check the logs above to see:")
        logger.info("   • Which images are being skipped and why")
        logger.info("   • Configuration issues that might affect image processing")
        logger.info("   • Strategy decisions for each content type")
        
    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
