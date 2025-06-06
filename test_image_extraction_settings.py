#!/usr/bin/env python3
"""
Test different image extraction settings to find optimal values
"""

import os
import sys
import logging
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_current_settings():
    """Analyze current image extraction settings"""
    logger.info("⚙️ CURRENT IMAGE EXTRACTION SETTINGS")
    logger.info("=" * 50)
    
    pdf_settings = config_manager.pdf_processing_settings
    
    # Key image extraction settings
    settings_to_check = [
        ('extract_images', True, 'Enable/disable image extraction'),
        ('min_image_width_px', 50, 'Minimum image width in pixels'),
        ('min_image_height_px', 50, 'Minimum image height in pixels'),
        ('perform_ocr_on_images', True, 'Enable OCR on extracted images'),
        ('min_ocr_words_for_translation', 3, 'Minimum OCR words to consider for translation')
    ]
    
    logger.info("📋 Current settings:")
    current_settings = {}
    
    for setting_name, default_value, description in settings_to_check:
        current_value = pdf_settings.get(setting_name, default_value)
        current_settings[setting_name] = current_value
        logger.info(f"   • {setting_name}: {current_value} ({description})")
    
    # Analyze potential issues
    logger.info("\n🔍 Analysis:")
    issues = []
    recommendations = []
    
    if not current_settings['extract_images']:
        issues.append("Image extraction is disabled")
        recommendations.append("Set extract_images = true in config.ini")
    
    min_width = current_settings['min_image_width_px']
    min_height = current_settings['min_image_height_px']
    
    if min_width >= 100 or min_height >= 100:
        issues.append(f"Image size thresholds are very high ({min_width}x{min_height})")
        recommendations.append("Try reducing min_image_width_px and min_image_height_px to 30-50")
    elif min_width >= 50 or min_height >= 50:
        logger.info(f"   ✅ Image size thresholds are reasonable ({min_width}x{min_height})")
    else:
        logger.info(f"   ⚠️ Image size thresholds are low ({min_width}x{min_height}) - might extract too many small images")
    
    min_ocr_words = current_settings['min_ocr_words_for_translation']
    if min_ocr_words > 5:
        issues.append(f"OCR word threshold is high ({min_ocr_words})")
        recommendations.append("Consider reducing min_ocr_words_for_translation to 1-3")
    
    if issues:
        logger.warning("⚠️ Potential issues found:")
        for issue in issues:
            logger.warning(f"   • {issue}")
        
        logger.info("\n💡 Recommendations:")
        for rec in recommendations:
            logger.info(f"   • {rec}")
    else:
        logger.info("   ✅ Settings look good for image extraction")
    
    return current_settings

def suggest_alternative_settings():
    """Suggest alternative settings for better image extraction"""
    logger.info("\n🔧 SUGGESTED ALTERNATIVE SETTINGS")
    logger.info("=" * 50)
    
    alternatives = [
        {
            'name': 'Conservative (High Quality)',
            'settings': {
                'min_image_width_px': 100,
                'min_image_height_px': 100,
                'min_ocr_words_for_translation': 1
            },
            'description': 'Only extract larger, high-quality images'
        },
        {
            'name': 'Balanced (Recommended)',
            'settings': {
                'min_image_width_px': 50,
                'min_image_height_px': 50,
                'min_ocr_words_for_translation': 2
            },
            'description': 'Good balance between quality and coverage'
        },
        {
            'name': 'Aggressive (Maximum Coverage)',
            'settings': {
                'min_image_width_px': 30,
                'min_image_height_px': 30,
                'min_ocr_words_for_translation': 1
            },
            'description': 'Extract more images, including smaller ones'
        },
        {
            'name': 'Permissive (Extract Everything)',
            'settings': {
                'min_image_width_px': 20,
                'min_image_height_px': 20,
                'min_ocr_words_for_translation': 0
            },
            'description': 'Extract all images, including very small ones'
        }
    ]
    
    for alt in alternatives:
        logger.info(f"\n📋 {alt['name']}:")
        logger.info(f"   Description: {alt['description']}")
        logger.info(f"   Settings:")
        for setting, value in alt['settings'].items():
            logger.info(f"     • {setting} = {value}")

