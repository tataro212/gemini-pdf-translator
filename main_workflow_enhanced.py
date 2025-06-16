"""
Enhanced Main Workflow Module for Ultimate PDF Translator

Integrates all the fixes while preserving the two-pass TOC generation:
1. Unicode font support for Greek characters
2. TOC-aware parsing to prevent structural collapse  
3. Enhanced proper noun handling
4. Better PDF conversion with font embedding

This module extends the existing main_workflow.py without breaking compatibility.
"""

import os
import asyncio
import time
import logging
import sys
from pathlib import Path

# Import enhanced components
from document_generator import WordDocumentGenerator as EnhancedWordDocumentGenerator
from translation_service_enhanced import enhanced_translation_service
from pdf_parser_enhanced import enhanced_pdf_parser

# Import original components for compatibility
from config_manager import config_manager

logger = logging.getLogger(__name__)

class EnhancedPDFTranslator:
    """Enhanced PDF translator with all fixes integrated"""
    
    def __init__(self):
        self.document_generator = EnhancedWordDocumentGenerator()
        self.translation_service = enhanced_translation_service
        self.pdf_parser = enhanced_pdf_parser
        self.settings = config_manager.word_output_settings
        
        logger.info("Enhanced PDF Translator initialized with all fixes")
    
    async def translate_document_enhanced(self, input_path: str, output_dir: str) -> bool:
        """
        Enhanced document translation workflow with all fixes applied
        """
        try:
            start_time = time.time()
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            logger.info(f"Starting enhanced translation: {base_name}")
            
            # PHASE 1: Enhanced PDF Parsing with TOC awareness
            logger.info("Phase 1: Enhanced PDF parsing with TOC awareness")
            extracted_pages = self.pdf_parser.extract_pdf_with_enhanced_structure(input_path)
            
            if not extracted_pages:
                logger.error("No content extracted from PDF")
                return False
            
            # PHASE 2: Content Processing and Translation
            logger.info("Phase 2: Enhanced content processing and translation")
            processed_content = await self._process_content_enhanced(extracted_pages)
            
            # PHASE 3: Document Generation with Unicode Support and Two-Pass TOC
            logger.info("Phase 3: Enhanced document generation with Unicode support")
            docx_path = os.path.join(output_dir, f"{base_name}_translated_enhanced.docx")
            
            # Use enhanced document generator with Unicode font support
            success = self.document_generator.create_word_document_with_structure(
                processed_content, docx_path, 
                image_folder_path=os.path.join(output_dir, "images"),
                cover_page_data=None
            )
            
            if not success:
                logger.error("Document generation failed")
                return False
            
            # PHASE 4: Enhanced PDF Conversion (if enabled)
            if self.settings.get('convert_to_pdf', False):
                logger.info("Phase 4: Enhanced PDF conversion with Unicode support")
                pdf_path = os.path.join(output_dir, f"{base_name}_translated_enhanced.pdf")
                
                # Import the enhanced PDF conversion function
                from document_generator import convert_word_to_pdf
                pdf_success = convert_word_to_pdf(docx_path, pdf_path)
                
                if pdf_success:
                    logger.info(f"Enhanced PDF created: {pdf_path}")
                else:
                    logger.warning("Enhanced PDF conversion failed, but DOCX was created successfully")
            
            total_time = time.time() - start_time
            logger.info(f"Enhanced translation completed in {total_time:.2f} seconds")
            logger.info(f"Output: {docx_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Enhanced translation failed: {e}")
            return False
    
    async def _process_content_enhanced(self, extracted_pages):
        """
        Enhanced content processing with proper noun handling and missing letter fixes
        """
        try:
            # Convert extracted pages to translatable content
            content_blocks = []
            
            for page_data in extracted_pages:
                if page_data.get('type') == 'toc_page':
                    # Skip TOC pages for translation, they will be regenerated
                    logger.info(f"Skipping TOC page {page_data.get('page_num', 'unknown')}")
                    continue
                
                if page_data.get('type') == 'content_page':
                    # Process content blocks from enhanced extraction
                    for block in page_data.get('content_blocks', []):
                        if block.get('type') == 'text' and block.get('content'):
                            content_blocks.append({
                                'text': block['content'],
                                'page_num': block.get('page_num', 0),
                                'bbox': block.get('bbox', [0, 0, 0, 0])
                            })
                
                elif page_data.get('type') == 'simple_text':
                    # Handle simple text extraction fallback
                    if page_data.get('content'):
                        content_blocks.append({
                            'text': page_data['content'],
                            'page_num': page_data.get('page_num', 0),
                            'bbox': [0, 0, 0, 0]
                        })
            
            # Translate content blocks using enhanced translation service
            translated_blocks = []
            
            for block in content_blocks:
                try:
                    # Use enhanced translation service with proper noun handling
                    translated_text = await self.translation_service.translate_text_enhanced(
                        block['text'],
                        target_language=config_manager.translation_enhancement_settings['target_language'],
                        prev_context="",  # Could be enhanced with actual context
                        next_context="",  # Could be enhanced with actual context
                        item_type="text"
                    )
                    
                    translated_blocks.append({
                        'original_text': block['text'],
                        'translated_text': translated_text,
                        'page_num': block['page_num'],
                        'bbox': block['bbox']
                    })
                    
                except Exception as e:
                    logger.warning(f"Translation failed for block on page {block['page_num']}: {e}")
                    # Keep original text if translation fails
                    translated_blocks.append({
                        'original_text': block['text'],
                        'translated_text': block['text'],
                        'page_num': block['page_num'],
                        'bbox': block['bbox']
                    })
            
            logger.info(f"Enhanced content processing complete: {len(translated_blocks)} blocks processed")
            return translated_blocks
            
        except Exception as e:
            logger.error(f"Enhanced content processing failed: {e}")
            raise

