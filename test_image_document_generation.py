#!/usr/bin/env python3
"""
Test Image Document Generation

This script specifically tests whether images are being properly included
in the final Word document generation process.

Usage: python test_image_document_generation.py
"""

import os
import sys
import logging
import tempfile
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_image_document_generation():
    """Test the complete image processing pipeline"""
    
    pdf_path = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return False
    
    logger.info("🧪 Testing complete image processing pipeline...")
    
    try:
        from pdf_parser import PDFParser, StructuredContentExtractor
        from document_generator import WordDocumentGenerator
        from config_manager import config_manager
        
        # Step 1: Extract images
        logger.info("📷 Step 1: Extracting images...")
        parser = PDFParser()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_images = parser.extract_images_from_pdf(pdf_path, temp_dir)
            logger.info(f"✅ Extracted {len(extracted_images)} images")
            
            # Log image details
            for i, img in enumerate(extracted_images[:3]):  # First 3 images
                logger.info(f"   Image {i+1}: {img.get('filename')} ({img.get('width')}x{img.get('height')})")
            
            # Step 2: Create structured content
            logger.info("📋 Step 2: Creating structured content...")
            extractor = StructuredContentExtractor()
            document = extractor.extract_structured_content_from_pdf(pdf_path, extracted_images)
            
            # Count image blocks
            image_blocks = [block for block in document.content_blocks if hasattr(block, 'image_path') and block.image_path]
            logger.info(f"✅ Created {len(image_blocks)} image blocks in document")
            
            # Log image block details
            for i, img_block in enumerate(image_blocks):
                logger.info(f"   Image Block {i+1}: {os.path.basename(img_block.image_path)} on page {img_block.page_num}")
                logger.info(f"      Path exists: {os.path.exists(img_block.image_path)}")
                logger.info(f"      OCR text: {img_block.ocr_text[:50] if img_block.ocr_text else 'None'}...")
            
            # Step 3: Test document generation
            logger.info("📄 Step 3: Testing document generation...")
            
            # Create a small test document with just the first few blocks including images
            test_blocks = []
            added_images = 0
            
            for block in document.content_blocks[:50]:  # First 50 blocks
                test_blocks.append(block)
                if hasattr(block, 'image_path') and block.image_path:
                    added_images += 1
                    if added_images >= 2:  # Include at least 2 images
                        break
            
            # Create test document
            test_document = type(document)(
                title="Test Document with Images",
                content_blocks=test_blocks,
                source_filepath=pdf_path,
                total_pages=1,
                metadata={'test': True}
            )
            
            logger.info(f"📝 Created test document with {len(test_blocks)} blocks including {added_images} images")
            
            # Generate Word document
            generator = WordDocumentGenerator()
            
            test_output_path = os.path.join(temp_dir, "test_with_images.docx")
            
            # Use the actual image directory from extracted images
            image_folder = temp_dir
            
            logger.info(f"🔧 Generating Word document with images from: {image_folder}")

            result_path = generator.create_word_document_from_structured_document(
                structured_document=test_document,
                output_filepath=test_output_path,
                image_folder_path=image_folder
            )
            
            if result_path and os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                logger.info(f"✅ Test document generated successfully: {file_size} bytes")
                
                # Check if the file size suggests images were included
                if file_size > 50000:  # More than 50KB suggests images
                    logger.info("🖼️ File size suggests images were included")
                    return True
                else:
                    logger.warning("⚠️ File size is small - images may not be included")
                    return False
            else:
                logger.error("❌ Document generation failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def test_main_workflow_image_processing():
    """Test the main workflow's image processing"""
    
    logger.info("🔄 Testing main workflow image processing...")
    
    try:
        from main_workflow import UltimatePDFTranslator
        
        translator = UltimatePDFTranslator()
        
        # Check if image processing is enabled
        if hasattr(translator, 'config_manager'):
            extract_images = translator.config_manager.get_config_value('PDFProcessing', 'extract_images', True, bool)
            perform_ocr = translator.config_manager.get_config_value('PDFProcessing', 'perform_ocr_on_images', True, bool)
            
            logger.info(f"✅ Main workflow configuration:")
            logger.info(f"   Extract images: {extract_images}")
            logger.info(f"   Perform OCR: {perform_ocr}")
            
            if not extract_images:
                logger.error("❌ Image extraction is disabled in main workflow!")
                return False
            
            return True
        else:
            logger.warning("⚠️ Could not access config manager")
            return False
            
    except Exception as e:
        logger.error(f"❌ Main workflow test failed: {e}")
        return False

def check_recent_translation_output():
    """Check if recent translation outputs contain images"""
    
    logger.info("📁 Checking recent translation outputs...")
    
    # Look for recent translation outputs
    possible_dirs = [
        "C:\\Users\\30694\\Downloads\\sickdays\\A World Beyond Physics _ The Emergence and Evolution of Life",
        "output",
        "translated_documents"
    ]
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            logger.info(f"📂 Checking directory: {dir_path}")
            
            # Look for Word documents
            for file in os.listdir(dir_path):
                if file.endswith('.docx') and 'translated' in file.lower():
                    file_path = os.path.join(dir_path, file)
                    file_size = os.path.getsize(file_path)
                    
                    logger.info(f"📄 Found translated document: {file}")
                    logger.info(f"   Size: {file_size:,} bytes")
                    
                    if file_size > 100000:  # More than 100KB
                        logger.info("✅ File size suggests images may be included")
                    else:
                        logger.warning("⚠️ File size is small - images may be missing")
                    
                    return True
    
    logger.warning("⚠️ No recent translation outputs found")
    return False

def main():
    """Main test function"""
    
    logger.info("🧪 TESTING IMAGE DOCUMENT GENERATION PIPELINE")
    logger.info("="*60)
    
    # Test 1: Complete pipeline test
    logger.info("\n🧪 Test 1: Complete image processing pipeline")
    pipeline_success = test_image_document_generation()
    
    # Test 2: Main workflow configuration
    logger.info("\n🧪 Test 2: Main workflow configuration")
    workflow_success = test_main_workflow_image_processing()
    
    # Test 3: Check recent outputs
    logger.info("\n🧪 Test 3: Recent translation outputs")
    output_check = check_recent_translation_output()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY:")
    logger.info(f"   Pipeline Test: {'✅ PASS' if pipeline_success else '❌ FAIL'}")
    logger.info(f"   Workflow Config: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    logger.info(f"   Output Check: {'✅ PASS' if output_check else '❌ FAIL'}")
    
    if pipeline_success and workflow_success:
        logger.info("\n✅ CONCLUSION: Image processing pipeline is working correctly!")
        logger.info("💡 If you're not seeing images in final documents, the issue may be:")
        logger.info("   • Image file paths not being preserved during translation")
        logger.info("   • Document viewer not displaying images properly")
        logger.info("   • Images being filtered out during processing")
    else:
        logger.info("\n❌ CONCLUSION: There are issues with the image processing pipeline")
        logger.info("💡 Check the error messages above for specific problems")
    
    return pipeline_success and workflow_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
