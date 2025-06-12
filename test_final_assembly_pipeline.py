"""
Test Script for Final Document Assembly Pipeline

This script demonstrates how to use the new comprehensive strategy for final document assembly
that ensures TOC and visual elements are correctly placed while bypassing image translation.
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

def test_final_assembly_pipeline():
    """Test the final document assembly pipeline with a sample PDF"""
    
    try:
        # Import the pipeline
        from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline
        
        logger.info("🧪 Testing Final Document Assembly Pipeline...")
        
        # Initialize pipeline
        pipeline = FinalDocumentAssemblyPipeline()
        
        # Test configuration
        test_pdf_path = "sample_document.pdf"  # Replace with actual PDF path
        test_output_dir = "test_output"
        target_language = "Greek"
        
        # Check if test PDF exists
        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found: {test_pdf_path}")
            logger.info("Please provide a valid PDF path to test the pipeline")
            return False
        
        # Run the pipeline
        async def run_test():
            results = await pipeline.process_pdf_with_final_assembly(
                pdf_path=test_pdf_path,
                output_dir=test_output_dir,
                target_language=target_language
            )
            return results
        
        # Execute the test
        results = asyncio.run(run_test())
        
        # Display results
        logger.info("🎉 Test completed successfully!")
        logger.info("📊 Results Summary:")
        logger.info(f"   • Status: {results['status']}")
        logger.info(f"   • Input file: {results['input_file']}")
        logger.info(f"   • Output directory: {results['output_directory']}")
        
        if 'output_files' in results:
            for file_type, file_path in results['output_files'].items():
                logger.info(f"   • {file_type}: {os.path.basename(file_path)}")
        
        if 'processing_statistics' in results:
            stats = results['processing_statistics']
            logger.info("📈 Processing Statistics:")
            for stat_name, stat_value in stats.items():
                logger.info(f"   • {stat_name.replace('_', ' ').title()}: {stat_value}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Please ensure all required modules are available")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_individual_components():
    """Test individual components of the assembly pipeline"""
    
    logger.info("🔧 Testing individual components...")
    
    # Test 1: Hybrid Content Reconciler
    try:
        from hybrid_content_reconciler import HybridContentReconciler
        reconciler = HybridContentReconciler()
        logger.info("✅ Hybrid Content Reconciler: Available")
    except ImportError:
        logger.error("❌ Hybrid Content Reconciler: Not available")
    
    # Test 2: Enhanced Document Generator
    try:
        from enhanced_document_generator import EnhancedDocumentGenerator
        generator = EnhancedDocumentGenerator()
        logger.info("✅ Enhanced Document Generator: Available")
    except ImportError:
        logger.error("❌ Enhanced Document Generator: Not available")
    
    # Test 3: Structured Document Model
    try:
        from structured_document_model import Document, ContentType, Heading, Paragraph, ImagePlaceholder
        logger.info("✅ Structured Document Model: Available")
    except ImportError:
        logger.error("❌ Structured Document Model: Not available")
    
    # Test 4: Existing Pipeline Components
    try:
        from nougat_integration import NougatIntegration
        from async_translation_service import AsyncTranslationService
        logger.info("✅ Existing Pipeline Components: Available")
    except ImportError:
        logger.error("❌ Existing Pipeline Components: Not available")

def demonstrate_usage():
    """Demonstrate how to use the pipeline in your existing workflow"""
    
    logger.info("📖 Usage Demonstration:")
    
    usage_example = '''
# Example: Integrate the Final Assembly Pipeline into your existing workflow

import asyncio
from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline

async def translate_pdf_with_final_assembly(pdf_path, output_dir, target_language="Greek"):
    """
    Translate PDF using the comprehensive final assembly strategy.
    
    This ensures:
    - TOC is generated with accurate page numbers
    - Images are preserved without translation
    - Visual elements are correctly positioned
    - Document structure is maintained
    """
    
    # Initialize the pipeline
    pipeline = FinalDocumentAssemblyPipeline()
    
    # Process the PDF
    results = await pipeline.process_pdf_with_final_assembly(
        pdf_path=pdf_path,
        output_dir=output_dir,
        target_language=target_language
    )
    
    return results

# Usage in your main workflow
async def main():
    pdf_file = "document.pdf"
    output_folder = "translated_output"
    
    results = await translate_pdf_with_final_assembly(pdf_file, output_folder)
    
    if results['status'] == 'success':
        print(f"✅ Translation completed: {results['output_files']['word_document']}")
    else:
        print(f"❌ Translation failed: {results.get('error', 'Unknown error')}")

# Run the translation
asyncio.run(main())
'''
    
    print(usage_example)

def integration_guide():
    """Provide integration guide for existing codebase"""
    
    logger.info("🔗 Integration Guide:")
    
    integration_steps = '''
INTEGRATION STEPS FOR EXISTING CODEBASE:

1. REPLACE EXISTING DOCUMENT GENERATION:
   
   # OLD: Using existing document_generator.py
   from document_generator import WordDocumentGenerator
   generator = WordDocumentGenerator()
   generator.create_word_document_from_structured_document(...)
   
   # NEW: Using enhanced final assembly pipeline
   from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline
   pipeline = FinalDocumentAssemblyPipeline()
   results = await pipeline.process_pdf_with_final_assembly(...)

2. UPDATE MAIN WORKFLOW:
   
   # In main_workflow.py, replace the structured document workflow with:
   
   async def translate_pdf_structured_with_final_assembly(self, filepath, output_dir, ...):
       pipeline = FinalDocumentAssemblyPipeline()
       return await pipeline.process_pdf_with_final_assembly(filepath, output_dir, target_language)

3. CONFIGURE IMAGE BYPASS:
   
   # The pipeline automatically bypasses image translation
   # Images are preserved in the final document without translation
   # This addresses your requirement: "i dont want any pictures to be sent for translation"

4. BENEFITS OF THE NEW APPROACH:
   
   ✅ Unified Nougat + PyMuPDF processing
   ✅ Proper TOC generation with accurate page numbers
   ✅ Image bypass (no translation for visual content)
   ✅ Enhanced visual element positioning
   ✅ Structured document integrity throughout pipeline
   ✅ Quality validation and comprehensive reporting

5. BACKWARD COMPATIBILITY:
   
   # The new pipeline can work alongside existing code
   # Gradually migrate workflows to use the new assembly strategy
   # Existing translation services and configurations are preserved
'''
    
    print(integration_steps)

if __name__ == "__main__":
    logger.info("🚀 Final Document Assembly Pipeline - Test Suite")
    logger.info("=" * 60)
    
    # Test individual components
    test_individual_components()
    
    print("\n" + "=" * 60)
    
    # Demonstrate usage
    demonstrate_usage()
    
    print("\n" + "=" * 60)
    
    # Integration guide
    integration_guide()
    
    print("\n" + "=" * 60)
    
    # Run full pipeline test (if PDF available)
    logger.info("🧪 Running full pipeline test...")
    success = test_final_assembly_pipeline()
    
    if success:
        logger.info("🎉 All tests completed successfully!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")
