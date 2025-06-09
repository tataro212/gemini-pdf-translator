#!/usr/bin/env python3
"""
Test script for the enhanced PDF translation workflow with advanced features
"""

import asyncio
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhanced_workflow():
    """Test the enhanced workflow with advanced features"""
    
    logger.info("🚀 Testing Enhanced PDF Translation Workflow")
    logger.info("=" * 60)
    
    try:
        # Import the enhanced translator
        from main_workflow import UltimatePDFTranslator
        
        # Initialize the translator
        logger.info("🔧 Initializing Enhanced PDF Translator...")
        translator = UltimatePDFTranslator()
        
        # Check if advanced features are available
        if hasattr(translator, 'advanced_pipeline') and translator.advanced_pipeline:
            logger.info("✅ Advanced features are available and initialized!")
            
            # Get pipeline stats
            stats = translator.advanced_pipeline.get_pipeline_stats()
            logger.info("📊 Pipeline Statistics:")
            logger.info(f"   Available OCR engines: {stats['ocr_performance']['available_engines']}")
            logger.info(f"   Semantic cache ready: {translator.advanced_pipeline.semantic_cache.embedding_available}")
            logger.info(f"   Self-correction enabled: {translator.advanced_pipeline.self_correcting_translator is not None}")
            
        else:
            logger.warning("⚠️ Advanced features not available - using standard workflow")
        
        # Test with a sample text (simulating PDF content)
        logger.info("\n🔍 Testing Advanced Text Processing...")
        
        if translator.advanced_pipeline:
            # Test semantic caching
            test_texts = [
                "The machine learning model achieved 95% accuracy on the test dataset.",
                "The ML algorithm reached 95% precision on the testing data.",  # Similar
                "Today is a sunny day with clear skies."  # Different
            ]
            
            logger.info("🧠 Testing semantic caching...")
            cache_results = []
            
            for i, text in enumerate(test_texts):
                result = await translator.advanced_pipeline.process_text_chunks_advanced([text], "Greek")
                cache_results.append(result[0])
                
                logger.info(f"   Text {i+1}: Cache hit = {result[0].cache_hit}, "
                           f"Semantic hit = {result[0].semantic_cache_hit}")
            
            # Test content validation
            logger.info("🔍 Testing content validation...")
            from structured_content_validator import StructuredContentValidator
            
            validator = StructuredContentValidator()
            
            # Test table validation
            test_table = """| Feature | Status |
|---------|--------|
| OCR | Active |
| Translation | Active |"""
            
            broken_table = """| Feature | Status |
| OCR | Active | Extra |"""
            
            result1 = validator.validate_content(test_table, test_table)
            result2 = validator.validate_content(test_table, broken_table)
            
            logger.info(f"   Valid table validation: {result1.is_valid}")
            logger.info(f"   Broken table detection: {not result2.is_valid} (issues: {len(result2.issues)})")
            
        logger.info("\n✅ Enhanced workflow test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_configuration():
    """Test configuration loading for advanced features"""
    
    logger.info("⚙️ Testing Configuration...")
    
    try:
        from config_manager import config_manager
        
        # Check if advanced features are enabled in config
        use_advanced = config_manager.get_config_value('TranslationEnhancements', 'use_advanced_features', True, bool)
        logger.info(f"   Advanced features enabled in config: {use_advanced}")
        
        # Check other relevant settings
        target_language = config_manager.translation_enhancement_settings.get('target_language', 'Greek')
        logger.info(f"   Target language: {target_language}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    
    logger.info("📦 Testing Module Imports...")
    
    try:
        # Test standard modules
        from main_workflow import UltimatePDFTranslator
        from config_manager import config_manager
        from translation_service import translation_service
        logger.info("   ✅ Standard modules imported")
        
        # Test advanced modules
        from advanced_translation_pipeline import AdvancedTranslationPipeline
        from self_correcting_translator import SelfCorrectingTranslator
        from hybrid_ocr_processor import HybridOCRProcessor
        from semantic_cache import SemanticCache
        logger.info("   ✅ Advanced modules imported")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    logger.info("🎯 Enhanced PDF Translator Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Enhanced Workflow Test", test_enhanced_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            
            results.append((test_name, success))
            logger.info(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
        except Exception as e:
            logger.error(f"❌ FAILED: {test_name} - {e}")
            results.append((test_name, False))
        
        logger.info("-" * 40)
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Enhanced workflow is ready to use.")
        logger.info("\n💡 Next Steps:")
        logger.info("   1. Run 'python main_workflow.py' to use the enhanced translator")
        logger.info("   2. The system will automatically use advanced features when available")
        logger.info("   3. Check the logs for advanced feature performance metrics")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
