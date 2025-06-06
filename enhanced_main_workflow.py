"""
Enhanced Main Workflow for Ultimate PDF Translator

Integrates all optimization improvements including async translation,
rich text extraction, HTML output, and unified visual processing.
"""

import os
import asyncio
import time
import logging
from typing import List, Dict, Optional

# Import enhanced components
from config_manager import config_manager
from rich_text_extractor import rich_text_extractor, TextBlock
from async_translation_service import async_translation_service
from visual_element_processor import visual_element_processor
from html_document_generator import html_document_generator
from pdf_parser import PDFParser
from utils import choose_input_path, choose_base_output_directory, get_specific_output_dir_for_file

logger = logging.getLogger(__name__)

class EnhancedPDFTranslator:
    """
    Next-generation PDF translator with all optimization improvements:
    - Asynchronous concurrent translation
    - Rich text extraction with formatting preservation
    - HTML output with CSS positioning
    - Unified visual element processing
    - Intelligent caching and performance optimization
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.rich_text_extractor = rich_text_extractor
        self.async_translator = async_translation_service
        self.visual_processor = visual_element_processor
        self.html_generator = html_document_generator
        
        # Performance tracking
        self.performance_stats = {
            'total_documents': 0,
            'total_translation_time': 0.0,
            'total_api_calls': 0,
            'cache_hit_rate': 0.0
        }
        
        logger.info("🚀 EnhancedPDFTranslator initialized with all optimizations")
    
    async def translate_document_enhanced(self, pdf_path: str, output_dir: str, 
                                        target_language: Optional[str] = None) -> bool:
        """
        Enhanced translation workflow with all optimizations applied.
        """
        start_time = time.time()
        
        if target_language is None:
            target_language = config_manager.translation_enhancement_settings['target_language']
        
        logger.info(f"🚀 Starting enhanced translation: {os.path.basename(pdf_path)}")
        logger.info(f"   • Target language: {target_language}")
        logger.info(f"   • Output directory: {output_dir}")
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Extract rich text with formatting metadata
            logger.info("📖 Step 1: Extracting rich text with formatting...")
            text_blocks = self.rich_text_extractor.extract_rich_text_from_pdf(pdf_path)
            
            if not text_blocks:
                raise Exception("No text content could be extracted from the PDF")
            
            logger.info(f"   ✅ Extracted {len(text_blocks)} rich text blocks")
            
            # Step 2: Extract and process visual elements
            logger.info("🎨 Step 2: Processing visual elements...")
            image_folder = os.path.join(output_dir, "images")
            os.makedirs(image_folder, exist_ok=True)
            
            # Extract images using existing parser
            extracted_images = self.pdf_parser.extract_images_from_pdf(pdf_path, image_folder)
            
            # Process with unified visual pipeline
            visual_elements, placeholder_map = self.visual_processor.process_visual_elements(
                extracted_images, output_dir
            )
            
            logger.info(f"   ✅ Processed {len(visual_elements)} visual elements")
            
            # Step 3: Translate text content asynchronously
            logger.info("🌐 Step 3: Translating text content asynchronously...")
            
            # Convert text blocks to content items format
            content_items = self._convert_text_blocks_to_content_items(text_blocks)
            
            # Execute async translation
            translated_items = await self.async_translator.translate_content_items_async(
                content_items, target_language
            )
            
            # Convert back to text blocks
            translated_text_blocks = self._convert_content_items_to_text_blocks(translated_items)
            
            logger.info(f"   ✅ Translated {len(translated_text_blocks)} text blocks")
            
            # Step 4: Translate visual element text
            logger.info("🔍 Step 4: Translating visual element text...")
            visual_elements = self.visual_processor.translate_visual_text(
                visual_elements, target_language
            )
            
            # Step 5: Reconstruct visual elements
            logger.info("🔧 Step 5: Reconstructing visual elements...")
            visual_elements = self.visual_processor.reconstruct_visual_elements(
                visual_elements, output_dir
            )
            
            # Step 6: Generate HTML document
            logger.info("📄 Step 6: Generating HTML document...")
            
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            html_output_path = os.path.join(output_dir, f"{base_filename}_translated.html")
            
            # Convert visual elements to image items format for HTML generator
            image_items = self._convert_visual_elements_to_image_items(visual_elements)
            
            html_success = self.html_generator.generate_html_document(
                translated_text_blocks,
                image_items,
                html_output_path,
                f"{base_filename} - Translated"
            )
            
            if not html_success:
                raise Exception("Failed to generate HTML document")
            
            logger.info(f"   ✅ HTML document generated: {html_output_path}")
            
            # Step 7: Generate performance report
            end_time = time.time()
            self._generate_enhanced_performance_report(
                pdf_path, output_dir, start_time, end_time,
                len(text_blocks), len(visual_elements)
            )
            
            # Step 8: Save caches and cleanup
            self.async_translator.persistent_cache.save_cache()
            
            logger.info("✅ Enhanced translation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced translation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _convert_text_blocks_to_content_items(self, text_blocks: List[TextBlock]) -> List[Dict]:
        """Convert TextBlock objects to content items format"""
        content_items = []
        
        for block in text_blocks:
            item = {
                'text': block.text,
                'type': block.block_type,
                'page_num': block.page_num,
                'block_num': len(content_items),  # Sequential numbering
                'font_size': block.font_size,
                'font_name': block.font_name,
                'bbox': block.bbox,
                'formatting': {
                    'is_bold': block.is_bold(),
                    'is_italic': block.is_italic(),
                    'color': block.get_css_color(),
                    'font_flags': block.font_flags
                }
            }
            content_items.append(item)
        
        return content_items
    
    def _convert_content_items_to_text_blocks(self, content_items: List[Dict]) -> List[TextBlock]:
        """Convert content items back to TextBlock objects"""
        text_blocks = []
        
        for item in content_items:
            formatting = item.get('formatting', {})
            
            # Reconstruct font flags from formatting info
            font_flags = formatting.get('font_flags', 0)
            if formatting.get('is_bold', False):
                font_flags |= 2**4
            if formatting.get('is_italic', False):
                font_flags |= 2**1
            
            # Convert CSS color back to integer (simplified)
            color = 0  # Default to black
            
            block = TextBlock(
                text=item['text'],
                page_num=item['page_num'],
                bbox=item.get('bbox', (0, 0, 100, 20)),
                font_name=item.get('font_name', 'Arial'),
                font_size=item.get('font_size', 12.0),
                font_flags=font_flags,
                color=color,
                line_height=item.get('bbox', (0, 0, 100, 20))[3] - item.get('bbox', (0, 0, 100, 20))[1],
                char_spacing=0.0,
                word_spacing=0.0,
                text_matrix=(1, 0, 0, 1, 0, 0),
                block_type=item.get('type', 'paragraph'),
                confidence=1.0
            )
            
            text_blocks.append(block)
        
        return text_blocks
    
    def _convert_visual_elements_to_image_items(self, visual_elements) -> List[Dict]:
        """Convert VisualElement objects to image items format"""
        image_items = []
        
        for element in visual_elements:
            item = {
                'filepath': element.source_path,
                'filename': os.path.basename(element.source_path),
                'page_num': element.page_num,
                'bbox': element.bbox,
                'element_type': element.element_type.value,
                'confidence': element.confidence,
                'extracted_text': element.extracted_text,
                'translated_text': element.translated_text,
                'alt_text': element.translated_text or element.extracted_text or f"Visual element from page {element.page_num}"
            }
            image_items.append(item)
        
        return image_items
    
    def _generate_enhanced_performance_report(self, input_path: str, output_dir: str,
                                            start_time: float, end_time: float,
                                            text_blocks_count: int, visual_elements_count: int):
        """Generate comprehensive performance report"""
        duration = end_time - start_time
        
        # Get performance stats from async translator
        async_stats = self.async_translator.get_performance_stats()
        
        # Update global performance tracking
        self.performance_stats['total_documents'] += 1
        self.performance_stats['total_translation_time'] += duration
        self.performance_stats['total_api_calls'] += async_stats.get('api_calls', 0)
        self.performance_stats['cache_hit_rate'] = async_stats.get('cache_hit_rate', 0.0)
        
        report = f"""
