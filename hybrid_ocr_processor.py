"""
Hybrid OCR Strategy for Scanned Documents

This module provides a hybrid OCR approach that dynamically switches between
Nougat and traditional OCR engines based on quality assessment.
"""

import os
import logging
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class OCREngine(Enum):
    """Available OCR engines"""
    NOUGAT = "nougat"
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"

@dataclass
class OCRResult:
    """Result from OCR processing"""
    text: str
    confidence: float
    engine: OCREngine
    processing_time: float
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class QualityAssessment:
    """Quality assessment of OCR output"""
    overall_score: float
    text_confidence: float
    layout_coherence: float
    content_completeness: float
    language_consistency: float
    issues: List[str]
    recommendations: List[str]

class HybridOCRProcessor:
    """
    Intelligent OCR processor that dynamically selects the best OCR engine
    based on document characteristics and quality assessment.
    """
    
    def __init__(self, nougat_integration=None, config_manager=None):
        """
        Initialize the hybrid OCR processor.

        Args:
            nougat_integration: Existing NougatIntegration instance
            config_manager: Configuration manager for settings
        """
        self.nougat_integration = nougat_integration
        self.config_manager = config_manager
        self.quality_threshold = 0.7  # Minimum quality score for Nougat
        self.fallback_threshold = 0.4  # Minimum quality for any engine

        # Check available engines
        self.available_engines = self._check_available_engines()
        
        # Quality assessment patterns
        self.quality_patterns = {
            'garbled_text': re.compile(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]{3,}'),
            'repeated_chars': re.compile(r'(.)\1{4,}'),
            'incomplete_words': re.compile(r'\b\w{1,2}\b'),
            'mixed_languages': re.compile(r'[^\x00-\x7F]+'),  # Non-ASCII characters
            'structural_markers': re.compile(r'(#+\s|\*\s|\d+\.\s|\|.*\|)')
        }
        
        logger.info(f"🔧 Hybrid OCR processor initialized")
        logger.info(f"   Available engines: {[e.value for e in self.available_engines]}")
        logger.info(f"   Quality threshold: {self.quality_threshold}")
    
    def _check_available_engines(self) -> List[OCREngine]:
        """Check which OCR engines are available"""
        available = []
        
        # Check Nougat
        if self.nougat_integration and self.nougat_integration.nougat_available:
            available.append(OCREngine.NOUGAT)
        
        # Check Tesseract
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                available.append(OCREngine.TESSERACT)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check EasyOCR (only if enabled in config)
        enable_easyocr = True
        if self.config_manager:
            enable_easyocr = self.config_manager.get_config_value('TranslationEnhancements', 'enable_easyocr', False, bool)

        if enable_easyocr:
            try:
                import easyocr
                available.append(OCREngine.EASYOCR)
            except ImportError:
                pass
        
        return available
    
    async def process_document_hybrid(self, pdf_path: str, output_dir: str, 
                                    preferred_engine: OCREngine = OCREngine.NOUGAT) -> OCRResult:
        """
        Process document using hybrid OCR strategy.
        
        Args:
            pdf_path: Path to PDF document
            output_dir: Output directory for results
            preferred_engine: Preferred OCR engine to try first
            
        Returns:
            OCRResult with best available output
        """
        logger.info(f"🔄 Starting hybrid OCR processing: {os.path.basename(pdf_path)}")
        
        # Try preferred engine first
        if preferred_engine in self.available_engines:
            logger.info(f"🎯 Trying preferred engine: {preferred_engine.value}")
            result = await self._process_with_engine(pdf_path, output_dir, preferred_engine)
            
            if result:
                quality = self._assess_quality(result)
                logger.info(f"📊 Quality assessment: {quality.overall_score:.2f}")
                
                if quality.overall_score >= self.quality_threshold:
                    logger.info(f"✅ {preferred_engine.value} output meets quality threshold")
                    result.quality_metrics = quality.__dict__
                    return result
                else:
                    logger.warning(f"⚠️ {preferred_engine.value} quality below threshold: {quality.overall_score:.2f}")
                    logger.warning(f"   Issues: {', '.join(quality.issues)}")
        
        # Try fallback engines
        fallback_engines = [e for e in self.available_engines if e != preferred_engine]
        best_result = None
        best_quality_score = 0.0
        
        for engine in fallback_engines:
            logger.info(f"🔄 Trying fallback engine: {engine.value}")
            
            try:
                result = await self._process_with_engine(pdf_path, output_dir, engine)
                if result:
                    quality = self._assess_quality(result)
                    logger.info(f"📊 {engine.value} quality: {quality.overall_score:.2f}")
                    
                    if quality.overall_score > best_quality_score:
                        best_result = result
                        best_quality_score = quality.overall_score
                        best_result.quality_metrics = quality.__dict__
                        
                        if quality.overall_score >= self.quality_threshold:
                            logger.info(f"✅ {engine.value} meets quality threshold")
                            break
                            
            except Exception as e:
                logger.error(f"❌ {engine.value} processing failed: {e}")
                continue
        
        if best_result and best_quality_score >= self.fallback_threshold:
            logger.info(f"✅ Using best available result from {best_result.engine.value}")
            return best_result
        else:
            logger.error(f"❌ No OCR engine produced acceptable quality output")
            # Return empty result
            return OCRResult(
                text="",
                confidence=0.0,
                engine=OCREngine.NOUGAT,
                processing_time=0.0,
                quality_metrics={},
                metadata={'error': 'All OCR engines failed quality assessment'}
            )
    
    async def _process_with_engine(self, pdf_path: str, output_dir: str, 
                                 engine: OCREngine) -> Optional[OCRResult]:
        """Process document with specific OCR engine"""
        import time
        start_time = time.time()
        
        try:
            if engine == OCREngine.NOUGAT:
                return await self._process_with_nougat(pdf_path, output_dir, start_time)
            elif engine == OCREngine.TESSERACT:
                return await self._process_with_tesseract(pdf_path, output_dir, start_time)
            elif engine == OCREngine.EASYOCR:
                return await self._process_with_easyocr(pdf_path, output_dir, start_time)
            else:
                logger.error(f"Unsupported OCR engine: {engine}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing with {engine.value}: {e}")
            return None
    
    async def _process_with_nougat(self, pdf_path: str, output_dir: str, start_time: float) -> OCRResult:
        """Process document with Nougat"""
        if not self.nougat_integration:
            raise Exception("Nougat integration not available")
        
        # Use existing nougat integration
        nougat_result = await self.nougat_integration.process_pdf_with_nougat(pdf_path, output_dir)
        
        processing_time = time.time() - start_time
        
        return OCRResult(
            text=nougat_result.get('content', ''),
            confidence=nougat_result.get('confidence', 0.5),
            engine=OCREngine.NOUGAT,
            processing_time=processing_time,
            quality_metrics={},
            metadata=nougat_result
        )
    
    async def _process_with_tesseract(self, pdf_path: str, output_dir: str, start_time: float) -> OCRResult:
        """Process document with Tesseract OCR"""
        import time
        
        # Convert PDF to images first
        images = self._pdf_to_images(pdf_path, output_dir)
        
        all_text = []
        total_confidence = 0.0
        
        for image_path in images:
            # Run Tesseract with confidence scores and proper encoding
            cmd = ['tesseract', image_path, 'stdout', '-c', 'tessedit_create_tsv=1']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')

                if result.returncode == 0 and result.stdout:
                    # Parse TSV output for text and confidence
                    lines = result.stdout.strip().split('\n')
                    page_text = []
                    confidences = []

                    for line in lines[1:]:  # Skip header
                        parts = line.split('\t')
                        if len(parts) >= 12 and parts[11].strip():  # Text column
                            page_text.append(parts[11])
                            try:
                                conf = float(parts[10])  # Confidence column
                                confidences.append(conf)
                            except (ValueError, IndexError):
                                confidences.append(50.0)  # Default confidence

                    if page_text:  # Only add if we got text
                        all_text.append(' '.join(page_text))
                        if confidences:
                            total_confidence += sum(confidences) / len(confidences)
                else:
                    # Fallback: try simple text extraction
                    cmd_simple = ['tesseract', image_path, 'stdout']
                    result_simple = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
                    if result_simple.returncode == 0 and result_simple.stdout.strip():
                        all_text.append(result_simple.stdout.strip())
                        total_confidence += 70.0  # Default confidence for simple extraction

            except subprocess.TimeoutExpired:
                logger.warning(f"Tesseract timeout for image: {image_path}")
                continue
            except Exception as e:
                logger.warning(f"Tesseract error for image {image_path}: {e}")
                continue
        
        # Clean up temporary images
        for image_path in images:
            try:
                os.remove(image_path)
            except:
                pass
        
        final_text = '\n\n'.join(all_text)
        avg_confidence = total_confidence / len(images) if images else 0.0
        processing_time = time.time() - start_time
        
        return OCRResult(
            text=final_text,
            confidence=avg_confidence / 100.0,  # Normalize to 0-1
            engine=OCREngine.TESSERACT,
            processing_time=processing_time,
            quality_metrics={},
            metadata={'pages_processed': len(images)}
        )
    
    async def _process_with_easyocr(self, pdf_path: str, output_dir: str, start_time: float) -> OCRResult:
        """Process document with EasyOCR"""
        import easyocr
        import time
        
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])  # Add more languages as needed
        
        # Convert PDF to images
        images = self._pdf_to_images(pdf_path, output_dir)
        
        all_text = []
        total_confidence = 0.0
        
        for image_path in images:
            results = reader.readtext(image_path)
            
            page_text = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                page_text.append(text)
                confidences.append(confidence)
            
            all_text.append(' '.join(page_text))
            if confidences:
                total_confidence += sum(confidences) / len(confidences)
        
        # Clean up temporary images
        for image_path in images:
            try:
                os.remove(image_path)
            except:
                pass
        
        final_text = '\n\n'.join(all_text)
        avg_confidence = total_confidence / len(images) if images else 0.0
        processing_time = time.time() - start_time
        
        return OCRResult(
            text=final_text,
            confidence=avg_confidence,
            engine=OCREngine.EASYOCR,
            processing_time=processing_time,
            quality_metrics={},
            metadata={'pages_processed': len(images)}
        )
    
    def _pdf_to_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """Convert PDF pages to images for OCR processing"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                
                image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)
            
            doc.close()
            return image_paths
            
        except ImportError:
            logger.error("PyMuPDF not available for PDF to image conversion")
            return []
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def _assess_quality(self, ocr_result: OCRResult) -> QualityAssessment:
        """Assess the quality of OCR output"""
        text = ocr_result.text
        issues = []
        recommendations = []

        # 1. Text confidence score (from OCR engine)
        text_confidence = ocr_result.confidence

        # 2. Layout coherence (check for structural elements)
        layout_score = self._assess_layout_coherence(text)

        # 3. Content completeness (check for garbled or incomplete text)
        completeness_score = self._assess_content_completeness(text, issues, recommendations)

        # 4. Language consistency
        language_score = self._assess_language_consistency(text, issues)

        # Calculate overall score (weighted average)
        overall_score = (
            text_confidence * 0.3 +
            layout_score * 0.25 +
            completeness_score * 0.3 +
            language_score * 0.15
        )

        return QualityAssessment(
            overall_score=overall_score,
            text_confidence=text_confidence,
            layout_coherence=layout_score,
            content_completeness=completeness_score,
            language_consistency=language_score,
            issues=issues,
            recommendations=recommendations
        )

    def _assess_layout_coherence(self, text: str) -> float:
        """Assess how well the layout structure is preserved"""
        if not text.strip():
            return 0.0

        score = 0.5  # Base score

        # Check for structural markers
        if self.quality_patterns['structural_markers'].search(text):
            score += 0.3  # Bonus for preserved structure

        # Check for reasonable paragraph breaks
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if 10 <= avg_paragraph_length <= 200:  # Reasonable paragraph length
                score += 0.2

        return min(score, 1.0)

    def _assess_content_completeness(self, text: str, issues: List[str],
                                   recommendations: List[str]) -> float:
        """Assess content completeness and detect issues"""
        if not text.strip():
            issues.append("No text extracted")
            recommendations.append("Try different OCR engine or improve image quality")
            return 0.0

        score = 1.0

        # Check for garbled text
        garbled_matches = self.quality_patterns['garbled_text'].findall(text)
        if garbled_matches:
            penalty = min(len(garbled_matches) * 0.1, 0.4)
            score -= penalty
            issues.append(f"Garbled text detected ({len(garbled_matches)} instances)")
            recommendations.append("Consider using different OCR engine for better text recognition")

        # Check for repeated characters (OCR artifacts)
        repeated_matches = self.quality_patterns['repeated_chars'].findall(text)
        if repeated_matches:
            penalty = min(len(repeated_matches) * 0.05, 0.2)
            score -= penalty
            issues.append(f"Repeated character artifacts ({len(repeated_matches)} instances)")

        # Check for too many incomplete words
        words = text.split()
        if words:
            incomplete_words = len(self.quality_patterns['incomplete_words'].findall(text))
            incomplete_ratio = incomplete_words / len(words)
            if incomplete_ratio > 0.3:
                score -= 0.3
                issues.append(f"High ratio of incomplete words ({incomplete_ratio:.1%})")
                recommendations.append("Document may be low quality or heavily damaged")

        return max(score, 0.0)

    def _assess_language_consistency(self, text: str, issues: List[str]) -> float:
        """Assess language consistency in the text"""
        if not text.strip():
            return 0.0

        # Check for mixed character sets (may indicate OCR confusion)
        non_ascii_chars = len(self.quality_patterns['mixed_languages'].findall(text))
        total_chars = len(text)

        if total_chars == 0:
            return 0.0

        non_ascii_ratio = non_ascii_chars / total_chars

        # Some non-ASCII is normal for many languages, but too much may indicate issues
        if non_ascii_ratio > 0.5:
            issues.append(f"High ratio of non-ASCII characters ({non_ascii_ratio:.1%})")
            return 0.3
        elif non_ascii_ratio > 0.2:
            return 0.7
        else:
            return 1.0

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about OCR processing performance"""
        return {
            'available_engines': [e.value for e in self.available_engines],
            'quality_threshold': self.quality_threshold,
            'fallback_threshold': self.fallback_threshold
        }