def create_config_update_script():
    """Create a script to update config.ini with new settings"""
    logger.info("\n🛠️ CONFIG UPDATE HELPER")
    logger.info("=" * 50)
    
    script_content = '''#!/usr/bin/env python3
"""
Update config.ini with new image extraction settings
"""

import configparser
import os

def update_config(settings_dict):
    """Update config.ini with new settings"""
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Ensure the section exists
    if 'pdf_processing_settings' not in config:
        config.add_section('pdf_processing_settings')
    
    # Update settings
    for key, value in settings_dict.items():
        config.set('pdf_processing_settings', key, str(value))
        print(f"✅ Updated {key} = {value}")
    
    # Write back to file
    with open(config_file, 'w') as f:
        config.write(f)
    
    print(f"✅ Config updated successfully!")
    return True

if __name__ == "__main__":
    print("🔧 CONFIG UPDATER")
    print("Choose a preset or enter custom values:")
    print()
    print("1. Conservative (100x100, OCR words: 1)")
    print("2. Balanced (50x50, OCR words: 2)")  
    print("3. Aggressive (30x30, OCR words: 1)")
    print("4. Permissive (20x20, OCR words: 0)")
    print("5. Custom")
    
    choice = input("Enter choice (1-5): ").strip()
    
    presets = {
        '1': {'min_image_width_px': 100, 'min_image_height_px': 100, 'min_ocr_words_for_translation': 1},
        '2': {'min_image_width_px': 50, 'min_image_height_px': 50, 'min_ocr_words_for_translation': 2},
        '3': {'min_image_width_px': 30, 'min_image_height_px': 30, 'min_ocr_words_for_translation': 1},
        '4': {'min_image_width_px': 20, 'min_image_height_px': 20, 'min_ocr_words_for_translation': 0},
    }
    
    if choice in presets:
        settings = presets[choice]
        update_config(settings)
    elif choice == '5':
        print("Enter custom values:")
        try:
            width = int(input("Min image width (px): "))
            height = int(input("Min image height (px): "))
            ocr_words = int(input("Min OCR words: "))
            
            settings = {
                'min_image_width_px': width,
                'min_image_height_px': height,
                'min_ocr_words_for_translation': ocr_words
            }
            update_config(settings)
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
    else:
        print("❌ Invalid choice")
'''
    
    with open('update_image_config.py', 'w') as f:
        f.write(script_content)
    
    logger.info("✅ Created update_image_config.py")
    logger.info("💡 Run 'python update_image_config.py' to easily update your settings")

def diagnose_extraction_issues():
    """Diagnose common image extraction issues"""
    logger.info("\n🔍 COMMON IMAGE EXTRACTION ISSUES")
    logger.info("=" * 50)
    
    issues_and_solutions = [
        {
            'issue': 'Only 3 images extracted when there should be 20+',
            'causes': [
                'Image size thresholds too high (min_image_width_px/height_px)',
                'Images are embedded as vector graphics (not raster images)',
                'Images are part of complex PDF objects',
                'Aspect ratio filtering removing thin images'
            ],
            'solutions': [
                'Reduce min_image_width_px and min_image_height_px to 20-30',
                'Check if PDF uses vector graphics instead of raster images',
                'Try different PDF processing tools',
                'Adjust aspect ratio threshold in code'
            ]
        },
        {
            'issue': 'Images extracted but not included in translation',
            'causes': [
                'Images classified as LOW importance and skipped',
                'OCR word threshold too high',
                'Translation strategy filtering out images',
                'Smart grouping excluding images'
            ],
            'solutions': [
                'Set min_ocr_words_for_translation to 0 or 1',
                'Check translation strategy settings',
                'Verify image items are in structured content',
                'Check smart grouping logic'
            ]
        },
        {
            'issue': 'Too many small/irrelevant images extracted',
            'causes': [
                'Image size thresholds too low',
                'Aspect ratio filtering disabled',
                'Decorative elements being extracted'
            ],
            'solutions': [
                'Increase min_image_width_px and min_image_height_px',
                'Enable aspect ratio filtering',
                'Add better image quality detection'
            ]
        }
    ]
    
    for item in issues_and_solutions:
        logger.info(f"\n❓ Issue: {item['issue']}")
        logger.info("   Possible causes:")
        for cause in item['causes']:
            logger.info(f"     • {cause}")
        logger.info("   Solutions:")
        for solution in item['solutions']:
            logger.info(f"     • {solution}")

def main():
    """Main function"""
    logger.info("🔧 IMAGE EXTRACTION SETTINGS ANALYZER")
    logger.info("This tool helps diagnose and fix image extraction issues")
    
    # Analyze current settings
    current_settings = analyze_current_settings()
    
    # Suggest alternatives
    suggest_alternative_settings()
    
    # Create config update helper
    create_config_update_script()
    
    # Diagnose common issues
    diagnose_extraction_issues()
    
    logger.info("\n🎯 SUMMARY")
    logger.info("=" * 50)
    logger.info("💡 Next steps:")
    logger.info("   1. Review your current settings above")
    logger.info("   2. If only 3 images are extracted, try 'Aggressive' or 'Permissive' settings")
    logger.info("   3. Use 'python update_image_config.py' to easily change settings")
    logger.info("   4. Re-run your PDF translation to test new settings")
    logger.info("   5. Use 'python trace_image_pipeline.py your_pdf.pdf' to trace the full pipeline")

if __name__ == "__main__":
    main()
