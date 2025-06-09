"""
Main Workflow Module for Ultimate PDF Translator

Orchestrates the complete translation workflow using all modular components
"""

import os
import asyncio
import time
import logging
import sys
import re

logger = logging.getLogger(__name__)

# Import all modular components
from config_manager import config_manager
from pdf_parser import PDFParser, StructuredContentExtractor
from ocr_processor import SmartImageAnalyzer
from translation_service import translation_service
from optimization_manager import optimization_manager
from document_generator import document_generator, pdf_converter
from drive_uploader import drive_uploader
from nougat_integration import NougatIntegration  # Enhanced Nougat integration
from nougat_only_integration import NougatOnlyIntegration  # NOUGAT-ONLY mode
from enhanced_document_intelligence import DocumentTextRestructurer  # Footnote handling

# Import structured document model for new workflow
try:
    from structured_document_model import Document as StructuredDocument
    STRUCTURED_MODEL_AVAILABLE = True
except ImportError:
    STRUCTURED_MODEL_AVAILABLE = False
    logger.warning("Structured document model not available")
from utils import (
    choose_input_path, choose_base_output_directory,
    get_specific_output_dir_for_file, estimate_translation_cost,
    ProgressTracker
)

# Import advanced features (with fallback if not available)
try:
    from advanced_translation_pipeline import AdvancedTranslationPipeline
    from self_correcting_translator import SelfCorrectingTranslator
    from hybrid_ocr_processor import HybridOCRProcessor
    from semantic_cache import SemanticCache
    ADVANCED_FEATURES_AVAILABLE = True
    logger.info("✅ Advanced features available: Self-correction, Hybrid OCR, Semantic caching")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning(f"⚠️ Advanced features not available: {e}")
    logger.info("💡 Install advanced features with: pip install -r advanced_features_requirements.txt")

# Import intelligent pipeline (with fallback if not available)
try:
    from intelligent_pdf_translator import IntelligentPDFTranslator
    from advanced_document_analyzer import AdvancedDocumentAnalyzer
    from translation_strategy_manager import TranslationStrategyManager
    INTELLIGENT_PIPELINE_AVAILABLE = True
    logger.info("🧠 Intelligent pipeline available: Content-aware routing, Strategic processing")
except ImportError as e:
    INTELLIGENT_PIPELINE_AVAILABLE = False
    logger.warning(f"⚠️ Intelligent pipeline not available: {e}")
    logger.info("💡 Intelligent pipeline requires additional dependencies")