async def translate_pdf_with_all_fixes(input_path: str, output_dir: str) -> bool:
    """
    Main function to translate PDF with all enhanced fixes applied
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create enhanced translator instance
    translator = EnhancedPDFTranslator()
    
    # Run enhanced translation
    return await translator.translate_document_enhanced(input_path, output_dir)

async def main():
    """
    Enhanced main function with GUI file dialogs (same as original workflow)
    """
    logger.info("=== ENHANCED PDF TRANSLATOR WITH ALL FIXES ===")
    logger.info("Fixes applied:")
    logger.info("1. Unicode font support for Greek characters")
    logger.info("2. TOC-aware parsing to prevent structural collapse")
    logger.info("3. Enhanced proper noun handling and missing letter fixes")
    logger.info("4. Better PDF conversion with font embedding")
    logger.info("5. Preserved two-pass TOC generation")
    
    # Import GUI utilities from utils.py
    from utils import choose_input_path, choose_base_output_directory, get_specific_output_dir_for_file
    
    # Get input files using GUI dialog
    input_path, process_mode = choose_input_path()
    if not input_path:
        logger.info("No input selected. Exiting.")
        return True
    
    # Get output directory using GUI dialog
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
    
    # Initialize enhanced translator
    translator = EnhancedPDFTranslator()
    
    # Process files
    processed_count = 0
    
    for i, filepath in enumerate(files_to_process):
        logger.info(f"\n>>> Processing file {i+1}/{len(files_to_process)}: {os.path.basename(filepath)} <<<")
        
        specific_output_dir = get_specific_output_dir_for_file(main_output_directory, filepath)
        if not specific_output_dir:
            logger.error(f"Could not create output directory for {os.path.basename(filepath)}")
            continue
        
        try:
            success = await translator.translate_document_enhanced(filepath, specific_output_dir)
            if success:
                processed_count += 1
                logger.info(f"SUCCESS: Successfully processed: {os.path.basename(filepath)}")
            else:
                logger.error(f"FAILED: Failed to process: {os.path.basename(filepath)}")
        except Exception as e:
            logger.error(f"ERROR: Error processing {os.path.basename(filepath)}: {e}")
    
    # Final summary
    logger.info(f"\n=== ENHANCED TRANSLATION SUMMARY ===")
    logger.info(f"Files processed: {processed_count}/{len(files_to_process)}")
    logger.info(f"Output directory: {main_output_directory}")
    
    return processed_count > 0

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Handle command line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ["--help", "-h"]:
            print("Enhanced PDF Translator - With All Fixes")
            print("Usage: python main_workflow_enhanced.py")
            print("The script will show file dialogs for input and output selection")
            sys.exit(0)
    
    # Run the enhanced workflow
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)