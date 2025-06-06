#!/usr/bin/env python3
"""
Trace images through the entire PDF processing pipeline to find where they're being lost
"""

import os
import sys
import logging
import tempfile
from pdf_parser import PDFParser, StructuredContentExtractor
from optimization_manager import SmartGroupingProcessor
from translation_strategy_manager import TranslationStrategyManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def trace_image_processing_pipeline(pdf_path):
    """Trace images through the entire processing pipeline"""
    logger.info("🔍 TRACING IMAGE PROCESSING PIPELINE")
    logger.info("=" * 60)
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        image_output_dir = os.path.join(temp_dir, "images")
        
        # Step 1: Image Extraction
        logger.info("\n📷 STEP 1: Image Extraction")
        logger.info("-" * 40)
        
        parser = PDFParser()
        extracted_images = parser.extract_images_from_pdf(pdf_path, image_output_dir)
        
        logger.info(f"✅ Extracted {len(extracted_images)} images")
        for i, img in enumerate(extracted_images[:5]):  # Show first 5
            logger.info(f"   {i+1}. {img['filename']} ({img['width']}x{img['height']}) - Page {img['page_num']}")
        if len(extracted_images) > 5:
            logger.info(f"   ... and {len(extracted_images) - 5} more images")
        
        # Step 2: Structured Content Extraction
        logger.info("\n📋 STEP 2: Structured Content Extraction")
        logger.info("-" * 40)
        
        extractor = StructuredContentExtractor()
        structured_content = extractor.extract_structured_content_from_pdf(pdf_path, extracted_images)
        
        # Count content types
        content_counts = {}
        image_items = []
        
        for item in structured_content:
            item_type = item.get('type', 'unknown')
            content_counts[item_type] = content_counts.get(item_type, 0) + 1
            
            if item_type == 'image':
                image_items.append(item)
        
        logger.info(f"✅ Structured content: {len(structured_content)} items")
        for content_type, count in content_counts.items():
            logger.info(f"   • {content_type}: {count}")
        
        logger.info(f"📷 Image items in structured content: {len(image_items)}")
        for i, img in enumerate(image_items[:3]):  # Show first 3
            logger.info(f"   {i+1}. {img.get('filename', 'unknown')} - Page {img.get('page_num', 'unknown')}")
        
        # Step 3: Translation Strategy Optimization
        logger.info("\n🎯 STEP 3: Translation Strategy Optimization")
        logger.info("-" * 40)
        
        strategy_manager = TranslationStrategyManager()
        optimized_content, strategy_stats = strategy_manager.optimize_content_for_strategy(structured_content)
        
        # Count after strategy optimization
        optimized_counts = {}
        optimized_images = []
        
        for item in optimized_content:
            item_type = item.get('type', 'unknown')
            optimized_counts[item_type] = optimized_counts.get(item_type, 0) + 1
            
            if item_type == 'image':
                optimized_images.append(item)
        
        logger.info(f"✅ After strategy optimization: {len(optimized_content)} items")
        for content_type, count in optimized_counts.items():
            logger.info(f"   • {content_type}: {count}")
        
        logger.info(f"📷 Images after strategy optimization: {len(optimized_images)}")
        logger.info(f"📊 Strategy stats: {strategy_stats}")
        
        # Step 4: Smart Grouping
        logger.info("\n🔄 STEP 4: Smart Grouping")
        logger.info("-" * 40)
        
        grouping_processor = SmartGroupingProcessor()
        grouped_content = grouping_processor.create_smart_groups(optimized_content)
        
        # Analyze groups
        total_items_in_groups = 0
        images_in_groups = 0
        
        for group in grouped_content:
            group_items = group.get('items', [])
            total_items_in_groups += len(group_items)
            
            for item in group_items:
                if item.get('type') == 'image':
                    images_in_groups += 1
        
        logger.info(f"✅ Created {len(grouped_content)} groups with {total_items_in_groups} total items")
        logger.info(f"📷 Images in groups: {images_in_groups}")
        
        # Summary
        logger.info("\n🎯 PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📷 Images at each stage:")
        logger.info(f"   1. Extracted from PDF: {len(extracted_images)}")
        logger.info(f"   2. In structured content: {len(image_items)}")
        logger.info(f"   3. After strategy optimization: {len(optimized_images)}")
        logger.info(f"   4. In final groups: {images_in_groups}")
        
        # Identify where images are being lost
        if len(extracted_images) != len(image_items):
            lost_in_structuring = len(extracted_images) - len(image_items)
            logger.warning(f"⚠️ {lost_in_structuring} images lost during structured content extraction!")
        
        if len(image_items) != len(optimized_images):
            lost_in_strategy = len(image_items) - len(optimized_images)
            logger.warning(f"⚠️ {lost_in_strategy} images lost during strategy optimization!")
        
        if len(optimized_images) != images_in_groups:
            lost_in_grouping = len(optimized_images) - images_in_groups
            logger.warning(f"⚠️ {lost_in_grouping} images lost during smart grouping!")
        
        if len(extracted_images) == images_in_groups:
            logger.info("✅ All extracted images preserved through the pipeline!")
        
        return {
            'extracted': len(extracted_images),
            'structured': len(image_items),
            'optimized': len(optimized_images),
            'grouped': images_in_groups,
            'total_content_items': len(structured_content),
            'total_optimized_items': len(optimized_content),
            'total_groups': len(grouped_content)
        }

def analyze_specific_pdf():
    """Analyze a specific PDF file if available"""
    # Look for PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if pdf_files:
        logger.info(f"Found {len(pdf_files)} PDF files:")
        for i, pdf_file in enumerate(pdf_files[:5]):  # Show first 5
            logger.info(f"   {i+1}. {pdf_file}")
        
        # Use the first PDF file for analysis
        test_pdf = pdf_files[0]
        logger.info(f"\n🔍 Analyzing: {test_pdf}")
        
        try:
            results = trace_image_processing_pipeline(test_pdf)
            return results
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        logger.warning("No PDF files found in current directory")
        logger.info("💡 To test with a specific PDF, place it in the current directory and run again")
        return None

def main():
    """Main function"""
    logger.info("🔍 IMAGE PIPELINE TRACER")
    logger.info("This tool traces images through the entire PDF processing pipeline")
    
    # Check if a specific PDF path was provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        logger.info(f"📄 Using provided PDF: {pdf_path}")
        results = trace_image_processing_pipeline(pdf_path)
    else:
        logger.info("📄 Looking for PDF files in current directory...")
        results = analyze_specific_pdf()
    
    if results:
        logger.info("\n🎯 ANALYSIS COMPLETE")
        logger.info("=" * 60)
        logger.info("💡 Key findings:")
        
        if results['extracted'] > results['grouped']:
            lost_images = results['extracted'] - results['grouped']
            logger.warning(f"   • {lost_images} images are being lost in the pipeline")
            logger.info("   • Check the logs above to see where they're being lost")
        else:
            logger.info("   • All extracted images are preserved through the pipeline")
        
        if results['extracted'] < 10:
            logger.info(f"   • Only {results['extracted']} images extracted - check extraction criteria")
            logger.info("   • Images might be too small or have high aspect ratios")
        
        logger.info(f"   • Total content items: {results['total_content_items']}")
        logger.info(f"   • Items after optimization: {results['total_optimized_items']}")
        logger.info(f"   • Final groups created: {results['total_groups']}")

if __name__ == "__main__":
    main()
