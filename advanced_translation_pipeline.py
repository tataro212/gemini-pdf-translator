"""
Advanced Translation Pipeline Integration

This module demonstrates how to integrate the three advanced features:
1. Self-Correcting Translation Loop
2. Hybrid OCR Strategy
3. Semantic Caching

It provides a complete enhanced translation pipeline that can be integrated
with the existing PDF translation workflow.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from self_correcting_translator import SelfCorrectingTranslator
from hybrid_ocr_processor import HybridOCRProcessor, OCREngine
from semantic_cache import SemanticCache

logger = logging.getLogger(__name__)

@dataclass
class AdvancedTranslationResult:
    """Result from advanced translation pipeline"""
    translated_text: str
    ocr_engine_used: str
    ocr_quality_score: float
    validation_passed: bool
    correction_attempts: int
    cache_hit: bool
    semantic_cache_hit: bool
    processing_time: float
    confidence_score: float
    metadata: Dict[str, Any]

class AdvancedTranslationPipeline:
    """
    Enhanced translation pipeline that combines all three advanced features
    for maximum quality and efficiency.
    """
    
    def __init__(self, base_translator, nougat_integration=None,
                 cache_dir: str = "advanced_cache", config_manager=None):
        """
        Initialize the advanced translation pipeline.

        Args:
            base_translator: Base translation service (e.g., translation_service)
            nougat_integration: Existing NougatIntegration instance
            cache_dir: Directory for semantic cache storage
            config_manager: Configuration manager for settings
        """
        # Initialize components
        self.semantic_cache = SemanticCache(cache_dir=cache_dir)
        self.hybrid_ocr = HybridOCRProcessor(
            nougat_integration=nougat_integration,
            config_manager=config_manager
        )
        self.self_correcting_translator = SelfCorrectingTranslator(
            base_translator=base_translator,
            max_correction_attempts=2
        )
        
        # Pipeline statistics
        self.pipeline_stats = {
            'total_documents': 0,
            'ocr_engine_usage': {},
            'cache_performance': {},
            'correction_performance': {},
            'processing_times': []
        }
        
        logger.info("🚀 Advanced Translation Pipeline initialized")
        logger.info("   ✅ Semantic caching enabled")
        logger.info("   ✅ Hybrid OCR strategy enabled")
        logger.info("   ✅ Self-correcting translation enabled")
    
    async def process_document_advanced(self, pdf_path: str, output_dir: str,
                                      target_language: str = "Greek",
                                      preferred_ocr: OCREngine = OCREngine.NOUGAT) -> AdvancedTranslationResult:
        """
        Process document using the complete advanced pipeline.
        
        Args:
            pdf_path: Path to PDF document
            output_dir: Output directory
            target_language: Target language for translation
            preferred_ocr: Preferred OCR engine
            
        Returns:
            AdvancedTranslationResult with comprehensive processing information
        """
        start_time = time.time()
        self.pipeline_stats['total_documents'] += 1
        
        logger.info(f"🔄 Starting advanced processing: {pdf_path}")
        
        try:
            # Step 1: Hybrid OCR Processing
            logger.info("📖 Step 1: Hybrid OCR Processing")
            ocr_result = await self.hybrid_ocr.process_document_hybrid(
                pdf_path, output_dir, preferred_ocr
            )
            
            # Update OCR statistics
            engine_name = ocr_result.engine.value
            self.pipeline_stats['ocr_engine_usage'][engine_name] = (
                self.pipeline_stats['ocr_engine_usage'].get(engine_name, 0) + 1
            )
            
            if not ocr_result.text.strip():
                logger.error("❌ OCR processing failed - no text extracted")
                return self._create_error_result("OCR processing failed", start_time)
            
            logger.info(f"✅ OCR completed using {engine_name} (quality: {ocr_result.quality_metrics.get('overall_score', 0):.2f})")
            
            # Step 2: Semantic Cache Check
            logger.info("🧠 Step 2: Semantic Cache Check")
            cached_translation = self.semantic_cache.get_cached_translation(
                ocr_result.text, target_language, "gemini-1.5-pro"
            )
            
            cache_hit = cached_translation is not None
            semantic_cache_hit = False
            
            if cache_hit:
                # Check if it was a semantic hit (not exact)
                cache_stats = self.semantic_cache.get_cache_stats()
                semantic_cache_hit = cache_stats['semantic_hits'] > 0
                
                logger.info(f"🎯 Cache hit! {'Semantic' if semantic_cache_hit else 'Exact'} match found")
                
                processing_time = time.time() - start_time
                return AdvancedTranslationResult(
                    translated_text=cached_translation,
                    ocr_engine_used=engine_name,
                    ocr_quality_score=ocr_result.quality_metrics.get('overall_score', 0),
                    validation_passed=True,
                    correction_attempts=0,
                    cache_hit=True,
                    semantic_cache_hit=semantic_cache_hit,
                    processing_time=processing_time,
                    confidence_score=1.0,
                    metadata={'source': 'cache', 'ocr_metadata': ocr_result.metadata}
                )
            
            # Step 3: Self-Correcting Translation
            logger.info("🔧 Step 3: Self-Correcting Translation")
            translation_result = await self.self_correcting_translator.translate_with_validation(
                ocr_result.text, target_language
            )
            
            # Step 4: Cache the Result
            logger.info("💾 Step 4: Caching Translation")
            quality_score = translation_result['final_confidence']
            self.semantic_cache.cache_translation(
                ocr_result.text, target_language, "gemini-1.5-pro",
                translation_result['translation'], quality_score=quality_score
            )
            
            # Compile final result
            processing_time = time.time() - start_time
            self.pipeline_stats['processing_times'].append(processing_time)
            
            result = AdvancedTranslationResult(
                translated_text=translation_result['translation'],
                ocr_engine_used=engine_name,
                ocr_quality_score=ocr_result.quality_metrics.get('overall_score', 0),
                validation_passed=translation_result['validation_result'].is_valid,
                correction_attempts=len(translation_result['correction_attempts']),
                cache_hit=False,
                semantic_cache_hit=False,
                processing_time=processing_time,
                confidence_score=quality_score,
                metadata={
                    'ocr_metadata': ocr_result.metadata,
                    'validation_issues': translation_result['validation_result'].issues,
                    'correction_attempts': translation_result['correction_attempts']
                }
            )
            
            logger.info(f"✅ Advanced processing completed in {processing_time:.2f}s")
            logger.info(f"   OCR Engine: {engine_name}")
            logger.info(f"   Validation: {'✅' if result.validation_passed else '❌'}")
            logger.info(f"   Corrections: {result.correction_attempts}")
            logger.info(f"   Confidence: {result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Advanced processing failed: {e}")
            return self._create_error_result(f"Processing failed: {e}", start_time)
    
    async def process_text_chunks_advanced(self, text_chunks: List[str], 
                                         target_language: str = "Greek") -> List[AdvancedTranslationResult]:
        """
        Process multiple text chunks using advanced translation features.
        
        Args:
            text_chunks: List of text chunks to translate
            target_language: Target language
            
        Returns:
            List of AdvancedTranslationResult for each chunk
        """
        logger.info(f"🔄 Processing {len(text_chunks)} text chunks with advanced pipeline")
        
        results = []
        
        for i, chunk in enumerate(text_chunks):
            logger.info(f"📝 Processing chunk {i+1}/{len(text_chunks)}")
            start_time = time.time()
            
            try:
                # Check semantic cache
                cached_translation = self.semantic_cache.get_cached_translation(
                    chunk, target_language, "gemini-1.5-pro"
                )
                
                if cached_translation:
                    cache_stats = self.semantic_cache.get_cache_stats()
                    semantic_hit = cache_stats['semantic_hits'] > 0
                    
                    result = AdvancedTranslationResult(
                        translated_text=cached_translation,
                        ocr_engine_used="N/A",
                        ocr_quality_score=1.0,
                        validation_passed=True,
                        correction_attempts=0,
                        cache_hit=True,
                        semantic_cache_hit=semantic_hit,
                        processing_time=time.time() - start_time,
                        confidence_score=1.0,
                        metadata={'source': 'cache'}
                    )
                else:
                    # Use self-correcting translation
                    translation_result = await self.self_correcting_translator.translate_with_validation(
                        chunk, target_language
                    )
                    
                    # Cache the result
                    self.semantic_cache.cache_translation(
                        chunk, target_language, "gemini-1.5-pro",
                        translation_result['translation'],
                        quality_score=translation_result['final_confidence']
                    )
                    
                    result = AdvancedTranslationResult(
                        translated_text=translation_result['translation'],
                        ocr_engine_used="N/A",
                        ocr_quality_score=1.0,
                        validation_passed=translation_result['validation_result'].is_valid,
                        correction_attempts=len(translation_result['correction_attempts']),
                        cache_hit=False,
                        semantic_cache_hit=False,
                        processing_time=time.time() - start_time,
                        confidence_score=translation_result['final_confidence'],
                        metadata={
                            'validation_issues': translation_result['validation_result'].issues,
                            'correction_attempts': translation_result['correction_attempts']
                        }
                    )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Failed to process chunk {i+1}: {e}")
                results.append(self._create_error_result(f"Chunk processing failed: {e}", start_time))
        
        return results
    
    def _create_error_result(self, error_message: str, start_time: float) -> AdvancedTranslationResult:
        """Create an error result"""
        return AdvancedTranslationResult(
            translated_text="",
            ocr_engine_used="error",
            ocr_quality_score=0.0,
            validation_passed=False,
            correction_attempts=0,
            cache_hit=False,
            semantic_cache_hit=False,
            processing_time=time.time() - start_time,
            confidence_score=0.0,
            metadata={'error': error_message}
        )
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        # Get component stats
        cache_stats = self.semantic_cache.get_cache_stats()
        correction_stats = self.self_correcting_translator.get_correction_stats()
        ocr_stats = self.hybrid_ocr.get_processing_stats()
        
        # Calculate averages
        avg_processing_time = (
            sum(self.pipeline_stats['processing_times']) / len(self.pipeline_stats['processing_times'])
            if self.pipeline_stats['processing_times'] else 0.0
        )
        
        return {
            'pipeline_overview': {
                'total_documents_processed': self.pipeline_stats['total_documents'],
                'average_processing_time': avg_processing_time,
                'ocr_engine_usage': self.pipeline_stats['ocr_engine_usage']
            },
            'semantic_cache_performance': cache_stats,
            'correction_performance': correction_stats,
            'ocr_performance': ocr_stats
        }
    
    def optimize_pipeline(self) -> Dict[str, str]:
        """Provide optimization recommendations based on usage statistics"""
        stats = self.get_pipeline_stats()
        recommendations = []
        
        # Cache performance recommendations
        cache_hit_rate = stats['semantic_cache_performance']['hit_rate']
        if cache_hit_rate < 0.3:
            recommendations.append("Consider lowering semantic similarity threshold to increase cache hits")
        elif cache_hit_rate > 0.8:
            recommendations.append("Cache performance is excellent - consider increasing similarity threshold for higher precision")
        
        # Correction performance recommendations
        correction_rate = stats['correction_performance'].get('correction_success_rate', 0)
        if correction_rate < 0.7:
            recommendations.append("High correction failure rate - consider improving base translation prompts")
        
        # OCR performance recommendations
        ocr_usage = stats['pipeline_overview']['ocr_engine_usage']
        if 'tesseract' in ocr_usage and ocr_usage['tesseract'] > ocr_usage.get('nougat', 0):
            recommendations.append("Frequent Tesseract usage detected - consider improving document quality or Nougat configuration")
        
        return {
            'recommendations': recommendations,
            'current_performance': f"Cache hit rate: {cache_hit_rate:.1%}, Avg processing time: {stats['pipeline_overview']['average_processing_time']:.2f}s"
        }
