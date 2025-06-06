#!/usr/bin/env python3
"""
Update image extraction settings to be more aggressive
"""

import configparser
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_image_settings():
    """Update config.ini with more aggressive image extraction settings"""
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        logger.error(f"Config file not found: {config_file}")
        return False
    
    # Read current config with proper encoding
    config = configparser.ConfigParser()
    with open(config_file, 'r', encoding='utf-8') as f:
        config.read_file(f)
    
    # Ensure the section exists
    if 'pdf_processing_settings' not in config:
        config.add_section('pdf_processing_settings')
    
    # Aggressive settings for maximum image extraction
    new_settings = {
        'min_image_width_px': '30',
        'min_image_height_px': '30', 
        'min_ocr_words_for_translation': '0',
        'extract_images': 'true'
    }
    
    logger.info("Updating image extraction settings to 'Aggressive' mode:")
    
    # Update settings
    for key, value in new_settings.items():
        old_value = config.get('pdf_processing_settings', key, fallback='not set')
        config.set('pdf_processing_settings', key, value)
        logger.info(f"  {key}: {old_value} -> {value}")
    
    # Write back to file with proper encoding
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    
    logger.info("Config updated successfully!")
    logger.info("New settings should extract more images (30x30 pixels minimum)")
    return True

if __name__ == "__main__":
    logger.info("Updating image extraction settings for better coverage...")
    success = update_image_settings()
    
    if success:
        logger.info("Ready to re-run PDF translation with new settings!")
    else:
        logger.error("Failed to update settings")
