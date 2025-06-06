"""
Main Workflow Module for Ultimate PDF Translator

Orchestrates the complete translation workflow using all modular components
"""

import os
import asyncio
import time
import logging
import sys

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
from utils import (
    choose_input_path, choose_base_output_directory,
    get_specific_output_dir_for_file, estimate_translation_cost,
    ProgressTracker
)

logger = logging.getLogger(__name__)

class UltimatePDFTranslator:
    """Main orchestrator class for the PDF translation workflow with enhanced Nougat integration"""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.content_extractor = StructuredContentExtractor()
        self.image_analyzer = SmartImageAnalyzer()
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
        
    async def translate_document_async(self, filepath, output_dir_for_this_file, 
                                     target_language_override=None, precomputed_style_guide=None):
        """Main async translation workflow"""
        
        logger.info(f"🚀 Starting translation of: {os.path.basename(filepath)}")
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
            word_success = document_generator.create_word_document_with_structure(
                final_content, word_output_path, image_folder, cover_page_data
            )
            
            if not word_success:
                raise Exception("Failed to create Word document")
            
            # Step 9: Convert to PDF
            logger.info("📑 Step 9: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(word_output_path, pdf_output_path)

            if not pdf_success:
                logger.warning("⚠️ PDF conversion failed, but Word document was created successfully")
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
