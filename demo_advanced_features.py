#!/usr/bin/env python3
"""
Demo script showing the advanced features in action
"""

import asyncio
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_self_correcting_translation():
    """Demo the self-correcting translation feature"""
    
    logger.info("🔧 DEMO: Self-Correcting Translation")
    logger.info("=" * 50)
    
    from self_correcting_translator import SelfCorrectingTranslator
    from translation_service import translation_service
    
    # Initialize self-correcting translator
    correcting_translator = SelfCorrectingTranslator(
        base_translator=translation_service,
        max_correction_attempts=2
    )
    
    # Test with a table that might have translation issues
    test_table = """| Feature | Description | Status |
|---------|-------------|--------|
| OCR Engine | Optical Character Recognition | ✅ Active |
| Translation | Multi-language support | ✅ Active |
| Validation | Structure integrity checking | 🔄 Testing |
| Caching | Semantic similarity matching | 🆕 New |"""
    
    logger.info("📝 Original table:")
    logger.info(test_table)
    
    logger.info("\n🔄 Translating with validation and correction...")
    start_time = time.time()
    
    result = await correcting_translator.translate_with_validation(
        text=test_table,
        target_language="Greek",
        item_type="table"
    )
    
    processing_time = time.time() - start_time
    
    logger.info(f"\n✅ Translation completed in {processing_time:.2f}s")
    logger.info(f"📊 Validation passed: {result['validation_result'].is_valid}")
    logger.info(f"🔧 Correction attempts: {len(result['correction_attempts'])}")
    logger.info(f"🎯 Final confidence: {result['final_confidence']:.2f}")
    
    if result['validation_result'].issues:
        logger.info("⚠️ Issues found:")
        for issue in result['validation_result'].issues:
            logger.info(f"   • {issue}")
    
    logger.info(f"\n📝 Translated table:")
    logger.info(result['translation'])
    
    return result

async def demo_semantic_caching():
    """Demo the semantic caching feature"""
    
    logger.info("\n🧠 DEMO: Semantic Caching")
    logger.info("=" * 50)
    
    from semantic_cache import SemanticCache
    
    # Initialize semantic cache
    cache = SemanticCache(
        cache_dir="demo_semantic_cache",
        similarity_threshold=0.8,
        max_cache_size=100
    )
    
    # Test texts with semantic similarity
    texts = [
        "The machine learning model achieved 95% accuracy on the test dataset.",
        "The ML algorithm reached 95% precision on the testing data.",  # Similar
        "The artificial intelligence system obtained 95% correctness on evaluation data.",  # Similar
        "Today is a sunny day with clear skies and warm weather."  # Different
    ]
    
    logger.info("📝 Test texts:")
    for i, text in enumerate(texts, 1):
        logger.info(f"   {i}. {text}")
    
    # Cache the first translation
    logger.info("\n💾 Caching first translation...")
    translation1 = "Το μοντέλο μηχανικής μάθησης επέτυχε ακρίβεια 95% στο σύνολο δεδομένων δοκιμής."
    cache.cache_translation(
        text=texts[0],
        target_language="Greek",
        model_name="gemini-1.5-pro",
        translation=translation1,
        quality_score=0.95
    )
    
    # Test semantic similarity matching
    logger.info("\n🔍 Testing semantic similarity matching:")
    
    for i, text in enumerate(texts[1:], 2):
        cached_result = cache.get_cached_translation(
            text=text,
            target_language="Greek",
            model_name="gemini-1.5-pro"
        )
        
        if cached_result:
            logger.info(f"   Text {i}: ✅ Cache hit (semantic match)")
            logger.info(f"      → {cached_result[:50]}...")
        else:
            logger.info(f"   Text {i}: ❌ No cache match")
    
    # Display cache statistics
    stats = cache.get_cache_stats()
    logger.info(f"\n📊 Cache Statistics:")
    logger.info(f"   Total queries: {stats['total_queries']}")
    logger.info(f"   Hit rate: {stats['hit_rate']:.1%}")
    logger.info(f"   Semantic hit rate: {stats['semantic_hit_rate']:.1%}")
    logger.info(f"   Cache size: {stats['cache_size']} entries")
    
    return cache

