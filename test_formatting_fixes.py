#!/usr/bin/env python3
"""
Test script to verify the formatting fixes for line breaks and TOC page numbering
"""

import os
import sys
import logging
import asyncio
from main_workflow import UltimatePDFTranslator
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_text_splitting():
    """Test the enhanced text splitting logic"""
    logger.info("🧪 Testing enhanced text splitting logic...")
    
    from optimization_manager import SmartGroupingProcessor
    
    processor = SmartGroupingProcessor()
    
    # Test case 1: Text that should not be split into artificial paragraphs
    test_text = """This is a continuous paragraph that should remain as one unit. It contains multiple sentences that flow naturally together. The previous version would incorrectly split this into multiple paragraphs.

This is a second paragraph that should be separate. It has its own meaning and context. This should remain as a distinct unit.

This is a third paragraph with its own content. It should also remain intact without artificial line breaks."""
    
    # Create mock original group
    original_group = [
        {'text': 'First item text', 'type': 'paragraph'},
        {'text': 'Second item text', 'type': 'paragraph'},
        {'text': 'Third item text', 'type': 'paragraph'}
    ]
    
    # Test the splitting
    result = processor.split_translated_group(test_text, original_group)
    
    logger.info(f"✅ Split result: {len(result)} items")
    for i, item in enumerate(result):
        logger.info(f"  Item {i+1}: {item['text'][:100]}...")
        
    return len(result) == len(original_group)

def test_page_estimation():
    """Test the enhanced page estimation for TOC"""
    logger.info("🧪 Testing enhanced page estimation...")
    
    from document_generator import PageEstimator
    
    estimator = PageEstimator()
    
    # Test with various content types that should span multiple pages
    long_paragraph = 'This is a very long paragraph with substantial content that would take multiple lines in a document. It contains detailed information and explanations that would naturally span several lines when formatted in a Word document. ' * 3

    test_content = [
        {'type': 'h1', 'text': 'Chapter 1: Introduction'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'h2', 'text': 'Section 1.1: Overview'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'image', 'filename': 'test.png'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'h1', 'text': 'Chapter 2: Methodology'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'h2', 'text': 'Section 2.1: Data Collection'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'image', 'filename': 'test2.png'},
        {'type': 'paragraph', 'text': long_paragraph},
        {'type': 'h1', 'text': 'Chapter 3: Results'},
        {'type': 'paragraph', 'text': long_paragraph},
    ]
    
    page_progression = []
    for item in test_content:
        estimator.process_item(item)
        current_page = estimator.get_current_page()
        page_progression.append((item['type'], current_page))
        logger.info(f"  {item['type']}: Page {current_page}")
    
    stats = estimator.get_estimation_stats()
    logger.info(f"✅ Estimation stats: {stats}")
    
    # Check that pages progress logically
    pages = [p[1] for p in page_progression]
    is_logical = all(pages[i] <= pages[i+1] for i in range(len(pages)-1))
    
    return is_logical and pages[-1] > 1  # Should have multiple pages

def test_toc_generation():
    """Test TOC generation with proper page numbers"""
    logger.info("🧪 Testing TOC generation...")
    
    from document_generator import WordDocumentGenerator
    
    generator = WordDocumentGenerator()
    
    # Create test content with headings
    test_content = [
        {'type': 'h1', 'text': 'Introduction', 'page_num': 1},
        {'type': 'paragraph', 'text': 'Introduction content.'},
        {'type': 'h2', 'text': 'Background', 'page_num': 1},
        {'type': 'paragraph', 'text': 'Background content.'},
        {'type': 'h1', 'text': 'Methodology', 'page_num': 2},
        {'type': 'paragraph', 'text': 'Methodology content.'},
        {'type': 'h2', 'text': 'Data Collection', 'page_num': 3},
        {'type': 'paragraph', 'text': 'Data collection content.'},
        {'type': 'h1', 'text': 'Results', 'page_num': 4},
        {'type': 'paragraph', 'text': 'Results content.'},
    ]
    
    # Extract TOC headings
    headings = generator._extract_toc_headings(test_content)
    
    logger.info(f"✅ Extracted {len(headings)} TOC headings:")
    for heading in headings:
        logger.info(f"  {heading['level']}: {heading['text']} - Page {heading['estimated_page']}")
    
    # Check that page numbers are reasonable and progressive
    h1_pages = [h['estimated_page'] for h in headings if h['level'] == 1]
    is_progressive = all(h1_pages[i] <= h1_pages[i+1] for i in range(len(h1_pages)-1))
    
    return len(headings) > 0 and is_progressive and not all(p == 1 for p in h1_pages)

async def test_full_workflow():
    """Test the full workflow with a small document"""
    logger.info("🧪 Testing full workflow...")
    
    # Check if we have any PDF files to test with
    test_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not test_files:
        logger.warning("No PDF files found for full workflow test")
        return True
    
    # Use the first available PDF file
    test_file = test_files[0]
    logger.info(f"Testing with file: {test_file}")
    
    # Create output directory
    output_dir = "test_formatting_output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        translator = UltimatePDFTranslator()
        await translator.translate_document_async(test_file, output_dir)
        
        # Check if output files were created
        word_file = os.path.join(output_dir, f"{os.path.splitext(test_file)[0]}_translated.docx")
        pdf_file = os.path.join(output_dir, f"{os.path.splitext(test_file)[0]}_translated.pdf")
        
        word_exists = os.path.exists(word_file)
        pdf_exists = os.path.exists(pdf_file)
        
        logger.info(f"✅ Word file created: {word_exists}")
        logger.info(f"✅ PDF file created: {pdf_exists}")
        
        return word_exists
        
    except Exception as e:
        logger.error(f"Full workflow test failed: {e}")
        return False

async def main():
    """Run all formatting tests"""
    logger.info("🚀 Starting formatting fixes verification tests...")
    
    tests = [
        ("Text Splitting", test_text_splitting),
        ("Page Estimation", test_page_estimation),
        ("TOC Generation", test_toc_generation),
    ]
    
    results = {}
    
    # Run individual component tests
    for test_name, test_func in tests:
        try:
            logger.info(f"\n--- Running {test_name} Test ---")
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Run full workflow test if component tests pass
    if all(results.values()):
        logger.info(f"\n--- Running Full Workflow Test ---")
        try:
            workflow_result = await test_full_workflow()
            results["Full Workflow"] = workflow_result
            status = "✅ PASSED" if workflow_result else "❌ FAILED"
            logger.info(f"Full Workflow: {status}")
        except Exception as e:
            logger.error(f"Full workflow test failed with error: {e}")
            results["Full Workflow"] = False
    
    # Summary
    logger.info(f"\n🎯 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All formatting fixes are working correctly!")
        return True
    else:
        logger.warning("⚠️ Some tests failed. Please review the fixes.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
