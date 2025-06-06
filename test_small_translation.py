"""
Small Test Translation Script

Tests the complete modular workflow with a real PDF file but limits processing
to avoid excessive API usage during testing.
"""

import os
import asyncio
import logging
import tempfile
import shutil
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_small_translation():
    """Test the complete translation workflow with a small sample"""
    
    logger.info("🧪 STARTING SMALL TRANSLATION TEST")
    logger.info("=" * 50)
    
    # Available test PDFs
    test_pdfs = [
        r"C:\Users\30694\Desktop\27212-Article Text-65124-1-10-20190429.pdf",
        r"C:\Users\30694\Desktop\754-Article Text-4691-1-10-20200127.pdf", 
        r"C:\Users\30694\Desktop\799-810+v.pdf"
    ]
    
    # Find the first available PDF
    test_pdf = None
    for pdf_path in test_pdfs:
        if os.path.exists(pdf_path):
            test_pdf = pdf_path
            break
    
    if not test_pdf:
        logger.error("❌ No test PDF files found. Please ensure at least one PDF exists.")
        return False
    
    logger.info(f"📄 Using test PDF: {os.path.basename(test_pdf)}")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "test_output")
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"📁 Output directory: {output_dir}")
        
        try:
            # Import the main workflow
            from main_workflow import UltimatePDFTranslator
            
            # Create translator instance
            translator = UltimatePDFTranslator()
            
            # Test Step 1: PDF Parsing
            logger.info("🔍 Step 1: Testing PDF parsing...")
            
            # Extract images (limited test)
            image_folder = os.path.join(output_dir, "images")
            extracted_images = translator.pdf_parser.extract_images_from_pdf(test_pdf, image_folder)
            logger.info(f"✅ Extracted {len(extracted_images)} images")
            
            # Extract cover page
            cover_data = translator.pdf_parser.extract_cover_page_from_pdf(test_pdf, output_dir)
            logger.info(f"✅ Cover page: {'extracted' if cover_data else 'not available'}")
            
            # Test Step 2: Content Extraction (limited)
            logger.info("📝 Step 2: Testing content extraction...")
            
            structured_content = translator.content_extractor.extract_structured_content_from_pdf(
                test_pdf, extracted_images
            )
            
            if not structured_content:
                logger.error("❌ No content extracted from PDF")
                return False
            
            logger.info(f"✅ Extracted {len(structured_content)} content items")
            
            # Show sample of extracted content
            text_items = [item for item in structured_content if item.get('type') != 'image' and item.get('text')]
            if text_items:
                sample_item = text_items[0]
                sample_text = sample_item.get('text', '')[:100]
                logger.info(f"📄 Sample content: '{sample_text}...'")
            
            # Test Step 3: Optimization (without translation)
            logger.info("⚡ Step 3: Testing optimization...")
            
            from optimization_manager import optimization_manager
            
            # Test with first 5 text items only to limit API usage
            test_items = text_items[:5] if len(text_items) > 5 else text_items
            
            if test_items:
                batches, params = optimization_manager.optimize_content_for_translation(
                    test_items, "Ελληνικά"
                )
                logger.info(f"✅ Optimization: {len(test_items)} items → {len(batches)} batches")
                logger.info(f"✅ Optimization params: {params}")
            else:
                logger.warning("⚠️ No text items found for optimization test")
            
            # Test Step 4: Translation Service (single item test)
            logger.info("🌐 Step 4: Testing translation service...")
            
            from translation_service import translation_service
            
            if test_items:
                # Test with just the first item to minimize API usage
                test_text = test_items[0].get('text', '')[:200]  # Limit to 200 chars
                
                logger.info(f"🔤 Testing translation of: '{test_text[:50]}...'")
                
                try:
                    # This will make an actual API call
                    translated_text = await translation_service.translate_text(
                        test_text, 
                        target_language="Ελληνικά",
                        style_guide="academic document"
                    )
                    
                    logger.info(f"✅ Translation successful!")
                    logger.info(f"🔤 Original: '{test_text[:50]}...'")
                    logger.info(f"🔤 Translated: '{translated_text[:50]}...'")
                    
                except Exception as e:
                    logger.error(f"❌ Translation failed: {e}")
                    return False
            
            # Test Step 5: Document Generation (with sample content)
            logger.info("📄 Step 5: Testing document generation...")
            
            from document_generator import document_generator
            
            # Create a small sample document
            sample_content = [
                {'type': 'h1', 'text': 'Test Document', 'page_num': 1, 'block_num': 1},
                {'type': 'paragraph', 'text': 'This is a test paragraph.', 'page_num': 1, 'block_num': 2},
                {'type': 'paragraph', 'text': 'Another test paragraph.', 'page_num': 1, 'block_num': 3}
            ]
            
            word_output = os.path.join(output_dir, "test_document.docx")
            
            success = document_generator.create_word_document_with_structure(
                sample_content, word_output, image_folder, cover_data
            )
            
            if success and os.path.exists(word_output):
                logger.info(f"✅ Word document created: {word_output}")
                file_size = os.path.getsize(word_output)
                logger.info(f"📊 File size: {file_size:,} bytes")
            else:
                logger.error("❌ Word document creation failed")
                return False
            
            # Test Step 6: PDF Conversion
            logger.info("📑 Step 6: Testing PDF conversion...")
            
            from document_generator import pdf_converter
            
            pdf_output = os.path.join(output_dir, "test_document.pdf")
            
            try:
                pdf_success = pdf_converter.convert_word_to_pdf(word_output, pdf_output)
                
                if pdf_success and os.path.exists(pdf_output):
                    logger.info(f"✅ PDF conversion successful: {pdf_output}")
                    pdf_size = os.path.getsize(pdf_output)
                    logger.info(f"📊 PDF size: {pdf_size:,} bytes")
                else:
                    logger.warning("⚠️ PDF conversion failed (this is optional)")
            except Exception as e:
                logger.warning(f"⚠️ PDF conversion error: {e} (this is optional)")
            
            # Test Step 7: Google Drive (test availability only)
            logger.info("☁️ Step 7: Testing Google Drive availability...")
            
            from drive_uploader import drive_uploader
            
            if drive_uploader.is_available():
                logger.info("✅ Google Drive is available and authenticated")
            else:
                logger.info("ℹ️ Google Drive not available (optional feature)")
            
            # Save caches
            translation_service.save_caches()
            logger.info("✅ Translation cache saved")
            
            logger.info("=" * 50)
            logger.info("🎉 SMALL TRANSLATION TEST COMPLETED SUCCESSFULLY!")
            logger.info("=" * 50)
            
            # Show what was created
            logger.info("📁 Generated files:")
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    logger.info(f"  • {file} ({size:,} bytes)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Main async wrapper for the test"""
    return await test_small_translation()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n✅ ALL TESTS PASSED! The modular PDF translator is working correctly.")
            print("🚀 You can now use 'python main_workflow.py' for full translations.")
        else:
            print("\n❌ Some tests failed. Please check the output above for details.")
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        import traceback
        traceback.print_exc()
