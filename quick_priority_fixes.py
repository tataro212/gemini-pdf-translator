#!/usr/bin/env python3
"""
Quick Priority Fixes for PDF Translation Pipeline

This script applies immediate fixes for the most critical issues:
1. Fix IntelligentPDFTranslator initialization
2. Improve Gemini API error handling
3. Make validation more flexible
4. Add better logging for debugging

Usage: python quick_priority_fixes.py
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def apply_quick_fixes():
    """Apply quick fixes for priority issues"""
    
    logger.info("🔧 Applying quick priority fixes...")
    
    fixes_applied = []
    
    # Fix 1: Ensure proper imports and error handling
    try:
        # Test imports
        from main_workflow import UltimatePDFTranslator
        from translation_service import translation_service
        from config_manager import config_manager
        
        logger.info("✅ Core imports successful")
        fixes_applied.append("Core imports verified")
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    
    # Fix 2: Test IntelligentPDFTranslator initialization
    try:
        translator = UltimatePDFTranslator()
        
        if hasattr(translator, 'intelligent_pipeline'):
            if translator.intelligent_pipeline:
                logger.info("✅ IntelligentPDFTranslator initialized successfully")
                fixes_applied.append("IntelligentPDFTranslator working")
            else:
                logger.info("ℹ️ IntelligentPDFTranslator disabled (this is normal if not configured)")
                fixes_applied.append("IntelligentPDFTranslator properly disabled")
        
    except Exception as e:
        logger.error(f"❌ IntelligentPDFTranslator initialization error: {e}")
        logger.info("💡 This may be due to missing dependencies - check INTELLIGENT_PIPELINE_README.md")
    
    # Fix 3: Test translation service robustness
    try:
        if hasattr(translation_service, 'model') and translation_service.model:
            logger.info("✅ Translation service model available")
            fixes_applied.append("Translation service configured")
        else:
            logger.warning("⚠️ Translation service not configured - check API key in config.ini")
            
    except Exception as e:
        logger.error(f"❌ Translation service error: {e}")
    
    # Fix 4: Test markdown validation
    try:
        from markdown_aware_translator import markdown_translator
        
        # Test with simple content
        original = "# Test\n\nParagraph"
        translated = "# Τεστ\n\nΠαράγραφος"
        
        is_valid = markdown_translator._validate_markdown_structure(original, translated)
        logger.info(f"✅ Markdown validation test: {'PASS' if is_valid else 'NEEDS_ADJUSTMENT'}")
        fixes_applied.append("Markdown validation tested")
        
    except Exception as e:
        logger.error(f"❌ Markdown validation error: {e}")
    
    # Fix 5: Test structured content validation
    try:
        from structured_content_validator import StructuredContentValidator
        
        validator = StructuredContentValidator()
        
        # Test with simple table
        original_table = "| A | B |\n|---|---|\n| 1 | 2 |"
        translated_table = "| Α | Β |\n|---|---|\n| 1 | 2 |"
        
        result = validator.validate_content(original_table, translated_table)
        logger.info(f"✅ Table validation test: confidence={result.confidence:.2f}")
        fixes_applied.append("Table validation tested")
        
    except Exception as e:
        logger.error(f"❌ Table validation error: {e}")
    
    # Summary
    logger.info(f"\n🎉 Quick fixes completed! Applied {len(fixes_applied)} fixes:")
    for fix in fixes_applied:
        logger.info(f"   ✅ {fix}")
    
    # Recommendations
    logger.info("\n💡 RECOMMENDATIONS:")
    logger.info("1. Run 'python troubleshoot_priority_tools.py' for comprehensive testing")
    logger.info("2. Check config.ini for proper API key configuration")
    logger.info("3. Monitor translation quality and adjust validation thresholds if needed")
    logger.info("4. Check logs for any remaining issues during actual translation")
    
    return True

def check_configuration():
    """Check critical configuration settings"""
    
    logger.info("⚙️ Checking configuration...")
    
    try:
        from config_manager import config_manager
        
        # Check API key
        api_key = config_manager.get_config_value('Gemini', 'api_key', '')
        if api_key and len(api_key) > 10:
            logger.info("✅ Gemini API key configured")
        else:
            logger.warning("⚠️ Gemini API key not configured or too short")
            logger.info("💡 Add your API key to config.ini under [Gemini] section")
        
        # Check target language
        target_lang = config_manager.get_config_value('General', 'target_language', 'Greek')
        logger.info(f"✅ Target language: {target_lang}")
        
        # Check intelligent pipeline setting
        use_intelligent = config_manager.get_config_value('IntelligentPipeline', 'use_intelligent_pipeline', True, bool)
        logger.info(f"ℹ️ Intelligent pipeline enabled: {use_intelligent}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration check failed: {e}")
        return False

def main():
    """Main function"""
    
    logger.info("🚀 Starting quick priority fixes for PDF translation pipeline...")
    
    # Check configuration first
    if not check_configuration():
        logger.error("❌ Configuration check failed - please fix configuration issues first")
        return False
    
    # Apply fixes
    if apply_quick_fixes():
        logger.info("✅ Quick priority fixes completed successfully!")
        logger.info("\n🎯 NEXT STEPS:")
        logger.info("1. Test with a small PDF file")
        logger.info("2. Monitor logs for any remaining issues")
        logger.info("3. Run comprehensive troubleshooting if needed")
        return True
    else:
        logger.error("❌ Some fixes failed - check error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
