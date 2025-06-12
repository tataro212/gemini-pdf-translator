#!/usr/bin/env python3
"""
Debug script to test the latest translation fixes and identify the real issues.
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug_translation.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_translation_debug():
    """Test the translation with detailed debugging"""
    
    try:
        # Import required modules
        from main_workflow import MainWorkflow
        from config_manager import config_manager
        
        logger.info("🔧 Starting Translation Debug Test")
        logger.info("=" * 60)
        
        # Initialize workflow
        workflow = MainWorkflow()
        
        # Find a test PDF file
        test_files = [
            "test.pdf",
            "sample.pdf", 
            "document.pdf"
        ]
        
        test_file = None
        for filename in test_files:
            if os.path.exists(filename):
                test_file = filename
                break
        
        if not test_file:
            logger.error("❌ No test PDF file found. Please place a PDF file in the current directory.")
            logger.info("💡 Expected files: test.pdf, sample.pdf, or document.pdf")
            return
        
        logger.info(f"📄 Using test file: {test_file}")
        
        # Set up output directory
        output_dir = "debug_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Test document extraction first
        logger.info("🔍 Step 1: Testing document extraction...")
        
        try:
            from pdf_parser import StructuredContentExtractor
            extractor = StructuredContentExtractor()
            
            # Extract images
            image_folder = os.path.join(output_dir, "images")
            os.makedirs(image_folder, exist_ok=True)
            
            extracted_images = workflow.pdf_parser.extract_images_from_pdf(test_file, image_folder)
            logger.info(f"📷 Extracted {len(extracted_images)} images")
            
            # Extract structured content
            document = extractor.extract_structured_content_from_pdf(test_file, extracted_images)
            
            if document:
                stats = document.get_statistics()
                logger.info(f"📊 Document extraction successful:")
                logger.info(f"   • Total blocks: {stats['total_blocks']}")
                logger.info(f"   • Total pages: {stats['total_pages']}")
                logger.info(f"   • Translatable blocks: {stats['translatable_blocks']}")
                
                for block_type, count in stats['blocks_by_type'].items():
                    logger.info(f"   • {block_type}: {count}")
                    
                # Test translation service
                logger.info("🌐 Step 2: Testing translation service...")
                
                from translation_service import translation_service
                
                # Get translatable blocks
                translatable_blocks = document.get_translatable_blocks()
                logger.info(f"🎯 Found {len(translatable_blocks)} translatable blocks")
                
                if translatable_blocks:
                    # Test translating just the first few blocks
                    test_blocks = translatable_blocks[:3]
                    logger.info(f"🧪 Testing translation of first {len(test_blocks)} blocks...")
                    
                    for i, block in enumerate(test_blocks):
                        try:
                            logger.info(f"📝 Testing block {i+1}: {type(block).__name__}")
                            logger.info(f"   Content preview: {block.content[:100]}...")
                            
                            # Test individual translation
                            translated_content = await translation_service._translate_content_block(
                                block.content, "Greek", "", type(block).__name__.lower()
                            )
                            
                            logger.info(f"✅ Block {i+1} translated successfully")
                            logger.info(f"   Translation preview: {translated_content[:100]}...")
                            
                        except Exception as e:
                            logger.error(f"❌ Block {i+1} translation failed: {type(e).__name__}: {str(e)}")
                            logger.error(f"   Block content: {block.content[:200]}...")
                            
                            # Try to get more details about the error
                            import traceback
                            logger.error(f"   Full traceback: {traceback.format_exc()}")
                
                # Test full parallel translation
                logger.info("🚀 Step 3: Testing parallel translation...")
                
                try:
                    translated_document = await translation_service.translate_document(
                        document, "Greek", ""
                    )
                    
                    if translated_document:
                        translated_stats = translated_document.get_statistics()
                        logger.info(f"✅ Parallel translation successful:")
                        logger.info(f"   • Translated blocks: {translated_stats['total_blocks']}")
                        logger.info(f"   • Translatable blocks: {translated_stats['translatable_blocks']}")
                    else:
                        logger.error("❌ Parallel translation returned None")
                        
                except Exception as e:
                    logger.error(f"❌ Parallel translation failed: {type(e).__name__}: {str(e)}")
                    import traceback
                    logger.error(f"   Full traceback: {traceback.format_exc()}")
            
            else:
                logger.error("❌ Document extraction failed - no document returned")
                
        except Exception as e:
            logger.error(f"❌ Document extraction failed: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"   Full traceback: {traceback.format_exc()}")
        
        logger.info("🔧 Debug test completed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Debug test failed: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_translation_debug())
