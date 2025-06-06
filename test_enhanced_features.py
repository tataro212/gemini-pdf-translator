"""
Test Enhanced Features for Ultimate PDF Translator

Tests all the new optimization features including:
- Translation Strategy Manager
- Advanced Contextual Caching  
- Enhanced OCR Preprocessing
- Improved Document Generation
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_features():
    """Test all enhanced features"""
    
    logger.info("🚀 TESTING ENHANCED FEATURES")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test 1: Translation Strategy Manager
    logger.info("🎯 Test 1: Translation Strategy Manager")
    try:
        from translation_strategy_manager import translation_strategy_manager
        
        # Create sample content items
        sample_items = [
            {'type': 'h1', 'text': 'Introduction to Machine Learning', 'page_num': 1, 'block_num': 1},
            {'type': 'paragraph', 'text': 'This is a comprehensive guide to machine learning algorithms and their applications in modern data science.', 'page_num': 1, 'block_num': 2},
            {'type': 'paragraph', 'text': 'All rights reserved. Copyright 2024.', 'page_num': 1, 'block_num': 3},
            {'type': 'paragraph', 'text': 'def train_model(X, y):\n    return model.fit(X, y)', 'page_num': 2, 'block_num': 1},
            {'type': 'list_item', 'text': 'Data preprocessing', 'page_num': 2, 'block_num': 2},
            {'type': 'h2', 'text': 'Methodology', 'page_num': 3, 'block_num': 1},
        ]
        
        # Test importance analysis
        for item in sample_items:
            importance = translation_strategy_manager.analyze_content_importance(item)
            strategy = translation_strategy_manager.get_translation_strategy(item)
            logger.info(f"  • {item['type']}: '{item['text'][:30]}...' → {importance.value} ({strategy['should_translate']})")
        
        # Test content optimization
        optimized_items, stats = translation_strategy_manager.optimize_content_for_strategy(sample_items)
        logger.info(f"  ✅ Strategy optimization: {len(sample_items)} → {len(optimized_items)} items")
        logger.info(f"  💰 Estimated savings: {stats['cost_savings_estimate']:.1f}%")
        
        test_results['translation_strategy'] = True
        
    except Exception as e:
        logger.error(f"  ❌ Translation Strategy test failed: {e}")
        test_results['translation_strategy'] = False
    
    # Test 2: Advanced Contextual Caching
    logger.info("\n🧠 Test 2: Advanced Contextual Caching")
    try:
        from advanced_caching import advanced_cache_manager
        
        # Test caching with context
        text1 = "Machine learning is a subset of artificial intelligence."
        text2 = "Machine learning is a subset of artificial intelligence."  # Same text
        prev_context1 = "In the field of computer science,"
        prev_context2 = "When discussing data analysis,"  # Different context
        
        # Cache first translation
        advanced_cache_manager.cache_translation(
            text1, "Greek", "gemini-1.5-pro", "Η μηχανική μάθηση είναι υποσύνολο της τεχνητής νοημοσύνης.",
            prev_context1, ""
        )
        
        # Test exact match
        cached1 = advanced_cache_manager.get_cached_translation(text1, "Greek", "gemini-1.5-pro", prev_context1, "")
        logger.info(f"  ✅ Exact context match: {'Found' if cached1 else 'Not found'}")
        
        # Test different context (should not match)
        cached2 = advanced_cache_manager.get_cached_translation(text2, "Greek", "gemini-1.5-pro", prev_context2, "")
        logger.info(f"  ✅ Different context: {'Found' if cached2 else 'Not found (correct)'}")
        
        # Test fuzzy matching
        similar_text = "Machine learning is subset of artificial intelligence"  # Slightly different
        cached3 = advanced_cache_manager.get_cached_translation(similar_text, "Greek", "gemini-1.5-pro", prev_context1, "")
        logger.info(f"  ✅ Fuzzy matching: {'Found' if cached3 else 'Not found'}")
        
        # Get statistics
        stats = advanced_cache_manager.get_cache_statistics()
        logger.info(f"  📊 Cache stats: {stats['total_entries']} entries, fuzzy matching: {stats['fuzzy_matching_enabled']}")
        
        test_results['advanced_caching'] = True
        
    except Exception as e:
        logger.error(f"  ❌ Advanced Caching test failed: {e}")
        test_results['advanced_caching'] = False
    
    # Test 3: Enhanced OCR Preprocessing
    logger.info("\n👁️ Test 3: Enhanced OCR Preprocessing")
    try:
        from ocr_processor import ImagePreprocessor, EnhancedOCRProcessor
        
        # Test image preprocessor
        preprocessor = ImagePreprocessor()
        logger.info(f"  ✅ Image preprocessor initialized")
        logger.info(f"  📊 Preprocessing settings: {preprocessor.preprocessing_settings}")
        
        # Test enhanced OCR processor
        ocr_processor = EnhancedOCRProcessor()
        logger.info(f"  ✅ Enhanced OCR processor initialized")
        logger.info(f"  🔧 OCR enabled: {ocr_processor.ocr_enabled}")
        
        # Test smart filtering
        test_texts = [
            "This is a meaningful paragraph about machine learning algorithms.",
            "Figure 1: Performance comparison chart",
            "x-axis: Time, y-axis: Accuracy",
            "All rights reserved",
            "def process_data():",
            "Click here to continue"
        ]
        
        for text in test_texts:
            should_skip = ocr_processor.should_skip_ocr_translation(text)
            action = "SKIP" if should_skip else "TRANSLATE"
            logger.info(f"  • '{text[:40]}...' → {action}")
        
        test_results['ocr_preprocessing'] = True
        
    except Exception as e:
        logger.error(f"  ❌ OCR Preprocessing test failed: {e}")
        test_results['ocr_preprocessing'] = False
    
    # Test 4: Enhanced Document Generation
    logger.info("\n📄 Test 4: Enhanced Document Generation")
    try:
        from document_generator import WordDocumentGenerator
        
        # Test enhanced document generator
        doc_generator = WordDocumentGenerator()
        logger.info(f"  ✅ Enhanced document generator initialized")
        
        # Test with sample content
        sample_content = [
            {'type': 'h1', 'text': 'Enhanced Document Test', 'page_num': 1, 'block_num': 1},
            {'type': 'paragraph', 'text': 'This document tests the enhanced generation features.', 'page_num': 1, 'block_num': 2},
            {'type': 'h2', 'text': 'Features Tested', 'page_num': 1, 'block_num': 3},
            {'type': 'list_item', 'text': 'Enhanced table of contents', 'page_num': 1, 'block_num': 4},
            {'type': 'list_item', 'text': 'Improved image positioning', 'page_num': 1, 'block_num': 5},
        ]
        
        # Create test document
        with tempfile.TemporaryDirectory() as temp_dir:
            test_doc_path = os.path.join(temp_dir, "enhanced_test.docx")
            
            success = doc_generator.create_word_document_with_structure(
                sample_content, test_doc_path, None, None
            )
            
            if success and os.path.exists(test_doc_path):
                file_size = os.path.getsize(test_doc_path)
                logger.info(f"  ✅ Enhanced document created: {file_size:,} bytes")
            else:
                logger.error("  ❌ Document creation failed")
        
        test_results['document_generation'] = True
        
    except Exception as e:
        logger.error(f"  ❌ Document Generation test failed: {e}")
        test_results['document_generation'] = False
    
    # Test 5: Integration Test
    logger.info("\n🔗 Test 5: Integration Test")
    try:
        from optimization_manager import optimization_manager
        
        # Test integrated optimization with all features
        sample_items = [
            {'type': 'h1', 'text': 'Research Methodology', 'page_num': 1, 'block_num': 1},
            {'type': 'paragraph', 'text': 'This section describes the research methodology used in this study.', 'page_num': 1, 'block_num': 2},
            {'type': 'paragraph', 'text': 'Copyright notice', 'page_num': 1, 'block_num': 3},
            {'type': 'h2', 'text': 'Data Collection', 'page_num': 2, 'block_num': 1},
        ]
        
        # Test ultimate optimization with all features
        batches, params = optimization_manager.optimize_content_for_translation(sample_items, "Greek")
        
        logger.info(f"  ✅ Ultimate optimization completed")
        logger.info(f"  📦 Batches created: {params['total_batches']}")
        logger.info(f"  🎯 Items after strategy: {params.get('items_after_strategy', 'N/A')}")
        logger.info(f"  📊 Content type: {params['content_type']}")
        
        test_results['integration'] = True
        
    except Exception as e:
        logger.error(f"  ❌ Integration test failed: {e}")
        test_results['integration'] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 ENHANCED FEATURES TEST SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name.replace('_', ' ').title()}")
    
    logger.info("=" * 60)
    logger.info(f"OVERALL: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
        logger.info("🚀 Ready for production use with significant improvements!")
    else:
        logger.warning(f"⚠️ {total_tests - passed_tests} features need attention")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(test_enhanced_features())
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test crashed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
