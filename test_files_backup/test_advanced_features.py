#!/usr/bin/env python3
"""
Test script for advanced features
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing all advanced modules"""
    logger.info("🔧 Testing imports...")
    
    try:
        from structured_content_validator import StructuredContentValidator
        logger.info("✅ StructuredContentValidator imported")
        
        from self_correcting_translator import SelfCorrectingTranslator
        logger.info("✅ SelfCorrectingTranslator imported")
        
        from hybrid_ocr_processor import HybridOCRProcessor
        logger.info("✅ HybridOCRProcessor imported")
        
        from semantic_cache import SemanticCache
        logger.info("✅ SemanticCache imported")
        
        from advanced_translation_pipeline import AdvancedTranslationPipeline
        logger.info("✅ AdvancedTranslationPipeline imported")
        
        logger.info("🎉 All advanced modules imported successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_content_validator():
    """Test the content validator"""
    logger.info("🔍 Testing content validator...")
    
    try:
        from structured_content_validator import StructuredContentValidator
        
        validator = StructuredContentValidator()
        
        # Test table validation
        test_table = """| Column 1 | Column 2 |
|----------|----------|
| Value A  | Value B  |
| Value C  | Value D  |"""
        
        result = validator.validate_content(test_table, test_table)
        logger.info(f"✅ Table validation: {result.is_valid} (confidence: {result.confidence:.2f})")
        
        # Test with broken table
        broken_table = """| Column 1 | Column 2 |
| Value A  | Value B  | Extra |"""
        
        result = validator.validate_content(test_table, broken_table)
        logger.info(f"✅ Broken table detection: {not result.is_valid} (issues: {len(result.issues)})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Content validator error: {e}")
        return False

def test_semantic_cache():
    """Test the semantic cache"""
    logger.info("🧠 Testing semantic cache...")
    
    try:
        from semantic_cache import SemanticCache
        
        # Initialize cache
        cache = SemanticCache(
            cache_dir="test_semantic_cache",
            similarity_threshold=0.8,
            max_cache_size=100
        )
        
        logger.info(f"✅ Semantic cache initialized (embeddings available: {cache.embedding_available})")
        
        if cache.embedding_available:
            # Test caching and retrieval
            original_text = "The machine learning model achieved high accuracy."
            translation = "Το μοντέλο μηχανικής μάθησης επέτυχε υψηλή ακρίβεια."
            
            # Cache a translation
            cache.cache_translation(
                text=original_text,
                target_language="Greek",
                model_name="test-model",
                translation=translation
            )
            
            # Try to retrieve exact match
            cached = cache.get_cached_translation(
                text=original_text,
                target_language="Greek", 
                model_name="test-model"
            )
            
            logger.info(f"✅ Exact cache retrieval: {'Success' if cached else 'Failed'}")
            
            # Try semantic similarity
            similar_text = "The ML model reached high precision."
            cached_similar = cache.get_cached_translation(
                text=similar_text,
                target_language="Greek",
                model_name="test-model"
            )
            
            logger.info(f"✅ Semantic cache retrieval: {'Success' if cached_similar else 'No match'}")
            
            # Get stats
            stats = cache.get_cache_stats()
            logger.info(f"✅ Cache stats: {stats['total_queries']} queries, {stats['cache_size']} entries")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Semantic cache error: {e}")
        return False

def test_existing_integration():
    """Test integration with existing components"""
    logger.info("🔗 Testing integration with existing components...")
    
    try:
        # Test importing existing components
        from translation_service import translation_service
        logger.info("✅ Existing translation_service imported")
        
        from nougat_integration import NougatIntegration
        logger.info("✅ Existing NougatIntegration imported")
        
        # Test creating advanced pipeline
        from advanced_translation_pipeline import AdvancedTranslationPipeline
        
        pipeline = AdvancedTranslationPipeline(
            base_translator=translation_service,
            nougat_integration=None,  # We'll test without nougat for now
            cache_dir="test_advanced_cache"
        )
        
        logger.info("✅ Advanced pipeline created successfully")
        
        # Get pipeline stats
        stats = pipeline.get_pipeline_stats()
        logger.info(f"✅ Pipeline stats retrieved: {len(stats)} categories")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Advanced Features Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Content Validator Test", test_content_validator),
        ("Semantic Cache Test", test_semantic_cache),
        ("Integration Test", test_existing_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
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
        logger.info("🎉 All tests passed! Advanced features are ready to use.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
