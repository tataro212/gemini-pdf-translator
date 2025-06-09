"""
Advanced Features Integration Guide

This module provides examples and integration patterns for the three advanced features:
1. Self-Correcting Translation Loop for Tables and Code
2. Hybrid OCR Strategy for Scanned Documents  
3. Semantic Caching using Vector Embeddings

It shows how to integrate these with your existing PDF translation pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Any

# Import your existing components
from config_manager import config_manager
from translation_service import translation_service
from nougat_integration import NougatIntegration

# Import the new advanced components
from advanced_translation_pipeline import AdvancedTranslationPipeline
from self_correcting_translator import SelfCorrectingTranslator
from hybrid_ocr_processor import HybridOCRProcessor, OCREngine
from semantic_cache import SemanticCache

logger = logging.getLogger(__name__)

class EnhancedPDFTranslator:
    """
    Enhanced PDF Translator that integrates all advanced features
    with your existing nougat-first architecture.
    """
    
    def __init__(self):
        """Initialize the enhanced translator with all advanced features"""
        
        # Initialize existing components
        self.base_translator = translation_service
        self.nougat_integration = NougatIntegration()
        
        # Initialize advanced components
        self.advanced_pipeline = AdvancedTranslationPipeline(
            base_translator=self.base_translator,
            nougat_integration=self.nougat_integration,
            cache_dir="advanced_semantic_cache"
        )
        
        logger.info("🚀 Enhanced PDF Translator initialized with advanced features")
    
    async def translate_pdf_enhanced(self, pdf_path: str, output_dir: str, 
                                   target_language: str = None) -> Dict[str, Any]:
        """
        Translate PDF using the enhanced pipeline with all advanced features.
        
        This method demonstrates how to integrate the advanced features
        with your existing workflow.
        """
        if target_language is None:
            target_language = config_manager.translation_enhancement_settings.get('target_language', 'Greek')
        
        logger.info(f"🔄 Starting enhanced PDF translation: {pdf_path}")
        logger.info(f"   Target language: {target_language}")
        logger.info(f"   Advanced features: ✅ Enabled")
        
        # Use the advanced pipeline for complete processing
        result = await self.advanced_pipeline.process_document_advanced(
            pdf_path=pdf_path,
            output_dir=output_dir,
            target_language=target_language,
            preferred_ocr=OCREngine.NOUGAT  # Maintain nougat-first strategy
        )
        
        # Log comprehensive results
        logger.info("📊 Enhanced Translation Results:")
        logger.info(f"   ✅ OCR Engine Used: {result.ocr_engine_used}")
        logger.info(f"   ✅ OCR Quality Score: {result.ocr_quality_score:.2f}")
        logger.info(f"   ✅ Validation Passed: {result.validation_passed}")
        logger.info(f"   ✅ Correction Attempts: {result.correction_attempts}")
        logger.info(f"   ✅ Cache Hit: {result.cache_hit} (Semantic: {result.semantic_cache_hit})")
        logger.info(f"   ✅ Processing Time: {result.processing_time:.2f}s")
        logger.info(f"   ✅ Confidence Score: {result.confidence_score:.2f}")
        
        return {
            'success': True,
            'translated_text': result.translated_text,
            'advanced_metrics': {
                'ocr_engine': result.ocr_engine_used,
                'ocr_quality': result.ocr_quality_score,
                'validation_passed': result.validation_passed,
                'corrections_made': result.correction_attempts,
                'cache_performance': {
                    'hit': result.cache_hit,
                    'semantic_hit': result.semantic_cache_hit
                },
                'processing_time': result.processing_time,
                'confidence': result.confidence_score
            },
            'metadata': result.metadata
        }

# Example 1: Standalone Self-Correcting Translation
async def example_self_correcting_translation():
    """Example of using the self-correcting translator standalone"""
    
    logger.info("🔧 Example 1: Self-Correcting Translation")
    
    # Initialize the self-correcting translator
    correcting_translator = SelfCorrectingTranslator(
        base_translator=translation_service,
        max_correction_attempts=2
    )
    
    # Example table content that might have translation issues
    table_content = """
