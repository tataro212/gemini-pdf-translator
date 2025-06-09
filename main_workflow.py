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
        
    async def translate_document_async(self, filepath, output_dir_for_this_file,
                                     target_language_override=None, precomputed_style_guide=None,
                                     use_advanced_features=None):
        """Main async translation workflow with optional advanced features"""

        logger.info(f"🚀 Starting translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        # Determine if we should use advanced features
        use_advanced = use_advanced_features if use_advanced_features is not None else self.use_advanced_features

        if self.advanced_pipeline and use_advanced:
            logger.info("🎯 Using advanced translation pipeline")
            return await self._translate_document_advanced(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        else:
            logger.info("📝 Using standard translation workflow")
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

            # Use the advanced pipeline for complete processing
            logger.info("🔄 Processing with advanced pipeline...")
            advanced_result = await self.advanced_pipeline.process_document_advanced(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language
            )

            # Generate documents from the advanced result
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Convert the advanced result to structured content format
            logger.debug(f"🔍 Advanced result debug:")
            logger.debug(f"   • Translated text length: {len(advanced_result.translated_text) if advanced_result.translated_text else 0}")
            logger.debug(f"   • Translated text preview: {advanced_result.translated_text[:200] if advanced_result.translated_text else 'EMPTY'}")

            structured_content = self._convert_advanced_result_to_content(advanced_result, output_dir_for_this_file)

            logger.debug(f"🔍 Structured content debug:")
            logger.debug(f"   • Content items created: {len(structured_content)}")
            if structured_content:
                type_counts = {}
                for item in structured_content:
                    item_type = item.get('type', 'unknown')
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1
                logger.debug(f"   • Content breakdown: {type_counts}")
            else:
                logger.error("❌ NO STRUCTURED CONTENT CREATED - This will cause document generation to fail!")

            # Generate Word document
            logger.info("📄 Generating Word document from advanced translation...")
            logger.debug(f"   • Target path: {word_output_path}")
            logger.debug(f"   • Image folder: {os.path.join(output_dir_for_this_file, 'images')}")
            logger.debug(f"   • Content items to process: {len(structured_content)}")

            try:
                saved_word_filepath = document_generator.create_word_document_with_structure(
                    structured_content, word_output_path, os.path.join(output_dir_for_this_file, "images"), None
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
                logger.error(f"   • Structured content length: {len(structured_content)}")
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
        """Parse translated content to preserve heading structure"""
        content_items = []
        lines = translated_text.split('\n')
        current_paragraph = []
        block_num = 1

        for line in lines:
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                # If we have accumulated paragraph content, save it
                if current_paragraph:
                    content_items.append({
                        'type': 'paragraph',
                        'text': '\n'.join(current_paragraph),
                        'page_num': 1,
                        'block_num': block_num
                    })
                    current_paragraph = []
                    block_num += 1
                continue

            # Check for markdown headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            if heading_match:
                # Save any accumulated paragraph first
                if current_paragraph:
                    content_items.append({
                        'type': 'paragraph',
                        'text': '\n'.join(current_paragraph),
                        'page_num': 1,
                        'block_num': block_num
                    })
                    current_paragraph = []
                    block_num += 1

                # Add heading
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                content_items.append({
                    'type': f'h{level}',
                    'text': heading_text,
                    'page_num': 1,
                    'block_num': block_num
                })
                block_num += 1
                continue

            # Check for potential headings (bold text, title-like lines)
            potential_heading_type = self._detect_potential_heading_type(line_stripped)
            if potential_heading_type:
                # Save any accumulated paragraph first
                if current_paragraph:
                    content_items.append({
                        'type': 'paragraph',
                        'text': '\n'.join(current_paragraph),
                        'page_num': 1,
                        'block_num': block_num
                    })
                    current_paragraph = []
                    block_num += 1

                # Add detected heading
                content_items.append({
                    'type': potential_heading_type,
                    'text': self._clean_heading_text(line_stripped),
                    'page_num': 1,
                    'block_num': block_num
                })
                block_num += 1
                continue

            # Regular text line - add to current paragraph
            current_paragraph.append(line_stripped)

        # Don't forget the last paragraph
        if current_paragraph:
            content_items.append({
                'type': 'paragraph',
                'text': '\n'.join(current_paragraph),
                'page_num': 1,
                'block_num': block_num
            })

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
