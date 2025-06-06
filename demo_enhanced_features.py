#!/usr/bin/env python3
"""
Demonstration of Enhanced PDF Translator Features

This script showcases all the new optimization features including:
- Asynchronous concurrent translation
- Rich text extraction with formatting
- HTML output generation
- Unified visual element processing
- Two-tier caching system
"""

import os
import asyncio
import time
import logging
from pathlib import Path

# Import enhanced components
from enhanced_main_workflow import EnhancedPDFTranslator
from rich_text_extractor import rich_text_extractor
from async_translation_service import async_translation_service, TranslationTask
from visual_element_processor import visual_element_processor
from html_document_generator import html_document_generator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_sample_pdf():
    """Find a sample PDF file for demonstration"""
    current_dir = Path('.')
    pdf_files = list(current_dir.glob('*.pdf'))
    
    if pdf_files:
        return str(pdf_files[0])
    
    logger.warning("No PDF files found in current directory")
    logger.info("Please place a PDF file in the current directory to run the demo")
    return None

async def demo_async_translation():
    """Demonstrate asynchronous translation capabilities"""
    logger.info("\n🚀 DEMO: Asynchronous Translation")
    logger.info("=" * 50)
    
    # Create sample translation tasks
    sample_texts = [
        "This is a sample paragraph for translation.",
        "Another paragraph with different content.",
        "A third paragraph to demonstrate concurrent processing.",
        "Scientific research shows that concurrent processing improves efficiency.",
        "The methodology used in this study follows established protocols."
    ]
    
    tasks = []
    for i, text in enumerate(sample_texts):
        task = TranslationTask(
            text=text,
            target_language="Greek",
            item_type="paragraph",
            priority=1
        )
        tasks.append(task)
    
    logger.info(f"📝 Created {len(tasks)} translation tasks")
    
    # Time the concurrent translation
    start_time = time.time()
    translated_texts = await async_translation_service.translate_batch_concurrent(tasks)
    end_time = time.time()
    
    logger.info(f"⚡ Concurrent translation completed in {end_time - start_time:.2f} seconds")
    
    # Show results
    for i, (original, translated) in enumerate(zip(sample_texts, translated_texts)):
        logger.info(f"Task {i+1}:")
        logger.info(f"  Original: {original[:50]}...")
        logger.info(f"  Translated: {translated[:50]}...")
    
    # Show performance statistics
    stats = async_translation_service.get_performance_stats()
    logger.info(f"\n📊 Performance Statistics:")
    logger.info(f"  • Cache hit rate: {stats.get('cache_hit_rate', 0)*100:.1f}%")
    logger.info(f"  • API calls made: {stats.get('api_calls', 0)}")
    logger.info(f"  • Memory cache hits: {stats.get('cache_hits_memory', 0)}")
    logger.info(f"  • Persistent cache hits: {stats.get('cache_hits_persistent', 0)}")

def demo_rich_text_extraction(pdf_path):
    """Demonstrate rich text extraction with formatting metadata"""
    logger.info("\n🎨 DEMO: Rich Text Extraction")
    logger.info("=" * 50)
    
    logger.info(f"📖 Extracting rich text from: {os.path.basename(pdf_path)}")
    
    # Extract rich text blocks
    text_blocks = rich_text_extractor.extract_rich_text_from_pdf(pdf_path)
    
    if not text_blocks:
        logger.warning("No text blocks extracted")
        return
    
    logger.info(f"✅ Extracted {len(text_blocks)} text blocks with formatting metadata")
    
    # Analyze document structure
    structure_analysis = rich_text_extractor.get_document_structure_analysis(text_blocks)
    
    logger.info(f"\n📊 Document Structure Analysis:")
    logger.info(f"  • Total pages: {structure_analysis.get('total_pages', 0)}")
    logger.info(f"  • Total blocks: {structure_analysis.get('total_blocks', 0)}")
    
    # Show block type distribution
    block_distribution = structure_analysis.get('block_type_distribution', {})
    logger.info(f"  • Block types:")
    for block_type, count in block_distribution.items():
        logger.info(f"    - {block_type}: {count}")
    
    # Show dominant fonts
    dominant_fonts = structure_analysis.get('dominant_fonts', [])[:3]
    logger.info(f"  • Top fonts:")
    for font_info, count in dominant_fonts:
        logger.info(f"    - {font_info}: {count} occurrences")
    
    # Show sample blocks with formatting
    logger.info(f"\n📝 Sample Text Blocks (first 3):")
    for i, block in enumerate(text_blocks[:3]):
        logger.info(f"  Block {i+1}:")
        logger.info(f"    Text: {block.text[:60]}...")
        logger.info(f"    Type: {block.block_type}")
        logger.info(f"    Font: {block.font_name}, Size: {block.font_size}pt")
        logger.info(f"    Bold: {block.is_bold()}, Italic: {block.is_italic()}")
        logger.info(f"    Color: {block.get_css_color()}")
        logger.info(f"    Position: {block.bbox}")