def demo_content_validation():
    """Demo the content validation feature"""
    
    logger.info("\n🔍 DEMO: Content Validation")
    logger.info("=" * 50)
    
    from structured_content_validator import StructuredContentValidator
    
    validator = StructuredContentValidator()
    
    # Test different content types
    test_cases = [
        {
            "name": "Valid Table",
            "original": "| Col1 | Col2 |\n|------|------|\n| A | B |\n| C | D |",
            "translated": "| Στήλη1 | Στήλη2 |\n|--------|--------|\n| Α | Β |\n| Γ | Δ |"
        },
        {
            "name": "Broken Table",
            "original": "| Col1 | Col2 |\n|------|------|\n| A | B |\n| C | D |",
            "translated": "| Στήλη1 | Στήλη2 |\n| Α | Β | Επιπλέον |\n| Γ | Δ |"
        },
        {
            "name": "Code Block",
            "original": "```python\nprint('Hello World')\n```",
            "translated": "```python\nprint('Γεια σου Κόσμε')\n```"
        },
        {
            "name": "LaTeX Formula",
            "original": "$$E = mc^2$$",
            "translated": "$$E = mc^2$$"
        }
    ]
    
    logger.info("📝 Testing content validation:")
    
    for test_case in test_cases:
        result = validator.validate_content(
            test_case["original"], 
            test_case["translated"]
        )
        
        status = "✅ Valid" if result.is_valid else "❌ Invalid"
        logger.info(f"   {test_case['name']}: {status} (confidence: {result.confidence:.2f})")
        
        if result.issues:
            for issue in result.issues:
                logger.info(f"      Issue: {issue}")
        
        if result.suggested_fixes:
            for fix in result.suggested_fixes:
                logger.info(f"      Fix: {fix}")
    
    return validator

async def demo_hybrid_ocr():
    """Demo the hybrid OCR feature (without actual PDF)"""
    
    logger.info("\n📖 DEMO: Hybrid OCR Strategy")
    logger.info("=" * 50)
    
    from hybrid_ocr_processor import HybridOCRProcessor
    from nougat_integration import NougatIntegration
    
    # Initialize hybrid OCR processor
    nougat_integration = NougatIntegration()
    hybrid_ocr = HybridOCRProcessor(nougat_integration=nougat_integration)
    
    logger.info("🔧 Hybrid OCR Processor initialized")
    logger.info(f"   Available engines: {[e.value for e in hybrid_ocr.available_engines]}")
    logger.info(f"   Quality threshold: {hybrid_ocr.quality_threshold}")
    logger.info(f"   Fallback threshold: {hybrid_ocr.fallback_threshold}")
    
    # Show quality assessment capabilities
    logger.info("\n📊 Quality Assessment Features:")
    logger.info("   • Text confidence scoring")
    logger.info("   • Layout coherence analysis")
    logger.info("   • Content completeness checking")
    logger.info("   • Language consistency validation")
    logger.info("   • Automatic engine fallback")
    
    return hybrid_ocr

async def main():
    """Run all demos"""
    
    logger.info("🎯 Advanced Features Demo")
    logger.info("=" * 60)
    
    try:
        # Demo 1: Self-correcting translation
        await demo_self_correcting_translation()
        
        # Demo 2: Semantic caching
        await demo_semantic_caching()
        
        # Demo 3: Content validation
        demo_content_validation()
        
        # Demo 4: Hybrid OCR
        await demo_hybrid_ocr()
        
        logger.info("\n🎉 All demos completed successfully!")
        logger.info("\n💡 Key Benefits:")
        logger.info("   ✅ Improved translation quality through validation")
        logger.info("   ✅ Reduced API costs through semantic caching")
        logger.info("   ✅ Better OCR reliability with hybrid strategy")
        logger.info("   ✅ Automatic error detection and correction")
        
        logger.info("\n🚀 Ready to use with your PDF translation workflow!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
