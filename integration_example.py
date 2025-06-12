"""
Integration Example: Final Document Assembly Pipeline

This example shows how to integrate the new comprehensive strategy into your existing workflow.
The pipeline ensures that TOC and visual elements are correctly placed while bypassing image translation.
"""

import os
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def translate_pdf_with_comprehensive_assembly(pdf_path: str, output_dir: str, target_language: str = "Greek"):
    """
    Translate PDF using the comprehensive final assembly strategy.
    
    This function demonstrates how to use the new pipeline that:
    1. Runs Nougat and PyMuPDF in parallel
    2. Reconciles their outputs into unified content blocks
    3. Bypasses image translation (USER REQUIREMENT)
    4. Generates accurate TOC with proper page numbers
    5. Assembles high-fidelity Word document
    
    Args:
        pdf_path: Path to input PDF file
        output_dir: Directory for output files
        target_language: Target language for translation
        
    Returns:
        Dictionary with processing results and file paths
    """
    
    try:
        # Import the final assembly pipeline
        from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline
        
        logger.info(f"🚀 Starting comprehensive PDF translation...")
        logger.info(f"   📄 Input: {os.path.basename(pdf_path)}")
        logger.info(f"   🌐 Target language: {target_language}")
        logger.info(f"   📁 Output directory: {output_dir}")
        logger.info(f"   🖼️ Image translation: BYPASSED (as requested)")
        
        # Initialize the pipeline
        pipeline = FinalDocumentAssemblyPipeline()
        
        # Process the PDF with comprehensive assembly
        results = await pipeline.process_pdf_with_final_assembly(
            pdf_path=pdf_path,
            output_dir=output_dir,
            target_language=target_language
        )
        
        # Display results
        if results['status'] == 'success':
            logger.info("🎉 Translation completed successfully!")
            
            # Output files
            output_files = results.get('output_files', {})
            if 'word_document' in output_files:
                logger.info(f"📄 Word document: {os.path.basename(output_files['word_document'])}")
            if 'images_folder' in output_files:
                logger.info(f"🖼️ Images folder: {os.path.basename(output_files['images_folder'])}")
            
            # Processing statistics
            stats = results.get('processing_statistics', {})
            logger.info("📊 Processing Statistics:")
            logger.info(f"   • Text blocks translated: {stats.get('translated_blocks', 0)}")
            logger.info(f"   • Images preserved: {stats.get('preserved_images', 0)}")
            logger.info(f"   • TOC entries generated: {stats.get('toc_entries', 0)}")
            logger.info(f"   • Visual elements extracted: {stats.get('visual_elements', 0)}")
            
            # Validation results
            validation = results.get('validation_results', {})
            if validation.get('issues'):
                logger.warning(f"⚠️ Issues found: {', '.join(validation['issues'])}")
            else:
                logger.info("✅ All validation checks passed")
                
        else:
            logger.error(f"❌ Translation failed: {results.get('error', 'Unknown error')}")
        
        return results
        
    except ImportError as e:
        logger.error(f"❌ Pipeline components not available: {e}")
        logger.info("💡 Please ensure all required modules are installed")
        return {'status': 'error', 'error': f'Import error: {e}'}
        
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        return {'status': 'error', 'error': str(e)}

def integrate_with_existing_workflow():
    """
    Example of how to integrate the new pipeline with your existing main_workflow.py
    """
    
    logger.info("🔗 Integration with existing workflow:")
    
    integration_code = '''
# In your main_workflow.py, add this method:

async def translate_pdf_with_final_assembly_integration(self, filepath, output_dir, target_language_override=None):
    """
    Integration method that uses the new comprehensive assembly strategy.
    Falls back to existing methods if the new pipeline is not available.
    """
    try:
        # Try to use the new comprehensive assembly pipeline
        from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline
        
        pipeline = FinalDocumentAssemblyPipeline()
        target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']
        
        results = await pipeline.process_pdf_with_final_assembly(
            pdf_path=filepath,
            output_dir=output_dir,
            target_language=target_language
        )
        
        return results
        
    except ImportError:
        # Fallback to existing structured document approach
        logger.info("🔄 Using existing structured document approach...")
        return await self.translate_pdf_structured_document_model(
            filepath, output_dir, target_language_override
        )

# Then in your main translation method, use:
if use_comprehensive_assembly:
    results = await self.translate_pdf_with_final_assembly_integration(filepath, output_dir, target_language)
else:
    results = await self.translate_pdf_structured_document_model(filepath, output_dir, target_language)
'''
    
    print(integration_code)

async def example_usage():
    """Example usage of the comprehensive assembly pipeline"""
    
    # Example PDF path (replace with your actual PDF)
    pdf_path = "sample_document.pdf"
    output_dir = "comprehensive_output"
    target_language = "Greek"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        logger.warning(f"Example PDF not found: {pdf_path}")
        logger.info("Please provide a valid PDF path to test the pipeline")
        
        # Create a mock example for demonstration
        logger.info("📝 Mock example (replace with actual PDF path):")
        pdf_path = "your_document.pdf"
    
    # Translate using comprehensive assembly
    results = await translate_pdf_with_comprehensive_assembly(
        pdf_path=pdf_path,
        output_dir=output_dir,
        target_language=target_language
    )
    
    return results

def benefits_summary():
    """Summary of benefits provided by the new comprehensive assembly strategy"""
    
    logger.info("🎯 Benefits of the Comprehensive Assembly Strategy:")
    
    benefits = '''
✅ SOLVED PROBLEMS:

1. TOC Generation:
   - Two-pass generation ensures accurate page numbers
   - Proper hyperlinks to document sections
   - Handles complex document structures

2. Image Handling:
   - Images bypass translation entirely (USER REQUIREMENT)
   - Visual elements preserved in correct positions
   - Proper image sizing and formatting

3. Content Integration:
   - Nougat provides high-quality text and structure
   - PyMuPDF provides accurate visual element extraction
   - Intelligent correlation between text and images

4. Document Quality:
   - Maintains document structure throughout pipeline
   - Preserves formatting and layout
   - Generates professional-quality output

5. Pipeline Reliability:
   - Parallel processing for efficiency
   - Fallback mechanisms for robustness
   - Comprehensive validation and reporting

🔧 TECHNICAL IMPROVEMENTS:

• Hybrid parsing strategy (Nougat + PyMuPDF)
• Unified content block reconciliation
• Enhanced document generator with block-specific rendering
• Image bypass configuration
• Quality validation framework
• Comprehensive error handling and logging

📊 PERFORMANCE BENEFITS:

• Parallel content extraction
• Efficient visual element correlation
• Optimized document assembly
• Reduced processing time for complex documents
'''
    
    print(benefits)

if __name__ == "__main__":
    logger.info("🚀 Comprehensive Final Assembly Pipeline - Integration Example")
    logger.info("=" * 70)
    
    # Show benefits
    benefits_summary()
    
    print("\n" + "=" * 70)
    
    # Show integration guide
    integrate_with_existing_workflow()
    
    print("\n" + "=" * 70)
    
    # Run example
    logger.info("🧪 Running example usage...")
    try:
        results = asyncio.run(example_usage())
        
        if results and results.get('status') == 'success':
            logger.info("🎉 Example completed successfully!")
        else:
            logger.info("ℹ️ Example completed (check logs for details)")
            
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
    
    print("\n" + "=" * 70)
    logger.info("✅ Integration example completed!")
    logger.info("💡 Use this code as a template for your own integration")