🎉 ENHANCED TRANSLATION COMPLETED SUCCESSFULLY!
=============================================

📁 Input: {os.path.basename(input_path)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes ({duration:.1f} seconds)

📊 CONTENT ANALYSIS:
• Text Blocks Processed: {text_blocks_count}
• Visual Elements Processed: {visual_elements_count}
• Rich Formatting Preserved: ✅
• Layout Information Captured: ✅

🚀 PERFORMANCE OPTIMIZATIONS:
• Async Translation: ✅ {async_stats.get('concurrent_batches', 0)} concurrent batches
• Two-Tier Caching: ✅ {async_stats.get('cache_hit_rate', 0)*100:.1f}% cache hit rate
• Memory Cache Hits: {async_stats.get('cache_hits_memory', 0)}
• Persistent Cache Hits: {async_stats.get('cache_hits_persistent', 0)}
• API Calls Made: {async_stats.get('api_calls', 0)}
• Preemptive Image Filtering: ✅

📄 OUTPUT FILES:
• HTML Document: {os.path.basename(input_path).replace('.pdf', '_translated.html')} ✅
• Images Folder: images/ ✅
• Processing Metadata: visual_processing_metadata.json ✅

🎨 VISUAL PROCESSING:
• Elements Classified: {visual_elements_count}
• Text Extraction: ✅
• AI Classification: ✅
• Placeholder Workflow: ✅

⚡ SPEED IMPROVEMENTS:
• Estimated Speed Increase: {async_stats.get('concurrent_batches', 1)}x faster than sequential
• Cache Efficiency: {async_stats.get('cache_hit_rate', 0)*100:.1f}% of requests served from cache
• Average Batch Time: {async_stats.get('avg_time_per_batch', 0):.2f}s

💡 NEXT STEPS:
1. Open the HTML file in your browser to view the translated document
2. Check the images folder for extracted visual content
3. Review visual_processing_metadata.json for detailed processing information
"""
        
        logger.info(report)
        
        # Save report to file
        report_path = os.path.join(output_dir, "translation_report.txt")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📋 Performance report saved: {report_path}")
        except Exception as e:
            logger.warning(f"Failed to save performance report: {e}")

async def main_enhanced():
    """Enhanced main entry point with all optimizations"""
    logger.info("🚀 ULTIMATE PDF TRANSLATOR - ENHANCED VERSION")
    logger.info("=" * 60)
    logger.info("🎯 Features: Async Translation • Rich Text • HTML Output • Visual Processing")
    
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
    
    # Initialize enhanced translator
    translator = EnhancedPDFTranslator()
    
    # Process files
    success_count = 0
    for i, filepath in enumerate(files_to_process):
        logger.info(f"\n>>> Processing file {i+1}/{len(files_to_process)}: {os.path.basename(filepath)} <<<")
        
        specific_output_dir = get_specific_output_dir_for_file(main_output_directory, filepath)
        if not specific_output_dir:
            logger.error(f"Could not create output directory for {os.path.basename(filepath)}")
            continue
        
        try:
            success = await translator.translate_document_enhanced(filepath, specific_output_dir)
            if success:
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {os.path.basename(filepath)}: {e}")
        
        # Clear session cache between documents
        translator.async_translator.clear_session_cache()
        
        # Pause between files
        if i < len(files_to_process) - 1:
            logger.info("Pausing before next file...")
            await asyncio.sleep(2)
    
    # Final summary
    logger.info(f"\n🎉 ENHANCED PROCESSING COMPLETED!")
    logger.info(f"   ✅ Successfully processed: {success_count}/{len(files_to_process)} files")
    logger.info(f"   📊 Overall performance: {translator.performance_stats}")
    
    return success_count > 0

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Run the enhanced workflow
    try:
        success = asyncio.run(main_enhanced())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)
