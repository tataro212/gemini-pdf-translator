#!/usr/bin/env python3
"""
Simple demonstration of the PDF conversion fix
"""

import os
import logging
from document_generator import PDFConverter, WordDocumentGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_document():
    """Create a test Word document"""
    logger.info("📝 Creating test Word document...")
    
    test_content = [
        {'type': 'h1', 'text': 'Test Document', 'page_num': 1, 'block_num': 1},
        {'type': 'paragraph', 'text': 'This is a test document to demonstrate the PDF conversion fix.', 'page_num': 1, 'block_num': 2},
        {'type': 'h2', 'text': 'Section 1', 'page_num': 1, 'block_num': 3},
        {'type': 'paragraph', 'text': 'Content for section 1 with some detailed information.', 'page_num': 1, 'block_num': 4},
    ]
    
    generator = WordDocumentGenerator()
    word_path = "demo_test.docx"
    
    success = generator.create_word_document_with_structure(
        test_content, word_path, None, None
    )
    
    if success:
        logger.info(f"✅ Test Word document created: {word_path}")
        return word_path
    else:
        logger.error("❌ Failed to create test Word document")
        return None

def test_successful_conversion():
    """Test successful PDF conversion"""
    logger.info("\n🧪 Testing successful PDF conversion...")
    
    word_path = create_test_document()
    if not word_path:
        return False
    
    pdf_path = "demo_test.pdf"
    converter = PDFConverter()
    
    success = converter.convert_word_to_pdf(word_path, pdf_path)
    
    if success:
        logger.info("✅ PDF conversion successful!")
        logger.info(f"   Word file: {word_path}")
        logger.info(f"   PDF file: {pdf_path}")
        
        # Check file sizes
        word_size = os.path.getsize(word_path)
        pdf_size = os.path.getsize(pdf_path)
        logger.info(f"   Word size: {word_size:,} bytes")
        logger.info(f"   PDF size: {pdf_size:,} bytes")
        
        # Clean up
        os.remove(word_path)
        os.remove(pdf_path)
        return True
    else:
        logger.error("❌ PDF conversion failed")
        if os.path.exists(word_path):
            os.remove(word_path)
        return False

def test_workflow_behavior():
    """Test how the workflow behaves with PDF conversion"""
    logger.info("\n🧪 Testing workflow behavior...")
    
    word_path = create_test_document()
    if not word_path:
        return False
    
    pdf_path = "demo_workflow_test.pdf"
    converter = PDFConverter()
    
    # Test the conversion
    success = converter.convert_word_to_pdf(word_path, pdf_path)
    
    # Simulate workflow behavior
    logger.info("📋 Simulating workflow behavior:")
    
    if success:
        logger.info("✅ Word document created successfully")
        logger.info("✅ PDF conversion successful")
        logger.info("📄 Both files available for user")
        
        # Files to upload/report
        files_created = ["Word Document ✅", "PDF Document ✅"]
        
    else:
        logger.info("✅ Word document created successfully")
        logger.info("⚠️ PDF conversion failed, but Word document is available")
        logger.info("💡 User can manually convert Word to PDF if needed")
        
        # Files to upload/report
        files_created = ["Word Document ✅", "PDF Document ❌ (Conversion failed)"]
    
    logger.info("\n📊 Final Status:")
    for file_status in files_created:
        logger.info(f"   • {file_status}")
    
    # Clean up
    if os.path.exists(word_path):
        os.remove(word_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    return True

def demonstrate_error_handling():
    """Demonstrate enhanced error handling"""
    logger.info("\n🧪 Demonstrating enhanced error handling...")
    
    converter = PDFConverter()
    
    # Test with non-existent file
    logger.info("   Testing with non-existent file...")
    success = converter.convert_word_to_pdf("nonexistent.docx", "output.pdf")
    
    if not success:
        logger.info("   ✅ Correctly handled missing input file")
    else:
        logger.error("   ❌ Should have failed with missing input file")
        return False
    
    return True

def main():
    """Run the PDF fix demonstration"""
    logger.info("🎉 PDF CONVERSION FIX DEMONSTRATION")
    logger.info("=" * 50)
    logger.info("This demo shows how the PDF conversion issues are now handled")
    
    tests = [
        ("Successful Conversion", test_successful_conversion),
        ("Workflow Behavior", test_workflow_behavior),
        ("Error Handling", demonstrate_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"\n{test_name}: {status}")
        except Exception as e:
            logger.error(f"\n{test_name}: ❌ FAILED - {e}")
            results.append(False)
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("🎯 DEMONSTRATION SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("\n🎉 PDF CONVERSION FIX IS WORKING!")
        logger.info("✅ Key Improvements:")
        logger.info("   • Enhanced error handling and diagnostics")
        logger.info("   • Graceful fallback when PDF conversion fails")
        logger.info("   • Clear user feedback about file status")
        logger.info("   • Word document always created (primary output)")
        logger.info("   • Helpful troubleshooting suggestions")
        
        logger.info("\n💡 What this means for users:")
        logger.info("   • You'll always get a Word document (.docx)")
        logger.info("   • PDF will be created when possible")
        logger.info("   • Clear messages if PDF conversion fails")
        logger.info("   • Suggestions for manual conversion")
        
    else:
        logger.warning("\n⚠️ Some issues detected. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
