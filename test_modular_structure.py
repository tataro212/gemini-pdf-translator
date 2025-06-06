"""
Test Script for Modular PDF Translator Structure

Validates that all modules can be imported and basic functionality works
"""

import sys
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported successfully"""
    logger.info("🔍 Testing module imports...")
    
    modules_to_test = [
        'config_manager',
        'utils', 
        'ocr_processor',
        'pdf_parser',
        'translation_service',
        'optimization_manager',
        'document_generator',
        'drive_uploader',
        'main_workflow'
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            logger.info(f"  ✅ {module_name}")
        except Exception as e:
            logger.error(f"  ❌ {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
    
    return failed_imports

def test_config_manager():
    """Test configuration manager functionality"""
    logger.info("🔧 Testing config manager...")
    
    try:
        from config_manager import config_manager
        
        # Test basic configuration access
        gemini_settings = config_manager.gemini_settings
        pdf_settings = config_manager.pdf_processing_settings
        word_settings = config_manager.word_output_settings
        
        logger.info(f"  ✅ Gemini model: {gemini_settings['model_name']}")
        logger.info(f"  ✅ Target language: {config_manager.translation_enhancement_settings['target_language']}")
        logger.info(f"  ✅ Smart grouping: {config_manager.optimization_settings['enable_smart_grouping']}")
        
        # Test validation
        issues, recommendations = config_manager.validate_configuration()
        logger.info(f"  ✅ Configuration validation: {len(issues)} issues, {len(recommendations)} recommendations")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Config manager test failed: {e}")
        return False

def test_optimization_manager():
    """Test optimization manager functionality"""
    logger.info("⚡ Testing optimization manager...")
    
    try:
        from optimization_manager import optimization_manager
        
        # Create sample content items
        sample_items = [
            {'type': 'paragraph', 'text': 'This is a test paragraph.', 'page_num': 1, 'block_num': 1},
            {'type': 'paragraph', 'text': 'This is another test paragraph.', 'page_num': 1, 'block_num': 2},
            {'type': 'h1', 'text': 'Test Heading', 'page_num': 1, 'block_num': 3},
            {'type': 'paragraph', 'text': 'More content here.', 'page_num': 2, 'block_num': 1},
        ]
        
        # Test smart grouping
        groups = optimization_manager.grouping_processor.create_smart_groups(sample_items)
        logger.info(f"  ✅ Smart grouping: {len(sample_items)} items → {len(groups)} groups")
        
        # Test content optimization
        batches, params = optimization_manager.optimize_content_for_translation(sample_items, "Greek")
        logger.info(f"  ✅ Content optimization: {len(batches)} batches created")
        logger.info(f"  ✅ Optimization params: {params}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Optimization manager test failed: {e}")
        return False

def test_translation_service():
    """Test translation service (without making actual API calls)"""
    logger.info("🌐 Testing translation service...")
    
    try:
        from translation_service import translation_service
        
        # Test cache functionality
        cache = translation_service.cache
        logger.info(f"  ✅ Translation cache initialized: {cache.enabled}")
        
        # Test glossary functionality
        glossary = translation_service.glossary
        logger.info(f"  ✅ Glossary manager initialized: {glossary.enabled}")
        
        # Test prompt generation
        prompt = translation_service.prompt_generator.generate_translation_prompt(
            "Test text", "Greek", "academic style"
        )
        logger.info(f"  ✅ Prompt generation: {len(prompt)} characters")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Translation service test failed: {e}")
        return False

def test_document_generator():
    """Test document generator functionality"""
    logger.info("📄 Testing document generator...")
    
    try:
        from document_generator import document_generator
        
        # Test that the generator is properly initialized
        logger.info(f"  ✅ Word settings loaded: {document_generator.word_settings}")
        
        # Test bookmark counter reset
        document_generator.reset_bookmark_counter()
        logger.info("  ✅ Bookmark counter reset")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Document generator test failed: {e}")
        return False

def test_drive_uploader():
    """Test Google Drive uploader (without actual authentication)"""
    logger.info("☁️ Testing Google Drive uploader...")
    
    try:
        from drive_uploader import drive_uploader
        
        # Test availability check
        is_available = drive_uploader.is_available()
        logger.info(f"  ✅ Google Drive availability: {is_available}")
        
        # Test settings
        settings = drive_uploader.drive_settings
        logger.info(f"  ✅ Drive settings loaded: {settings}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Drive uploader test failed: {e}")
        return False

def test_ocr_processor():
    """Test OCR processor functionality"""
    logger.info("👁️ Testing OCR processor...")
    
    try:
        from ocr_processor import OCRProcessor, SmartImageAnalyzer
        
        # Test basic OCR processor
        ocr = OCRProcessor()
        logger.info(f"  ✅ OCR processor initialized: {ocr.ocr_enabled}")
        
        # Test smart filtering
        test_texts = [
            "This is a simple sentence that should be translated.",
            "Figure 1: Chart showing data",
            "x-axis y-axis legend",
            "Click here to continue"
        ]
        
        for text in test_texts:
            should_skip = ocr.should_skip_ocr_translation(text)
            logger.info(f"  ✅ OCR filtering '{text[:30]}...': {'skip' if should_skip else 'translate'}")
        
        # Test image analyzer
        analyzer = SmartImageAnalyzer()
        logger.info("  ✅ Smart image analyzer initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ OCR processor test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    logger.info("🔧 Testing utilities...")
    
    try:
        from utils import clean_text_of_markers, get_cache_key, ProgressTracker
        
        # Test text cleaning
        dirty_text = "This is text¹ with markers² and footnotes³"
        clean_text = clean_text_of_markers(dirty_text)
        logger.info(f"  ✅ Text cleaning: '{dirty_text}' → '{clean_text}'")
        
        # Test cache key generation
        cache_key = get_cache_key("test text", "Greek", "gemini-1.5-pro")
        logger.info(f"  ✅ Cache key generation: {cache_key[:20]}...")
        
        # Test progress tracker
        tracker = ProgressTracker(10)
        tracker.update(completed=3)
        logger.info("  ✅ Progress tracker initialized and updated")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Utils test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    logger.info("🚀 STARTING MODULAR STRUCTURE TESTS")
    logger.info("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Manager", test_config_manager),
        ("Optimization Manager", test_optimization_manager),
        ("Translation Service", test_translation_service),
        ("Document Generator", test_document_generator),
        ("Drive Uploader", test_drive_uploader),
        ("OCR Processor", test_ocr_processor),
        ("Utilities", test_utils)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Module Imports":
                failed_imports = test_func()
                results[test_name] = len(failed_imports) == 0
                if failed_imports:
                    logger.error(f"Failed imports: {failed_imports}")
            else:
                results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
        
        logger.info("")  # Add spacing between tests
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("=" * 50)
    logger.info(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Modular structure is working correctly.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
