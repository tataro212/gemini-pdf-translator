#!/usr/bin/env python3
"""
Test Advanced Pipeline with Images

This script tests the fixed advanced pipeline to ensure it preserves images
during the translation process.

Usage: python test_advanced_pipeline_with_images.py
"""

import os
import sys
import logging
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_advanced_pipeline_with_images():
    """Test the advanced pipeline with image preservation"""
    
    pdf_path = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return False
    
    logger.info("🧪 Testing advanced pipeline with image preservation...")
    
    try:
        from main_workflow import UltimatePDFTranslator
        import tempfile
        
        # Create translator instance
        translator = UltimatePDFTranslator()
        
        # Check if advanced pipeline is available
        if not translator.advanced_pipeline:
            logger.error("❌ Advanced pipeline not available")
            return False
        
        logger.info("✅ Advanced pipeline available")
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "test_output")
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"📁 Using temporary output directory: {output_dir}")
            
            # Test the advanced translation workflow
            logger.info("🔄 Starting advanced translation test...")
            
            result = await translator._translate_document_advanced(
                filepath=pdf_path,
                output_dir_for_this_file=output_dir,
                target_language_override="Greek"
            )
            
            # Check if Word document was created
            expected_docx = os.path.join(output_dir, "A World Beyond Physics _ The Emergence and Evolution of Life _translated.docx")
            
            if os.path.exists(expected_docx):
                file_size = os.path.getsize(expected_docx)
                logger.info(f"✅ Word document created: {file_size:,} bytes")
                
                # Check if images folder was created
                images_folder = os.path.join(output_dir, "images")
                if os.path.exists(images_folder):
                    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    logger.info(f"🖼️ Images folder contains {len(image_files)} image files")
                    
                    # Check document for images using our verification script
                    logger.info("🔍 Checking document for embedded images...")
                    
                    try:
                        from verify_images_in_translated_document import check_images_in_docx
                        has_images = check_images_in_docx(expected_docx)
                        
                        if has_images:
                            logger.info("🎉 SUCCESS: Advanced pipeline preserved images in translated document!")
                            return True
                        else:
                            logger.warning("⚠️ Document created but no images detected")
                            return False
                            
                    except ImportError:
                        logger.warning("⚠️ Image verification script not available, checking file size instead")
                        
                        # Large file size suggests images are included
                        if file_size > 100000:  # More than 100KB
                            logger.info("🎉 SUCCESS: File size suggests images are included!")
                            return True
                        else:
                            logger.warning("⚠️ File size is small - images may not be included")
                            return False
                else:
                    logger.warning("⚠️ Images folder not created")
                    return False
            else:
                logger.error("❌ Word document was not created")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

async def test_structured_document_creation():
    """Test structured document creation with images"""
    
    logger.info("🧪 Testing structured document creation...")
    
    try:
        from pdf_parser import PDFParser, StructuredContentExtractor
        import tempfile
        
        pdf_path = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
        
        if not os.path.exists(pdf_path):
            logger.error(f"❌ PDF file not found: {pdf_path}")
            return False
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract images
            parser = PDFParser()
            extracted_images = parser.extract_images_from_pdf(pdf_path, temp_dir)
            logger.info(f"🖼️ Extracted {len(extracted_images)} images")
            
            # Create structured document
            extractor = StructuredContentExtractor()
            document = extractor.extract_structured_content_from_pdf(pdf_path, extracted_images)
            
            if hasattr(document, 'content_blocks'):
                logger.info(f"📊 Created structured document with {len(document.content_blocks)} blocks")
                
                # Count image blocks
                image_blocks = [block for block in document.content_blocks if hasattr(block, 'image_path') and block.image_path]
                logger.info(f"🖼️ Document contains {len(image_blocks)} image blocks")
                
                if len(image_blocks) > 0:
                    logger.info("✅ Structured document creation with images works correctly!")
                    return True
                else:
                    logger.warning("⚠️ No image blocks found in structured document")
                    return False
            else:
                logger.error("❌ Structured document creation failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Structured document test failed: {e}")
        return False

async def main():
    """Main test function"""
    
    logger.info("🧪 TESTING ADVANCED PIPELINE WITH IMAGE PRESERVATION")
    logger.info("="*60)
    
    # Test 1: Structured document creation
    logger.info("\n🧪 Test 1: Structured document creation with images")
    structured_test = await test_structured_document_creation()
    
    # Test 2: Advanced pipeline with images
    logger.info("\n🧪 Test 2: Advanced pipeline with image preservation")
    pipeline_test = await test_advanced_pipeline_with_images()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY:")
    logger.info(f"   Structured Document: {'✅ PASS' if structured_test else '❌ FAIL'}")
    logger.info(f"   Advanced Pipeline: {'✅ PASS' if pipeline_test else '❌ FAIL'}")
    
    if structured_test and pipeline_test:
        logger.info("\n🎉 SUCCESS: Advanced pipeline now preserves images correctly!")
        logger.info("💡 The fix has resolved the 'zero non-text items' issue")
        logger.info("🖼️ Images should now appear in translated documents")
    elif structured_test:
        logger.info("\n⚠️ PARTIAL SUCCESS: Structured documents work but pipeline needs adjustment")
        logger.info("💡 The image extraction works, but translation application may need fixes")
    else:
        logger.info("\n❌ FAILURE: Issues remain with image processing")
        logger.info("💡 Check the error messages above for specific problems")
    
    return structured_test and pipeline_test

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