| Feature | Description | Status |
|---------|-------------|--------|
| OCR | Optical Character Recognition | ✅ Active |
| Translation | Multi-language support | ✅ Active |
| Caching | Semantic similarity matching | 🔄 Beta |
"""
    
    # Translate with validation and correction
    result = await correcting_translator.translate_with_validation(
        text=table_content,
        target_language="Greek",
        item_type="table"
    )
    
    logger.info("📊 Self-Correction Results:")
    logger.info(f"   Validation Passed: {result['validation_result'].is_valid}")
    logger.info(f"   Correction Attempts: {len(result['correction_attempts'])}")
    logger.info(f"   Final Confidence: {result['final_confidence']:.2f}")
    
    if result['correction_attempts']:
        logger.info("   Corrections Made:")
        for i, attempt in enumerate(result['correction_attempts']):
            logger.info(f"     Attempt {i+1}: {'✅ Success' if attempt.success else '❌ Failed'}")
    
    return result

# Example 2: Hybrid OCR Strategy
async def example_hybrid_ocr():
    """Example of using the hybrid OCR processor"""
    
    logger.info("📖 Example 2: Hybrid OCR Strategy")
    
    # Initialize hybrid OCR processor
    nougat_integration = NougatIntegration()
    hybrid_ocr = HybridOCRProcessor(nougat_integration=nougat_integration)
    
    # Example: Process a scanned document
    pdf_path = "example_scanned_document.pdf"  # Replace with actual path
    output_dir = "ocr_output"
    
    try:
        # Process with hybrid strategy (Nougat first, fallback to Tesseract)
        ocr_result = await hybrid_ocr.process_document_hybrid(
            pdf_path=pdf_path,
            output_dir=output_dir,
            preferred_engine=OCREngine.NOUGAT
        )
        
        logger.info("📊 Hybrid OCR Results:")
        logger.info(f"   Engine Used: {ocr_result.engine.value}")
        logger.info(f"   Confidence: {ocr_result.confidence:.2f}")
        logger.info(f"   Processing Time: {ocr_result.processing_time:.2f}s")
        logger.info(f"   Text Length: {len(ocr_result.text)} characters")
        
        # Quality assessment details
        if 'overall_score' in ocr_result.quality_metrics:
            quality = ocr_result.quality_metrics
            logger.info("   Quality Assessment:")
            logger.info(f"     Overall Score: {quality['overall_score']:.2f}")
            logger.info(f"     Text Confidence: {quality['text_confidence']:.2f}")
            logger.info(f"     Layout Coherence: {quality['layout_coherence']:.2f}")
            logger.info(f"     Content Completeness: {quality['content_completeness']:.2f}")
        
        return ocr_result
        
    except Exception as e:
        logger.error(f"❌ Hybrid OCR example failed: {e}")
        return None

# Example 3: Semantic Caching
async def example_semantic_caching():
    """Example of using semantic caching"""
    
    logger.info("🧠 Example 3: Semantic Caching")
    
    # Initialize semantic cache
    semantic_cache = SemanticCache(
        cache_dir="example_semantic_cache",
        similarity_threshold=0.85,
        max_cache_size=1000
    )
    
    # Example texts with semantic similarity
    original_text = "The machine learning model achieved 95% accuracy on the test dataset."
    similar_text = "The ML model reached 95% precision on the testing data."
    different_text = "The weather today is sunny and warm."
    
    target_language = "Greek"
    
    # Cache the first translation
    translation1 = "Το μοντέλο μηχανικής μάθησης επέτυχε ακρίβεια 95% στο σύνολο δεδομένων δοκιμής."
    semantic_cache.cache_translation(
        text=original_text,
        target_language=target_language,
        model_name="gemini-1.5-pro",
        translation=translation1,
        quality_score=0.95
    )
    
    # Test semantic similarity matching
    logger.info("🔍 Testing semantic similarity matching:")
    
    # Should find semantic match
    cached_result1 = semantic_cache.get_cached_translation(
        similar_text, target_language, "gemini-1.5-pro"
    )
    logger.info(f"   Similar text cache hit: {'✅ Yes' if cached_result1 else '❌ No'}")
    
    # Should not find match
    cached_result2 = semantic_cache.get_cached_translation(
        different_text, target_language, "gemini-1.5-pro"
    )
    logger.info(f"   Different text cache hit: {'✅ Yes' if cached_result2 else '❌ No'}")
    
    # Display cache statistics
    stats = semantic_cache.get_cache_stats()
    logger.info("📊 Cache Statistics:")
    logger.info(f"   Total Queries: {stats['total_queries']}")
    logger.info(f"   Hit Rate: {stats['hit_rate']:.1%}")
    logger.info(f"   Semantic Hit Rate: {stats['semantic_hit_rate']:.1%}")
    logger.info(f"   Cache Size: {stats['cache_size']}")
    
    return semantic_cache

# Example 4: Complete Integration
async def example_complete_integration():
    """Example showing complete integration of all advanced features"""
    
    logger.info("🚀 Example 4: Complete Advanced Integration")
    
    # Initialize enhanced translator
    enhanced_translator = EnhancedPDFTranslator()
    
    # Example: Translate a PDF with all advanced features
    pdf_path = "example_document.pdf"  # Replace with actual path
    output_dir = "enhanced_output"
    target_language = "Greek"
    
    try:
        result = await enhanced_translator.translate_pdf_enhanced(
            pdf_path=pdf_path,
            output_dir=output_dir,
            target_language=target_language
        )
        
        if result['success']:
            logger.info("✅ Enhanced translation completed successfully!")
            
            # Display advanced metrics
            metrics = result['advanced_metrics']
            logger.info("📊 Advanced Performance Metrics:")
            logger.info(f"   OCR Engine: {metrics['ocr_engine']}")
            logger.info(f"   OCR Quality: {metrics['ocr_quality']:.2f}")
            logger.info(f"   Validation: {'✅ Passed' if metrics['validation_passed'] else '❌ Failed'}")
            logger.info(f"   Corrections: {metrics['corrections_made']}")
            logger.info(f"   Cache Hit: {'✅ Yes' if metrics['cache_performance']['hit'] else '❌ No'}")
            logger.info(f"   Processing Time: {metrics['processing_time']:.2f}s")
            logger.info(f"   Confidence: {metrics['confidence']:.2f}")
            
            # Get pipeline optimization recommendations
            recommendations = enhanced_translator.advanced_pipeline.optimize_pipeline()
            if recommendations['recommendations']:
                logger.info("💡 Optimization Recommendations:")
                for rec in recommendations['recommendations']:
                    logger.info(f"   • {rec}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Complete integration example failed: {e}")
        return None

# Main example runner
async def run_all_examples():
    """Run all examples to demonstrate the advanced features"""
    
    logger.info("🎯 Running Advanced Features Examples")
    logger.info("=" * 60)
    
    # Run examples
    await example_self_correcting_translation()
    logger.info("-" * 60)
    
    await example_hybrid_ocr()
    logger.info("-" * 60)
    
    await example_semantic_caching()
    logger.info("-" * 60)
    
    await example_complete_integration()
    logger.info("=" * 60)
    
    logger.info("✅ All examples completed!")

# Integration with existing main_workflow.py
def integrate_with_existing_workflow():
    """
    Example of how to integrate advanced features with your existing main_workflow.py
    """
    
    # In your main_workflow.py, you can enhance the UltimatePDFTranslator class:
    
    integration_code = '''
    # Add to your main_workflow.py imports:
    from advanced_translation_pipeline import AdvancedTranslationPipeline
    
    # In UltimatePDFTranslator.__init__():
    self.advanced_pipeline = AdvancedTranslationPipeline(
        base_translator=translation_service,
        nougat_integration=self.nougat_integration,
        cache_dir="semantic_cache"
    )
    
    # In your translation method, add an option for advanced processing:
    async def translate_document_async(self, filepath, output_dir_for_this_file, 
                                     target_language_override=None, use_advanced_features=True):
        
        if use_advanced_features:
            # Use advanced pipeline
            result = await self.advanced_pipeline.process_document_advanced(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language_override or self.target_language
            )
            
            # Process the advanced result...
            return self._process_advanced_result(result)
        else:
            # Use existing workflow
            return await self._existing_translation_workflow(...)
    '''
    
    logger.info("📝 Integration Code Example:")
    logger.info(integration_code)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(run_all_examples())
    
    # Show integration example
    integrate_with_existing_workflow()
