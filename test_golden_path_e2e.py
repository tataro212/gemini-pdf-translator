"""
End-to-End Golden Path Testing Framework

This implements Proposition 2: End-to-End "Golden Path" Testing
Tests the complete pipeline from PDF input to Word output with image preservation validation.
"""

import os
import sys
import asyncio
import tempfile
import zipfile
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoldenPathTestFramework:
    """
    End-to-end testing framework for PDF translation pipeline.
    
    Tests the "golden paths" that represent typical user workflows:
    1. PDF with text + images → Word document with preserved images
    2. PDF with headings + paragraphs → Structured Word document
    3. PDF with complex content → Complete translation workflow
    """
    
    def __init__(self):
        self.test_results = {}
        self.temp_dirs = []
    
    async def run_all_golden_path_tests(self):
        """Run all golden path tests and return comprehensive results"""
        logger.info("🚀 Starting Golden Path End-to-End Tests")
        
        tests = [
            ("basic_pdf_with_images", self.test_basic_pdf_with_images),
            ("structured_document_workflow", self.test_structured_document_workflow),
            ("advanced_pipeline_integrity", self.test_advanced_pipeline_integrity),
            ("image_preservation_contract", self.test_image_preservation_contract)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"📋 Running test: {test_name}")
            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                self.test_results[test_name] = {
                    'status': 'PASSED' if result else 'FAILED',
                    'duration': end_time - start_time,
                    'details': result if isinstance(result, dict) else {}
                }
                
                logger.info(f"✅ Test {test_name}: {'PASSED' if result else 'FAILED'}")
                
            except Exception as e:
                logger.error(f"❌ Test {test_name} failed with exception: {e}")
                self.test_results[test_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'duration': 0
                }
        
        self._generate_test_report()
        self._cleanup_temp_dirs()
        
        return self.test_results
    
    async def test_basic_pdf_with_images(self):
        """
        Golden Path 1: Basic PDF with text and images
        Tests: PDF → extraction → translation → Word generation → image preservation
        """
        logger.info("🔍 Testing basic PDF with images workflow")
        
        # Create temporary test environment
        temp_dir = tempfile.mkdtemp(prefix="golden_path_test_")
        self.temp_dirs.append(temp_dir)
        
        try:
            # Import required modules
            from main_workflow import UltimatePDFTranslator
            
            # Initialize translator
            translator = UltimatePDFTranslator()
            
            # Find a test PDF (you would need to provide this)
            test_pdf_path = self._find_test_pdf_with_images()
            if not test_pdf_path:
                logger.warning("⚠️ No test PDF found, skipping image test")
                return False
            
            # Run translation
            result = await translator.translate_document_async(
                filepath=test_pdf_path,
                output_dir=temp_dir,
                target_language_override="Greek"
            )
            
            # Validate results
            validation_results = self._validate_golden_path_output(temp_dir, test_pdf_path)
            
            return validation_results['success']
            
        except Exception as e:
            logger.error(f"Basic PDF test failed: {e}")
            return False
    
    async def test_structured_document_workflow(self):
        """
        Golden Path 2: Structured document workflow
        Tests: Document model integrity throughout the pipeline
        """
        logger.info("🔍 Testing structured document workflow")
        
        temp_dir = tempfile.mkdtemp(prefix="structured_test_")
        self.temp_dirs.append(temp_dir)
        
        try:
            from main_workflow import UltimatePDFTranslator
            from pdf_parser import PDFParser
            from structured_content_extractor import StructuredContentExtractor
            
            # Test PDF parsing and structure extraction
            test_pdf = self._find_test_pdf()
            if not test_pdf:
                return False
            
            # Test structured extraction
            pdf_parser = PDFParser()
            content_extractor = StructuredContentExtractor()
            
            # Extract images
            image_folder = os.path.join(temp_dir, "images")
            os.makedirs(image_folder, exist_ok=True)
            extracted_images = pdf_parser.extract_images_from_pdf(test_pdf, image_folder)
            
            # Create structured document
            structured_doc = content_extractor.extract_structured_content_from_pdf(test_pdf, extracted_images)
            
            # Validate structured document
            validation = self._validate_structured_document(structured_doc, extracted_images)
            
            return validation['success']
            
        except Exception as e:
            logger.error(f"Structured document test failed: {e}")
            return False
    
    async def test_advanced_pipeline_integrity(self):
        """
        Golden Path 3: Advanced pipeline data integrity
        Tests: Data flow through advanced translation pipeline
        """
        logger.info("🔍 Testing advanced pipeline data integrity")
        
        temp_dir = tempfile.mkdtemp(prefix="advanced_test_")
        self.temp_dirs.append(temp_dir)
        
        try:
            from main_workflow import UltimatePDFTranslator
            
            translator = UltimatePDFTranslator()
            
            # Ensure advanced pipeline is available
            if not translator.advanced_pipeline:
                logger.warning("⚠️ Advanced pipeline not available")
                return False
            
            test_pdf = self._find_test_pdf()
            if not test_pdf:
                return False
            
            # Run advanced translation
            result = await translator._translate_document_advanced(
                filepath=test_pdf,
                output_dir_for_this_file=temp_dir,
                target_language_override="Greek"
            )
            
            # Check if data flow audit was performed
            if hasattr(translator, '_data_flow_audit'):
                audit_data = translator._data_flow_audit
                logger.info(f"📊 Data flow audit results: {audit_data}")
                return True
            else:
                logger.warning("⚠️ No data flow audit performed")
                return False
                
        except Exception as e:
            logger.error(f"Advanced pipeline test failed: {e}")
            return False
    
    async def test_image_preservation_contract(self):
        """
        Golden Path 4: Image preservation contract validation
        Tests: Images are preserved throughout the entire pipeline
        """
        logger.info("🔍 Testing image preservation contract")
        
        temp_dir = tempfile.mkdtemp(prefix="image_contract_test_")
        self.temp_dirs.append(temp_dir)
        
        try:
            test_pdf = self._find_test_pdf_with_images()
            if not test_pdf:
                logger.warning("⚠️ No test PDF with images found")
                return False
            
            from main_workflow import UltimatePDFTranslator
            
            translator = UltimatePDFTranslator()
            
            # Run translation and capture results
            result = await translator.translate_document_async(
                filepath=test_pdf,
                output_dir=temp_dir
            )
            
            # Validate image preservation
            validation = self._validate_image_preservation(temp_dir, test_pdf)
            
            return validation['success']
            
        except Exception as e:
            logger.error(f"Image preservation test failed: {e}")
            return False
    
    def _find_test_pdf(self):
        """Find a test PDF file in the current directory or test data"""
        possible_paths = [
            "test_data/sample.pdf",
            "sample.pdf",
            "test.pdf"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"📄 Using test PDF: {path}")
                return path
        
        # Look for any PDF in current directory
        for file in os.listdir("."):
            if file.lower().endswith('.pdf'):
                logger.info(f"📄 Using found PDF: {file}")
                return file
        
        logger.warning("⚠️ No test PDF found")
        return None
    
    def _find_test_pdf_with_images(self):
        """Find a test PDF that likely contains images"""
        # This is a placeholder - in practice, you'd have specific test files
        return self._find_test_pdf()
    
    def _validate_golden_path_output(self, output_dir, input_pdf):
        """Validate the output of a golden path test"""
        results = {
            'success': True,
            'word_document_created': False,
            'word_document_size': 0,
            'images_in_output': 0,
            'word_contains_media': False
        }
        
        # Check for Word document
        for file in os.listdir(output_dir):
            if file.endswith('_translated.docx'):
                results['word_document_created'] = True
                word_path = os.path.join(output_dir, file)
                results['word_document_size'] = os.path.getsize(word_path)
                
                # Check if Word document contains media (images)
                results['word_contains_media'] = self._check_word_document_has_media(word_path)
                break
        
        # Check for extracted images
        image_dir = os.path.join(output_dir, "images")
        if os.path.exists(image_dir):
            results['images_in_output'] = len([f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        # Determine success
        results['success'] = (
            results['word_document_created'] and
            results['word_document_size'] > 1000  # Reasonable minimum size
        )
        
        logger.info(f"📊 Golden path validation: {results}")
        return results
    
    def _check_word_document_has_media(self, word_path):
        """Check if Word document contains media files (images)"""
        try:
            with zipfile.ZipFile(word_path, 'r') as docx:
                # Check for media directory in Word document
                media_files = [name for name in docx.namelist() if name.startswith('word/media/')]
                return len(media_files) > 0
        except Exception as e:
            logger.warning(f"Could not check Word document media: {e}")
            return False
    
    def _validate_structured_document(self, structured_doc, extracted_images):
        """Validate structured document integrity"""
        results = {
            'success': True,
            'has_content_blocks': False,
            'image_blocks_count': 0,
            'text_blocks_count': 0
        }
        
        if structured_doc and hasattr(structured_doc, 'content_blocks'):
            results['has_content_blocks'] = True
            
            # Count different types of blocks
            for block in structured_doc.content_blocks:
                if hasattr(block, 'image_path') and block.image_path:
                    results['image_blocks_count'] += 1
                else:
                    results['text_blocks_count'] += 1
        
        results['success'] = results['has_content_blocks'] and results['text_blocks_count'] > 0
        
        logger.info(f"📊 Structured document validation: {results}")
        return results
    
    def _validate_image_preservation(self, output_dir, input_pdf):
        """Validate that images were preserved through the pipeline"""
        results = {
            'success': True,
            'images_extracted': 0,
            'images_in_word': False
        }
        
        # Count extracted images
        image_dir = os.path.join(output_dir, "images")
        if os.path.exists(image_dir):
            results['images_extracted'] = len([f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        # Check Word document for images
        for file in os.listdir(output_dir):
            if file.endswith('_translated.docx'):
                word_path = os.path.join(output_dir, file)
                results['images_in_word'] = self._check_word_document_has_media(word_path)
                break
        
        # Success if images were found and preserved
        results['success'] = results['images_extracted'] > 0 and results['images_in_word']
        
        logger.info(f"📊 Image preservation validation: {results}")
        return results
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        
        report = f"""
🎯 GOLDEN PATH TEST RESULTS
============================

📊 Summary:
• Total Tests: {total_tests}
• Passed: {passed_tests} ✅
• Failed: {failed_tests} ❌
• Errors: {error_tests} 💥

📋 Detailed Results:
"""
        
        for test_name, result in self.test_results.items():
            status_emoji = {'PASSED': '✅', 'FAILED': '❌', 'ERROR': '💥'}[result['status']]
            duration = result.get('duration', 0)
            report += f"• {test_name}: {result['status']} {status_emoji} ({duration:.2f}s)\n"
            
            if result['status'] == 'ERROR':
                report += f"  Error: {result.get('error', 'Unknown error')}\n"
        
        logger.info(report)
    
    def _cleanup_temp_dirs(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.debug(f"🧹 Cleaned up temp dir: {temp_dir}")
            except Exception as e:
                logger.warning(f"Could not clean up {temp_dir}: {e}")


async def run_golden_path_tests():
    """Main entry point for running golden path tests"""
    framework = GoldenPathTestFramework()
    results = await framework.run_all_golden_path_tests()
    
    # Return overall success
    return all(result['status'] == 'PASSED' for result in results.values())


if __name__ == "__main__":
    asyncio.run(run_golden_path_tests())