class UltimatePDFTranslator:
    """Main orchestrator class for the PDF translation workflow with enhanced Nougat integration"""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.content_extractor = StructuredContentExtractor()
        self.image_analyzer = SmartImageAnalyzer()
        self.text_restructurer = DocumentTextRestructurer()  # For footnote handling
        self.quality_report_messages = []

        # Check for NOUGAT-ONLY mode preference
        nougat_only_mode = config_manager.get_config_value('General', 'nougat_only_mode', False, bool)

        try:
            if nougat_only_mode:
                # Initialize NOUGAT-ONLY integration (no fallback)
                logger.info("🚀 NOUGAT-ONLY MODE: Initializing comprehensive visual extraction...")
                self.nougat_integration = NougatOnlyIntegration(config_manager)

                if self.nougat_integration.nougat_available:
                    logger.info("🎯 NOUGAT-ONLY: Replacing PDF parser with Nougat-only extraction")
                    self.nougat_integration.enhance_pdf_parser_nougat_only(self.pdf_parser)
                    logger.info("✅ PDF parser converted to NOUGAT-ONLY mode")
                    logger.info("📊 Will extract: Paintings, Schemata, Diagrams, Equations, Tables, Everything!")
                    self.nougat_only_mode = True
                else:
                    logger.error("❌ NOUGAT-ONLY MODE requires Nougat to be available!")
                    logger.error("❌ Falling back to enhanced Nougat integration...")
                    nougat_only_mode = False

            if not nougat_only_mode:
                # Initialize enhanced Nougat integration with priority mode
                self.nougat_integration = NougatIntegration(config_manager)
                self.nougat_only_mode = False

                # Enhance PDF parser with Nougat capabilities
                if self.nougat_integration.nougat_available or self.nougat_integration.use_alternative:
                    logger.info("🚀 Enhancing PDF parser with Nougat capabilities...")
                    self.nougat_integration.enhance_pdf_parser_with_nougat(self.pdf_parser)
                    logger.info("✅ PDF parser enhanced - prioritizing visual content with Nougat intelligence")
                else:
                    logger.warning("⚠️ Nougat not available - using traditional PDF processing")

        except Exception as e:
            logger.error(f"❌ Error initializing Nougat integration: {e}")
            logger.warning("⚠️ Falling back to traditional PDF processing without Nougat")
            # Initialize basic integration as fallback
            self.nougat_integration = None
            self.nougat_only_mode = False

        # Initialize advanced features if available
        self.advanced_pipeline = None
        self.use_advanced_features = config_manager.get_config_value('General', 'use_advanced_features', True, bool)

        if ADVANCED_FEATURES_AVAILABLE and self.use_advanced_features:
            try:
                logger.info("🚀 Initializing advanced translation features...")
                self.advanced_pipeline = AdvancedTranslationPipeline(
                    base_translator=translation_service,
                    nougat_integration=self.nougat_integration,
                    cache_dir="advanced_semantic_cache",
                    config_manager=config_manager
                )
                logger.info("✅ Advanced features initialized successfully!")
                logger.info("   🔧 Self-correcting translation enabled")
                logger.info("   📖 Hybrid OCR strategy enabled")
                logger.info("   🧠 Semantic caching enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize advanced features: {e}")
                logger.warning("⚠️ Falling back to standard translation workflow")
                self.advanced_pipeline = None
        elif not ADVANCED_FEATURES_AVAILABLE:
            logger.info("💡 Advanced features not available - using standard workflow")
        else:
            logger.info("⚙️ Advanced features disabled in configuration")

        # Initialize intelligent pipeline if available
        self.intelligent_pipeline = None
        self.use_intelligent_pipeline = config_manager.get_config_value('IntelligentPipeline', 'use_intelligent_pipeline', True, bool)

        if INTELLIGENT_PIPELINE_AVAILABLE and self.use_intelligent_pipeline:
            try:
                logger.info("🧠 Initializing intelligent processing pipeline...")
                # Use the correct initialization - IntelligentPDFTranslator only takes max_workers parameter
                max_workers = config_manager.get_config_value('IntelligentPipeline', 'max_concurrent_tasks', 4, int)
                self.intelligent_pipeline = IntelligentPDFTranslator(max_workers=max_workers)
                logger.info("✅ Intelligent pipeline initialized successfully!")
                logger.info("   🎯 Content-aware routing enabled")
                logger.info("   📊 Strategic tool selection enabled")
                logger.info("   ⚡ Parallel processing enabled")
                logger.info("   🧠 Semantic caching enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize intelligent pipeline: {e}")
                logger.warning("⚠️ Falling back to advanced or standard workflow")
                self.intelligent_pipeline = None
                # Log the full traceback for debugging
                import traceback
                logger.debug(f"Full traceback: {traceback.format_exc()}")
        elif not INTELLIGENT_PIPELINE_AVAILABLE:
            logger.info("💡 Intelligent pipeline not available - using advanced/standard workflow")
        else:
            logger.info("⚙️ Intelligent pipeline disabled in configuration")
        
    async def translate_document_async(self, filepath, output_dir_for_this_file,
                                     target_language_override=None, precomputed_style_guide=None,
                                     use_advanced_features=None):
        """Main async translation workflow with optional advanced features"""

        logger.info(f"🚀 Starting translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        # Determine processing pipeline priority
        use_advanced = use_advanced_features if use_advanced_features is not None else self.use_advanced_features

        # Priority 1: Intelligent Pipeline (if available and enabled)
        if self.intelligent_pipeline and self.use_intelligent_pipeline:
            logger.info("🧠 Using intelligent processing pipeline")
            return await self._translate_document_intelligent(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Priority 2: Advanced Pipeline (if available and enabled)
        elif self.advanced_pipeline and use_advanced:
            logger.info("🎯 Using advanced translation pipeline")
            return await self._translate_document_advanced(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Priority 3: Structured Document Model (if available)
        elif STRUCTURED_MODEL_AVAILABLE:
            logger.info("🏗️ Using structured document model workflow")
            return await self._translate_document_structured(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Fallback: Standard workflow
        else:
            logger.info("📝 Using standard translation workflow")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

    async def _translate_document_intelligent(self, filepath, output_dir_for_this_file,
                                            target_language_override=None, precomputed_style_guide=None):
        """Intelligent translation workflow using the dynamic processing pipeline"""

        logger.info(f"🧠 Starting INTELLIGENT translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # Step 1: Extract structured document
            logger.info("📄 Step 1: Extracting structured document...")

            # Extract images first
            image_folder = os.path.join(output_dir_for_this_file, "images")
            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Extract cover page
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)

            # Extract structured content as Document object
            if STRUCTURED_MODEL_AVAILABLE:
                document = self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
                if not document or not document.content_blocks:
                    raise Exception("No content could be extracted from the PDF")
                logger.info(f"📊 Extracted document: {document.get_statistics()}")
            else:
                # Fallback to legacy format and convert
                from structured_document_model import convert_legacy_structured_content_to_document
                legacy_content = self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
                document = convert_legacy_structured_content_to_document(
                    legacy_content,
                    title=os.path.splitext(os.path.basename(filepath))[0],
                    source_filepath=filepath
                )

            # Step 2: Process with intelligent pipeline
            logger.info("🧠 Step 2: Processing with intelligent pipeline...")
            intelligent_result = await self.intelligent_pipeline.translate_document_intelligently(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language
            )

            # Step 3: Generate output documents
            logger.info("📄 Step 3: Generating output documents...")
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Generate Word document from processed document
            saved_word_filepath = document_generator.create_word_document_from_structured_document(
                intelligent_result.processed_document, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document from intelligent translation")

            # Convert to PDF
            logger.info("📑 Step 4: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            # Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 5: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)

            # Generate intelligent final report
            end_time = time.time()
            self._generate_intelligent_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                intelligent_result, drive_results, pdf_success
            )

            # Save caches
            translation_service.save_caches()

            logger.info("✅ Intelligent translation workflow completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ Intelligent translation workflow failed: {e}")
            logger.info("🔄 Falling back to advanced translation workflow...")
            if self.advanced_pipeline:
                return await self._translate_document_advanced(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )
            else:
                return await self._translate_document_standard(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )

    async def _translate_document_advanced(self, filepath, output_dir_for_this_file,
                                         target_language_override=None, precomputed_style_guide=None):
        """Advanced translation workflow using the enhanced pipeline"""

        logger.info(f"🚀 Starting ADVANCED translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # STEP 1: Extract structured document with images FIRST
            logger.info("📄 Step 1: Extracting structured document with images...")

            # Extract images and create structured document
            pdf_parser = PDFParser()
            image_folder = os.path.join(output_dir_for_this_file, "images")
            os.makedirs(image_folder, exist_ok=True)

            # Extract images
            extracted_images = pdf_parser.extract_images_from_pdf(filepath, image_folder)
            logger.info(f"🖼️ Extracted {len(extracted_images)} images")

            # Create structured document with images
            content_extractor = StructuredContentExtractor()
            structured_document = content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
            logger.info(f"📊 Created structured document with {len(structured_document.content_blocks)} blocks")

            # Count image blocks
            image_blocks = [block for block in structured_document.content_blocks if hasattr(block, 'image_path') and block.image_path]
            logger.info(f"🖼️ Document contains {len(image_blocks)} image blocks")

            # STEP 2: Use advanced pipeline for translation only
            logger.info("🔄 Step 2: Processing translation with advanced pipeline...")
            advanced_result = await self.advanced_pipeline.process_document_advanced(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language
            )

            # STEP 3: Apply translation to structured document
            logger.info("🔧 Step 3: Applying translation to structured document...")
            translated_document = self._apply_translation_to_structured_document(
                structured_document, advanced_result.translated_text
            )

            # Generate documents from the translated structured document
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Extract cover page if enabled
            cover_page_data = None
            if config_manager.pdf_processing_settings['extract_cover_page']:
                cover_page_data = self._extract_cover_page(filepath, output_dir_for_this_file)

            # Generate Word document using structured document model (preserves images!)
            logger.info("📄 Generating Word document from translated structured document...")
            logger.info(f"   🖼️ Including {len(image_blocks)} images from: {image_folder}")

            try:
                saved_word_filepath = document_generator.create_word_document_from_structured_document(
                    translated_document, word_output_path, image_folder, cover_page_data
                )

                logger.debug(f"   • Document generator returned: {saved_word_filepath}")

                if saved_word_filepath and os.path.exists(saved_word_filepath):
                    file_size = os.path.getsize(saved_word_filepath)
                    logger.info(f"✅ Word document created successfully: {file_size} bytes")
                else:
                    logger.error(f"❌ Document generator returned path but file doesn't exist!")
                    logger.error(f"   • Returned path: {saved_word_filepath}")
                    logger.error(f"   • Expected path: {word_output_path}")
                    logger.error(f"   • File exists check: {os.path.exists(saved_word_filepath) if saved_word_filepath else 'N/A'}")
                    raise Exception("Word document was not created - file missing after generation")

            except Exception as doc_error:
                logger.error(f"❌ Document generation failed with error: {doc_error}")
                logger.error(f"   • Structured document blocks: {len(translated_document.content_blocks) if translated_document else 'N/A'}")
                logger.error(f"   • Target directory exists: {os.path.exists(output_dir_for_this_file)}")
                logger.error(f"   • Target directory writable: {os.access(output_dir_for_this_file, os.W_OK)}")
                raise Exception(f"Failed to create Word document from advanced translation: {doc_error}")

            if not saved_word_filepath:
                raise Exception("Failed to create Word document from advanced translation")

            # Convert to PDF
            logger.info("📑 Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            # Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)

            # Generate enhanced final report
            end_time = time.time()
            self._generate_advanced_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                advanced_result, drive_results, pdf_success
            )

            # Save caches
            translation_service.save_caches()

            logger.info("✅ Advanced translation workflow completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ Advanced translation workflow failed: {e}")
            logger.info("🔄 Falling back to standard translation workflow...")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

    async def _translate_document_standard(self, filepath, output_dir_for_this_file,
                                         target_language_override=None, precomputed_style_guide=None):
        """Standard translation workflow (original implementation)"""

        start_time = time.time()
        
        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")
            
            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)
            
            # Set up output paths with proper path normalization
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            # Normalize the output directory path to fix mixed separators
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            image_folder = os.path.join(output_dir_for_this_file, "images")
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))
            
            # Step 1: Extract images from PDF (with enhanced Nougat or fallback)
            if self.nougat_integration is None:
                logger.info("📷 Step 1: Extracting images with traditional PDF processing...")
                logger.warning("⚠️ Nougat not available - using standard image extraction")
            elif self.nougat_only_mode:
                logger.info("📷 Step 1: NOUGAT-ONLY visual content extraction...")
                logger.info("🎯 NOUGAT-ONLY: Paintings, Schemata, Diagrams, Equations, Tables, Everything!")
                logger.info("🚫 NO FALLBACK: Traditional image extraction disabled")
            else:
                logger.info("📷 Step 1: Extracting images with Nougat capabilities...")
                if hasattr(self.pdf_parser, 'nougat_enhanced'):
                    logger.info("🎯 Using enhanced mode: Mathematical equations, Complex tables, Scientific diagrams")

            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Report analysis results based on available integration
            if self.nougat_integration is None:
                logger.info("📊 Traditional PDF analysis: Using standard image extraction methods")
                logger.info(f"   📷 Extracted {len(extracted_images)} images using conventional methods")
            elif self.nougat_only_mode and hasattr(self.pdf_parser, '_nougat_only_analysis'):
                # NOUGAT-ONLY mode analysis
                analysis = self.pdf_parser._nougat_only_analysis
                visual_elements = analysis.get('visual_elements', [])

                # Count by category
                categories = {}
                for element in visual_elements:
                    cat = element.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1

                logger.info(f"📊 NOUGAT-ONLY analysis: {len(visual_elements)} total visual elements")
                for category, count in categories.items():
                    logger.info(f"   📋 {category}: {count}")

                high_priority = len([e for e in visual_elements if e.get('priority', 0) >= 0.9])
                if high_priority > 0:
                    logger.info(f"⭐ Found {high_priority} high-priority elements")

            elif hasattr(self.pdf_parser, '_nougat_analysis'):
                # Enhanced Nougat mode analysis
                nougat_analysis = self.pdf_parser._nougat_analysis
                summary = nougat_analysis.get('summary', {})
                logger.info(f"📊 Nougat analysis: {summary.get('mathematical_elements', 0)} equations, "
                           f"{summary.get('tabular_elements', 0)} tables, "
                           f"{summary.get('visual_elements', 0)} visual elements")

                priority_count = summary.get('high_priority_count', 0)
                if priority_count > 0:
                    logger.info(f"⭐ Found {priority_count} high-priority elements for enhanced processing")
            else:
                logger.info(f"📊 Standard analysis: Extracted {len(extracted_images)} images using traditional methods")
            
            # Step 2: Extract cover page
            logger.info("📄 Step 2: Extracting cover page...")
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)
            
            # Step 3: Extract structured content
            logger.info("📝 Step 3: Extracting structured content...")
            structured_content = self.content_extractor.extract_structured_content_from_pdf(
                filepath, extracted_images
            )

            if not structured_content:
                raise Exception("No content could be extracted from the PDF")

            # Step 3.5: Restructure text to separate footnotes
            logger.info("🔧 Step 3.5: Restructuring text and separating footnotes...")
            structured_content = self._restructure_content_text(structured_content)
            
            # Step 4: Analyze images for translation
            logger.info("🔍 Step 4: Analyzing images...")
            if extracted_images:
                image_paths = [img['filepath'] for img in extracted_images]
                image_analysis = self.image_analyzer.batch_analyze_images(image_paths)
                
                # Add OCR text to image items in structured content
                self._integrate_image_analysis(structured_content, image_analysis)
            
            # Step 5: Optimize content for translation
            logger.info("⚡ Step 5: Optimizing content...")
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']
            
            # Filter out image items for optimization (they don't need translation)
            text_items = [item for item in structured_content if item.get('type') != 'image']
            
            optimized_batches, optimization_params = optimization_manager.optimize_content_for_translation(
                text_items, target_language
            )
            
            # Step 6: Translate content
            logger.info("🌐 Step 6: Translating content...")
            translated_content = await self._translate_batches(
                optimized_batches, target_language, precomputed_style_guide
            )
            
            # Step 7: Reconstruct full content with images
            logger.info("🔧 Step 7: Reconstructing document...")
            final_content = self._reconstruct_full_content(structured_content, translated_content)
            
            # Step 8: Generate Word document
            logger.info("📄 Step 8: Generating Word document...")
            saved_word_filepath = document_generator.create_word_document_with_structure(
                final_content, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document")

            # Step 9: Convert to PDF using the exact path returned from save
            logger.info("📑 Step 9: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            if not pdf_success:
                logger.warning("⚠️ PDF conversion failed, but Word document was created successfully")
                logger.info(f"💡 Word document available at: {saved_word_filepath}")
                logger.info("💡 You can manually convert the Word document to PDF if needed")

            # Step 10: Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 10: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                # Only include PDF if conversion was successful
                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)
            
            # Step 11: Generate final report
            end_time = time.time()
            self._generate_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                len(structured_content), len(translated_content), drive_results, pdf_success
            )
            
            # Save translation cache
            translation_service.save_caches()
            
            logger.info("✅ Translation workflow completed successfully!")
            return precomputed_style_guide  # Return for potential reuse in batch processing
            
        except Exception as e:
            logger.error(f"❌ Translation workflow failed: {e}")
            raise

    async def _translate_document_structured(self, filepath, output_dir_for_this_file,
                                           target_language_override=None, precomputed_style_guide=None):
        """
        New structured document translation workflow using the refactored document model.
        This method implements the structured document model approach for better content integrity.
        """
        if not STRUCTURED_MODEL_AVAILABLE:
            logger.warning("Structured document model not available, falling back to standard workflow")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set up output paths
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            image_folder = os.path.join(output_dir_for_this_file, "images")
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Step 1: Extract images from PDF
            logger.info("📷 Step 1: Extracting images...")
            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Step 2: Extract cover page
            logger.info("📄 Step 2: Extracting cover page...")
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)

            # Step 3: Extract structured content as Document object
            logger.info("📝 Step 3: Extracting structured document...")
            document = self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)

            if not document or not document.content_blocks:
                raise Exception("No content could be extracted from the PDF")

            logger.info(f"📊 Extracted document: {document.get_statistics()}")

            # Step 4: Analyze images for translation (integrate with Document)
            logger.info("🔍 Step 4: Analyzing images...")
            if extracted_images:
                image_paths = [img['filepath'] for img in extracted_images]
                image_analysis = self.image_analyzer.batch_analyze_images(image_paths)
                self._integrate_image_analysis_into_document(document, image_analysis)

            # Step 5: Translate the structured document
            logger.info("🌐 Step 5: Translating structured document...")
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            translated_document = await translation_service.translate_document(
                document, target_language, precomputed_style_guide or ""
            )

            # Step 6: Generate Word document from structured document
            logger.info("📄 Step 6: Generating Word document...")
            saved_word_filepath = document_generator.create_word_document_from_structured_document(
                translated_document, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document")

            # Step 7: Convert to PDF
            logger.info("📑 Step 7: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            if not pdf_success:
                logger.warning("⚠️ PDF conversion failed, but Word document was created successfully")
                logger.info(f"💡 Word document available at: {saved_word_filepath}")

            # Step 8: Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 8: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)

            # Step 9: Generate final report
            end_time = time.time()
            self._generate_structured_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                document, translated_document, drive_results, pdf_success
            )

            # Save translation cache
            translation_service.save_caches()

            logger.info("✅ Structured document translation completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ Structured document translation failed: {e}")
            raise

    def _integrate_image_analysis_into_document(self, document, image_analysis):
        """Integrate image analysis results into Document object"""
        # Create a mapping of image filenames to analysis results
        analysis_map = {
            os.path.basename(analysis['path']): analysis
            for analysis in image_analysis
        }

        # Update ImagePlaceholder blocks in the document
        for block in document.content_blocks:
            if hasattr(block, 'image_path') and block.image_path:
                filename = os.path.basename(block.image_path)
                if filename in analysis_map:
                    analysis = analysis_map[filename]
                    if analysis['should_translate'] and analysis['extracted_text']:
                        block.ocr_text = analysis['extracted_text']
                        block.translation_needed = True
                        # Update original_text with OCR text for potential translation
                        if not block.original_text:
                            block.original_text = analysis['extracted_text']
                    else:
                        block.translation_needed = False

    def _generate_structured_final_report(self, input_filepath, output_dir, start_time, end_time,
                                        original_document, translated_document, drive_results, pdf_success=True):
        """Generate final report for structured document translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Document statistics
        original_stats = original_document.get_statistics()
        translated_stats = translated_document.get_statistics()

        stats_section = f"""
📊 DOCUMENT STATISTICS:
• Original Title: {original_document.title}
• Translated Title: {translated_document.title}
• Total Pages: {original_document.total_pages}
• Content Blocks: {original_stats['total_blocks']} → {translated_stats['total_blocks']}
• Translatable Blocks: {original_stats['translatable_blocks']}
• Non-translatable Blocks: {original_stats['non_translatable_blocks']}

📋 CONTENT BREAKDOWN:
"""
        for content_type, count in original_stats['blocks_by_type'].items():
            stats_section += f"• {content_type.replace('_', ' ').title()}: {count}\n"

        report = f"""
🎉 STRUCTURED DOCUMENT TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=================================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{stats_section}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _integrate_image_analysis(self, structured_content, image_analysis):
        """Integrate image analysis results into structured content"""
        # Create a mapping of image filenames to analysis results
        analysis_map = {
            os.path.basename(analysis['path']): analysis 
            for analysis in image_analysis
        }
        
        # Update image items in structured content
        for item in structured_content:
            if item.get('type') == 'image':
                filename = item.get('filename')
                if filename in analysis_map:
                    analysis = analysis_map[filename]
                    if analysis['should_translate'] and analysis['extracted_text']:
                        item['ocr_text'] = analysis['extracted_text']
                        item['translation_needed'] = True
                    else:
                        item['translation_needed'] = False

    def _restructure_content_text(self, structured_content):
        """Restructure text content to separate footnotes from main content"""
        restructured_content = []
        footnotes_collected = []

        for item in structured_content:
            if item.get('type') in ['paragraph', 'text'] and item.get('text'):
                # Apply text restructuring to separate footnotes
                try:
                    restructured = self.text_restructurer.analyze_and_restructure_text(item['text'])

                    # Update the main content
                    if restructured['main_content']:
                        item['text'] = restructured['main_content']
                        restructured_content.append(item)

                    # Collect footnotes
                    if restructured['footnotes']:
                        for footnote in restructured['footnotes']:
                            footnote_item = {
                                'type': 'footnote',
                                'text': footnote,
                                'page_num': item.get('page_num', 0),
                                'source_block': item.get('block_num', 0)
                            }
                            footnotes_collected.append(footnote_item)

                        logger.info(f"📝 Separated {len(restructured['footnotes'])} footnotes from page {item.get('page_num', 'unknown')}")

                except Exception as e:
                    logger.warning(f"Failed to restructure text on page {item.get('page_num', 'unknown')}: {e}")
                    # Keep original item if restructuring fails
                    restructured_content.append(item)
            else:
                # Keep non-text items as-is
                restructured_content.append(item)

        # Add footnotes at the end if any were found
        if footnotes_collected:
            logger.info(f"📋 Total footnotes collected: {len(footnotes_collected)}")
            restructured_content.extend(footnotes_collected)

        return restructured_content

    async def _translate_batches(self, optimized_batches, target_language, style_guide):
        """Translate optimized batches of content"""
        translated_items = []
        total_batches = len(optimized_batches)
        
        progress_tracker = ProgressTracker(total_batches)
        
        for batch_idx, batch in enumerate(optimized_batches):
            logger.info(f"Translating batch {batch_idx + 1}/{total_batches}")
            
            batch_start_time = time.time()
            
            try:
                # Translate each group in the batch
                for group_idx, group in enumerate(batch):
                    logger.debug(f"Processing group {group_idx + 1}/{len(batch)} with {len(group)} items")

                    # Combine group items for translation
                    combined_text = optimization_manager.grouping_processor.combine_group_for_translation(group)
                    logger.debug(f"Combined text length: {len(combined_text)} characters")

                    # Translate the combined text
                    logger.debug("Sending text to translation service...")
                    translated_text = await translation_service.translate_text(
                        combined_text, target_language, style_guide
                    )
                    logger.debug(f"Received translated text length: {len(translated_text)} characters")

                    # Log the raw translation for debugging
                    logger.debug(f"Raw translated text preview: {translated_text[:200]}...")

                    # Split the translated text back into individual items
                    logger.debug("Splitting translated text back into individual items...")
                    translated_group = optimization_manager.grouping_processor.split_translated_group(
                        translated_text, group
                    )
                    logger.debug(f"Split resulted in {len(translated_group)} items")

                    translated_items.extend(translated_group)
                
                # Record performance
                batch_time = time.time() - batch_start_time
                optimization_manager.record_batch_performance(
                    len(str(batch)), batch_time, 1.0  # Success rate = 1.0 for successful batches
                )
                
                progress_tracker.update(completed=1)
                
            except Exception as e:
                logger.error(f"Failed to translate batch {batch_idx + 1}: {e}")
                
                # Add original items as fallback
                for group in batch:
                    translated_items.extend(group)
                
                progress_tracker.update(failed=1)
        
        progress_tracker.finish()
        return translated_items
    
    def _reconstruct_full_content(self, original_content, translated_text_items):
        """Reconstruct full content by merging translated text with images"""
        # Create a mapping of translated items by their original position/identifier
        translated_map = {}
        
        for item in translated_text_items:
            # Use page_num and block_num as identifier
            key = (item.get('page_num'), item.get('block_num'))
            translated_map[key] = item
        
        # Reconstruct the full content
        final_content = []
        
        for original_item in original_content:
            if original_item.get('type') == 'image':
                # Keep image items as-is
                final_content.append(original_item)
            else:
                # Use translated version if available
                key = (original_item.get('page_num'), original_item.get('block_num'))
                if key in translated_map:
                    final_content.append(translated_map[key])
                else:
                    # Fallback to original
                    final_content.append(original_item)
        
        return final_content

    def _apply_translation_to_structured_document(self, structured_document, translated_text):
        """Apply translated text to structured document while preserving images and structure"""

        if not STRUCTURED_MODEL_AVAILABLE:
            logger.error("❌ Structured document model not available for translation application")
            return structured_document

        try:
            from structured_document_model import Document as StructuredDocument

            # Split translated text into paragraphs
            translated_paragraphs = [p.strip() for p in translated_text.split('\n\n') if p.strip()]

            # Create new content blocks with translated text
            translated_blocks = []
            paragraph_index = 0

            for block in structured_document.content_blocks:
                if hasattr(block, 'get_content_type'):
                    content_type = block.get_content_type().value

                    if content_type == 'image_placeholder':
                        # Keep image blocks unchanged
                        translated_blocks.append(block)
                        logger.debug(f"🖼️ Preserved image block: {os.path.basename(block.image_path) if block.image_path else 'unknown'}")

                    elif content_type in ['paragraph', 'heading', 'list_item']:
                        # Apply translation to text blocks
                        if paragraph_index < len(translated_paragraphs):
                            # Create new block with translated content
                            new_block = type(block)(
                                block_type=block.block_type,
                                original_text=block.original_text,
                                page_num=block.page_num,
                                bbox=block.bbox,
                                content=translated_paragraphs[paragraph_index]
                            )

                            # Copy any additional attributes
                            if hasattr(block, 'level'):
                                new_block.level = block.level
                            if hasattr(block, 'list_type'):
                                new_block.list_type = block.list_type

                            translated_blocks.append(new_block)
                            paragraph_index += 1
                            logger.debug(f"📝 Translated {content_type}: {translated_paragraphs[paragraph_index-1][:50]}...")
                        else:
                            # No more translated text, keep original
                            translated_blocks.append(block)
                            logger.debug(f"⚠️ No translation available for {content_type}, keeping original")

                    else:
                        # Keep other blocks unchanged (tables, equations, etc.)
                        translated_blocks.append(block)
                        logger.debug(f"📋 Preserved {content_type} block")
                else:
                    # Fallback for blocks without get_content_type method
                    translated_blocks.append(block)
                    logger.debug("📋 Preserved block (no content type)")

            # Create new translated document
            translated_document = StructuredDocument(
                title=f"{structured_document.title} (Translated)",
                content_blocks=translated_blocks,
                source_filepath=structured_document.source_filepath,
                total_pages=structured_document.total_pages,
                metadata={
                    **structured_document.metadata,
                    'translated': True,
                    'translation_method': 'advanced_pipeline'
                }
            )

            logger.info(f"✅ Applied translation to structured document:")
            logger.info(f"   📊 Original blocks: {len(structured_document.content_blocks)}")
            logger.info(f"   📊 Translated blocks: {len(translated_blocks)}")
            logger.info(f"   📝 Paragraphs translated: {paragraph_index}")

            # Count preserved images
            image_blocks = [block for block in translated_blocks if hasattr(block, 'image_path') and block.image_path]
            logger.info(f"   🖼️ Images preserved: {len(image_blocks)}")

            return translated_document

        except Exception as e:
            logger.error(f"❌ Failed to apply translation to structured document: {e}")
            logger.warning("⚠️ Returning original document")
            return structured_document

    def _convert_advanced_result_to_content(self, advanced_result, output_dir):
        """Convert advanced translation result to structured content format with heading preservation"""
        content_items = []

        if advanced_result.translated_text:
            # Enhanced parsing to preserve heading structure
            content_items = self._parse_translated_content_with_structure(advanced_result.translated_text)

            # If no structure was detected, fall back to simple paragraph parsing
            if not content_items:
                paragraphs = advanced_result.translated_text.split('\n\n')
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        content_items.append({
                            'type': 'paragraph',
                            'text': paragraph.strip(),
                            'page_num': 1,
                            'block_num': i + 1
                        })

        return content_items

    def _parse_translated_content_with_structure(self, translated_text):
        """Parse translated content to preserve heading structure, handle images, and clean placeholders."""
        content_items = []
        lines = translated_text.split('\\n')
        current_paragraph_lines = []
        block_num = 1

        def save_current_paragraph():
            nonlocal block_num # Allow modification of block_num from outer scope
            if current_paragraph_lines:
                # Join lines, then strip the whole paragraph, then check if it's just "" or empty
                paragraph_text = '\\n'.join(current_paragraph_lines).strip()
                if paragraph_text and paragraph_text != '""':
                    content_items.append({
                        'type': 'paragraph',
                        'text': paragraph_text,
                        'page_num': 1, # Placeholder, needs better page context if available
                        'block_num': block_num
                    })
                    block_num += 1
                current_paragraph_lines.clear()

        for line in lines:
            line_stripped = line.strip()

            # 1. Handle lines that should be skipped or act as paragraph breaks
            # Skip Nougat placeholders for missing/empty pages
            if (re.fullmatch(r"\[ΕΛΛΕΙΠΟΥΣΑ_ΣΕΛΙΔΑ_ΚΕΝΗ:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_EMPTY:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_FAIL:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_POST:\d*\]", line_stripped)):
                save_current_paragraph()
                logger.debug(f"Skipping Nougat placeholder: {line_stripped}")
                continue
            
            # Skip empty lines, standalone quotes, and other formatting artifacts
            if (not line_stripped or
                line_stripped == '""' or
                line_stripped == '"' or
                line_stripped == "''" or
                line_stripped == "'" or
                re.fullmatch(r'["\'\s]*', line_stripped)):  # Only quotes and whitespace
                save_current_paragraph()
                continue

            # 2. Handle special block types (images, headings)
            image_match = re.fullmatch(r"\\[IMAGE:\\s*(.+?)\\s*\\]", line_stripped)
            if image_match:
                save_current_paragraph()
                image_filename = image_match.group(1)
                content_items.append({
                    'type': 'image',
                    'filename': image_filename,
                    'page_num': 1, # Placeholder for page number
                    'block_num': block_num
                })
                block_num += 1
                continue

            heading_match = re.match(r'^(#{1,6})\\s+(.+)$', line_stripped) # Markdown headings
            if heading_match:
                save_current_paragraph()
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                if heading_text: # Ensure heading text is not empty
                    content_items.append({
                        'type': f'h{level}',
                        'text': heading_text,
                        'page_num': 1, # Placeholder
                        'block_num': block_num
                    })
                    block_num += 1
                continue
            
            potential_heading_type = self._detect_potential_heading_type(line_stripped) # Custom heading detection
            if potential_heading_type:
                save_current_paragraph()
                heading_text = self._clean_heading_text(line_stripped)
                if heading_text: # Ensure heading text is not empty
                    content_items.append({
                        'type': potential_heading_type,
                        'text': heading_text,
                        'page_num': 1, # Placeholder
                        'block_num': block_num
                    })
                    block_num += 1
                continue

            # 3. If none of the above, it's part of a paragraph
            current_paragraph_lines.append(line_stripped) # Append the stripped line

        save_current_paragraph() # Save any remaining paragraph at the end

        return content_items

    def _detect_potential_heading_type(self, line):
        """Detect if a line is likely a heading and return its type"""
        if len(line) > 150:  # Too long to be a heading
            return None

        # Pattern 1: Bold text that looks like headings
        bold_pattern = r'^\*\*(.+?)\*\*$'
        if re.match(bold_pattern, line):
            heading_text = re.match(bold_pattern, line).group(1).strip()
            return self._determine_heading_level_from_content(heading_text)

        # Pattern 2: Lines that look like titles (short, capitalized, no period)
        if (len(line) < 100 and
            line[0].isupper() and
            not line.endswith('.') and
            not line.startswith('*') and
            ' ' in line):

            words = line.split()
            if (len(words) >= 3 and
                sum(1 for word in words if word[0].isupper()) >= len(words) * 0.6):
                return self._determine_heading_level_from_content(line)

        return None

    def _determine_heading_level_from_content(self, text):
        """Determine heading level based on content"""
        text_lower = text.lower()

        # Level 1: Main titles, document titles
        if any(keyword in text_lower for keyword in ['senda:', 'assessment', 'federation', 'militant']):
            return 'h1'

        # Level 2: Major sections
        elif any(keyword in text_lower for keyword in ['need for', 'discourse', 'powerful', 'conclusions', 'συμπεράσματα']):
            return 'h2'

        # Level 3: Subsections
        elif any(keyword in text_lower for keyword in ['what should', 'that said', 'implementation']):
            return 'h3'

        # Default to level 2 for other potential headings
        else:
            return 'h2'

    def _clean_heading_text(self, text):
        """Clean heading text by removing bold markers and extra formatting"""
        # Remove bold markers
        text = re.sub(r'^\*\*(.+?)\*\*$', r'\1', text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text

    def _generate_advanced_final_report(self, input_filepath, output_dir, start_time, end_time,
                                      advanced_result, drive_results, pdf_success=True):
        """Generate comprehensive final report for advanced translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Advanced metrics section
        advanced_metrics = f"""
🚀 ADVANCED FEATURES PERFORMANCE:
• OCR Engine Used: {advanced_result.ocr_engine_used}
• OCR Quality Score: {advanced_result.ocr_quality_score:.2f}
• Validation Passed: {'✅' if advanced_result.validation_passed else '❌'}
• Correction Attempts: {advanced_result.correction_attempts}
• Cache Hit: {'✅' if advanced_result.cache_hit else '❌'} (Semantic: {'✅' if advanced_result.semantic_cache_hit else '❌'})
• Processing Time: {advanced_result.processing_time:.2f}s
• Confidence Score: {advanced_result.confidence_score:.2f}
"""

        report = f"""
🎉 ADVANCED TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=======================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{advanced_metrics}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        # Get pipeline optimization recommendations
        if hasattr(self.advanced_pipeline, 'optimize_pipeline'):
            try:
                recommendations = self.advanced_pipeline.optimize_pipeline()
                if recommendations.get('recommendations'):
                    report += "\n💡 OPTIMIZATION RECOMMENDATIONS:\n"
                    for rec in recommendations['recommendations']:
                        report += f"• {rec}\n"
            except Exception as e:
                logger.debug(f"Could not get optimization recommendations: {e}")

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _generate_intelligent_final_report(self, input_filepath, output_dir, start_time, end_time,
                                         intelligent_result, drive_results, pdf_success=True):
        """Generate comprehensive final report for intelligent translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Intelligent pipeline metrics
        performance_metrics = intelligent_result.performance_metrics
        processing_plan = intelligent_result.processing_plan
        document_analysis = intelligent_result.document_analysis

        intelligent_metrics = f"""
🧠 INTELLIGENT PIPELINE PERFORMANCE:
• Document Category: {document_analysis.document_category.value}
• Processing Strategy: {processing_plan.optimization_notes[0] if processing_plan.optimization_notes else 'Standard'}
• Cost Savings: {intelligent_result.cost_savings:.1f}%
• Quality Score: {intelligent_result.quality_score:.2f}
• Processing Time: {intelligent_result.processing_time:.2f}s
• Parallel Groups: {len(processing_plan.parallel_groups)}
• Total Blocks: {len(processing_plan.routing_decisions)}

📊 TOOL USAGE:
"""

        # Add tool usage statistics
        for tool, count in performance_metrics.get('tool_usage', {}).items():
            intelligent_metrics += f"• {tool.replace('_', ' ').title()}: {count}\n"

        # Document analysis summary
        analysis_summary = f"""
📋 DOCUMENT ANALYSIS:
• Total Pages: {document_analysis.total_pages}
• High Priority Pages: {len(document_analysis.get_high_priority_pages())}
• Simple Text Pages: {len(document_analysis.get_simple_text_pages())}
• Estimated Complexity: {document_analysis.estimated_complexity:.2f}

🎯 PROCESSING RECOMMENDATIONS:
"""
        for rec in document_analysis.processing_recommendations[:5]:  # Show top 5
            analysis_summary += f"• {rec}\n"

        report = f"""
🎉 INTELLIGENT TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=======================================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{intelligent_metrics}

{analysis_summary}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _generate_final_report(self, input_filepath, output_dir, start_time, end_time,
                             original_items_count, translated_items_count, drive_results, pdf_success=True):
        """Generate comprehensive final report"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"
            files_section += f"\n  💡 Word document is available for manual conversion"

        report = f"""
🎉 TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=====================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes
📊 Items Processed: {original_items_count} → {translated_items_count}

{files_section}

{optimization_manager.get_final_performance_report()}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

async def main():
    """Main entry point for the application"""
    logger.info("--- ULTIMATE PDF TRANSLATOR (Modular Version) ---")
    
    # Validate configuration
    issues, recommendations = config_manager.validate_configuration()
    
    if issues:
        logger.error("❌ Configuration issues found:")
        for issue in issues:
            logger.error(f"  {issue}")
        return False
    
    if recommendations:
        logger.info("💡 Configuration recommendations:")
        for rec in recommendations:
            logger.info(f"  {rec}")
    
    # Get input files
    input_path, process_mode = choose_input_path()
    if not input_path:
        logger.info("No input selected. Exiting.")
        return True
    
    # Get output directory
    main_output_directory = choose_base_output_directory(
        os.path.dirname(input_path) if process_mode == 'file' else input_path
    )
    
    if not main_output_directory:
        logger.error("No output directory selected. Exiting.")
        return False
    
    # Collect files to process
    files_to_process = []
    if process_mode == 'file':
        files_to_process = [input_path]
    else:
        for filename in os.listdir(input_path):
            if filename.lower().endswith('.pdf'):
                files_to_process.append(os.path.join(input_path, filename))
    
    if not files_to_process:
        logger.error("No PDF files found to process.")
        return False
    
    # Estimate cost for single files
    if len(files_to_process) == 1:
        estimate_translation_cost(files_to_process[0], config_manager)
    
    # Initialize translator
    translator = UltimatePDFTranslator()
    
    # Process files
    for i, filepath in enumerate(files_to_process):
        logger.info(f"\n>>> Processing file {i+1}/{len(files_to_process)}: {os.path.basename(filepath)} <<<")
        
        specific_output_dir = get_specific_output_dir_for_file(main_output_directory, filepath)
        if not specific_output_dir:
            logger.error(f"Could not create output directory for {os.path.basename(filepath)}")
            continue
        
        try:
            await translator.translate_document_async(filepath, specific_output_dir)
        except Exception as e:
            logger.error(f"Failed to process {os.path.basename(filepath)}: {e}")
        
        # Pause between files
        if i < len(files_to_process) - 1:
            logger.info("Pausing before next file...")
            time.sleep(3)
    
    logger.info("--- ALL PROCESSING COMPLETED ---")
    return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Handle command line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ["--help", "-h"]:
            print("Ultimate PDF Translator - Modular Version")
            print("Usage: python main_workflow.py")
            print("The script will prompt for input files and settings")
            sys.exit(0)
    
    # Run the main workflow
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