def demo_visual_processing(pdf_path):
    """Demonstrate visual element processing pipeline"""
    logger.info("\n🖼️ DEMO: Visual Element Processing")
    logger.info("=" * 50)
    
    # Create temporary output directory
    output_dir = "demo_visual_output"
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"📁 Output directory: {output_dir}")
    
    # Extract images (using existing PDF parser)
    from pdf_parser import PDFParser
    pdf_parser = PDFParser()
    
    image_folder = os.path.join(output_dir, "images")
    os.makedirs(image_folder, exist_ok=True)
    
    logger.info(f"📷 Extracting images from PDF...")
    extracted_images = pdf_parser.extract_images_from_pdf(pdf_path, image_folder)
    
    if not extracted_images:
        logger.warning("No images extracted from PDF")
        return
    
    logger.info(f"✅ Extracted {len(extracted_images)} images")
    
    # Process with visual element processor
    logger.info(f"🔄 Processing visual elements...")
    visual_elements, placeholder_map = visual_element_processor.process_visual_elements(
        extracted_images, output_dir
    )
    
    logger.info(f"✅ Processed {len(visual_elements)} visual elements")
    
    # Show classification results
    type_distribution = {}
    for element in visual_elements:
        element_type = element.element_type.value
        type_distribution[element_type] = type_distribution.get(element_type, 0) + 1
    
    logger.info(f"\n📊 Visual Element Classification:")
    for element_type, count in type_distribution.items():
        logger.info(f"  • {element_type}: {count}")
    
    # Show high-confidence elements
    high_confidence_elements = [e for e in visual_elements if e.confidence > 0.8]
    logger.info(f"\n⭐ High-confidence elements ({len(high_confidence_elements)}):")
    for element in high_confidence_elements[:3]:
        logger.info(f"  • {element.element_id}: {element.element_type.value} (confidence: {element.confidence:.2f})")
    
    # Show placeholder mapping
    logger.info(f"\n🔗 Placeholder Mapping (first 3):")
    for i, (placeholder, element_id) in enumerate(list(placeholder_map.items())[:3]):
        logger.info(f"  • {placeholder} → {element_id}")
    
    return visual_elements

def demo_html_generation(pdf_path):
    """Demonstrate HTML document generation"""
    logger.info("\n📄 DEMO: HTML Document Generation")
    logger.info("=" * 50)
    
    # Create output directory
    output_dir = "demo_html_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract rich text
    logger.info("📖 Extracting rich text for HTML generation...")
    text_blocks = rich_text_extractor.extract_rich_text_from_pdf(pdf_path)
    
    if not text_blocks:
        logger.warning("No text blocks for HTML generation")
        return
    
    # Create sample image items (empty for demo)
    image_items = []
    
    # Generate HTML document
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    html_output_path = os.path.join(output_dir, f"{base_filename}_demo.html")
    
    logger.info(f"🏗️ Generating HTML document...")
    success = html_document_generator.generate_html_document(
        text_blocks,
        image_items,
        html_output_path,
        f"{base_filename} - Demo"
    )
    
    if success:
        logger.info(f"✅ HTML document generated: {html_output_path}")
        logger.info(f"🌐 Open in browser to view the formatted document")
        
        # Show file size
        file_size = os.path.getsize(html_output_path)
        logger.info(f"📊 File size: {file_size:,} bytes")
        
        # Count elements in HTML
        with open(html_output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        css_lines = html_content.count('\n        .font-style-')
        logger.info(f"🎨 Generated {css_lines} unique font styles")
        
    else:
        logger.error("❌ Failed to generate HTML document")

async def demo_complete_workflow(pdf_path):
    """Demonstrate the complete enhanced workflow"""
    logger.info("\n🚀 DEMO: Complete Enhanced Workflow")
    logger.info("=" * 50)
    
    # Create output directory
    output_dir = "demo_complete_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize enhanced translator
    translator = EnhancedPDFTranslator()
    
    logger.info(f"📄 Processing: {os.path.basename(pdf_path)}")
    logger.info(f"📁 Output: {output_dir}")
    
    # Run complete enhanced workflow
    start_time = time.time()
    success = await translator.translate_document_enhanced(
        pdf_path, 
        output_dir,
        target_language="Greek"
    )
    end_time = time.time()
    
    if success:
        logger.info(f"✅ Complete workflow finished in {end_time - start_time:.1f} seconds")
        
        # List generated files
        generated_files = list(Path(output_dir).rglob('*'))
        logger.info(f"📁 Generated {len(generated_files)} files:")
        for file_path in generated_files[:10]:  # Show first 10
            if file_path.is_file():
                size = file_path.stat().st_size
                logger.info(f"  • {file_path.name} ({size:,} bytes)")
        
        if len(generated_files) > 10:
            logger.info(f"  ... and {len(generated_files) - 10} more files")
    
    else:
        logger.error("❌ Complete workflow failed")

async def main():
    """Main demonstration function"""
    logger.info("🎉 ENHANCED PDF TRANSLATOR - FEATURE DEMONSTRATION")
    logger.info("=" * 70)
    
    # Find sample PDF
    pdf_path = find_sample_pdf()
    if not pdf_path:
        return
    
    logger.info(f"📄 Using sample PDF: {os.path.basename(pdf_path)}")
    
    try:
        # Demo 1: Asynchronous Translation
        await demo_async_translation()
        
        # Demo 2: Rich Text Extraction
        demo_rich_text_extraction(pdf_path)
        
        # Demo 3: Visual Processing
        visual_elements = demo_visual_processing(pdf_path)
        
        # Demo 4: HTML Generation
        demo_html_generation(pdf_path)
        
        # Demo 5: Complete Workflow
        await demo_complete_workflow(pdf_path)
        
        logger.info("\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info("Check the demo output folders for generated files:")
        logger.info("  • demo_visual_output/ - Visual processing results")
        logger.info("  • demo_html_output/ - HTML generation results")
        logger.info("  • demo_complete_output/ - Complete workflow results")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
