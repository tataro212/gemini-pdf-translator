"""
Final Document Assembly Pipeline

This module implements the comprehensive strategy for final document assembly,
ensuring that Table of Contents and visual elements are correctly placed in
the final translated document while bypassing image translation entirely.

This is the main integration point that connects:
1. Hybrid Content Reconciler (Nougat + PyMuPDF)
2. Enhanced Document Generator (High-fidelity assembly)
3. Image Bypass Logic (No translation for visual content)
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import core components
try:
    from hybrid_content_reconciler import HybridContentReconciler, VisualElement
    from enhanced_document_generator import EnhancedDocumentGenerator
    ASSEMBLY_COMPONENTS_AVAILABLE = True
except ImportError:
    ASSEMBLY_COMPONENTS_AVAILABLE = False

# Import existing pipeline components
try:
    from nougat_integration import NougatIntegration
    from pdf_parser import PDFParser
    from async_translation_service import AsyncTranslationService
    PIPELINE_COMPONENTS_AVAILABLE = True
except ImportError:
    PIPELINE_COMPONENTS_AVAILABLE = False

# Import structured document model
try:
    from structured_document_model import Document as StructuredDocument
    STRUCTURED_MODEL_AVAILABLE = True
except ImportError:
    STRUCTURED_MODEL_AVAILABLE = False

logger = logging.getLogger(__name__)

class FinalDocumentAssemblyPipeline:
    """
    Main pipeline that implements the comprehensive strategy for final document assembly.
    
    This pipeline ensures that:
    1. Nougat and PyMuPDF outputs are properly reconciled
    2. Visual elements are preserved without translation
    3. TOC is generated with accurate page numbers
    4. All content is correctly ordered in the final document
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        if ASSEMBLY_COMPONENTS_AVAILABLE:
            self.reconciler = HybridContentReconciler()
            self.document_generator = EnhancedDocumentGenerator()
        else:
            raise Exception("Assembly components not available")
        
        if PIPELINE_COMPONENTS_AVAILABLE:
            self.nougat_integration = NougatIntegration()
            self.pdf_parser = PDFParser()
            self.translation_service = AsyncTranslationService()
        else:
            raise Exception("Pipeline components not available")
        
        # Pipeline configuration
        self.config = {
            'bypass_image_translation': True,  # USER REQUIREMENT
            'preserve_visual_elements': True,
            'generate_toc': True,
            'parallel_processing': True,
            'quality_validation': True
        }
        
        # Processing statistics
        self.stats = {
            'nougat_blocks': 0,
            'visual_elements': 0,
            'translated_blocks': 0,
            'preserved_images': 0,
            'toc_entries': 0
        }
    
    async def process_pdf_with_final_assembly(self, pdf_path: str, output_dir: str, 
                                            target_language: str = "Greek") -> Dict[str, Any]:
        """
        Main processing method that implements the comprehensive assembly strategy.
        
        Args:
            pdf_path: Path to input PDF
            output_dir: Output directory for processed files
            target_language: Target language for translation
            
        Returns:
            Processing results with file paths and statistics
        """
        if not STRUCTURED_MODEL_AVAILABLE:
            raise Exception("Structured document model not available")
        
        self.logger.info("🚀 Starting Final Document Assembly Pipeline...")
        self.logger.info(f"   • Input PDF: {os.path.basename(pdf_path)}")
        self.logger.info(f"   • Output directory: {output_dir}")
        self.logger.info(f"   • Target language: {target_language}")
        self.logger.info(f"   • Image translation bypass: {self.config['bypass_image_translation']}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Phase 1: Parallel Content Extraction
            self.logger.info("📖 Phase 1: Parallel Content Extraction...")
            nougat_output, visual_elements = await self._extract_content_parallel(pdf_path, output_dir)
            
            # Phase 2: Hybrid Content Reconciliation
            self.logger.info("🔄 Phase 2: Hybrid Content Reconciliation...")
            unified_document = self.reconciler.reconcile_content(
                nougat_output, visual_elements, pdf_path, output_dir
            )
            
            # Phase 3: Selective Translation (Text Only)
            self.logger.info("🌐 Phase 3: Selective Translation...")
            translated_document = await self._translate_text_content_only(
                unified_document, target_language
            )
            
            # Phase 4: High-Fidelity Document Assembly
            self.logger.info("🏗️ Phase 4: High-Fidelity Document Assembly...")
            output_files = self._assemble_final_document(
                translated_document, output_dir, pdf_path
            )
            
            # Phase 5: Quality Validation
            if self.config['quality_validation']:
                self.logger.info("✅ Phase 5: Quality Validation...")
                validation_results = self._validate_final_output(output_files)
            else:
                validation_results = {'status': 'skipped'}
            
            # Generate final report
            results = self._generate_final_report(
                pdf_path, output_dir, output_files, validation_results
            )
            
            self.logger.info("🎉 Final Document Assembly Pipeline completed successfully!")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            raise
    
    async def _extract_content_parallel(self, pdf_path: str, output_dir: str) -> tuple:
        """
        Phase 1: Extract content using parallel Nougat and PyMuPDF processing.
        """
        self.logger.info("   🔄 Running Nougat and PyMuPDF in parallel...")
        
        # Create tasks for parallel execution
        nougat_task = asyncio.create_task(self._run_nougat_extraction(pdf_path, output_dir))
        pymupdf_task = asyncio.create_task(self._run_pymupdf_extraction(pdf_path, output_dir))
        
        # Wait for both to complete
        nougat_output, visual_elements = await asyncio.gather(nougat_task, pymupdf_task)
        
        self.stats['nougat_blocks'] = len(nougat_output.split('\n')) if nougat_output else 0
        self.stats['visual_elements'] = len(visual_elements)
        
        self.logger.info(f"   ✅ Parallel extraction completed:")
        self.logger.info(f"      • Nougat content: {len(nougat_output)} characters")
        self.logger.info(f"      • Visual elements: {len(visual_elements)}")
        
        return nougat_output, visual_elements
    
    async def _run_nougat_extraction(self, pdf_path: str, output_dir: str) -> str:
        """Run Nougat extraction for text and structure"""
        try:
            # Use existing Nougat integration
            result = self.nougat_integration.parse_pdf_with_nougat(pdf_path)
            if result and 'content' in result:
                return result['content']
            else:
                self.logger.warning("Nougat extraction returned no content")
                return ""
        except Exception as e:
            self.logger.error(f"Nougat extraction failed: {e}")
            return ""
    
    async def _run_pymupdf_extraction(self, pdf_path: str, output_dir: str) -> List[VisualElement]:
        """Run PyMuPDF extraction for visual elements"""
        try:
            # Use existing PDF parser for visual extraction
            visual_elements = []
            
            # Create images directory
            images_dir = os.path.join(output_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Extract visual elements using PDF parser
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract raster images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            element_id = f"page_{page_num + 1}_img_{img_index + 1}"
                            img_filename = f"{element_id}.png"
                            img_path = os.path.join(images_dir, img_filename)
                            
                            pix.save(img_path)
                            
                            # Get image rectangle
                            img_rects = page.get_image_rects(xref)
                            bbox = img_rects[0] if img_rects else (0, 0, 100, 100)
                            
                            visual_element = VisualElement(
                                element_id=element_id,
                                element_type='image',
                                source_path=img_path,
                                page_num=page_num + 1,
                                bbox=bbox,
                                width=pix.width,
                                height=pix.height,
                                classification='unknown'
                            )
                            
                            visual_elements.append(visual_element)
                        
                        pix = None
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
            
            doc.close()
            return visual_elements
            
        except Exception as e:
            self.logger.error(f"PyMuPDF extraction failed: {e}")
            return []
    
    async def _translate_text_content_only(self, unified_document: StructuredDocument, 
                                         target_language: str) -> StructuredDocument:
        """
        Phase 3: Translate only text content, bypassing all visual elements.
        """
        self.logger.info("   🌐 Translating text content (bypassing images)...")
        
        # Use existing translation service with structured document support
        translated_document = await self.translation_service.translate_document_structured(
            unified_document, target_language
        )
        
        # Count translated blocks
        translatable_blocks = [
            block for block in unified_document.content_blocks 
            if hasattr(block, 'get_content_type') and 
            block.get_content_type().value in ['heading', 'paragraph', 'list_item']
        ]
        
        preserved_images = [
            block for block in unified_document.content_blocks
            if hasattr(block, 'get_content_type') and 
            block.get_content_type().value == 'image_placeholder'
        ]
        
        self.stats['translated_blocks'] = len(translatable_blocks)
        self.stats['preserved_images'] = len(preserved_images)
        
        self.logger.info(f"   ✅ Translation completed:")
        self.logger.info(f"      • Translated blocks: {len(translatable_blocks)}")
        self.logger.info(f"      • Preserved images: {len(preserved_images)}")
        
        return translated_document
    
    def _assemble_final_document(self, translated_document: StructuredDocument, 
                               output_dir: str, pdf_path: str) -> Dict[str, str]:
        """
        Phase 4: Assemble final document with proper TOC and image placement.
        """
        self.logger.info("   🏗️ Assembling final Word document...")
        
        # Generate output filename
        base_filename = Path(pdf_path).stem
        word_output_path = os.path.join(output_dir, f"{base_filename}_translated.docx")
        images_folder = os.path.join(output_dir, "images")
        
        # Use enhanced document generator
        final_word_path = self.document_generator.create_document_from_structured(
            translated_document, word_output_path, images_folder
        )
        
        # Count TOC entries
        toc_entries = [
            block for block in translated_document.content_blocks
            if hasattr(block, 'get_content_type') and 
            block.get_content_type().value == 'heading'
        ]
        self.stats['toc_entries'] = len(toc_entries)
        
        self.logger.info(f"   ✅ Final document assembled:")
        self.logger.info(f"      • Word document: {os.path.basename(final_word_path)}")
        self.logger.info(f"      • TOC entries: {len(toc_entries)}")
        
        return {
            'word_document': final_word_path,
            'images_folder': images_folder
        }
    
    def _validate_final_output(self, output_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Phase 5: Validate that final output contains all expected elements.
        """
        validation_results = {
            'status': 'success',
            'word_document_exists': False,
            'images_folder_exists': False,
            'image_count': 0,
            'issues': []
        }
        
        try:
            # Check Word document
            word_path = output_files.get('word_document')
            if word_path and os.path.exists(word_path):
                validation_results['word_document_exists'] = True
                self.logger.info(f"   ✅ Word document validated: {os.path.basename(word_path)}")
            else:
                validation_results['issues'].append("Word document not found")
                validation_results['status'] = 'warning'
            
            # Check images folder
            images_folder = output_files.get('images_folder')
            if images_folder and os.path.exists(images_folder):
                validation_results['images_folder_exists'] = True
                
                # Count images
                image_files = [f for f in os.listdir(images_folder) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                validation_results['image_count'] = len(image_files)
                
                self.logger.info(f"   ✅ Images folder validated: {len(image_files)} images")
            else:
                validation_results['issues'].append("Images folder not found")
                validation_results['status'] = 'warning'
            
        except Exception as e:
            validation_results['status'] = 'error'
            validation_results['issues'].append(f"Validation error: {e}")
            self.logger.error(f"   ❌ Validation failed: {e}")
        
        return validation_results
    
    def _generate_final_report(self, pdf_path: str, output_dir: str, 
                             output_files: Dict[str, str], 
                             validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        report = {
            'input_file': os.path.basename(pdf_path),
            'output_directory': output_dir,
            'output_files': output_files,
            'processing_statistics': self.stats.copy(),
            'validation_results': validation_results,
            'pipeline_config': self.config.copy(),
            'status': 'success' if validation_results['status'] != 'error' else 'error'
        }
        
        # Log summary
        self.logger.info("📊 FINAL ASSEMBLY PIPELINE REPORT:")
        self.logger.info(f"   • Input: {report['input_file']}")
        self.logger.info(f"   • Status: {report['status'].upper()}")
        self.logger.info(f"   • Nougat blocks processed: {self.stats['nougat_blocks']}")
        self.logger.info(f"   • Visual elements extracted: {self.stats['visual_elements']}")
        self.logger.info(f"   • Text blocks translated: {self.stats['translated_blocks']}")
        self.logger.info(f"   • Images preserved: {self.stats['preserved_images']}")
        self.logger.info(f"   • TOC entries: {self.stats['toc_entries']}")
        
        if validation_results['issues']:
            self.logger.warning(f"   ⚠️ Issues: {', '.join(validation_results['issues'])}")
        
        return report
