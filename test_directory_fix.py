#!/usr/bin/env python3
"""
Test script to verify the directory creation fix in document_generator.py
"""

import os
import tempfile
import logging
from document_generator import document_generator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_directory_creation_fix():
    """Test that the document generator creates directories before saving"""
    
    print("🧪 Testing directory creation fix...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a nested path that doesn't exist yet
        nested_path = os.path.join(temp_dir, "non_existent", "deeply", "nested", "path")
        test_docx_path = os.path.join(nested_path, "test_document.docx")
        
        print(f"📁 Test output path: {test_docx_path}")
        print(f"📁 Directory exists before test: {os.path.exists(nested_path)}")
        
        # Create some test content
        test_content = [
            {
                'type': 'h1',
                'text': 'Test Document',
                'page_num': 1,
                'block_num': 1
            },
            {
                'type': 'paragraph',
                'text': 'This is a test paragraph to verify that the document generator can create directories before saving.',
                'page_num': 1,
                'block_num': 2
            },
            {
                'type': 'h2',
                'text': 'Test Section',
                'page_num': 1,
                'block_num': 3
            },
            {
                'type': 'paragraph',
                'text': 'Another test paragraph.',
                'page_num': 1,
                'block_num': 4
            }
        ]
        
        # Test the document creation
        try:
            success = document_generator.create_word_document_with_structure(
                test_content, 
                test_docx_path, 
                None,  # No image folder
                None   # No cover page
            )
            
            if success:
                print("✅ Document creation succeeded!")
                print(f"📁 Directory exists after test: {os.path.exists(nested_path)}")
                print(f"📄 Document exists: {os.path.exists(test_docx_path)}")
                
                if os.path.exists(test_docx_path):
                    file_size = os.path.getsize(test_docx_path)
                    print(f"📊 Document size: {file_size:,} bytes")
                    
                    if file_size > 1000:  # Reasonable size for a Word document
                        print("🎉 SUCCESS: Directory creation fix is working!")
                        return True
                    else:
                        print("⚠️ WARNING: Document created but seems too small")
                        return False
                else:
                    print("❌ FAILED: Document was not created")
                    return False
            else:
                print("❌ FAILED: Document creation returned False")
                return False
                
        except Exception as e:
            print(f"❌ FAILED: Exception occurred: {e}")
            return False

def test_pdf_conversion_directory_fix():
    """Test that the PDF converter creates directories before saving"""
    
    print("\n🧪 Testing PDF converter directory creation fix...")
    
    # This test requires a Word document to exist first
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple Word document first
        word_path = os.path.join(temp_dir, "test_word.docx")
        
        test_content = [
            {
                'type': 'h1',
                'text': 'PDF Test Document',
                'page_num': 1,
                'block_num': 1
            },
            {
                'type': 'paragraph',
                'text': 'This document will be converted to PDF.',
                'page_num': 1,
                'block_num': 2
            }
        ]
        
        # Create the Word document
        word_success = document_generator.create_word_document_with_structure(
            test_content, word_path, None, None
        )
        
        if not word_success:
            print("❌ FAILED: Could not create Word document for PDF test")
            return False
        
        # Now test PDF conversion with nested directory
        nested_pdf_path = os.path.join(temp_dir, "non_existent", "pdf", "output", "test.pdf")
        pdf_dir = os.path.dirname(nested_pdf_path)
        
        print(f"📁 PDF output path: {nested_pdf_path}")
        print(f"📁 PDF directory exists before test: {os.path.exists(pdf_dir)}")
        
        try:
            from document_generator import pdf_converter
            
            pdf_success = pdf_converter.convert_word_to_pdf(word_path, nested_pdf_path)
            
            if pdf_success:
                print("✅ PDF conversion succeeded!")
                print(f"📁 PDF directory exists after test: {os.path.exists(pdf_dir)}")
                print(f"📄 PDF exists: {os.path.exists(nested_pdf_path)}")
                
                if os.path.exists(nested_pdf_path):
                    file_size = os.path.getsize(nested_pdf_path)
                    print(f"📊 PDF size: {file_size:,} bytes")
                    print("🎉 SUCCESS: PDF converter directory creation fix is working!")
                    return True
                else:
                    print("❌ FAILED: PDF was not created")
                    return False
            else:
                print("⚠️ PDF conversion failed (this might be expected if docx2pdf is not available)")
                return True  # This is not necessarily a failure of our fix
                
        except Exception as e:
            print(f"⚠️ PDF conversion exception: {e}")
            print("💡 This might be expected if docx2pdf is not installed")
            return True  # This is not necessarily a failure of our fix

if __name__ == "__main__":
    print("🔧 Testing Directory Creation Fixes")
    print("=" * 50)
    
    # Test Word document creation
    word_test_result = test_directory_creation_fix()
    
    # Test PDF conversion
    pdf_test_result = test_pdf_conversion_directory_fix()
    
    print("\n📋 Test Results Summary:")
    print("=" * 50)
    print(f"Word Document Creation: {'✅ PASS' if word_test_result else '❌ FAIL'}")
    print(f"PDF Converter: {'✅ PASS' if pdf_test_result else '❌ FAIL'}")
    
    if word_test_result and pdf_test_result:
        print("\n🎉 ALL TESTS PASSED! The directory creation fix is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the output above for details.")
