import os
import asyncio
import logging
from main_workflow import UltimatePDFTranslator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow():
    try:
        # Initialize translator
        translator = UltimatePDFTranslator()
        
        # Test file path
        test_pdf = "test.pdf"
        if not os.path.exists(test_pdf):
            logger.error(f"Test PDF file '{test_pdf}' not found!")
            return False
            
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Run translation
        logger.info(f"Starting translation of {test_pdf}...")
        result = await translator.translate_document_async(
            filepath=test_pdf,
            output_dir_for_this_file=output_dir
        )
        
        if result:
            logger.info("✅ Translation completed successfully!")
            return True
        else:
            logger.error("❌ Translation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in workflow test: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_workflow()) 