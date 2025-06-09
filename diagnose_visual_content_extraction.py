#!/usr/bin/env python3
"""
Visual Content Extraction Diagnostic Tool

This script diagnoses why visual content (images, diagrams, tables, etc.) 
is not being extracted from PDFs despite having Nougat and other tools working.

Usage: python diagnose_visual_content_extraction.py [pdf_path]
"""

import os
import sys
import logging
import fitz  # PyMuPDF
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VisualContentDiagnostic:
    """Comprehensive diagnostic for visual content extraction issues"""
    
    def __init__(self):
        self.results = {}
        
    def diagnose_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Run comprehensive visual content diagnostic on a PDF"""
        
        if not os.path.exists(pdf_path):
            logger.error(f"❌ PDF file not found: {pdf_path}")
            return {'error': 'File not found'}
        
        logger.info(f"🔍 Diagnosing visual content extraction for: {os.path.basename(pdf_path)}")
        
        # Test 1: Basic PDF analysis
        basic_analysis = self._analyze_pdf_basic(pdf_path)
        
        # Test 2: PyMuPDF image detection
        pymupdf_images = self._test_pymupdf_image_extraction(pdf_path)
        
        # Test 3: Configuration check
        config_check = self._check_configuration()
        
        # Test 4: Nougat integration test
        nougat_test = self._test_nougat_integration(pdf_path)
        
        # Test 5: PDF parser test
        pdf_parser_test = self._test_pdf_parser(pdf_path)
        
        # Test 6: Content extractor test
        content_extractor_test = self._test_content_extractor(pdf_path)
        
        # Compile results
        results = {
            'pdf_path': pdf_path,
            'basic_analysis': basic_analysis,
            'pymupdf_images': pymupdf_images,
            'configuration': config_check,
            'nougat_integration': nougat_test,
            'pdf_parser': pdf_parser_test,
            'content_extractor': content_extractor_test
        }
        
        self._generate_diagnostic_report(results)
        return results
    
    def _analyze_pdf_basic(self, pdf_path: str) -> Dict[str, Any]:
        """Basic PDF analysis using PyMuPDF"""
        logger.info("📄 Running basic PDF analysis...")
        
        try:
            doc = fitz.open(pdf_path)
            
            total_pages = len(doc)
            total_images = 0
            pages_with_images = 0
            image_details = []
            
            for page_num in range(total_pages):
                page = doc[page_num]
                images = page.get_images(full=True)
                
                if images:
                    pages_with_images += 1
                    total_images += len(images)
                    
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        image_details.append({
                            'page': page_num + 1,
                            'index': img_index + 1,
                            'width': pix.width,
                            'height': pix.height,
                            'colorspace': pix.colorspace.name if pix.colorspace else 'Unknown',
                            'size_bytes': len(pix.tobytes())
                        })
                        
                        pix = None
            
            doc.close()
            
            result = {
                'total_pages': total_pages,
                'total_images': total_images,
                'pages_with_images': pages_with_images,
                'image_details': image_details[:10],  # First 10 images
                'status': 'success'
            }
            
            logger.info(f"✅ Basic analysis: {total_images} images found on {pages_with_images}/{total_pages} pages")
            return result
            
        except Exception as e:
            logger.error(f"❌ Basic PDF analysis failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _test_pymupdf_image_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """Test direct PyMuPDF image extraction"""
        logger.info("🖼️ Testing PyMuPDF image extraction...")
        
        try:
            import tempfile
            
            doc = fitz.open(pdf_path)
            extracted_images = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                for page_num in range(min(3, len(doc))):  # Test first 3 pages
                    page = doc[page_num]
                    images = page.get_images(full=True)
                    
                    for img_index, img in enumerate(images):
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            
                            if pix.width >= 8 and pix.height >= 8:  # Match config minimums
                                img_filename = f"test_page_{page_num + 1}_img_{img_index + 1}.png"
                                img_filepath = os.path.join(temp_dir, img_filename)
                                
                                if pix.colorspace and pix.colorspace.name != "CMYK":
                                    pix.save(img_filepath)
                                else:
                                    pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                                    pix_rgb.save(img_filepath)
                                    pix_rgb = None
                                
                                extracted_images.append({
                                    'page': page_num + 1,
                                    'filename': img_filename,
                                    'width': pix.width,
                                    'height': pix.height,
                                    'size_bytes': os.path.getsize(img_filepath)
                                })
                            
                            pix = None
                            
                        except Exception as e:
                            logger.warning(f"Failed to extract image {img_index + 1} from page {page_num + 1}: {e}")
            
            doc.close()
            
            result = {
                'extracted_count': len(extracted_images),
                'extracted_images': extracted_images,
                'status': 'success'
            }
            
            logger.info(f"✅ PyMuPDF extraction test: {len(extracted_images)} images extracted successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ PyMuPDF extraction test failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration settings"""
        logger.info("⚙️ Checking configuration...")
        
        try:
            from config_manager import config_manager
            
            config_values = {
                'extract_images': config_manager.get_config_value('PDFProcessing', 'extract_images', True, bool),
                'perform_ocr_on_images': config_manager.get_config_value('PDFProcessing', 'perform_ocr_on_images', True, bool),
                'min_image_width_px': config_manager.get_config_value('PDFProcessing', 'min_image_width_px', 8, int),
                'min_image_height_px': config_manager.get_config_value('PDFProcessing', 'min_image_height_px', 8, int),
                'extract_tables_as_images': config_manager.get_config_value('PDFProcessing', 'extract_tables_as_images', False, bool),
                'extract_figures_by_caption': config_manager.get_config_value('PDFProcessing', 'extract_figures_by_caption', True, bool),
                'use_advanced_features': config_manager.get_config_value('TranslationEnhancements', 'use_advanced_features', True, bool),
                'use_intelligent_pipeline': config_manager.get_config_value('IntelligentPipeline', 'use_intelligent_pipeline', True, bool)
            }
            
            logger.info("✅ Configuration loaded successfully")
            for key, value in config_values.items():
                logger.info(f"   {key}: {value}")
            
            return {'status': 'success', 'config': config_values}
            
        except Exception as e:
            logger.error(f"❌ Configuration check failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _test_nougat_integration(self, pdf_path: str) -> Dict[str, Any]:
        """Test Nougat integration"""
        logger.info("🧠 Testing Nougat integration...")
        
        try:
            from nougat_integration import NougatIntegration
            
            nougat = NougatIntegration()
            
            if not nougat.nougat_available:
                return {'status': 'unavailable', 'message': 'Nougat not available'}
            
            # Test basic Nougat functionality
            logger.info("🔧 Testing Nougat PDF parsing...")
            result = nougat.parse_pdf_with_nougat(pdf_path)
            
            if result:
                visual_elements = result.get('visual_elements', [])
                logger.info(f"✅ Nougat integration working: {len(visual_elements)} visual elements detected")
                
                return {
                    'status': 'success',
                    'visual_elements_count': len(visual_elements),
                    'visual_elements': visual_elements[:5],  # First 5 elements
                    'analysis': result.get('analysis', {})
                }
            else:
                logger.warning("⚠️ Nougat returned no results")
                return {'status': 'no_results', 'message': 'Nougat returned no results'}
            
        except Exception as e:
            logger.error(f"❌ Nougat integration test failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _test_pdf_parser(self, pdf_path: str) -> Dict[str, Any]:
        """Test PDF parser image extraction"""
        logger.info("📝 Testing PDF parser...")
        
        try:
            from pdf_parser import PDFParser
            import tempfile
            
            parser = PDFParser()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                extracted_images = parser.extract_images_from_pdf(pdf_path, temp_dir)
                
                logger.info(f"✅ PDF parser test: {len(extracted_images)} images extracted")
                
                return {
                    'status': 'success',
                    'extracted_count': len(extracted_images),
                    'extracted_images': extracted_images[:5]  # First 5 images
                }
                
        except Exception as e:
            logger.error(f"❌ PDF parser test failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _test_content_extractor(self, pdf_path: str) -> Dict[str, Any]:
        """Test content extractor"""
        logger.info("📋 Testing content extractor...")

        try:
            from pdf_parser import StructuredContentExtractor, PDFParser
            import tempfile

            # First extract images to test with
            parser = PDFParser()
            with tempfile.TemporaryDirectory() as temp_dir:
                extracted_images = parser.extract_images_from_pdf(pdf_path, temp_dir)
                logger.info(f"🖼️ Extracted {len(extracted_images)} images for content extractor test")

                extractor = StructuredContentExtractor()

                # Test with actual extracted images
                document = extractor.extract_structured_content_from_pdf(pdf_path, extracted_images)

            # Check if we got a Document object
            if hasattr(document, 'content_blocks'):
                # New structured document model
                content_blocks = document.content_blocks
                content_types = {}

                for block in content_blocks:
                    if hasattr(block, 'get_content_type'):
                        content_type = block.get_content_type().value
                    else:
                        content_type = type(block).__name__.lower()
                    content_types[content_type] = content_types.get(content_type, 0) + 1

                logger.info(f"✅ Content extractor test: {len(content_blocks)} content blocks extracted")
                logger.info(f"📊 Document statistics: {document.get_statistics() if hasattr(document, 'get_statistics') else 'N/A'}")

                for content_type, count in content_types.items():
                    logger.info(f"   {content_type}: {count}")

                # Check for images specifically (ImagePlaceholder blocks)
                image_blocks = [block for block in content_blocks if hasattr(block, 'get_content_type') and block.get_content_type().value == 'image_placeholder']
                logger.info(f"🖼️ Image blocks found: {len(image_blocks)}")

                # Also check for any blocks with image_path attribute
                blocks_with_images = [block for block in content_blocks if hasattr(block, 'image_path') and block.image_path]
                logger.info(f"📷 Blocks with image paths: {len(blocks_with_images)}")

                return {
                    'status': 'success',
                    'total_items': len(content_blocks),
                    'content_types': content_types,
                    'image_blocks': len(image_blocks),
                    'document_type': 'structured_document_model'
                }
            else:
                # Legacy format - list of items
                content_types = {}
                for item in document:
                    item_type = item.get('type', 'unknown')
                    content_types[item_type] = content_types.get(item_type, 0) + 1

                logger.info(f"✅ Content extractor test: {len(document)} items extracted (legacy format)")
                for content_type, count in content_types.items():
                    logger.info(f"   {content_type}: {count}")

                return {
                    'status': 'success',
                    'total_items': len(document),
                    'content_types': content_types,
                    'document_type': 'legacy_format'
                }

        except Exception as e:
            logger.error(f"❌ Content extractor test failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'status': 'error', 'error': str(e)}
    
    def _generate_diagnostic_report(self, results: Dict[str, Any]):
        """Generate comprehensive diagnostic report"""
        logger.info("\n" + "="*80)
        logger.info("🔍 VISUAL CONTENT EXTRACTION DIAGNOSTIC REPORT")
        logger.info("="*80)
        
        # Summary
        basic = results.get('basic_analysis', {})
        pymupdf = results.get('pymupdf_images', {})
        config = results.get('configuration', {})
        nougat = results.get('nougat_integration', {})
        parser = results.get('pdf_parser', {})
        extractor = results.get('content_extractor', {})
        
        logger.info(f"📄 PDF: {os.path.basename(results['pdf_path'])}")
        logger.info(f"📊 Basic Analysis: {basic.get('total_images', 0)} images in PDF")
        logger.info(f"🖼️ PyMuPDF Test: {pymupdf.get('extracted_count', 0)} images extracted")
        logger.info(f"⚙️ Configuration: {'✅' if config.get('status') == 'success' else '❌'}")
        logger.info(f"🧠 Nougat: {'✅' if nougat.get('status') == 'success' else '❌'} ({nougat.get('visual_elements_count', 0)} elements)")
        logger.info(f"📝 PDF Parser: {'✅' if parser.get('status') == 'success' else '❌'} ({parser.get('extracted_count', 0)} images)")
        logger.info(f"📋 Content Extractor: {'✅' if extractor.get('status') == 'success' else '❌'} ({extractor.get('total_items', 0)} items)")
        
        # Detailed analysis
        logger.info("\n🔍 DETAILED ANALYSIS:")
        
        if basic.get('total_images', 0) == 0:
            logger.info("❌ ISSUE: No images found in PDF by basic analysis")
            logger.info("   • PDF may not contain embedded images")
            logger.info("   • Images may be vector graphics or text-based diagrams")
            logger.info("   • Consider using Nougat for visual element detection")
        
        if config.get('config', {}).get('extract_images') == False:
            logger.info("❌ ISSUE: Image extraction disabled in configuration")
            logger.info("   • Set extract_images = True in config.ini")
        
        if nougat.get('status') != 'success':
            logger.info("⚠️ WARNING: Nougat integration not working optimally")
            logger.info(f"   • Status: {nougat.get('status', 'unknown')}")
            logger.info(f"   • Message: {nougat.get('message', 'No details')}")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        
        total_images = basic.get('total_images', 0)
        extracted_images = parser.get('extracted_count', 0)
        
        if total_images == 0:
            logger.info("1. PDF contains no embedded images")
            logger.info("   • Use Nougat to detect visual elements (diagrams, tables, equations)")
            logger.info("   • Enable figure extraction by caption")
            logger.info("   • Check if content is text-based with visual formatting")
        elif total_images > 0 and extracted_images == 0:
            logger.info("1. Images exist but extraction failed")
            logger.info("   • Check image size thresholds in config.ini")
            logger.info("   • Verify image extraction is enabled")
            logger.info("   • Check for permission issues with output directory")
        elif total_images > 0 and extracted_images > 0:
            logger.info("1. Image extraction working correctly")
            logger.info("   • Check content extractor integration")
            logger.info("   • Verify image placement in final document")
        
        logger.info("="*80)

def main():
    """Main diagnostic function"""
    
    if len(sys.argv) < 2:
        # Use a default test PDF if available
        test_pdfs = [
            "test.pdf",
            "sample.pdf",
            "document.pdf"
        ]
        
        pdf_path = None
        for test_pdf in test_pdfs:
            if os.path.exists(test_pdf):
                pdf_path = test_pdf
                break
        
        if not pdf_path:
            logger.error("❌ No PDF file specified and no test PDF found")
            logger.info("Usage: python diagnose_visual_content_extraction.py <pdf_path>")
            return False
    else:
        pdf_path = sys.argv[1]
    
    diagnostic = VisualContentDiagnostic()
    results = diagnostic.diagnose_pdf(pdf_path)
    
    return results.get('basic_analysis', {}).get('status') == 'success'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
