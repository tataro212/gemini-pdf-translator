#!/usr/bin/env python3
"""
Test Script for Structured Document Model

This script tests the new structured document model implementation
to ensure all components work together correctly.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_document_model():
    """Test the basic document model functionality"""
    logger.info("🧪 Testing Document Model...")
    
    try:
        from document_model import Document, Page, Heading, Paragraph, Footnote, Table
        
        # Create a test document
        doc = Document(title="Test Document")
        
        # Create a test page
        page1 = Page(page_number=1)
        
        # Add various content blocks
        heading1 = Heading(content="Introduction", level=1, page_num=1)
        paragraph1 = Paragraph(content="This is a test paragraph with some content.", page_num=1)
        footnote1 = Footnote(content="This is a footnote.", reference_id="1", page_num=1)
        table1 = Table(content="| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |", page_num=1)
        
        # Add blocks to page
        page1.add_block(heading1)
        page1.add_block(paragraph1)
        page1.add_block(footnote1)
        page1.add_block(table1)
        
        # Add page to document
        doc.add_page(page1)
        
        # Test document statistics
        stats = doc.get_statistics()
        logger.info(f"✅ Document created successfully:")
        logger.info(f"   • Title: {doc.title}")
        logger.info(f"   • Pages: {stats['total_pages']}")
        logger.info(f"   • Total blocks: {stats['total_blocks']}")
        logger.info(f"   • Headings: {stats['headings']}")
        logger.info(f"   • Paragraphs: {stats['paragraphs']}")
        logger.info(f"   • Footnotes: {stats['footnotes']}")
        
        # Test serialization
        doc_dict = doc.to_dict()
        logger.info(f"✅ Document serialization successful")
        
        # Test deserialization
        from document_model import create_document_from_dict
        restored_doc = create_document_from_dict(doc_dict)
        logger.info(f"✅ Document deserialization successful")
        logger.info(f"   • Restored title: {restored_doc.title}")
        logger.info(f"   • Restored blocks: {len(restored_doc.get_all_content_blocks())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document model test failed: {e}")
        return False

def test_nougat_processor():
    """Test the nougat processor with structured output"""
    logger.info("🧪 Testing Nougat Processor...")
    
    try:
        from nougat_first_processor import nougat_first_processor
        
        # Test if processor has the new structured method
        if hasattr(nougat_first_processor, 'process_document_structured'):
            logger.info("✅ Structured processing method found")
            return True
        else:
            logger.warning("⚠️ Structured processing method not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Nougat processor test failed: {e}")
        return False

def test_translation_service():
    """Test the translation service with structured content"""
    logger.info("🧪 Testing Translation Service...")
    
    try:
        from async_translation_service import AsyncTranslationService
        
        # Create service instance
        service = AsyncTranslationService()
        
        # Test if service has the new structured method
        if hasattr(service, 'translate_document_structured'):
            logger.info("✅ Structured translation method found")
            return True
        else:
            logger.warning("⚠️ Structured translation method not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Translation service test failed: {e}")
        return False

def test_assembler():
    """Test the high-fidelity assembler"""
    logger.info("🧪 Testing High-Fidelity Assembler...")
    
    try:
        from high_fidelity_assembler import HighFidelityAssembler
        
        # Create assembler instance
        assembler = HighFidelityAssembler()
        
        # Test if assembler has the new structured method
        if hasattr(assembler, 'assemble_structured_document'):
            logger.info("✅ Structured assembly method found")
            return True
        else:
            logger.warning("⚠️ Structured assembly method not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Assembler test failed: {e}")
        return False

def test_integration():
    """Test the complete integration workflow"""
    logger.info("🧪 Testing Complete Integration...")
    
    try:
        from document_model import Document, Page, Heading, Paragraph
        from high_fidelity_assembler import HighFidelityAssembler
        
        # Create a test document
        doc = Document(title="Integration Test Document")
        page1 = Page(page_number=1)
        
        heading1 = Heading(content="Test Heading", level=1, page_num=1)
        paragraph1 = Paragraph(content="This is a test paragraph for integration testing.", page_num=1)
        
        page1.add_block(heading1)
        page1.add_block(paragraph1)
        doc.add_page(page1)
        
        # Test assembler with structured document
        assembler = HighFidelityAssembler()
        
        # Create a test output file
        test_output = "test_output.html"
        
        success = assembler.assemble_structured_document(doc, test_output)
        
        if success and os.path.exists(test_output):
            logger.info("✅ Integration test successful - HTML file created")
            
            # Clean up test file
            os.remove(test_output)
            return True
        else:
            logger.warning("⚠️ Integration test failed - no output file created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Structured Document Model Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Document Model", test_document_model),
        ("Nougat Processor", test_nougat_processor),
        ("Translation Service", test_translation_service),
        ("Assembler", test_assembler),
        ("Integration", test_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} Test: PASSED")
            else:
                logger.warning(f"⚠️ {test_name} Test: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} Test: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Structured document model is ready.")
        return 0
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
